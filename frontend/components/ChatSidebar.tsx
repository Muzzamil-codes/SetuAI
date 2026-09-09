"use client";
import React from "react";
import { Conversation } from "../lib/types";
import { Plus, MessageSquare, Trash2, Settings, UserCircle, Briefcase } from "lucide-react";
import Link from "next/link";

interface ChatSidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export default function ChatSidebar({ conversations, activeId, onSelect, onNew, onDelete }: ChatSidebarProps) {
  return (
    <div className="w-[280px] h-screen flex flex-col bg-[var(--sidebar-bg)] border-r border-[var(--border)] shrink-0 transition-all duration-300">
      {/* Header */}
      <div className="px-5 py-6">
        <div className="flex items-center gap-3 mb-8">
          <div className="w-8 h-8 rounded-full overflow-hidden shadow-sm ring-1 ring-[var(--border)]">
             <img src="/logo.jpg" alt="SETU AI" className="w-full h-full object-cover" />
          </div>
          <span className="font-semibold text-[var(--foreground)] tracking-[0.02em] text-[15px]">SetuAI</span>
        </div>
        
        <button
          onClick={onNew}
          className="w-full flex items-center justify-between px-4 py-2.5 rounded-xl bg-[var(--accent)] hover:bg-[#1a1a1a] text-white shadow-sm transition-all duration-200 group"
        >
          <span className="text-[13px] font-medium tracking-wide">New Chat</span>
          <Plus className="w-4 h-4 opacity-70 group-hover:opacity-100 transition-opacity" />
        </button>
      </div>

      {/* Navigation Sections */}
      <div className="flex-1 overflow-y-auto px-3 space-y-6">
        
        {/* Recents */}
        <div>
          <div className="px-3 mb-2 flex items-center gap-2 text-[11px] font-semibold text-[var(--foreground-muted)] tracking-wider uppercase">
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Recent</span>
          </div>
          <div className="space-y-0.5">
            {conversations.length === 0 && (
              <p className="text-[13px] text-[var(--foreground-muted)] px-3 py-2 italic">No conversations yet</p>
            )}
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={`group flex items-center gap-2 px-3 py-2 rounded-xl cursor-pointer text-[13px] transition-colors duration-200 ${
                  activeId === conv.id
                    ? "bg-[var(--accent-light)] text-[var(--foreground)] font-medium shadow-sm"
                    : "text-[var(--foreground-muted)] hover:bg-[var(--accent-light)]/50 hover:text-[var(--foreground)]"
                }`}
                onClick={() => onSelect(conv.id)}
              >
                <span className="flex-1 truncate">{conv.title}</span>
                <button
                  onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
                  className="opacity-0 group-hover:opacity-100 text-[var(--foreground-muted)] hover:text-rose-500 transition-all"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Footer */}
      <div className="p-4 border-t border-[var(--border)]">
        <Link
          href="/settings"
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:bg-[var(--accent-light)] transition-all"
        >
          <Settings className="w-4 h-4" />
          <span className="font-medium">Settings</span>
        </Link>
      </div>
    </div>
  );
}
