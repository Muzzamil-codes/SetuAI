"use client";
import React, { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import TraceStream from "../../../components/TraceStream";
import ArtifactDownloadCard from "../../../components/ArtifactDownloadCard";
import { connectWebSocket } from "../../../lib/ws-client";
import { TraceEvent, ArtifactRef } from "../../../lib/types";
import { 
  ArrowLeft, 
  CheckCircle2, 
  Clock, 
  Terminal, 
  ShieldCheck, 
  RefreshCw, 
  Layers,
  AlertCircle,
  FileCheck
} from "lucide-react";

export default function TracePage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params?.taskId as string;

  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [artifacts, setArtifacts] = useState<ArtifactRef[]>([]);
  const [isCompleted, setIsCompleted] = useState(false);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isCompleted) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    timerRef.current = setInterval(() => {
      setElapsedSeconds((s) => s + 1);
    }, 1000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isCompleted]);

  useEffect(() => {
    if (!taskId) return;

    const cleanup = connectWebSocket(taskId, (evt: TraceEvent) => {
      setEvents((prev) => [...prev, evt]);
      if (evt.step === "done") {
        setIsCompleted(true);
        if (evt.payload?.artifacts) {
          setArtifacts(evt.payload.artifacts as ArtifactRef[]);
        }
      }
    });

    return () => cleanup();
  }, [taskId]);

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}s`;
  };

  // Determine current pipeline milestone
  const hasClassified = events.some((e) => e.step.toLowerCase() === "classify");
  const hasPlan = events.some((e) => e.step.toLowerCase() === "plan");
  const hasTool = events.some((e) => e.step.toLowerCase().includes("tool"));
  const hasVerify = events.some((e) => e.step.toLowerCase().includes("pass") || e.step.toLowerCase().includes("fail"));
  const hasDone = isCompleted || events.some((e) => e.step.toLowerCase() === "done");

  return (
    <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Breadcrumbs & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white text-xs font-mono transition"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Mission Control</span>
          </Link>
          <div className="h-4 w-px bg-slate-800 hidden sm:block" />
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-white tracking-wide">
                Agent Execution Cockpit
              </h1>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${
                isCompleted 
                  ? "bg-emerald-950/80 text-emerald-400 border-emerald-700/60"
                  : "bg-cyan-950/80 text-cyan-400 border-cyan-700/60 animate-pulse"
              }`}>
                {isCompleted ? "MISSION COMPLETE" : "PIPELINE EXECUTING"}
              </span>
            </div>
            <p className="text-[11px] font-mono text-slate-400 mt-0.5">
              Task ID: <span className="text-cyan-300 font-semibold">{taskId}</span>
            </p>
          </div>
        </div>

        {/* Live Elapsed Timer */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Elapsed:</span>
            <span className="text-emerald-400 font-bold">{formatTimer(elapsedSeconds)}</span>
          </div>
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 font-mono text-xs">
            <Terminal className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Events:</span>
            <span className="text-cyan-300 font-bold">{events.length}</span>
          </div>
        </div>
      </div>

      {/* Visual Pipeline Progress Track */}
      <div className="glass-panel p-4 rounded-2xl border border-slate-800 hidden sm:block">
        <div className="grid grid-cols-5 gap-2">
          {[
            { label: "1. Classify", active: hasClassified, done: hasPlan },
            { label: "2. Plan Graph", active: hasPlan, done: hasTool },
            { label: "3. Tool Execution", active: hasTool, done: hasVerify },
            { label: "4. AST Verify Gate", active: hasVerify, done: hasDone },
            { label: "5. Deliverables Ready", active: hasDone, done: hasDone },
          ].map((stage, idx) => (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border text-center transition-all ${
                stage.done
                  ? "bg-emerald-950/40 border-emerald-700/50 text-emerald-300"
                  : stage.active
                  ? "bg-cyan-950/40 border-cyan-500/60 text-cyan-300 shadow-md shadow-cyan-500/10"
                  : "bg-slate-900/40 border-slate-800/60 text-slate-600"
              }`}
            >
              <span className="text-[11px] font-mono font-semibold tracking-wider uppercase block">
                {stage.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Deliverable Artifacts Card (Shown if available) */}
      <ArtifactDownloadCard artifacts={artifacts} />

      {/* Real-time Streaming Trace Feed */}
      <TraceStream events={events} />
    </main>
  );
}