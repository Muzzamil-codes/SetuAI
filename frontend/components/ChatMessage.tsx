"use client";
import React, { useState } from "react";
import { ChatMessage as ChatMessageType, TraceEvent, ArtifactRef } from "../lib/types";
import MarkdownRenderer from "./MarkdownRenderer";
import { ChevronRight, ChevronDown, Download, FileText, FileSpreadsheet, File } from "lucide-react";

interface ChatMessageProps {
  message: ChatMessageType;
}

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

function StepBadge({ step }: { step: string }) {
  const colors: Record<string, string> = {
    classify: "bg-[#E5E3DD] text-[#6F6D68] border border-[#DDDAD3]",
    plan: "bg-[#E5E3DD] text-[#6F6D68] border border-[#DDDAD3]",
    tool_call: "bg-[#E5E3DD] text-[#6F6D68] border border-[#DDDAD3]",
    verify_pass: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    verify_fail: "bg-rose-50 text-rose-700 border border-rose-200",
    retry: "bg-amber-50 text-amber-700 border border-amber-200",
    generate: "bg-[#E5E3DD] text-[#6F6D68] border border-[#DDDAD3]",
    streaming: "bg-blue-50 text-blue-700 border border-blue-200",
    done: "bg-emerald-50 text-emerald-700 border border-emerald-200",
    error: "bg-rose-50 text-rose-700 border border-rose-200",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-mono shadow-sm ${colors[step] || "bg-[#E5E3DD] text-[#6F6D68]"}`}>
      {step}
    </span>
  );
}

function ArtifactCard({ artifact }: { artifact: ArtifactRef }) {
  const icon = artifact.type === "docx" ? <FileText className="w-4 h-4 text-blue-600" /> :
               artifact.type === "xlsx" ? <FileSpreadsheet className="w-4 h-4 text-emerald-600" /> :
               <File className="w-4 h-4 text-[#6F6D68]" />;
  
  const handleDownload = () => {
    const url = `${BACKEND_URL}/download/${artifact.path}`;
    window.open(url, "_blank");
  };

  return (
    <button
      onClick={handleDownload}
      className="flex items-center gap-2 px-3 py-2 rounded-xl border border-[var(--border)] hover:border-[var(--border-hover)] bg-[var(--input-bg)] shadow-sm hover:shadow transition-all text-xs"
    >
      {icon}
      <span className="text-[var(--foreground)] font-medium">{artifact.filename}</span>
      <Download className="w-3 h-3 text-[var(--foreground-muted)] ml-2" />
    </button>
  );
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const [showTrace, setShowTrace] = useState(false);
  const isUser = message.role === "user";
  const traceEvents = message.traceEvents || [];
  const artifacts = message.artifacts || [];
  const hasTrace = traceEvents.length > 0;

  const classifyEvent = traceEvents.find(e => e.step === "classify");
  const selectedModelName = classifyEvent?.payload?.selected_model?.name;

  return (
    <div className={`flex gap-4 px-4 py-6 ${isUser ? "justify-end" : "justify-start"}`}>
      
      {!isUser && (
        <div className="w-8 h-8 rounded-full overflow-hidden shrink-0 mt-0.5 shadow-sm ring-1 ring-[var(--border)]">
           <img src="/logo.jpg" alt="SETU AI" className="w-full h-full object-cover" />
        </div>
      )}

      <div className={`max-w-[75%] ${isUser ? "order-first" : ""}`}>
        
        {/* Model Badge */}
        {!isUser && selectedModelName && (
          <div className="flex items-center mb-2">
            <span className="px-2 py-0.5 rounded-full bg-[var(--sidebar-bg)] text-[var(--foreground-muted)] border border-[var(--border)] text-[10px] font-mono tracking-wide shadow-sm">
              Model: {selectedModelName}
            </span>
          </div>
        )}
        
        <div className={`px-5 py-4 ${
          isUser
            ? "bg-[var(--accent-light)] text-[var(--foreground)] rounded-[20px] rounded-tr-sm shadow-sm"
            : "text-[var(--foreground)]"
        }`}>
          {isUser ? (
            <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className="text-[15px] leading-relaxed prose prose-slate max-w-none">
              {message.isStreaming && !message.content ? (
                <div className="flex items-center gap-3 text-[var(--foreground-muted)] h-6">
                  <div className="flex items-center gap-1">
                    <div className="w-1.5 h-1.5 bg-[var(--foreground-muted)] rounded-full animate-pulse" style={{ animationDelay: "0ms" }} />
                    <div className="w-6 h-[1px] bg-[var(--border-hover)] relative overflow-hidden">
                      <div className="absolute inset-0 bg-[var(--foreground-muted)] w-full -translate-x-full animate-[shimmer_1.5s_infinite]" />
                    </div>
                    <div className="w-1.5 h-1.5 bg-[var(--foreground-muted)] rounded-full animate-pulse" style={{ animationDelay: "300ms" }} />
                  </div>
                  <span className="text-[13px] font-medium tracking-wide">
                    {traceEvents.some(e => e.step === "plan") ? "Generating response..." : "Understanding your request..."}
                  </span>
                </div>
              ) : (
                <MarkdownRenderer content={message.content} />
              )}
            </div>
          )}
        </div>

        {/* Artifacts */}
        {artifacts.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-4 pl-5">
            {artifacts.map((a, i) => <ArtifactCard key={i} artifact={a} />)}
          </div>
        )}

        {/* Collapsible Pipeline Details */}
        {!isUser && hasTrace && (
          <div className="mt-4 pl-5">
            <button
              onClick={() => setShowTrace(!showTrace)}
              className="flex items-center gap-1.5 text-[11px] font-medium text-[var(--foreground-muted)] hover:text-[var(--foreground)] transition-colors"
            >
              {showTrace ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              <span>Pipeline Trace ({traceEvents.length} steps)</span>
            </button>
            
            {showTrace && (
              <div className="mt-3 space-y-2 pl-2 border-l border-[var(--border)]">
                {traceEvents.filter(e => e.step !== "done").map((event, i) => (
                  <div key={i} className="flex items-start gap-2 text-[11px] font-mono text-[var(--foreground-muted)]">
                    <StepBadge step={event.step} />
                    <span className="truncate mt-0.5">
                      {event.step === "classify" && `→ ${event.payload?.task_type} (Model: ${event.payload?.selected_model?.name || 'auto'})`}
                      {event.step === "plan" && `→ ${(event.payload?.plan || "").slice(0, 80)}...`}
                      {event.step === "tool_call" && `→ ${event.payload?.tool_name}`}
                      {event.step === "verify_pass" && `→ ${event.payload?.detail}`}
                      {event.step === "verify_fail" && `→ ${event.payload?.detail}`}
                      {event.step === "retry" && `→ Attempt ${event.payload?.attempt}`}
                      {event.step === "streaming" && `→ Streaming from ${event.payload?.tool_name}...`}
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

    </div>
  );
}
