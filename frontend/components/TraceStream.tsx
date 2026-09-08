"use client";
import React, { useState } from "react";
import { TraceEvent } from "../lib/types";
import { 
  Brain, 
  ListOrdered, 
  Wrench, 
  ShieldCheck, 
  ShieldAlert, 
  RefreshCw, 
  FileCheck, 
  CheckCircle2, 
  AlertCircle, 
  ChevronDown, 
  ChevronRight, 
  Clock, 
  Cpu, 
  Terminal,
  Code
} from "lucide-react";

interface TraceStreamProps {
  events: TraceEvent[];
  theme?: string;
}

export default function TraceStream({ events }: TraceStreamProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (idx: number) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  const getStepConfig = (step: string) => {
    const s = step.toLowerCase();
    if (s === "classify") {
      return {
        label: "CLASSIFY",
        icon: <Brain className="w-4 h-4 text-purple-400" />,
        badgeColor: "bg-purple-950/80 text-purple-300 border-purple-800/60",
        borderGlow: "border-purple-900/40",
      };
    }
    if (s === "plan") {
      return {
        label: "ORCHESTRATE & PLAN",
        icon: <ListOrdered className="w-4 h-4 text-indigo-400" />,
        badgeColor: "bg-indigo-950/80 text-indigo-300 border-indigo-800/60",
        borderGlow: "border-indigo-900/40",
      };
    }
    if (s.includes("tool")) {
      return {
        label: "TOOL EXECUTION",
        icon: <Wrench className="w-4 h-4 text-amber-400" />,
        badgeColor: "bg-amber-950/80 text-amber-300 border-amber-800/60",
        borderGlow: "border-amber-900/40",
      };
    }
    if (s.includes("pass")) {
      return {
        label: "FORMAL AST VERIFIED",
        icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
        badgeColor: "bg-emerald-950/90 text-emerald-300 border-emerald-600/70 shadow-sm shadow-emerald-500/20",
        borderGlow: "border-emerald-500/50 bg-emerald-950/10",
      };
    }
    if (s.includes("fail")) {
      return {
        label: "FAULT ISOLATED",
        icon: <ShieldAlert className="w-4 h-4 text-rose-400" />,
        badgeColor: "bg-rose-950/90 text-rose-300 border-rose-700/70",
        borderGlow: "border-rose-800/50 bg-rose-950/10",
      };
    }
    if (s === "retry") {
      return {
        label: "SELF-HEAL RETRY",
        icon: <RefreshCw className="w-4 h-4 text-yellow-400 animate-spin" />,
        badgeColor: "bg-yellow-950/80 text-yellow-300 border-yellow-700/60",
        borderGlow: "border-yellow-800/50",
      };
    }
    if (s === "generate") {
      return {
        label: "ARTIFACT SYNTHESIS",
        icon: <FileCheck className="w-4 h-4 text-blue-400" />,
        badgeColor: "bg-blue-950/80 text-blue-300 border-blue-800/60",
        borderGlow: "border-blue-900/40",
      };
    }
    if (s === "done") {
      return {
        label: "MISSION COMPLETED",
        icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
        badgeColor: "bg-emerald-950/90 text-emerald-300 border-emerald-500/70",
        borderGlow: "border-emerald-500/60 bg-emerald-950/20",
      };
    }
    if (s === "error") {
      return {
        label: "PIPELINE FAULT",
        icon: <AlertCircle className="w-4 h-4 text-rose-400" />,
        badgeColor: "bg-rose-950/90 text-rose-300 border-rose-700/70",
        borderGlow: "border-rose-800/60",
      };
    }
    return {
      label: step.toUpperCase(),
      icon: <Terminal className="w-4 h-4 text-slate-400" />,
      badgeColor: "bg-slate-900 text-slate-300 border-slate-700",
      borderGlow: "border-slate-800",
    };
  };

  const renderContent = (evt: TraceEvent) => {
    const p = evt.payload || {};
    const s = evt.step.toLowerCase();

    if (s === "classify") {
      return (
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-slate-400 text-xs font-mono">Task Classification:</span>
            <span className="text-white font-mono font-semibold text-xs px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
              {p.task_type || "autonomous_execution"}
            </span>
          </div>
          {p.selected_model && (
            <div className="flex items-center gap-2 text-xs font-mono text-purple-300">
              <Cpu className="w-3.5 h-3.5 text-purple-400" />
              <span>Selected Sovereign Model: <strong>{p.selected_model.name || p.selected_model}</strong></span>
            </div>
          )}
        </div>
      );
    }

    if (s === "plan") {
      return (
        <div className="space-y-2">
          <p className="text-xs text-slate-300 font-mono leading-relaxed">
            {p.plan || "Deterministic execution graph compiled."}
          </p>
          {p.retry_count > 0 && (
            <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-800">
              Iteration #{p.retry_count}
            </span>
          )}
        </div>
      );
    }

    if (s.includes("tool")) {
      return (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-slate-400 text-xs font-mono">Invoked Tool:</span>
              <span className="text-amber-300 font-mono font-bold text-xs px-2 py-0.5 rounded bg-amber-950/60 border border-amber-800/60">
                {p.tool_name || "native_tool"}
              </span>
            </div>
            <span className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded border ${
              p.success !== false
                ? "bg-emerald-950/80 text-emerald-400 border-emerald-800"
                : "bg-rose-950/80 text-rose-400 border-rose-800"
            }`}>
              {p.success !== false ? "SUCCESS" : "FAILED"}
            </span>
          </div>

          {p.input_summary && (
            <div className="p-2 rounded-lg bg-slate-950/90 border border-slate-800/80 text-[11px] font-mono text-slate-300 overflow-x-auto">
              <span className="text-slate-500">Payload: </span>
              {typeof p.input_summary === "string" ? p.input_summary : JSON.stringify(p.input_summary)}
            </div>
          )}
        </div>
      );
    }

    if (s.includes("pass")) {
      return (
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-emerald-400 font-bold text-xs">Proof Check Succeeded:</span>
            <span className="text-xs font-mono text-emerald-300 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
              {p.verification_type || "Numeric Tolerance & Code AST"}
            </span>
          </div>
          <p className="text-xs text-slate-300 font-mono">
            {p.detail || "Mathematical assertion verified within specified epsilon bounds."}
          </p>
        </div>
      );
    }

    if (s.includes("fail")) {
      return (
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <span className="text-rose-400 font-bold text-xs">Verification Check Failed:</span>
            <span className="text-xs font-mono text-rose-300 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800">
              {p.verification_type || "Assertion Deviation"}
            </span>
          </div>
          <p className="text-xs text-slate-300 font-mono">
            {p.detail || "Value out of certified limits. Dispatching self-healing remediation."}
          </p>
        </div>
      );
    }

    if (s === "retry") {
      return (
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-mono text-yellow-300">
            <RefreshCw className="w-3.5 h-3.5 animate-spin text-yellow-400" />
            <span>Autonomous Self-Heal Loop (Attempt {p.attempt || 1}/{p.max_retries || 3})</span>
          </div>
          {p.reason && (
            <p className="text-xs text-slate-300 font-mono bg-yellow-950/30 p-2 rounded border border-yellow-900/40">
              Reason: {p.reason}
            </p>
          )}
        </div>
      );
    }

    if (s === "generate") {
      return (
        <div className="flex items-center gap-2">
          <span className="text-slate-400 text-xs font-mono">Deliverable Created:</span>
          <span className="text-blue-300 font-mono font-semibold text-xs px-2 py-0.5 rounded bg-blue-950 border border-blue-800">
            {p.filename || p.artifact_type || "OpenXML File"}
          </span>
        </div>
      );
    }

    if (s === "done") {
      return (
        <div className="space-y-2">
          <p className="text-xs text-slate-200 font-mono whitespace-pre-wrap leading-relaxed">
            {p.summary || "Agent task completed with 100% verification compliance."}
          </p>
          {p.artifacts && p.artifacts.length > 0 && (
            <div className="flex flex-wrap gap-2 pt-1">
              {p.artifacts.map((a: any, i: number) => (
                <span
                  key={i}
                  className="text-[11px] font-mono px-2.5 py-1 rounded-lg bg-emerald-950/60 text-emerald-300 border border-emerald-700/60 flex items-center gap-1.5"
                >
                  <FileCheck className="w-3.5 h-3.5" />
                  {a.filename}
                </span>
              ))}
            </div>
          )}
        </div>
      );
    }

    if (s === "error") {
      return (
        <div className="p-2.5 rounded bg-rose-950/50 border border-rose-800 text-xs font-mono text-rose-200">
          {p.error || "Execution terminated unexpectedly."}
        </div>
      );
    }

    return (
      <div className="text-xs font-mono text-slate-300">
        {typeof p === "string" ? p : JSON.stringify(p)}
      </div>
    );
  };

  return (
    <div className="glass-panel p-6 rounded-2xl space-y-4 shadow-xl border border-slate-800">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <h3 className="font-bold text-sm text-slate-200 uppercase tracking-wider font-mono">
            Live Execution Telemetry
          </h3>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
            WebSocket Stream
          </span>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-mono text-slate-400">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>{events.length} Steps</span>
          </div>
          {events.length > 0 && (
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
            </span>
          )}
        </div>
      </div>

      <div className="space-y-3 max-h-[540px] overflow-y-auto pr-1">
        {events.length === 0 ? (
          <div className="p-8 text-center border border-dashed border-slate-800 rounded-xl">
            <div className="w-10 h-10 mx-auto mb-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-slate-500">
              <Terminal className="w-5 h-5 animate-pulse" />
            </div>
            <p className="text-xs font-mono text-slate-400">Waiting for agent execution telemetry...</p>
            <p className="text-[11px] font-mono text-slate-600 mt-1">Events will stream here in real-time as tasks execute</p>
          </div>
        ) : (
          events.map((evt, idx) => {
            const config = getStepConfig(evt.step);
            const isExpanded = expandedIndex === idx;

            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border transition-all ${config.borderGlow} bg-slate-900/60 hover:bg-slate-900/90`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2.5">
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-md border flex items-center gap-1.5 ${config.badgeColor}`}>
                      {config.icon}
                      {config.label}
                    </span>
                    <span className="text-[11px] font-mono text-slate-500">
                      Step #{idx + 1}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-slate-500">
                      {evt.timestamp || ""}
                    </span>
                    <button
                      type="button"
                      onClick={() => toggleExpand(idx)}
                      className="text-slate-500 hover:text-slate-300 p-1 rounded hover:bg-slate-800 transition"
                      title="Inspect raw payload"
                    >
                      {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                <div className="pl-1">
                  {renderContent(evt)}
                </div>

                {/* Collapsible raw JSON inspector */}
                {isExpanded && (
                  <div className="mt-3 pt-3 border-t border-slate-800/80">
                    <div className="flex items-center gap-1.5 mb-1 text-[10px] font-mono text-slate-400">
                      <Code className="w-3 h-3 text-cyan-400" />
                      <span>Raw Event Payload:</span>
                    </div>
                    <pre className="p-2.5 rounded-lg bg-black/80 border border-slate-800 text-[10px] font-mono text-cyan-300 overflow-x-auto">
                      {JSON.stringify(evt, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
