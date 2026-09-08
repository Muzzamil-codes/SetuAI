"use client";
import React from "react";
import Link from "next/link";
import { Shield, Cpu, Lock, Sparkles, Terminal, Activity, CheckCircle2 } from "lucide-react";

export default function Navbar() {
  return (
    <header className="w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Left: Brand Identity */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500/20 via-cyan-500/10 to-transparent border border-emerald-500/30 flex items-center justify-center shadow-lg shadow-emerald-500/10 group-hover:border-emerald-500/60 transition-all">
            <Shield className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-base tracking-wider text-white bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text">
                SETU<span className="text-emerald-400 font-mono">.AI</span>
              </span>
              <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-emerald-950/80 text-emerald-400 border border-emerald-700/50">
                AIR-GAPPED
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400 hidden sm:block">
              Sovereign Defense & PSU AI Workbench • Local Sandbox & Formal AST
            </p>
          </div>
        </Link>

        {/* Center: Live Telemetry Status Pills */}
        <div className="hidden lg:flex items-center gap-3">
          {/* Air-gap Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <span className="text-slate-400 font-mono text-[11px]">Egress:</span>
            <span className="text-emerald-400 font-semibold font-mono text-[11px]">ZERO (100% Offline)</span>
          </div>

          {/* Model Status */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400 font-mono text-[11px]">Compute:</span>
            <span className="text-cyan-300 font-semibold font-mono text-[11px]">DeepSeek-R1 + Qwen2.5</span>
          </div>

          {/* Sandbox Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900/90 border border-slate-800 text-xs">
            <Lock className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400 font-mono text-[11px]">Sandbox:</span>
            <span className="text-amber-300 font-semibold font-mono text-[11px]">Podman / SymPy AST</span>
          </div>
        </div>

        {/* Right: Operations & Links */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="text-slate-300">Gateway:</span>
            <span className="text-emerald-400 font-semibold">Active :8000</span>
          </div>
          <Link
            href="/settings"
            className="text-xs font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 transition"
          >
            Models
          </Link>
        </div>
      </div>
    </header>
  );
}
