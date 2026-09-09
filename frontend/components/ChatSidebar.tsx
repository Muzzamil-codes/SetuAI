"use client";
import React from "react";
import { Conversation } from "../lib/types";
import { Plus, MessageSquare, Trash2, Settings } from "lucide-react";
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
    <div className="w-64 h-screen flex flex-col bg-[#111] border-r border-[#2a2a2a] shrink-0">
      {/* Header */}
      <div className="p-4 border-b border-[#2a2a2a]">
        <button
          onClick={onNew}
          className="w-full flex items-center gap-2 px-3 py-2.5 rounded-lg border border-[#2a2a2a] hover:border-[#444] hover:bg-[#1a1a1a] text-sm text-white transition"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 && (
          <p className="text-xs text-[#666] text-center py-8">No conversations yet</p>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer text-sm transition ${
              activeId === conv.id
                ? "bg-[#2a2a2a] text-white"
                : "text-[#999] hover:bg-[#1a1a1a] hover:text-white"
            }`}
            onClick={() => onSelect(conv.id)}
          >
            <MessageSquare className="w-4 h-4 shrink-0 opacity-50" />
            <span className="flex-1 truncate text-xs">{conv.title}</span>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(conv.id); }}
              className="opacity-0 group-hover:opacity-100 text-[#666] hover:text-red-400 transition"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-[#2a2a2a]">
        <Link
          href="/settings"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-xs text-[#888] hover:text-white hover:bg-[#1a1a1a] transition"
        >
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </Link>
      </div>
    </div>
  );
}
