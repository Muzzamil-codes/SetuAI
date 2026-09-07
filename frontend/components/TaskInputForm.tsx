"use client";
import React, { useState } from "react";
import { ColorTheme } from "./ThemeToggle";

interface TaskInputFormProps {
  onTaskStarted: (taskId: string) => void;
  theme?: ColorTheme;
}

export default function TaskInputForm({ onTaskStarted, theme = "light" }: TaskInputFormProps) {
  const [instructions, setInstructions] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const isDark = theme === "dark";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instructions.trim()) return;

    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onTaskStarted("demo-task-101");
    }, 600);
  };

  return (
    <form
      onSubmit={handleSubmit}
      className={`p-6 rounded-xl border space-y-5 transition-colors ${
        isDark
          ? "bg-black border-zinc-800 text-white shadow-2xl"
          : "bg-white border-gray-200 text-gray-900 shadow-md"
      }`}
    >
      <div>
        <label className={`block text-sm font-semibold mb-2 ${isDark ? "text-zinc-200" : "text-gray-800"}`}>
          Task Instructions
        </label>
        <textarea
          rows={4}
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          placeholder="e.g. Read this scanned report and draft approval note..."
          className={`w-full p-3 rounded-lg border text-sm focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors ${
            isDark
              ? "bg-zinc-900 border-zinc-800 text-white placeholder-zinc-500"
              : "bg-white border-gray-300 text-gray-900 placeholder-gray-400"
          }`}
          required
        />
      </div>

      <div>
        <label className={`block text-sm font-semibold mb-2 ${isDark ? "text-zinc-200" : "text-gray-800"}`}>
          Attachment (Image or Document)
        </label>
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className={`block w-full text-sm cursor-pointer ${
            isDark
              ? "text-zinc-400 file:bg-zinc-800 file:text-zinc-200 hover:file:bg-zinc-700"
              : "text-gray-500 file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          } file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold`}
        />
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-medium rounded-lg shadow transition"
      >
        {loading ? "Initializing Agent..." : "Run AI Pipeline"}
      </button>
    </form>
  );
}