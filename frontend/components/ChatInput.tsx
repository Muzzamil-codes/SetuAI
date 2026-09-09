"use client";
import React, { useState, useRef } from "react";
import { Send, Paperclip, X, ChevronDown, Sparkles } from "lucide-react";

export interface ModelOption {
  value: string;
  label: string;
}

interface ChatInputProps {
  onSend: (message: string, file: File | null) => void;
  disabled?: boolean;
  isGenerating?: boolean;
  onStop?: () => void;
  model: string;
  onModelChange: (model: string) => void;
  availableModels: ModelOption[];
}

export default function ChatInput({ onSend, disabled, isGenerating, onStop, model, onModelChange, availableModels = [] }: ChatInputProps) {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!text.trim() && !file) return;
    if (isGenerating) return;
    onSend(text.trim(), file);
    setText("");
    setFile(null);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  };

  const selectedLabel = availableModels.find(m => m.value === model)?.label || "Auto";

  return (
    <div className="p-4 md:p-6 bg-gradient-to-t from-[var(--background)] via-[var(--background)] to-transparent w-full">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative">
        
        {/* File preview */}
        {file && (
          <div className="absolute bottom-[110%] left-4 flex items-center gap-2 mb-2 px-3 py-1.5 rounded-xl bg-[var(--input-bg)] shadow-card border border-[var(--border)] text-[12px] text-[var(--foreground-muted)] w-fit animate-fade-in">
            <Paperclip className="w-3.5 h-3.5" />
            <span className="truncate max-w-[200px] font-medium">{file.name}</span>
            <button type="button" onClick={() => setFile(null)} className="hover:text-[var(--foreground)] p-0.5 rounded-md hover:bg-[var(--accent-light)] transition">
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {/* Floating Command Bar */}
        <div className="flex flex-col bg-[var(--input-bg)] border border-[var(--border)] rounded-[20px] shadow-composer p-1.5 focus-within:border-[var(--border-hover)] focus-within:shadow-[0_8px_30px_rgba(0,0,0,0.08)] transition-all duration-300">
          
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask SetuAI anything..."
            className="w-full bg-transparent text-[15px] text-[var(--foreground)] placeholder:text-[#A8A59D] outline-none resize-none max-h-[200px] px-3 pt-3 pb-2 leading-relaxed"
            disabled={disabled}
          />

          <div className="flex items-center justify-between px-2 pb-1 pt-2">
            
            <div className="flex items-center gap-1">
              {/* File attach */}
              <label className={`cursor-pointer p-2 rounded-xl transition ${isGenerating ? 'opacity-50 cursor-not-allowed text-[var(--foreground-muted)]' : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--accent-light)]/50'}`}>
                <Paperclip className="w-4 h-4" />
                <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" disabled={isGenerating} />
              </label>

              {/* Model selector */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => !isGenerating && setShowModelDropdown(!showModelDropdown)}
                  disabled={isGenerating}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-[12px] font-medium transition ${isGenerating ? 'opacity-50 cursor-not-allowed text-[var(--foreground-muted)]' : 'text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--accent-light)]/50'}`}
                >
                  <Sparkles className="w-3.5 h-3.5 opacity-70" />
                  <span>{selectedLabel}</span>
                  <ChevronDown className="w-3 h-3 opacity-50" />
                </button>
                {showModelDropdown && (
                  <div className="absolute bottom-full mb-2 left-0 bg-[var(--input-bg)] border border-[var(--border)] rounded-xl shadow-card py-1.5 min-w-[180px] z-50">
                    {availableModels.map((m) => (
                      <button
                        key={m.value}
                        type="button"
                        onClick={() => { onModelChange(m.value); setShowModelDropdown(false); }}
                        className={`w-full flex items-center justify-between px-4 py-2 text-[13px] hover:bg-[var(--accent-light)] transition ${
                          model === m.value ? "text-[var(--foreground)] font-semibold" : "text-[var(--foreground-muted)]"
                        }`}
                      >
                        {m.label}
                        {m.value === "auto" && <span className="text-[10px] text-[var(--foreground-muted)] font-mono ml-2 border border-[var(--border)] px-1.5 rounded bg-[var(--background)]">AUTO</span>}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Send or Stop button */}
            {isGenerating ? (
              <button
                type="button"
                onClick={onStop}
                className="p-2.5 px-3 rounded-xl bg-zinc-800 border border-zinc-700 text-white hover:bg-zinc-700 transition-all shadow-sm flex items-center gap-2"
              >
                <div className="w-2.5 h-2.5 bg-white rounded-[2px]" />
                <span className="text-[12px] font-medium pr-1">Stop</span>
              </button>
            ) : (
              <button
                type="submit"
                disabled={disabled || (!text.trim() && !file)}
                className="p-2.5 rounded-xl bg-[var(--accent)] text-white hover:bg-[#1a1a1a] disabled:opacity-30 disabled:hover:bg-[var(--accent)] disabled:cursor-not-allowed transition-all transform active:scale-95 shadow-sm"
              >
                <Send className="w-4 h-4 ml-0.5" />
              </button>
            )}
          </div>
        </div>

      </form>
    </div>
  );
}
