"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getModels, saveModels } from "../../lib/api";

type ModelEntry = {
  name: string;
  modality: string;
  role: string;
  quant: string;
  vram_mb: number;
  endpoint: string;
};

export default function SettingsPage() {
  const router = useRouter();
  const [models, setModels] = useState<ModelEntry[]>([]);
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    async function load() {
      try {
        const data = await getModels();
        setModels(data);
      } catch (err: any) {
        setError(err.message);
      }
    }
    load();
  }, []);

  const handleSaveAll = async () => {
    setStatus("");
    setError("");
    try {
      await saveModels(models);
      setStatus("Settings saved successfully!");
    } catch (err: any) {
      setError(err.message);
    }
  };

  const addModel = () => {
    setModels([
      ...models,
      {
        name: "new-model",
        modality: "text",
        role: "reasoning",
        quant: "4-bit",
        vram_mb: 4000,
        endpoint: "http://127.0.0.1:11434/v1"
      }
    ]);
  };

  const updateModel = (index: number, field: keyof ModelEntry, value: any) => {
    const updated = [...models];
    (updated[index] as any)[field] = value;
    setModels(updated);
  };

  const removeModel = (index: number) => {
    setModels(models.filter((_, i) => i !== index));
  };

  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wide">
            Local Model Gateway Configuration
          </h1>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Configure sovereign LLM & VLM inference endpoints (Ollama / vLLM / llama.cpp)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/")}
            className="px-3 py-1.5 text-xs font-mono bg-slate-900 border border-slate-800 rounded-xl hover:bg-slate-800 text-slate-300 transition"
          >
            ← Mission Control
          </button>
          <button
            onClick={handleSaveAll}
            className="px-4 py-1.5 text-xs font-mono font-medium bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl transition shadow-lg shadow-emerald-600/20"
          >
            Save Registry
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3.5 bg-rose-950/50 border border-rose-800 text-rose-300 rounded-xl text-xs font-mono">
          {error}
        </div>
      )}
      {status && (
        <div className="p-3.5 bg-emerald-950/50 border border-emerald-800 text-emerald-300 rounded-xl text-xs font-mono">
          {status}
        </div>
      )}

      <div className="space-y-4">
        {models.map((model, idx) => (
          <div key={idx} className="p-5 glass-panel rounded-2xl border border-slate-800 space-y-4 relative shadow-xl">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono font-bold text-white px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                  #{idx + 1}
                </span>
                <span className="text-xs font-mono text-cyan-300 font-semibold">{model.name}</span>
              </div>
              <button 
                onClick={() => removeModel(idx)}
                className="text-rose-400 hover:text-rose-300 text-xs font-mono px-2 py-1 rounded bg-rose-950/50 border border-rose-800/60 hover:bg-rose-900/50 transition"
              >
                Remove
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Model Identifier (Ollama / Local)</label>
                <input
                  type="text"
                  value={model.name}
                  onChange={(e) => updateModel(idx, "name", e.target.value)}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Local Inference Endpoint</label>
                <input
                  type="text"
                  value={model.endpoint}
                  onChange={(e) => updateModel(idx, "endpoint", e.target.value)}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Pipeline Role</label>
                <select
                  value={model.role}
                  onChange={(e) => updateModel(idx, "role", e.target.value)}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                >
                  <option value="reasoning">reasoning (Deterministic & SymPy Verification)</option>
                  <option value="codegen">codegen (Code Sandbox & OpenXML Artifacts)</option>
                  <option value="extraction">extraction (Vision / OCR)</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Modality</label>
                <select
                  value={model.modality}
                  onChange={(e) => updateModel(idx, "modality", e.target.value)}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                >
                  <option value="text">text (Standard LLM)</option>
                  <option value="vision">vision (Multimodal VLM)</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Quantization</label>
                <input
                  type="text"
                  value={model.quant}
                  onChange={(e) => updateModel(idx, "quant", e.target.value)}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Estimated VRAM (MB)</label>
                <input
                  type="number"
                  value={model.vram_mb}
                  onChange={(e) => updateModel(idx, "vram_mb", Number(e.target.value))}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={addModel}
        className="w-full py-3.5 border border-dashed border-slate-800 rounded-2xl text-xs font-mono text-slate-400 hover:text-emerald-400 hover:border-emerald-500/50 hover:bg-slate-900/40 transition"
      >
        + Register Additional Sovereign Model Endpoint
      </button>
    </main>
  );
}
