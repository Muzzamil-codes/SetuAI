"use client";
import React, { useState, useEffect, useRef, useCallback } from "react";
import ChatSidebar from "../components/ChatSidebar";
import ChatMessage from "../components/ChatMessage";
import ChatInput from "../components/ChatInput";
import { uploadFile, submitTask } from "../lib/api";
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
  const chatEndRef = useRef<HTMLDivElement>(null);
  const wsCleanupRef = useRef<(() => void) | null>(null);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = loadConversations();
    setConversations(saved);
    if (saved.length > 0) setActiveId(saved[0].id);
  }, []);

  // Save to localStorage whenever conversations change
  useEffect(() => {
    if (conversations.length > 0) saveConversations(conversations);
  }, [conversations]);

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversations, activeId]);

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

    try {
      let modality: "text" | "image" | "file" = "text";
      let content = text;

      if (file) {
        const uploadedPath = await uploadFile(file);
        content = uploadedPath;
        modality = file.type.startsWith("image/") ? "image" : "file";
      }

      const taskId = await submitTask({
        modality,
        content,
        context: { original_instructions: text },
        model_override: model,
      });

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

            const updatedEvents = [...(m.traceEvents || []), event];
            let updatedContent = m.content;
            let updatedArtifacts = m.artifacts || [];
            let stillStreaming = true;

            if (event.step === "done") {
              updatedContent = event.payload?.summary || "Task completed.";
              updatedArtifacts = event.payload?.artifacts || [];
              stillStreaming = false;
            } else if (event.step === "error") {
              updatedContent = `Error: ${event.payload?.error || "Unknown error"}`;
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
        <div className="flex-1 overflow-y-auto">
          {!activeConversation || activeConversation.messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <h1 className="text-2xl font-semibold text-white mb-2">SETU AI</h1>
                <p className="text-sm text-[#666]">Sovereign AI Workbench</p>
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
          model={model}
          onModelChange={setModel}
        />
      </div>
    </div>
  );
}
