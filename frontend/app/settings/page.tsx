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
    <div className="h-screen overflow-y-auto bg-[var(--background)]">
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-[var(--border)]">
          <div>
            <h1 className="text-2xl font-bold text-[var(--foreground)] tracking-tight">
            Model Gateway Configuration
          </h1>
          <p className="text-[13px] text-[var(--foreground-muted)] mt-1">
            Configure sovereign LLM & VLM inference endpoints (Ollama / vLLM)
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/")}
            className="px-4 py-2 text-[13px] font-medium bg-[var(--input-bg)] border border-[var(--border)] rounded-xl hover:border-[var(--border-hover)] hover:bg-[var(--accent-light)]/50 text-[var(--foreground)] transition-all shadow-sm"
          >
            ← Mission Control
          </button>
          <button
            onClick={handleSaveAll}
            className="px-5 py-2 text-[13px] font-medium bg-[var(--accent)] hover:bg-[#1a1a1a] text-white rounded-xl transition-all shadow-sm transform active:scale-95"
          >
            Save Registry
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 rounded-xl text-[13px] font-medium shadow-sm">
          {error}
        </div>
      )}
      {status && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 rounded-xl text-[13px] font-medium shadow-sm">
          {status}
        </div>
      )}

      <div className="space-y-5">
        {models.map((model, idx) => (
          <div key={idx} className="p-6 bg-[var(--input-bg)] rounded-[20px] border border-[var(--border)] space-y-5 relative shadow-card hover:shadow-composer transition-shadow duration-300">
            <div className="flex items-center justify-between pb-3 border-b border-[var(--border)]">
              <div className="flex items-center gap-3">
                <span className="text-[11px] font-mono font-bold text-[var(--foreground-muted)] px-2 py-0.5 rounded bg-[var(--accent-light)] border border-[var(--border)]">
                  #{idx + 1}
                </span>
                <span className="text-[14px] font-semibold text-[var(--foreground)]">{model.name}</span>
              </div>
              <button 
                onClick={() => removeModel(idx)}
                className="text-rose-600 hover:text-rose-700 text-[12px] font-medium px-3 py-1.5 rounded-lg bg-rose-50 border border-rose-100 hover:bg-rose-100 transition-colors"
              >
                Remove
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div>
                <label className="block text-[12px] font-medium text-[var(--foreground-muted)] mb-1.5">Model Identifier (Ollama / Local)</label>
                <input
                  type="text"
                  value={model.name}
                  onChange={(e) => updateModel(idx, "name", e.target.value)}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                />
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[var(--foreground-muted)] mb-1.5">Local Inference Endpoint</label>
                <input
                  type="text"
                  value={model.endpoint}
                  onChange={(e) => updateModel(idx, "endpoint", e.target.value)}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                />
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[var(--foreground-muted)] mb-1.5">Pipeline Role</label>
                <select
                  value={model.role}
                  onChange={(e) => updateModel(idx, "role", e.target.value)}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                >
                  <option value="reasoning">reasoning (Deterministic & SymPy)</option>
                  <option value="codegen">codegen (Code Sandbox & Artifacts)</option>
                  <option value="extraction">extraction (Vision / OCR)</option>
                </select>
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[var(--foreground-muted)] mb-1.5">Modality</label>
                <select
                  value={model.modality}
                  onChange={(e) => updateModel(idx, "modality", e.target.value)}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                >
                  <option value="text">text (Standard LLM)</option>
                  <option value="vision">vision (Multimodal VLM)</option>
                </select>
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[var(--foreground-muted)] mb-1.5">Quantization</label>
                <input
                  type="text"
                  value={model.quant}
                  onChange={(e) => updateModel(idx, "quant", e.target.value)}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                />
              </div>
              <div>
                <label className="block text-[12px] font-medium text-[var(--foreground-muted)] mb-1.5">Estimated VRAM (MB)</label>
                <input
                  type="number"
                  value={model.vram_mb}
                  onChange={(e) => updateModel(idx, "vram_mb", Number(e.target.value))}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={addModel}
        className="w-full py-4 border-2 border-dashed border-[var(--border)] rounded-[20px] text-[13px] font-medium text-[var(--foreground-muted)] hover:text-[var(--foreground)] hover:border-[var(--border-hover)] hover:bg-[var(--accent-light)]/50 transition-all duration-200"
      >
        + Register Additional Sovereign Model Endpoint
      </button>
    </main>
    </div>
  );
}
