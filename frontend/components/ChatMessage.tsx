"use client";
import React, { useState } from "react";
import { ChatMessage as ChatMessageType, TraceEvent, ArtifactRef } from "../lib/types";
import MarkdownRenderer from "./MarkdownRenderer";
import { ChevronRight, ChevronDown, User, Bot, Download, FileText, FileSpreadsheet, File } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

function StepBadge({ step }: { step: string }) {
  const colors: Record<string, string> = {
    classify: "bg-[#2a2a2a] text-[#aaa]",
    plan: "bg-[#2a2a2a] text-[#aaa]",
    tool_call: "bg-[#2a2a2a] text-[#aaa]",
    verify_pass: "bg-[#1a2a1a] text-[#6a6]",
    verify_fail: "bg-[#2a1a1a] text-[#a66]",
    retry: "bg-[#2a2a1a] text-[#aa6]",
    generate: "bg-[#2a2a2a] text-[#aaa]",
    done: "bg-[#1a2a1a] text-[#6a6]",
    error: "bg-[#2a1a1a] text-[#a66]",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-mono ${colors[step] || "bg-[#2a2a2a] text-[#888]"}`}>
      {step}
    </span>
  );
}

function ArtifactCard({ artifact }: { artifact: ArtifactRef }) {
  const icon = artifact.type === "docx" ? <FileText className="w-4 h-4" /> :
               artifact.type === "xlsx" ? <FileSpreadsheet className="w-4 h-4" /> :
               <File className="w-4 h-4" />;
  
  const handleDownload = () => {
    const url = `${BACKEND_URL}/download/${artifact.path}`;
    window.open(url, "_blank");
  };

  return (
    <button
      onClick={handleDownload}
      className="flex items-center gap-2 px-3 py-2 rounded-lg border border-[#2a2a2a] hover:border-[#444] bg-[#111] hover:bg-[#1a1a1a] transition text-xs"
    >
      {icon}
      <span className="text-[#ccc]">{artifact.filename}</span>
      <Download className="w-3 h-3 text-[#666]" />
    </button>
  );
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [showTrace, setShowTrace] = useState(false);
  const isUser = message.role === "user";
  const traceEvents = message.traceEvents || [];
  const artifacts = message.artifacts || [];
  const hasTrace = traceEvents.length > 0;

  return (
    <div className={`flex gap-3 px-4 py-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-[#2a2a2a] flex items-center justify-center shrink-0 mt-1">
          <Bot className="w-4 h-4 text-[#888]" />
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? "order-first" : ""}`}>
        <div className={`rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-[#2a2a2a] text-white"
            : "bg-[#161616] border border-[#2a2a2a] text-[#ddd]"
        }`}>
          {isUser ? (
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div>
              {message.isStreaming && !message.content ? (
                <div className="flex items-center gap-2 text-sm text-[#888]">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                  <span>Thinking...</span>
                </div>
              ) : (
                <MarkdownRenderer content={message.content} />
              )}
            </div>
          )}
        </div>

        {/* Artifacts */}
        {artifacts.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-2">
            {artifacts.map((a, i) => <ArtifactCard key={i} artifact={a} />)}
          </div>
        )}

        {/* Collapsible Pipeline Details */}
        {!isUser && hasTrace && (
          <div className="mt-2">
            <button
              onClick={() => setShowTrace(!showTrace)}
              className="flex items-center gap-1.5 text-[11px] text-[#666] hover:text-[#aaa] transition"
            >
              {showTrace ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
              <span>Pipeline Details ({traceEvents.length} steps)</span>
            </button>
            {showTrace && (
              <div className="mt-2 space-y-1.5 pl-2 border-l border-[#2a2a2a]">
                {traceEvents.filter(e => e.step !== "done").map((event, i) => (
                  <div key={i} className="flex items-start gap-2 text-[11px] font-mono text-[#777]">
                    <StepBadge step={event.step} />
                    <span className="truncate">
                      {event.step === "classify" && `→ ${event.payload?.task_type} (${(event.payload?.confidence * 100).toFixed(0)}%)`}
                      {event.step === "plan" && `→ ${(event.payload?.plan || "").slice(0, 80)}...`}
                      {event.step === "tool_call" && `→ ${event.payload?.tool_name}`}
                      {event.step === "verify_pass" && `→ ${event.payload?.detail}`}
                      {event.step === "verify_fail" && `→ ${event.payload?.detail}`}
                      {event.step === "retry" && `→ Attempt ${event.payload?.attempt}`}
                      {event.step === "generate" && `→ ${event.payload?.artifact_type || "generating"}`}
                      {event.step === "error" && `→ ${event.payload?.error}`}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-7 h-7 rounded-full bg-[#333] flex items-center justify-center shrink-0 mt-1">
          <User className="w-4 h-4 text-[#aaa]" />
        </div>
      )}
    </div>
  );
}
