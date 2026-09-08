"use client";
import React from "react";
import { ArtifactRef } from "../lib/types";
import { ColorTheme } from "./ThemeToggle";

interface ArtifactDownloadCardProps {
  artifacts: ArtifactRef[];
  theme?: ColorTheme;
}

export default function ArtifactDownloadCard({ artifacts, theme = "elevated" }: ArtifactDownloadCardProps) {
  if (!artifacts || artifacts.length === 0) return null;

  const isCardWhite = theme === "light" || theme === "elevated";

  return (
    <div
      className={`p-4 rounded-xl border space-y-3 shadow-md transition-colors ${
        isCardWhite
          ? "bg-white border-gray-200"
          : "bg-zinc-950 border-zinc-800"
      }`}
    >
      <h3 className={`font-semibold text-sm ${isCardWhite ? "text-emerald-700" : "text-emerald-400"}`}>
        Generated Artifacts (Confidential On-Prem)
      </h3>
      <div className="space-y-2">
        {artifacts.map((art, i) => (
          <div
            key={i}
            className={`flex justify-between items-center p-2.5 rounded-lg border ${
              isCardWhite
                ? "bg-gray-50 border-gray-200"
                : "bg-zinc-900 border-zinc-800"
            }`}
          >
            <div className="flex items-center gap-2">
              <span
                className={`text-xs font-bold uppercase px-2 py-0.5 rounded border ${
                  isCardWhite
                    ? "bg-blue-50 text-blue-700 border-blue-200"
                    : "bg-blue-950 text-blue-400 border-blue-800"
                }`}
              >
                {art.type}
              </span>
              <span className={`text-xs font-medium ${isCardWhite ? "text-gray-800" : "text-zinc-200"}`}>
                {art.filename}
              </span>
            </div>
            <a
              href={`/${art.path}`}
              download={art.filename}
              className="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-3 py-1.5 rounded-md transition shadow"
            >
              Download
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}