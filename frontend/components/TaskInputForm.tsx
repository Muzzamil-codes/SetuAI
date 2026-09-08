"use client";
import React, { useState } from "react";
import { uploadFile, submitTask } from "../lib/api";
import { 
  Sparkles, 
  Send, 
  Paperclip, 
  X, 
  Cpu, 
  ShieldCheck, 
  FileText, 
  FileSpreadsheet, 
  Terminal, 
  AlertCircle,
  Layers,
  ArrowRight
} from "lucide-react";

interface TaskInputFormProps {
  onTaskStarted: (taskId: string) => void;
  theme?: string;
}

interface PresetScenario {
  id: string;
  icon: React.ReactNode;
  title: string;
  badge: string;
  badgeColor: string;
  model: string;
  prompt: string;
}

export default function TaskInputForm({ onTaskStarted }: TaskInputFormProps) {
  const [instructions, setInstructions] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null);

  const presets: PresetScenario[] = [
    {
      id: "valve_numeric",
      icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
      title: "Refinery Valve Safety Verification",
      badge: "AST SymPy Check",
      badgeColor: "bg-emerald-950/70 text-emerald-400 border-emerald-700/50",
      model: "DeepSeek-R1 (8B)",
      prompt: "Verify whether the refinery outlet pressure reading of 4.2 bar is strictly within the certified safety limit of 5.0 bar. Run the deterministic SymPy AST checker with 0.01 bar tolerance and generate the verification audit report.",
    },
    {
      id: "gm_docx",
      icon: <FileText className="w-4 h-4 text-blue-400" />,
      title: "Executive GM Approval Note (.docx)",
      badge: "Word Deliverable",
      badgeColor: "bg-blue-950/70 text-blue-400 border-blue-700/50",
      model: "Qwen2.5-Coder (7B)",
      prompt: "Draft an executive PSU General Manager Approval Note in Microsoft Word (.docx) for procuring hydrocracker emergency shutdown valves from L&T Heavy Engineering, including technical specifications table, estimated cost breakdown, and dual signatory approval blocks.",
    },
    {
      id: "vendor_xlsx",
      icon: <FileSpreadsheet className="w-4 h-4 text-green-400" />,
      title: "Vendor Comparative Statement (.xlsx)",
      badge: "Dynamic Formulas",
      badgeColor: "bg-green-950/70 text-green-400 border-green-700/50",
      model: "Qwen2.5-Coder (7B)",
      prompt: "Generate a tender comparative statement in Microsoft Excel (.xlsx) evaluating three vendors (L&T Heavy Engineering, BHEL, and Godrej Process Equipment) for high-pressure refinery pumps. Embed dynamic Excel '=SUM()' formulas, evaluate the lowest bidder, and generate variance calculations.",
    },
    {
      id: "fluid_sandbox",
      icon: <Terminal className="w-4 h-4 text-amber-400" />,
      title: "Darcy-Weisbach Fluid Sandbox",
      badge: "Zero-Egress Sandbox",
      badgeColor: "bg-amber-950/70 text-amber-400 border-amber-700/50",
      model: "DeepSeek-R1 (8B)",
      prompt: "Write a verified Python script to compute the Darcy-Weisbach head loss in a 120m crude oil line (diameter=0.15m, velocity=2.4m/s, f=0.022). Execute inside the rootless Podman zero-egress sandbox, catch any assertion faults, and self-heal automatically.",
    },
  ];

  const handleApplyPreset = (preset: PresetScenario) => {
    setSelectedPreset(preset.id);
    setInstructions(preset.prompt);
  };

  // Dynamic model routing prediction based on prompt content
  const getPredictedRouting = () => {
    const text = instructions.toLowerCase();
    if (!text) return null;
    if (text.includes("sympy") || text.includes("bar") || text.includes("pressure") || text.includes("tolerance") || text.includes("verify") || text.includes("darcy")) {
      return {
        model: "DeepSeek-R1 (8B)",
        type: "Deterministic Reasoning & Symbolic Math",
        badgeColor: "text-purple-400 border-purple-800/60 bg-purple-950/40",
      };
    }
    return {
      model: "Qwen2.5-Coder (7B)",
      type: "Structured Document & Code Synthesis",
      badgeColor: "text-cyan-400 border-cyan-800/60 bg-cyan-950/40",
    };
  };

  const predictedRouting = getPredictedRouting();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!instructions.trim()) return;

    setLoading(true);
    setError(null);

    try {
      let modality: "text" | "image" | "file" = "text";
      let content = instructions;

      if (file) {
        const uploadedPath = await uploadFile(file);
        content = uploadedPath;
        if (file.type.startsWith("image/")) {
          modality = "image";
        } else {
          modality = "file";
        }
      }

      const taskId = await submitTask({
        modality,
        content,
        context: { original_instructions: instructions },
      });

      onTaskStarted(taskId);
    } catch (err: any) {
      console.error("Task submission failed:", err);
      setError(err.message || "Failed to dispatch task to sovereign gateway. Ensure FastAPI is running on port 8000.");
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Quick Scenario Presets */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <label className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            Operational Presets (One-Click Scenarios)
          </label>
          <span className="text-[11px] font-mono text-slate-500">Live PSU / Refinery test cases</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {presets.map((preset) => {
            const isSelected = selectedPreset === preset.id;
            return (
              <button
                key={preset.id}
                type="button"
                onClick={() => handleApplyPreset(preset)}
                className={`p-3 rounded-xl text-left transition-all border flex flex-col justify-between group ${
                  isSelected
                    ? "bg-slate-800/90 border-emerald-500/50 shadow-md shadow-emerald-500/10"
                    : "bg-slate-900/60 hover:bg-slate-850 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-slate-800 border border-slate-700 group-hover:scale-105 transition-transform">
                      {preset.icon}
                    </div>
                    <span className="text-xs font-semibold text-slate-200 group-hover:text-white line-clamp-1">
                      {preset.title}
                    </span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border whitespace-nowrap ${preset.badgeColor}`}>
                    {preset.badge}
                  </span>
                </div>
                <div className="flex items-center justify-between pt-1 border-t border-slate-800/60 text-[11px] font-mono text-slate-400">
                  <span>Model: {preset.model}</span>
                  <ArrowRight className="w-3 h-3 text-slate-500 group-hover:text-emerald-400 group-hover:translate-x-0.5 transition-all" />
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Main Command Console Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-6 rounded-2xl space-y-4 shadow-2xl relative overflow-hidden">
        {/* Glowing border top accent */}
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-emerald-500/40 via-cyan-500/40 to-indigo-500/40" />

        {error && (
          <div className="p-3.5 bg-rose-950/50 border border-rose-800 text-rose-300 rounded-xl text-xs flex items-center gap-2.5">
            <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-mono uppercase tracking-wider text-slate-300 flex items-center gap-2">
              <Terminal className="w-3.5 h-3.5 text-cyan-400" />
              Sovereign Command Instructions
            </label>
            {predictedRouting && (
              <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-[11px] font-mono ${predictedRouting.badgeColor}`}>
                <Cpu className="w-3 h-3" />
                <span>Auto-Routing: <strong>{predictedRouting.model}</strong></span>
              </div>
            )}
          </div>
          <textarea
            rows={4}
            value={instructions}
            onChange={(e) => {
              setInstructions(e.target.value);
              setSelectedPreset(null);
            }}
            placeholder="Type your industrial directive or select an operational preset above (e.g. verify pressure tolerance, compile tender sheet with formulas, generate executive note)..."
            className="w-full p-3.5 rounded-xl bg-slate-950/80 border border-slate-800 text-slate-100 text-xs font-mono placeholder:text-slate-500 focus:outline-none focus:border-emerald-500/70 focus:ring-1 focus:ring-emerald-500/50 transition-all resize-y min-h-[105px]"
            required
          />
        </div>

        {/* Attachment upload */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800/80">
          <div className="flex items-center gap-2">
            <label className="cursor-pointer flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs font-mono transition">
              <Paperclip className="w-3.5 h-3.5 text-slate-400" />
              <span>Attach Document / P&ID Image</span>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
              />
            </label>
            {file && (
              <div className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-800/90 border border-slate-700 text-xs font-mono text-slate-300">
                <span className="truncate max-w-[200px]">{file.name}</span>
                <span className="text-[10px] text-slate-500">({(file.size / 1024).toFixed(1)} KB)</span>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="text-slate-400 hover:text-rose-400"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={loading || !instructions.trim()}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl font-medium text-xs tracking-wide text-white bg-gradient-to-r from-emerald-600 via-teal-600 to-cyan-600 hover:from-emerald-500 hover:to-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-emerald-500/20 transition-all group"
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Dispatching Pipeline...</span>
              </>
            ) : (
              <>
                <span>EXECUTE SOVEREIGN AGENT</span>
                <Send className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
