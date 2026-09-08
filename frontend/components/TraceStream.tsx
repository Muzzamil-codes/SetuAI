"use client";
import React from "react";
import { TraceEvent } from "../lib/types";
import { ColorTheme } from "./ThemeToggle";

interface TraceStreamProps {
  events: TraceEvent[];
  theme?: ColorTheme;
}

export default function TraceStream({ events, theme = "dark" }: TraceStreamProps) {
  const isCardWhite = theme === "light" || theme === "elevated";
  const textColor = isCardWhite ? "text-gray-700" : "text-zinc-200";

  const renderDetails = (evt: TraceEvent) => {
    const p = evt.payload || {};
    switch (evt.step.toLowerCase()) {
      case "classify":
        return (
          <p className={`text-xs ${textColor}`}>
            Task type: <strong>{p.task_type || "unknown"}</strong>
            {p.selected_model?.name && ` → Model: ${p.selected_model.name}`}
          </p>
        );
      case "plan":
        return (
          <p className={`text-xs ${textColor}`}>
            {p.plan || "Planning..."}
            {p.retry_count > 0 && ` (retry #${p.retry_count})`}
          </p>
        );
      case "tool":
      case "tool_call":
        return (
          <p className={`text-xs ${textColor}`}>
            Tool: <strong>{p.tool_name || "unknown"}</strong>
            {p.input_summary && ` — input: ${JSON.stringify(p.input_summary)}`}
            {" — "}
            {p.success ? "✅ success" : "❌ failed"}
          </p>
        );
      case "verify_pass":
      case "pass":
        return (
          <p className={`text-xs ${textColor}`}>
            ✓ Passed: {p.verification_type || "check"} — {p.detail || "verified"}
          </p>
        );
      case "verify_fail":
        return (
          <p className={`text-xs ${textColor}`}>
            ✗ Failed: {p.verification_type || "check"} — {p.detail || "failed"}
            {p.retry_count !== undefined && ` (attempt ${p.retry_count})`}
          </p>
        );
      case "retry":
        return (
          <p className={`text-xs ${textColor}`}>
            Retrying — attempt {p.attempt || "?"}/{p.max_retries || "?"}: {p.reason || ""}
          </p>
        );
      case "generate":
        return (
          <p className={`text-xs ${textColor}`}>
            Generating artifact: {p.artifact_type || "file"}
            {p.filename && ` → ${p.filename}`}
          </p>
        );
      case "done":
        return (
          <div className={`text-xs ${textColor} space-y-1`}>
            <p className="whitespace-pre-wrap">{p.summary || "Task complete."}</p>
            {p.artifacts && p.artifacts.length > 0 && (
              <div className="mt-2 space-y-1">
                {p.artifacts.map((a: any, i: number) => (
                  <div key={i} className={`text-[11px] px-2 py-1 rounded ${isCardWhite ? "bg-blue-50 text-blue-800" : "bg-blue-900/30 text-blue-300"}`}>
                    📄 {a.filename} ({a.type})
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      case "error":
        return (
          <p className="text-xs text-red-400">
            Error: {p.error || "Unknown error"}
          </p>
        );
      default:
        return (
          <p className={`text-xs ${textColor}`}>
            {JSON.stringify(p)}
          </p>
        );
    }
  };

  const getStepBadge = (step: string) => {
    const s = step.toLowerCase();
    const badges: Record<string, { label: string; color: string }> = {
      classify:    { label: "🧠 CLASSIFY", color: isCardWhite ? "bg-purple-100 text-purple-800" : "bg-purple-900/50 text-purple-300" },
      plan:        { label: "📋 PLAN",     color: isCardWhite ? "bg-slate-800 text-white" : "bg-white text-slate-900" },
      tool_call:   { label: "⚙ TOOL",     color: isCardWhite ? "bg-amber-100 text-amber-800" : "bg-amber-900/40 text-amber-300" },
      verify_pass: { label: "✓ PASS",     color: isCardWhite ? "bg-green-100 text-green-800" : "bg-green-900/40 text-green-300" },
      verify_fail: { label: "✗ FAIL",     color: isCardWhite ? "bg-red-100 text-red-800" : "bg-red-900/40 text-red-300" },
      retry:       { label: "🔄 RETRY",   color: isCardWhite ? "bg-yellow-100 text-yellow-800" : "bg-yellow-900/40 text-yellow-300" },
      generate:    { label: "📄 GENERATE", color: isCardWhite ? "bg-blue-100 text-blue-800" : "bg-blue-900/40 text-blue-300" },
      done:        { label: "✅ DONE",     color: isCardWhite ? "bg-green-100 text-green-800" : "bg-green-900/40 text-green-300" },
      error:       { label: "❌ ERROR",    color: isCardWhite ? "bg-red-100 text-red-800" : "bg-red-900/40 text-red-300" },
    };
    const match = badges[s] || (s.includes("pass") ? badges.verify_pass : s.includes("tool") ? badges.tool_call : null);
    return match || { label: step.toUpperCase(), color: isCardWhite ? "bg-slate-800 text-white" : "bg-white text-slate-900" };
  };

  return (
    <div
      className={`rounded-xl border p-5 shadow-lg font-mono text-xs transition-colors ${
        isCardWhite
          ? "bg-white border-gray-200"
          : "bg-slate-900 border-slate-800"
      }`}
    >
      <div className="space-y-3 max-h-[480px] overflow-y-auto">
        {events.length === 0 ? (
          <p className={`${isCardWhite ? "text-gray-400" : "text-zinc-500"} italic`}>
            Waiting for agent events...
          </p>
        ) : (
          events.map((evt, idx) => {
            const badge = getStepBadge(evt.step);
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-lg border flex flex-col gap-1.5 transition-colors ${
                  isCardWhite
                    ? "bg-gray-50 border-gray-200"
                    : "bg-slate-950/70 border-slate-800/80"
                }`}
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`font-bold text-[11px] px-2 py-0.5 rounded shadow-sm ${badge.color}`}
                  >
                    {badge.label}
                  </span>
                  <span
                    className={`text-[11px] font-mono ${
                      isCardWhite ? "text-gray-500" : "text-zinc-400"
                    }`}
                  >
                    {evt.timestamp}
                  </span>
                </div>
                <div className="pt-0.5">{renderDetails(evt)}</div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}