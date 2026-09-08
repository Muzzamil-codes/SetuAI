"use client";
import React from "react";
import { useRouter } from "next/navigation";
import TaskInputForm from "../components/TaskInputForm";
import { 
  Shield, 
  Cpu, 
  Lock, 
  FileSpreadsheet, 
  FileText, 
  CheckCircle2, 
  Layers, 
  Activity,
  ArrowRight,
  Terminal,
  Zap,
  HardDrive
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* 1. Hero & Institutional Telemetry Section */}
      <div className="relative rounded-3xl p-8 overflow-hidden glass-panel border border-slate-800 shadow-2xl">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -mb-8 -ml-8 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3 max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-950/70 text-emerald-400 border border-emerald-700/50 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping-slow" />
              <span>AIR-GAPPED DEFENSE & PSU AI WORKBENCH</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
              Sovereign Intelligence with{" "}
              <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">
                Formal Deterministic Proof
              </span>
            </h1>
            <p className="text-sm text-slate-300 leading-relaxed font-sans">
              Execute complex engineering, verification, and procurement workflows entirely on-premise.
              Zero cloud egress, formal AST & Podman sandbox execution, and native Microsoft Word and Excel deliverable synthesis.
            </p>
          </div>

          {/* Key telemetry cards */}
          <div className="grid grid-cols-2 gap-3 sm:w-auto w-full flex-shrink-0">
            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-emerald-400">
                <Shield className="w-4 h-4" />
                <span className="text-xs font-mono font-bold">100% On-Prem</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">0 Cloud API Requests</p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-cyan-400">
                <Cpu className="w-4 h-4" />
                <span className="text-xs font-mono font-bold">Local LLMs</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">DeepSeek-R1 + Qwen2.5</p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-purple-400">
                <Lock className="w-4 h-4" />
                <span className="text-xs font-mono font-bold">AST Verified</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">Mathematical SymPy Proof</p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-1">
              <div className="flex items-center gap-2 text-amber-400">
                <FileSpreadsheet className="w-4 h-4" />
                <span className="text-xs font-mono font-bold">Live Formulas</span>
              </div>
              <p className="text-[11px] text-slate-400 font-mono">Native OpenXML (.xlsx/.docx)</p>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Main Workbench Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Column: Command & Dispatch Console (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div>
              <h2 className="text-lg font-bold text-white tracking-wide">
                Operational Command Center
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                Select a mission scenario or formulate a custom industrial instruction
              </p>
            </div>
          </div>

          <TaskInputForm onTaskStarted={(id) => router.push(`/trace/${id}`)} />
        </div>

        {/* Right Column: Architectural Perimeter & Specifications (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* LangGraph Pipeline Architecture Card */}
          <div className="glass-panel p-6 rounded-2xl space-y-5 border border-slate-800 shadow-xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                  <Layers className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-sm text-white">Agentic Architecture</h3>
                  <p className="text-[11px] font-mono text-slate-400">Autonomous LangGraph Orchestration</p>
                </div>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 border border-indigo-800">
                Multi-Agent
              </span>
            </div>

            {/* Pipeline Flow Steps */}
            <div className="space-y-3 font-mono text-xs">
              <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-900/70 border border-slate-800">
                <div className="w-6 h-6 rounded-lg bg-purple-950/80 border border-purple-800 text-purple-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
                  1
                </div>
                <div>
                  <span className="font-bold text-slate-200">Task Classifier & Model Router</span>
                  <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Routes numeric/logic tasks to DeepSeek-R1 (8B) and code/deliverable tasks to Qwen2.5-Coder (7B).
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-900/70 border border-slate-800">
                <div className="w-6 h-6 rounded-lg bg-amber-950/80 border border-amber-800 text-amber-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
                  2
                </div>
                <div>
                  <span className="font-bold text-slate-200">Sandboxed Execution Tools</span>
                  <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Invokes zero-egress rootless Podman containers with strict memory (512MB) and timeout limits.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-900/70 border border-slate-800">
                <div className="w-6 h-6 rounded-lg bg-emerald-950/80 border border-emerald-800 text-emerald-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
                  3
                </div>
                <div>
                  <span className="font-bold text-slate-200">Deterministic AST Verification Gate</span>
                  <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Evaluates numeric assertions via SymPy AST allowlist and triggers autonomous self-healing on failure.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-900/70 border border-slate-800">
                <div className="w-6 h-6 rounded-lg bg-blue-950/80 border border-blue-800 text-blue-400 flex items-center justify-center font-bold text-xs flex-shrink-0">
                  4
                </div>
                <div>
                  <span className="font-bold text-slate-200">Native Office Deliverables Engine</span>
                  <p className="text-[11px] text-slate-400 font-sans mt-0.5">
                    Synthesizes Word (.docx) approval notes and Excel (.xlsx) sheets with dynamic formulas directly on disk.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Air-Gap Security Checklist */}
          <div className="glass-panel p-6 rounded-2xl space-y-4 border border-slate-800 shadow-xl">
            <div className="flex items-center gap-2 text-emerald-400 font-mono text-xs font-bold uppercase tracking-wider">
              <Shield className="w-4 h-4" />
              <span>Sovereignty & Security Guarantees</span>
            </div>

            <div className="space-y-2.5 text-xs font-mono">
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">Network Isolation</span>
                <span className="text-emerald-400 font-semibold">Podman --network=none</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">AST Allowlist</span>
                <span className="text-emerald-400 font-semibold">Safe Parse (No eval)</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">Excel Formulas</span>
                <span className="text-emerald-400 font-semibold">Real OpenXML =SUM()</span>
              </div>
              <div className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800/80">
                <span className="text-slate-300">Local Inference Gateway</span>
                <span className="text-emerald-400 font-semibold">Ollama Local GPU</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
