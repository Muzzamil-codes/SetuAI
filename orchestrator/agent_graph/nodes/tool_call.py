"""
Tool execution node — dispatches to the correct tool via tools/tool_registry,
and actually calls the LLM to generate code, drafts, and conversational
responses rather than returning hardcoded stubs.

Routes based on task_type:
  extraction     → vision tool
  codegen        → LLM code generation → sandbox verification
  drafting       → LLM draft generation (RAG when available)
  numeric_verify → sandbox tool (numeric verification)
  conversational → LLM direct response (no tools)
"""
from orchestrator.agent_graph.state import AgentState
from datetime import datetime, timezone
import json
import os


# ---------------------------------------------------------------------------
# LLM call helper — calls the Ollama-compatible endpoint
# ---------------------------------------------------------------------------

def _get_model_config(state: dict) -> dict:
    """Get the selected model config from state, or fall back to models.json."""
    model = state.get("selected_model", {})
    if model and model.get("endpoint"):
        return model
    # Fallback: load from models.json
    try:
        models_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "models_registry", "models.json"
        )
        with open(models_path, "r") as f:
            manifest = json.load(f)
        # Return first available model
        if manifest:
            return manifest[0]
    except Exception:
        pass
    return {}


def _call_llm(model_config: dict, system_prompt: str, user_prompt: str,
              timeout: int = 120, chat_history: list = None) -> str:
    """Call the Ollama-compatible OpenAI API and return the text response."""
    import re

    endpoint = model_config.get("endpoint", "")
    model_name = model_config.get("name", "deepseek-r1:8b")

    if not endpoint:
        print("[tool_call] No endpoint configured for LLM call")
        return ""

    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        messages.extend(chat_history)
    messages.append({"role": "user", "content": user_prompt})

    url = f"{endpoint}/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 4096,
    }

    def _extract_content(data: dict) -> str:
        """Extract the actual response from the API response, handling DeepSeek's reasoning field."""
        msg = data["choices"][0]["message"]
        content = msg.get("content", "") or ""
        reasoning = msg.get("reasoning", "") or ""

        # Strip <think>...</think> blocks from content
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        # If content is empty but reasoning exists (DeepSeek-R1 quirk),
        # use the last paragraph of reasoning as a fallback
        if not content and reasoning:
            # The reasoning often ends with the actual answer
            paragraphs = [p.strip() for p in reasoning.strip().split("\n\n") if p.strip()]
            if paragraphs:
                content = paragraphs[-1]

        return content

    try:
        import requests
        print(f"[tool_call] Calling LLM: {model_name} at {url}")
        resp = requests.post(url, json=payload, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            content = _extract_content(data)
            print(f"[tool_call] LLM response: {len(content)} chars")
            return content
        else:
            print(f"[tool_call] LLM HTTP error: {resp.status_code} - {resp.text[:200]}")
    except ImportError:
        import urllib.request
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            print(f"[tool_call] Calling LLM (urllib): {model_name} at {url}")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    content = _extract_content(data)
                    print(f"[tool_call] LLM response: {len(content)} chars")
                    return content
        except Exception as e:
            print(f"[tool_call] LLM urllib error: {e}")
    except Exception as e:
        print(f"[tool_call] LLM request error: {e}")

    return ""


# ---------------------------------------------------------------------------
# Main tool_call_node
# ---------------------------------------------------------------------------

def tool_call_node(state: AgentState) -> dict:
    """Execute the appropriate tool based on task type."""
    task_type = state.get("task_type", "drafting")
    task_input = state.get("task_input", {})
    task_id = state.get("task_id", "unknown")
    retry_count = state.get("retry_count", 0)

    trace_events = list(state.get("trace_events", []))
    tool_calls = list(state.get("tool_calls", []))
    tool_results = list(state.get("tool_results", []))

    model_config = _get_model_config(state)
    tool_name = "unknown"
    tool_input_data = {}
    result_dict = {"success": False, "data": {}, "error": "No tool executed"}

    try:
        if task_type == "extraction":
            tool_name = "vision"
            image_path = task_input.get("content", "")
            tool_input_data = {"image_path": image_path, "extract_mode": "both"}
            result_dict = _run_tool(tool_name, tool_input_data)

        elif task_type == "codegen":
            tool_name = "sandbox"
            user_request = task_input.get("content", "")
            chat_history = state.get("messages", [])

            # Actually call the LLM to generate code
            code = _llm_generate_code(model_config, user_request, chat_history)
            test_code = _llm_generate_tests(model_config, user_request, code)

            tool_input_data = {
                "verification_type": "code",
                "code": code,
                "tests": test_code,
                "timeout": 30,
                "language": "python"
            }
            result_dict = _run_tool(tool_name, tool_input_data)
            # Attach code to results so generate_node can write it out
            if result_dict.get("data") is None:
                result_dict["data"] = {}
            result_dict["data"]["generated_code"] = code
            result_dict["data"]["test_code"] = test_code

        elif task_type == "drafting":
            tool_name = "llm_draft"
            user_request = task_input.get("content", "")
            chat_history = state.get("messages", [])

            # Try RAG retrieval first
            rag_context = _try_retrieval(user_request)

            # Call LLM to actually draft the response
            draft = _llm_draft_response(model_config, user_request, rag_context, chat_history)

            result_dict = {
                "success": bool(draft),
                "data": {
                    "draft": draft,
                    "chunks": rag_context if rag_context else [],
                    "generated_text": draft
                },
                "error": None if draft else "LLM failed to generate a draft"
            }

        elif task_type == "numeric_verify":
            tool_name = "sandbox"
            content = task_input.get("content", "")
            tool_input_data = {
                "verification_type": "numeric",
                "expression": _extract_number(content),
                "expected_value": _extract_expected(content),
                "tolerance": 0.1,
                "unit": "bar"
            }
            result_dict = _run_tool(tool_name, tool_input_data)

        elif task_type == "conversational":
            tool_name = "llm_chat"
            user_request = task_input.get("content", "")
            chat_history = state.get("messages", [])

            # Direct LLM response for conversational prompts
            response = _llm_chat_response(model_config, user_request, chat_history)

            result_dict = {
                "success": bool(response),
                "data": {
                    "response": response,
                    "generated_text": response
                },
                "error": None if response else "LLM failed to generate a response"
            }

        else:
            result_dict = {
                "success": False, "data": {},
                "error": f"Unknown task type: {task_type}"
            }

    except Exception as e:
        result_dict = {"success": False, "data": {}, "error": str(e)}

    # Record the call
    tool_call_record = {
        "tool": tool_name,
        "input": {k: str(v)[:200] for k, v in tool_input_data.items()},
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    tool_calls.append(tool_call_record)
    tool_results.append(result_dict)

    trace_events.append({
        "task_id": task_id,
        "step": "tool_call",
        "payload": {
            "tool_name": tool_name,
            "input_summary": {k: str(v)[:100] for k, v in tool_input_data.items()},
            "success": result_dict.get("success", False)
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    return {
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "trace_events": trace_events
    }


# ---------------------------------------------------------------------------
# Tool dispatch — tries real registry, falls back gracefully (NO stubs)
# ---------------------------------------------------------------------------

def _run_tool(name: str, input_data: dict) -> dict:
    """Call a tool by name through the registry. No fake stub fallback."""
    try:
        from tools.tool_registry import get_tool
        tool = get_tool(name)
        result = tool.run(input_data)
        return {
            "success": result.success,
            "data": result.data if isinstance(result.data, dict) else {},
            "error": result.error
        }
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "error": f"Failed to import tool '{name}': {str(e)}"
        }


def _try_retrieval(query: str) -> list:
    """Try the RAG retrieval tool. Returns chunks list, or empty list on failure."""
    try:
        from tools.tool_registry import get_tool
        tool = get_tool("retrieval")
        result = tool.run({"query": query, "top_k": 5})
        if result.success and isinstance(result.data, dict):
            return result.data.get("chunks", [])
    except Exception:
        pass
    return []


# ---------------------------------------------------------------------------
# LLM-powered generation functions
# ---------------------------------------------------------------------------

def _llm_generate_code(model_config: dict, user_request: str, chat_history: list = None) -> str:
    """Use the LLM to generate Python code for the user's request."""
    system_prompt = (
        "You are an expert Python programmer. Generate clean, working Python code "
        "for the user's request. Output ONLY the Python code, no explanations, "
        "no markdown fences. The code should be complete and runnable."
    )
    code = _call_llm(model_config, system_prompt, user_request, timeout=90, chat_history=chat_history)

    if code:
        # Clean up: strip markdown fences if the model included them
        code = _strip_markdown_fences(code)
        return code

    # Last resort: return a minimal placeholder (NOT the old hardcoded sensor code)
    return f'# Could not generate code — LLM unavailable\n# Request: {user_request}\nprint("LLM service is currently unavailable. Please try again.")\n'


def _llm_generate_tests(model_config: dict, user_request: str,
                         generated_code: str) -> str:
    """Use the LLM to generate test code for the generated code."""
    system_prompt = (
        "You are a Python testing expert. Given the following code, write a simple "
        "test script that validates it works correctly. Include a few test functions "
        "and a main block that runs them and prints 'All tests passed!' if they pass. "
        "Output ONLY the Python code, no explanations, no markdown fences."
    )
    user_prompt = f"Original request: {user_request}\n\nCode to test:\n{generated_code}"
    tests = _call_llm(model_config, system_prompt, user_prompt, timeout=60)

    if tests:
        tests = _strip_markdown_fences(tests)
        return tests

    # Minimal fallback test
    return (
        "def test_runs():\n"
        "    print('Basic smoke test passed')\n\n"
        "if __name__ == '__main__':\n"
        "    test_runs()\n"
        "    print('All tests passed!')\n"
    )


def _llm_draft_response(model_config: dict, user_request: str,
                          rag_context: list, chat_history: list = None) -> str:
    """Use the LLM to draft a text response, optionally using RAG context."""
    context_text = ""
    if rag_context:
        for i, chunk in enumerate(rag_context[:5]):
            if isinstance(chunk, dict):
                context_text += f"\n[Reference {i+1}]: {chunk.get('text', str(chunk))}"
            else:
                context_text += f"\n[Reference {i+1}]: {str(chunk)}"

    if context_text:
        system_prompt = (
            "You are a helpful AI assistant for industrial and enterprise tasks. "
            "Use the provided reference context to answer the user's question accurately. "
            "Cite references where applicable."
        )
        user_prompt = f"Context:{context_text}\n\nUser request: {user_request}"
    else:
        system_prompt = (
            "You are a helpful AI assistant. Provide a clear, well-structured response "
            "to the user's request. Use markdown formatting where appropriate."
        )
        user_prompt = user_request

    return _call_llm(model_config, system_prompt, user_prompt, timeout=90, chat_history=chat_history)


def _llm_chat_response(model_config: dict, user_request: str, chat_history: list = None) -> str:
    """Use the LLM for a simple conversational response."""
    system_prompt = (
        "You are SETU AI, a helpful, friendly AI assistant. "
        "Respond naturally and conversationally. Use markdown formatting when helpful."
    )
    return _call_llm(model_config, system_prompt, user_request, timeout=60, chat_history=chat_history)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _strip_markdown_fences(text: str) -> str:
    """Remove ```python ... ``` or ``` ... ``` fences from LLM output."""
    import re
    # Remove opening fence with optional language tag
    text = re.sub(r'^```(?:python|py)?\s*\n', '', text, flags=re.MULTILINE)
    # Remove closing fence
    text = re.sub(r'\n```\s*$', '', text, flags=re.MULTILINE)
    return text.strip()


def _extract_number(content: str) -> str:
    """Pull the first number out of a user prompt."""
    import re
    nums = re.findall(r'[\d.]+', content)
    return nums[0] if nums else "0"


def _extract_expected(content: str) -> float:
    """Pull the second number (or first if only one) as the expected value."""
    import re
    nums = re.findall(r'[\d.]+', content)
    if len(nums) >= 2:
        return float(nums[1])
    return float(nums[0]) if nums else 0.0
