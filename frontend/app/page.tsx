"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import ChatSidebar from "../components/ChatSidebar";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import { uploadFile, submitTask, BACKEND_HTTP_URL } from "../lib/api";
import { connectWebSocket } from "../lib/ws-client";
import { Conversation, ChatMessage as ChatMessageType, TraceEvent, ArtifactRef } from "../lib/types";

const STORAGE_KEY = "setu-conversations";

function generateId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2);
}

function loadConversations(): Conversation[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveConversations(convs: Conversation[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(convs));
}

export default function HomePage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [model, setModel] = useState("auto");
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const userScrolledUpRef = useRef(false);
  const wsCleanupRef = useRef<(() => void) | null>(null);

  const [isLoaded, setIsLoaded] = useState(false);
  const [availableModels, setAvailableModels] = useState<{value: string, label: string}[]>([{value: "auto", label: "Auto"}]);

  // Load from API on mount (fallback to localStorage if offline)
  useEffect(() => {
    import("../lib/api").then(({ getConversations, getModels }) => {
      // 1. Fetch Models
      getModels().then(data => {
        const options = [{ value: "auto", label: "Auto" }];
        data.forEach(m => {
          options.push({ value: m.name, label: m.name });
        });
        setAvailableModels(options);
      }).catch(err => console.error("Failed to load models", err));

      // 2. Fetch Conversations
      getConversations().then(data => {
        setConversations(data);
        if (data.length > 0) setActiveId(data[0].id);
        setIsLoaded(true);
      }).catch(err => {
        console.warn("Backend unavailable, using local storage", err);
        const saved = loadConversations();
        setConversations(saved);
        if (saved.length > 0) setActiveId(saved[0].id);
        setIsLoaded(true);
      });
    });
  }, []);

  // Save to localStorage whenever conversations change (fast cache)
  // And sync the active conversation to the backend if it exists
  useEffect(() => {
    if (isLoaded) {
      saveConversations(conversations);
      const activeConv = conversations.find(c => c.id === activeId);
      if (activeConv && activeConv.messages.length > 0) {
        import("../lib/api").then(({ saveConversationAPI }) => {
          saveConversationAPI(activeConv).catch(console.error);
        });
      }
    }
  }, [conversations, isLoaded, activeId]);

  // Smart auto-scroll: only scroll down if user hasn't manually scrolled up
  useEffect(() => {
    if (!userScrolledUpRef.current) {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [conversations]);

  // Always scroll to bottom on chat switch
  useEffect(() => {
    userScrolledUpRef.current = false;
    chatEndRef.current?.scrollIntoView({ behavior: "instant" });
  }, [activeId]);

  const handleScroll = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const distFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    userScrolledUpRef.current = distFromBottom > 100;
  }, []);

  const activeConversation = conversations.find(c => c.id === activeId) || null;

  const updateConversation = useCallback((id: string, updater: (conv: Conversation) => Conversation) => {
    setConversations(prev => prev.map(c => c.id === id ? updater(c) : c));
  }, []);

  const handleNewChat = () => {
    const newConv: Conversation = {
      id: generateId(),
      title: "New Chat",
      messages: [],
      createdAt: new Date().toISOString(),
      model: model,
    };
    setConversations(prev => [newConv, ...prev]);
    setActiveId(newConv.id);
  };

  const handleDeleteChat = (id: string) => {
    setConversations(prev => prev.filter(c => c.id !== id));
    if (activeId === id) {
      setActiveId(conversations.find(c => c.id !== id)?.id || null);
    }
    // Delete from backend
    import("../lib/api").then(({ deleteConversationAPI }) => {
      deleteConversationAPI(id).catch(console.error);
    });
  };

  const handleStop = async () => {
    if (!currentTaskId) return;
    try {
      await fetch(`${BACKEND_HTTP_URL}/task/${currentTaskId}/cancel`, { method: 'POST' });
    } catch (e) {
      console.error(e);
    }
  };

  const handleSend = async (text: string, file: File | null) => {
    if (isProcessing) return;

    let convId = activeId;

    // Create new conversation if none active
    if (!convId) {
      const newConv: Conversation = {
        id: generateId(),
        title: text.slice(0, 40) || "New Chat",
        messages: [],
        createdAt: new Date().toISOString(),
        model: model,
      };
      setConversations(prev => [newConv, ...prev]);
      convId = newConv.id;
      setActiveId(convId);
    }

    // Update title if first message
    const conv = conversations.find(c => c.id === convId);
    if (conv && conv.messages.length === 0) {
      updateConversation(convId, c => ({ ...c, title: text.slice(0, 40) }));
    }

    // Add user message
    const userMsg: ChatMessageType = {
      id: generateId(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    // Add placeholder AI message
    const aiMsgId = generateId();
    const aiMsg: ChatMessageType = {
      id: aiMsgId,
      role: "assistant",
      content: "",
      timestamp: new Date().toISOString(),
      traceEvents: [],
      artifacts: [],
      isStreaming: true,
    };

    updateConversation(convId, c => ({
      ...c,
      messages: [...c.messages, userMsg, aiMsg],
    }));

    setIsProcessing(true);
    userScrolledUpRef.current = false;

    try {
      let modality: "text" | "image" | "file" = "text";
      let content = text;

      if (file) {
        const uploadedPath = await uploadFile(file);
        content = uploadedPath;
        modality = file.type.startsWith("image/") ? "image" : "file";
      }

      const chatHistory = (conv?.messages || []).map(m => ({
        role: m.role,
        content: m.content
      }));

      const taskId = await submitTask({
        modality,
        content,
        context: { 
          original_instructions: text,
          chat_history: chatHistory
        },
        model_override: model,
      });

      setCurrentTaskId(taskId);

      // Update AI message with taskId
      updateConversation(convId!, c => ({
        ...c,
        messages: c.messages.map(m =>
          m.id === aiMsgId ? { ...m, taskId } : m
        ),
      }));

      // Connect WebSocket for streaming
      if (wsCleanupRef.current) wsCleanupRef.current();

      wsCleanupRef.current = connectWebSocket(taskId, (event: TraceEvent) => {
        updateConversation(convId!, c => ({
          ...c,
          messages: c.messages.map(m => {
            if (m.id !== aiMsgId) return m;

            let updatedEvents = m.traceEvents || [];
            let updatedContent = m.content;
            let updatedArtifacts = m.artifacts || [];
            let stillStreaming = true;

            if (event.step === "stream_chunk") {
              updatedContent += event.payload?.chunk || "";
              
              // Add a trace event for streaming if it doesn't exist
              const hasStreaming = updatedEvents.some(e => e.step === "streaming");
              if (!hasStreaming) {
                updatedEvents = [...updatedEvents, {
                  task_id: event.task_id,
                  step: "streaming",
                  payload: { tool_name: "llm_chat" },
                  timestamp: new Date().toISOString()
                }];
              }
            } else {
              updatedEvents = [...updatedEvents, event];
            }

            if (event.step === "done") {
              // Only override with summary if we didn't stream any content
              if (!updatedContent || updatedContent.trim() === "") {
                updatedContent = event.payload?.summary || "Task completed.";
              }
              updatedArtifacts = event.payload?.artifacts || [];
              stillStreaming = false;
            } else if (event.step === "error") {
              if (!updatedContent || updatedContent.trim() === "") {
                updatedContent = `Error: ${event.payload?.error || "Unknown error"}`;
              }
              stillStreaming = false;
            }

            return {
              ...m,
              content: updatedContent,
              traceEvents: updatedEvents,
              artifacts: updatedArtifacts,
              isStreaming: stillStreaming,
            };
          }),
        }));

        if (event.step === "done" || event.step === "error") {
          setIsProcessing(false);
          setCurrentTaskId(null);
        }
      });
    } catch (err: any) {
      updateConversation(convId!, c => ({
        ...c,
        messages: c.messages.map(m =>
          m.id === aiMsgId
            ? { ...m, content: `Failed to connect: ${err.message}`, isStreaming: false }
            : m
        ),
      }));
      setIsProcessing(false);
      setCurrentTaskId(null);
    }
  };

  return (
    <div className="flex h-screen">
      <ChatSidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={handleNewChat}
        onDelete={handleDeleteChat}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat Messages */}
        <div ref={scrollContainerRef} onScroll={handleScroll} className="flex-1 overflow-y-auto">
          {!activeConversation || activeConversation.messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto px-4 -mt-10 animate-fade-in">
              <div className="text-center flex flex-col items-center mb-10">
                <div className="w-20 h-20 rounded-[24px] shadow-composer overflow-hidden mb-8 ring-1 ring-[var(--border)] animate-float">
                  <img src="/logo.jpg" alt="SETU AI" className="w-full h-full object-cover" />
                </div>
                <h1 className="text-3xl font-semibold text-[var(--foreground)] tracking-tight mb-3">SetuAI</h1>
                <p className="text-[15px] text-[var(--foreground-muted)]">Sovereign AI Workbench</p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg">
                {[
                  { title: "Analyze a document", desc: "Extract insights from PDFs or SOPs" },
                  { title: "Generate something", desc: "Draft approval notes or code" },
                  { title: "Work with my data", desc: "Create dashboards and spreadsheets" },
                  { title: "Explore an idea", desc: "Brainstorm and research securely" }
                ].map((card, idx) => (
                  <button 
                    key={idx} 
                    onClick={() => handleSend(card.desc, null)}
                    className="flex flex-col text-left p-4 rounded-[16px] bg-[var(--input-bg)] border border-[var(--border)] hover:border-[var(--border-hover)] shadow-sm hover:shadow-card transition-all duration-200 group"
                  >
                    <span className="text-[13px] font-semibold text-[var(--foreground)] mb-1 group-hover:text-blue-600 transition-colors">{card.title}</span>
                    <span className="text-[12px] text-[var(--foreground-muted)]">{card.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto py-6">
              {activeConversation.messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              <div ref={chatEndRef} />
            </div>
          )}
        </div>

        {/* Input Bar */}
        <ChatInput
          onSend={handleSend}
          disabled={isProcessing}
          isGenerating={isProcessing}
          onStop={handleStop}
          model={model}
          onModelChange={setModel}
          availableModels={availableModels}
        />
      </div>
    </div>
  );
}
