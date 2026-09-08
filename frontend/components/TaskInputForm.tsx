"use client";
import React, { useState } from "react";
import { ColorTheme } from "./ThemeToggle";
import { uploadFile, submitTask } from "../lib/api";

interface TaskInputFormProps {
  onTaskStarted: (taskId: string) => void;
  theme?: ColorTheme;
}

export default function TaskInputForm({ onTaskStarted, theme = "light" }: TaskInputFormProps) {
  const [instructions, setInstructions] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isDark = theme === "dark" || theme === "elevated";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instructions.trim()) return;

    setLoading(true);
    setError(null);

    try {
      let modality: "text" | "image" | "file" = "text";
      let content = instructions;

      // If a file is attached, upload it first
      if (file) {
        const uploadedPath = await uploadFile(file);
        content = uploadedPath;

        // Determine modality from file type
        if (file.type.startsWith("image/")) {
          modality = "image";
        } else {
          modality = "file";
        }
      }

      // Submit the task to the backend — this triggers the orchestrator
      const taskId = await submitTask({
        modality,
        content,
        context: { original_instructions: instructions },
      });

      onTaskStarted(taskId);
    } catch (err: any) {
      console.error("Task submission failed:", err);
      setError(err.message || "Failed to start task. Is the backend running?");
      setLoading(false);
    }
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
      {error && (
        <div className="p-3 bg-red-900/30 border border-red-700 text-red-300 rounded-lg text-sm">
          {error}
        </div>
      )}

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
        {file && (
          <p className={`mt-1 text-xs ${isDark ? "text-zinc-500" : "text-gray-400"}`}>
            Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
          </p>
        )}
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