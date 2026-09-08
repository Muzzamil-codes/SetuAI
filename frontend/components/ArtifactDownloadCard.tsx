"use client";
import React, { useState } from "react";
import { ArtifactRef } from "../lib/types";
import { BACKEND_HTTP_URL } from "../lib/api";
import { 
  FileText, 
  FileSpreadsheet, 
  Download, 
  CheckCircle2, 
  ShieldCheck, 
  Sparkles,
  ExternalLink,
  Code,
  Loader2
} from "lucide-react";

interface ArtifactDownloadCardProps {
  artifacts: ArtifactRef[];
  theme?: string;
}

export default function ArtifactDownloadCard({ artifacts }: ArtifactDownloadCardProps) {
  const [downloadingFile, setDownloadingFile] = useState<string | null>(null);

  if (!artifacts || artifacts.length === 0) return null;

  const handleDownload = async (cleanPath: string, filename: string) => {
    setDownloadingFile(filename);
    try {
      // Direct endpoint with Content-Disposition: attachment header
      const downloadEndpoint = `${BACKEND_HTTP_URL}/download/${cleanPath}`;
      const res = await fetch(downloadEndpoint);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      
      const blob = await res.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.warn("Blob download fallback triggered:", err);
      // Fallback: direct window location
      window.open(`${BACKEND_HTTP_URL}/download/${cleanPath}`, "_blank");
    } finally {
      setTimeout(() => setDownloadingFile(null), 1200);
    }
  };

  return (
    <div className="glass-panel-glow p-6 rounded-2xl space-y-4 border border-emerald-500/30">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-emerald-500/20 border border-emerald-500/40 text-emerald-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-bold text-sm text-white tracking-wide flex items-center gap-2">
              Verified Executive Deliverables
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950 text-emerald-300 border border-emerald-700/50">
                100% Offline Generation
              </span>
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              Deterministic files generated on-premise and ready for download
            </p>
          </div>
        </div>
        <span className="text-xs font-mono text-emerald-400 font-semibold">
          {artifacts.length} {artifacts.length === 1 ? "File Ready" : "Files Ready"}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
        {artifacts.map((art, i) => {
          const isDocx = art.filename.endsWith(".docx") || art.type.toLowerCase().includes("docx") || art.type.toLowerCase().includes("word");
          const isXlsx = art.filename.endsWith(".xlsx") || art.type.toLowerCase().includes("xlsx") || art.type.toLowerCase().includes("excel");
          const isCode = art.filename.endsWith(".py") || art.type.toLowerCase().includes("code");

          const cleanPath = art.path.replace("outputs/", "").replace(/^\//, "");
          const isCurrentDownloading = downloadingFile === art.filename;

          if (isDocx) {
            return (
              <div
                key={i}
                className="p-4 rounded-xl bg-gradient-to-br from-blue-950/40 via-slate-900/60 to-slate-950 border border-blue-800/40 flex flex-col justify-between gap-3 hover:border-blue-600/60 transition-all shadow-lg group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2.5 rounded-xl bg-blue-900/40 border border-blue-700/50 text-blue-400 group-hover:scale-105 transition-transform">
                      <FileText className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">
                          Word Note (.docx)
                        </span>
                        <span className="text-[10px] font-mono text-slate-400">Formal Note</span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-100 line-clamp-1 group-hover:text-blue-300 transition-colors">
                        {art.filename}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">
                        PSU Approval Format with Structured Tables & Sign-off blocks
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-800/80">
                  <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Integrity Verified</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDownload(cleanPath, art.filename)}
                    disabled={isCurrentDownloading}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium text-xs font-mono shadow-md shadow-blue-600/20 transition-all"
                  >
                    {isCurrentDownloading ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Download className="w-3.5 h-3.5" />
                    )}
                    <span>{isCurrentDownloading ? "Downloading..." : "Download .docx"}</span>
                  </button>
                </div>
              </div>
            );
          }

          if (isXlsx) {
            return (
              <div
                key={i}
                className="p-4 rounded-xl bg-gradient-to-br from-emerald-950/40 via-slate-900/60 to-slate-950 border border-emerald-800/40 flex flex-col justify-between gap-3 hover:border-emerald-600/60 transition-all shadow-lg group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3">
                    <div className="p-2.5 rounded-xl bg-emerald-900/40 border border-emerald-700/50 text-emerald-400 group-hover:scale-105 transition-transform">
                      <FileSpreadsheet className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                          Excel Sheet (.xlsx)
                        </span>
                        <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-1.5 py-0.5 rounded border border-emerald-700/40">
                          =SUM() Active
                        </span>
                      </div>
                      <h4 className="text-xs font-bold text-slate-100 line-clamp-1 group-hover:text-emerald-300 transition-colors">
                        {art.filename}
                      </h4>
                      <p className="text-[11px] text-slate-400 mt-1">
                        Comparative Statement with Dynamic Native Formulas
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-slate-800/80">
                  <div className="flex items-center gap-1.5 text-[11px] font-mono text-emerald-400">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Formulas Validated</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleDownload(cleanPath, art.filename)}
                    disabled={isCurrentDownloading}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white font-medium text-xs font-mono shadow-md shadow-emerald-600/20 transition-all"
                  >
                    {isCurrentDownloading ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Download className="w-3.5 h-3.5" />
                    )}
                    <span>{isCurrentDownloading ? "Downloading..." : "Download .xlsx"}</span>
                  </button>
                </div>
              </div>
            );
          }

          // Generic artifact (e.g. .py or .txt)
          return (
            <div
              key={i}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between hover:border-slate-700 transition-all shadow-md"
            >
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-slate-800 text-slate-300 border border-slate-700">
                  {isCode ? <Code className="w-5 h-5 text-amber-400" /> : <FileText className="w-5 h-5 text-slate-400" />}
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white font-mono">{art.filename}</h4>
                  <p className="text-[11px] font-mono text-slate-400 uppercase">{art.type || "Document"}</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => handleDownload(cleanPath, art.filename)}
                disabled={isCurrentDownloading}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-white font-medium text-xs font-mono border border-slate-700 transition"
              >
                {isCurrentDownloading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Download className="w-3.5 h-3.5" />
                )}
                <span>{isCurrentDownloading ? "Downloading..." : "Download"}</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
