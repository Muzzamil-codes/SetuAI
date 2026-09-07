"use client";
import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import TraceStream from "../../../components/TraceStream";
import ArtifactDownloadCard from "../../../components/ArtifactDownloadCard";
import { connectWebSocket } from "../../../lib/ws-client";
import { TraceEvent, ArtifactRef } from "../../../lib/types";
import { ColorTheme } from "../../../components/ThemeToggle";

export default function TracePage() {
  const params = useParams();
  const router = useRouter();
  const taskId = params?.taskId as string;

  const [theme, setTheme] = useState<ColorTheme>("dark");
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [artifacts, setArtifacts] = useState<ArtifactRef[]>([]);

  useEffect(() => {
    const saved = localStorage.getItem("setu-theme") as ColorTheme;
    if (saved) setTheme(saved);
  }, []);

  useEffect(() => {
    if (!taskId) return;

    const cleanup = connectWebSocket(taskId, (evt: TraceEvent) => {
      setEvents((prev) => [...prev, evt]);
      if (evt.step === "done" && evt.payload.artifacts) {
        setArtifacts(evt.payload.artifacts as ArtifactRef[]);
      }
    });

    return () => cleanup();
  }, [taskId]);

  const isBgDark = theme === "dark" || theme === "elevated";

  return (
    <main
      className={`min-h-screen p-6 flex flex-col items-center transition-colors duration-300 ${
        isBgDark ? "bg-black text-white" : "bg-gray-100 text-gray-900"
      }`}
    >
      <div className="w-full max-w-3xl space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold">Agent Execution Monitor</h1>
            <p className={`text-xs font-mono ${isBgDark ? "text-zinc-400" : "text-gray-500"}`}>
              Task ID: {taskId}
            </p>
          </div>
          <button
            onClick={() => router.push("/")}
            className={`text-xs px-3 py-1.5 rounded transition border ${
              isBgDark
                ? "bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border-zinc-700"
                : "bg-white hover:bg-gray-100 text-gray-800 border-gray-300"
            }`}
          >
            ← Back
          </button>
        </div>

        <TraceStream events={events} theme={theme} />
        <ArtifactDownloadCard artifacts={artifacts} theme={theme} />
      </div>
    </main>
  );
}