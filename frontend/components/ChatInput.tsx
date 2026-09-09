"use client";
import React, { useState, useRef } from "react";
import { Send, Paperclip, X, ChevronDown } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string, file: File | null) => void;
  disabled?: boolean;
  model: string;
  onModelChange: (model: string) => void;
}

const MODELS = [
  { value: "auto", label: "Auto" },
  { value: "deepseek-r1", label: "DeepSeek-R1" },
  { value: "qwen2.5-coder", label: "Qwen2.5-Coder" },
  { value: "llama3.2-vision", label: "LLama3.2-Vision" },
];

export default function ChatInput({ onSend, disabled, model, onModelChange }: ChatInputProps) {
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!text.trim() && !file) return;
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

  const selectedLabel = MODELS.find(m => m.value === model)?.label || "Auto";

  return (
    <div className="border-t border-[#2a2a2a] bg-[#0a0a0a] p-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
        {/* File preview */}
        {file && (
          <div className="flex items-center gap-2 mb-2 px-3 py-1.5 rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] text-xs text-[#aaa] w-fit">
            <span className="truncate max-w-[200px]">{file.name}</span>
            <button type="button" onClick={() => setFile(null)} className="text-[#666] hover:text-white">
              <X className="w-3 h-3" />
            </button>
          </div>
        )}

        <div className="flex items-end gap-2 bg-[#1a1a1a] border border-[#2a2a2a] rounded-xl px-3 py-2 focus-within:border-[#444]">
          {/* Model selector */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowModelDropdown(!showModelDropdown)}
              className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs text-[#888] hover:text-white hover:bg-[#2a2a2a] transition"
            >
              <span>{selectedLabel}</span>
              <ChevronDown className="w-3 h-3" />
            </button>
            {showModelDropdown && (
              <div className="absolute bottom-full mb-1 left-0 bg-[#1a1a1a] border border-[#2a2a2a] rounded-lg shadow-xl py-1 min-w-[160px] z-50">
                {MODELS.map((m) => (
                  <button
                    key={m.value}
                    type="button"
                    onClick={() => { onModelChange(m.value); setShowModelDropdown(false); }}
                    className={`w-full text-left px-3 py-1.5 text-xs hover:bg-[#2a2a2a] transition ${
                      model === m.value ? "text-white" : "text-[#888]"
                    }`}
                  >
                    {m.label}
                    {m.value === "auto" && <span className="text-[#555] ml-1">(classifier decides)</span>}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* File attach */}
          <label className="cursor-pointer p-1.5 rounded-lg text-[#666] hover:text-white hover:bg-[#2a2a2a] transition">
            <Paperclip className="w-4 h-4" />
            <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="hidden" />
          </label>

          {/* Text input */}
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            onChange={handleTextChange}
            onKeyDown={handleKeyDown}
            placeholder="Send a message..."
            className="flex-1 bg-transparent text-sm text-white placeholder:text-[#555] outline-none resize-none max-h-[200px]"
            disabled={disabled}
          />

          {/* Send button */}
          <button
            type="submit"
            disabled={disabled || (!text.trim() && !file)}
            className="p-2 rounded-lg bg-white text-black hover:bg-[#ddd] disabled:opacity-30 disabled:cursor-not-allowed transition"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <p className="text-[10px] text-[#444] text-center mt-2">SETU AI — Sovereign AI Workbench</p>
      </form>
    </div>
  );
}
