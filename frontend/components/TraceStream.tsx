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

  const renderDetails = (evt: TraceEvent) => {
    switch (evt.step.toLowerCase()) {
      case "classify":
        return (
          <p className={`text-xs ${isCardWhite ? "text-gray-700" : "text-zinc-200"}`}>
            Task type: {evt.payload?.task_type || "drafting"} ({evt.payload?.confidence || "94%"} confident)
          </p>
        );
      case "plan":
        return (
          <p className={`text-xs ${isCardWhite ? "text-gray-700" : "text-zinc-200"}`}>
            {evt.payload?.plan_summary || evt.message || "Extract fields, verify, draft note"}
          </p>
        );
      case "tool":
      case "tool_call":
        return (
          <p className={`text-xs ${isCardWhite ? "text-gray-700" : "text-zinc-200"}`}>
            Tool: {evt.payload?.tool_name || "extract_from_image"} — input: {JSON.stringify(evt.payload?.input || { image_path: "uploads/scan_001.jpg" })}
          </p>
        );
      case "pass":
      case "verify_pass":
        return (
          <p className={`text-xs ${isCardWhite ? "text-gray-700" : "text-zinc-200"}`}>
            Passed: {evt.payload?.check || "verify_numeric"} — {evt.payload?.detail || "within tolerance"}
          </p>
        );
      case "done":
        return (
          <p className={`text-xs ${isCardWhite ? "text-gray-700" : "text-zinc-200"}`}>
            {evt.payload?.summary || evt.message || "Extracted 6 fields from scan, verified 5, drafted approval note."}
          </p>
        );
      default:
        return evt.message ? (
          <p className={`text-xs ${isCardWhite ? "text-gray-700" : "text-zinc-200"}`}>{evt.message}</p>
        ) : null;
    }
  };

  const getStepBadge = (step: string) => {
    const s = step.toLowerCase();
    if (s.includes("pass")) return "✓ PASS";
    if (s.includes("tool")) return "⚙ TOOL";
    if (s.includes("classify")) return "CLASSIFY";
    if (s.includes("plan")) return "PLAN";
    if (s.includes("done")) return "DONE";
    return step.toUpperCase();
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
          events.map((evt, idx) => (
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
                  className={`font-bold text-[11px] px-2 py-0.5 rounded shadow-sm ${
                    isCardWhite
                      ? "bg-slate-800 text-white"
                      : "bg-white text-slate-900"
                  }`}
                >
                  {getStepBadge(evt.step)}
                </span>
                <span
                  className={`text-[11px] font-mono ${
                    isCardWhite ? "text-gray-500" : "text-zinc-400"
                  }`}
                >
                  {evt.timestamp || "2026-09-07T14:32:01Z"}
                </span>
              </div>
              <div className="pt-0.5">{renderDetails(evt)}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}