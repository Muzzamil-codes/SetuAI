"""
Unit tests for _clean_hallucinated_download_links in manager.py.
Verifies that hallucinated simulated links, fake download URLs, and unauthorized
document claims are completely stripped when no artifacts are requested or generated.
"""
import sys
import os
import pytest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from orchestrator.agent_graph.manager import _clean_hallucinated_download_links


def test_clean_hallucinated_asme_simulated_link():
    text = """
### ✅ Final Answer: 5.1 mm (minimum required wall thickness)

### 📁 Official Document Ready for Download

✅ Your **complete final report**, including all steps, formulas, and verification, is **already compiled** and available as an official document.

👉 **Download the final document**:  
[Download Final ASME B31.3 Pipe Thickness Report](http://localhost:3000/link-to-file) *(Note: This is a simulated link for demonstration; in real use, the file would be generated and attached)*

---

✅ **SetuAI** — Industrial Engineering & Plant Operations AI System
"""
    cleaned = _clean_hallucinated_download_links(text, has_artifacts=False)
    assert "5.1 mm" in cleaned
    assert "SetuAI" in cleaned
    assert "link-to-file" not in cleaned
    assert "simulated link" not in cleaned
    assert "Official Document Ready" not in cleaned
    assert "Download the final document" not in cleaned


def test_clean_modbus_simulated_link():
    text = """
📌 **Final Action for User**  
👉 **Your official pressure monitoring script is now ready for download.**

📎 **Download the complete document** (script + test results + logs) below:

[📥 Download PressureMonitoringScript_v1.0.docx](file://pressure_monitoring_script_v1.0.docx)

> ⚠️ *Note: This link is a simulated file path for demonstration. In a real environment, the actual file would be generated and made available via your system or cloud interface.*

---

✅ **SetuAI — Industrial Automation Specialist**
"""
    cleaned = _clean_hallucinated_download_links(text, has_artifacts=False)
    assert "simulated file path" not in cleaned
    assert "file://" not in cleaned
    assert "ready for download" not in cleaned
    assert "Download the complete document" not in cleaned


def test_clean_markdown_link_when_artifacts_exist():
    text = """
I have generated the official report for your inspection.
👉 [Download Report](http://localhost:3000/link-to-file)
The file is attached below.
"""
    cleaned = _clean_hallucinated_download_links(text, has_artifacts=True)
    # When artifacts exist, fake URLs are stripped to plain text
    assert "http://localhost:3000/link-to-file" not in cleaned
    assert "Download Report" in cleaned
    assert "The file is attached below." in cleaned
