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
    <main className="min-h-screen p-6 bg-gray-50 dark:bg-black text-gray-900 dark:text-white flex flex-col items-center">
      <div className="w-full max-w-4xl space-y-6">
        <div className="flex items-center justify-between mt-8 border-b border-gray-200 dark:border-zinc-800 pb-4">
          <div>
            <h1 className="text-3xl font-bold">Model Configuration</h1>
            <p className="text-sm text-gray-500 mt-1">
              Configure local and remote LLM/VLM connections visually.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => router.push("/")}
              className="px-4 py-2 text-sm bg-white dark:bg-zinc-800 border border-gray-200 dark:border-zinc-700 rounded hover:bg-gray-50 dark:hover:bg-zinc-700 transition"
            >
              Back to Home
            </button>
            <button
              onClick={handleSaveAll}
              className="px-4 py-2 text-sm bg-blue-600 hover:bg-blue-700 text-white font-medium rounded transition shadow"
            >
              Save Configuration
            </button>
          </div>
        </div>

        {error && <div className="p-4 bg-red-50 text-red-700 border border-red-200 rounded-lg">{error}</div>}
        {status && <div className="p-4 bg-green-50 text-green-700 border border-green-200 rounded-lg">{status}</div>}

        <div className="space-y-4">
          {models.map((model, idx) => (
            <div key={idx} className="p-5 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-xl shadow-sm relative">
              <button 
                onClick={() => removeModel(idx)}
                className="absolute top-4 right-4 text-red-500 hover:text-red-700 hover:bg-red-50 p-1 rounded transition text-sm"
              >
                Delete
              </button>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Model Name (e.g. llama3.2)</label>
                  <input
                    type="text"
                    value={model.name}
                    onChange={(e) => updateModel(idx, "name", e.target.value)}
                    className="w-full p-2 text-sm bg-gray-50 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Endpoint (e.g. http://192.168.1.10:11434/v1)</label>
                  <input
                    type="text"
                    value={model.endpoint}
                    onChange={(e) => updateModel(idx, "endpoint", e.target.value)}
                    className="w-full p-2 text-sm bg-gray-50 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Role Pipeline</label>
                  <select
                    value={model.role}
                    onChange={(e) => updateModel(idx, "role", e.target.value)}
                    className="w-full p-2 text-sm bg-gray-50 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="reasoning">reasoning (Verification & Drafting)</option>
                    <option value="codegen">codegen (Code Generation)</option>
                    <option value="extraction">extraction (Vision / OCR)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Modality</label>
                  <select
                    value={model.modality}
                    onChange={(e) => updateModel(idx, "modality", e.target.value)}
                    className="w-full p-2 text-sm bg-gray-50 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    <option value="text">text (Standard LLM)</option>
                    <option value="vision">vision (VLM)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Quantization</label>
                  <input
                    type="text"
                    value={model.quant}
                    onChange={(e) => updateModel(idx, "quant", e.target.value)}
                    className="w-full p-2 text-sm bg-gray-50 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">VRAM Required (MB)</label>
                  <input
                    type="number"
                    value={model.vram_mb}
                    onChange={(e) => updateModel(idx, "vram_mb", Number(e.target.value))}
                    className="w-full p-2 text-sm bg-gray-50 dark:bg-zinc-950 border border-gray-200 dark:border-zinc-800 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={addModel}
          className="w-full py-4 border-2 border-dashed border-gray-300 dark:border-zinc-700 rounded-xl text-gray-500 hover:text-gray-700 dark:hover:text-zinc-300 hover:bg-gray-50 dark:hover:bg-zinc-800/50 transition font-medium"
        >
          + Add New Model Connection
        </button>
      </div>
    </main>
  );
}
