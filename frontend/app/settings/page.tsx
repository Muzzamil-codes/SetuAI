"use client";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getModels, saveModels, getManagerModel, saveManagerModel, getKnowledgeFiles, uploadKnowledgeFile, deleteKnowledgeFile, reindexKnowledge, queryKnowledge, getEmbeddingConfig, saveEmbeddingConfig } from "../../lib/api";
import { Database, Search, Upload, Trash2, RefreshCw, HardDrive, Bot } from "lucide-react";

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
  const [managerModel, setManagerModel] = useState<string>("deepseek-r1:8b");
  const [status, setStatus] = useState<string>("");
  const [error, setError] = useState<string>("");
  
  // Knowledge Base State
  const [knowledgeFiles, setKnowledgeFiles] = useState<any[]>([]);
  const [ragQuery, setRagQuery] = useState("");
  const [ragResults, setRagResults] = useState<any[]>([]);
  const [ragLoading, setRagLoading] = useState(false);
  const [embeddingConfig, setEmbeddingConfig] = useState({ provider: "default", model_name: "", endpoint: "" });
  const [knowledgeStatus, setKnowledgeStatus] = useState("");
  const [reindexing, setReindexing] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await getModels();
        setModels(data);
      } catch (err: any) {
        setError(err.message);
      }
      try {
        const mgr = await getManagerModel();
        if (mgr) setManagerModel(mgr);
      } catch (err: any) {
        console.error("Failed to load manager model:", err);
      }
    }
    async function loadKnowledge() {
      try {
        const files = await getKnowledgeFiles();
        setKnowledgeFiles(files);
        const config = await getEmbeddingConfig();
        if (config) setEmbeddingConfig(config);
      } catch (err: any) {
        console.error("Failed to load knowledge info:", err);
      }
    }
    load();
    loadKnowledge();
  }, []);

  const handleSaveAll = async () => {
    setStatus("");
    setError("");
    try {
      await saveModels(models);
      await saveManagerModel(managerModel);
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

  // Knowledge Base Handlers
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    try {
      setKnowledgeStatus("Uploading...");
      await uploadKnowledgeFile(e.target.files[0]);
      setKnowledgeStatus("Upload successful");
      const files = await getKnowledgeFiles();
      setKnowledgeFiles(files);
    } catch (err: any) {
      setKnowledgeStatus("Upload failed: " + err.message);
    }
  };

  const handleDeleteFile = async (filename: string) => {
    try {
      await deleteKnowledgeFile(filename);
      const files = await getKnowledgeFiles();
      setKnowledgeFiles(files);
    } catch (err: any) {
      setKnowledgeStatus("Delete failed: " + err.message);
    }
  };

  const handleReindex = async () => {
    try {
      setReindexing(true);
      setKnowledgeStatus("Re-indexing...");
      await reindexKnowledge();
      setKnowledgeStatus("Re-indexing complete!");
    } catch (err: any) {
      setKnowledgeStatus("Re-index failed: " + err.message);
    } finally {
      setReindexing(false);
    }
  };

  const handleRagQuery = async () => {
    if (!ragQuery.trim()) return;
    try {
      setRagLoading(true);
      const data = await queryKnowledge(ragQuery);
      setRagResults(data.results || data || []);
    } catch (err: any) {
      setKnowledgeStatus("Query failed: " + err.message);
    } finally {
      setRagLoading(false);
    }
  };

  const handleSaveEmbeddingConfig = async () => {
    try {
      await saveEmbeddingConfig(embeddingConfig);
      setKnowledgeStatus("Embedding config saved!");
    } catch (err: any) {
      setKnowledgeStatus("Failed to save config: " + err.message);
    }
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

      {/* SetuAI Manager Agent Selection Card */}
      <div className="p-6 bg-[var(--input-bg)] rounded-[20px] border-2 border-purple-200/80 bg-gradient-to-br from-purple-50/40 via-[var(--input-bg)] to-transparent shadow-card space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[var(--border)]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-purple-100 border border-purple-200 flex items-center justify-center text-purple-700">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-[15px] font-bold text-[var(--foreground)]">SetuAI Manager Agent</h2>
              <p className="text-[12px] text-[var(--foreground-muted)]">
                The primary reasoning persona that converses with users and orchestrates specialist sub-graphs.
              </p>
            </div>
          </div>
          <span className="px-3 py-1 rounded-full bg-purple-100 text-purple-800 border border-purple-200 text-[11px] font-mono font-semibold self-start sm:self-center">
            Active: {managerModel || "deepseek-r1:8b"}
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 items-center">
          <div>
            <label className="block text-[12px] font-medium text-[var(--foreground)] mb-1.5">
              Select Manager Model
            </label>
            <select
              value={managerModel}
              onChange={(e) => setManagerModel(e.target.value)}
              className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-purple-400 focus:ring-2 focus:ring-purple-400/20 focus:outline-none transition-all"
            >
              {models.map((m) => (
                <option key={m.name} value={m.name}>
                  {m.name} ({m.role || m.modality})
                </option>
              ))}
            </select>
          </div>
          <div className="text-[12px] leading-relaxed text-[var(--foreground-muted)] bg-[var(--background)] p-3 rounded-xl border border-[var(--border)]">
            💡 When users chat in Mission Control, this model evaluates prompts in a ReAct loop, coordinates <code className="text-[11px] text-purple-700 bg-purple-50 px-1 py-0.5 rounded">codegen_graph</code>, <code className="text-[11px] text-blue-700 bg-blue-50 px-1 py-0.5 rounded">drafting_graph</code>, and <code className="text-[11px] text-emerald-700 bg-emerald-50 px-1 py-0.5 rounded">vision_graph</code>, and delivers final responses.
          </div>
        </div>
      </div>

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
                  value={model.name === managerModel ? "manager" : model.role}
                  onChange={(e) => {
                    const val = e.target.value;
                    updateModel(idx, "role", val);
                    if (val === "manager") {
                      setManagerModel(model.name);
                    }
                  }}
                  className="w-full p-2.5 text-[13px] font-mono bg-[var(--background)] border border-[var(--border)] rounded-xl text-[var(--foreground)] focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 focus:outline-none transition-all"
                >
                  <option value="manager">manager (SetuAI ReAct Orchestrator)</option>
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

      <hr className="border-slate-800 my-8" />

      {/* Knowledge Base & RAG Section */}
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-wide flex items-center gap-2">
            <Database className="w-5 h-5 text-cyan-400" />
            Knowledge Base & RAG Pipeline
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Upload SOPs, manuals, and reference documents for AI context grounding
          </p>
        </div>

        {knowledgeStatus && (
          <div className="p-3.5 bg-slate-900/50 border border-slate-800 text-slate-300 rounded-xl text-xs font-mono">
            {knowledgeStatus}
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Config & Upload */}
          <div className="space-y-6">
            {/* Embedding Model Configuration */}
            <div className="p-5 glass-panel rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-slate-400" />
                Embedding Model
              </h3>
              <div>
                <label className="block text-[11px] font-mono text-slate-400 mb-1">Provider</label>
                <select
                  value={embeddingConfig.provider}
                  onChange={(e) => setEmbeddingConfig({ ...embeddingConfig, provider: e.target.value })}
                  className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                >
                  <option value="default">Default (ChromaDB / all-MiniLM-L6-v2)</option>
                  <option value="ollama">Ollama</option>
                </select>
              </div>
              
              {embeddingConfig.provider === "ollama" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-[11px] font-mono text-slate-400 mb-1">Model Name</label>
                    <input
                      type="text"
                      placeholder="e.g. nomic-embed-text"
                      value={embeddingConfig.model_name}
                      onChange={(e) => setEmbeddingConfig({ ...embeddingConfig, model_name: e.target.value })}
                      className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="block text-[11px] font-mono text-slate-400 mb-1">Ollama Endpoint</label>
                    <input
                      type="text"
                      placeholder="http://localhost:11434"
                      value={embeddingConfig.endpoint}
                      onChange={(e) => setEmbeddingConfig({ ...embeddingConfig, endpoint: e.target.value })}
                      className="w-full p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                </div>
              )}
              
              <button
                onClick={handleSaveEmbeddingConfig}
                className="w-full py-2 text-xs font-mono font-medium bg-slate-800 hover:bg-slate-700 text-white rounded-xl transition"
              >
                Save Config
              </button>
            </div>

            {/* File Upload */}
            <div className="p-5 glass-panel rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <Upload className="w-4 h-4 text-slate-400" />
                Ingest Documents
              </h3>
              <div className="border-2 border-dashed border-slate-800 rounded-xl p-8 text-center bg-slate-950/50 hover:bg-slate-900/50 transition relative">
                <input 
                  type="file" 
                  onChange={handleFileUpload} 
                  className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  title="Upload a file"
                />
                <div className="pointer-events-none">
                  <Upload className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                  <p className="text-xs font-mono text-slate-400">Click or drag file to upload</p>
                  <p className="text-[10px] text-slate-500 mt-1">Supports PDF, TXT, MD, CSV</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: Files & RAG Testing */}
          <div className="space-y-6">
            {/* File List */}
            <div className="p-5 glass-panel rounded-2xl border border-slate-800 space-y-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-slate-400" />
                  Knowledge Files
                </h3>
                <button
                  onClick={handleReindex}
                  disabled={reindexing}
                  className="flex items-center gap-1.5 px-3 py-1.5 text-[11px] font-mono font-medium bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 rounded-lg hover:bg-emerald-600/30 transition disabled:opacity-50"
                >
                  <RefreshCw className={`w-3 h-3 ${reindexing ? 'animate-spin' : ''}`} />
                  {reindexing ? 'Indexing...' : 'Re-index All'}
                </button>
              </div>
              
              <div className="bg-slate-950/90 border border-slate-800 rounded-xl overflow-hidden max-h-[250px] overflow-y-auto">
                {knowledgeFiles.length === 0 ? (
                  <div className="p-4 text-center text-xs text-slate-500 font-mono">No files uploaded yet</div>
                ) : (
                  <ul className="divide-y divide-slate-800">
                    {knowledgeFiles.map((f, i) => (
                      <li key={i} className="p-3 flex items-center justify-between hover:bg-slate-900/50 transition">
                        <div className="flex flex-col overflow-hidden">
                          <span className="text-xs text-slate-300 font-mono truncate">{f.name || f.filename || f}</span>
                          {f.size && <span className="text-[10px] text-slate-500">{(f.size / 1024).toFixed(1)} KB</span>}
                        </div>
                        <button
                          onClick={() => handleDeleteFile(f.name || f.filename || f)}
                          className="p-1.5 text-rose-400 hover:text-rose-300 hover:bg-rose-950/50 rounded-lg transition"
                          title="Delete file"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>

            {/* RAG Query Test */}
            <div className="p-5 glass-panel rounded-2xl border border-slate-800 space-y-4">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <Search className="w-4 h-4 text-slate-400" />
                Vector Search Test
              </h3>
              
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Test retrieval..."
                  value={ragQuery}
                  onChange={(e) => setRagQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleRagQuery()}
                  className="flex-1 p-2.5 text-xs font-mono bg-slate-950/90 border border-slate-800 rounded-xl text-slate-200 focus:border-emerald-500 focus:outline-none"
                />
                <button
                  onClick={handleRagQuery}
                  disabled={ragLoading}
                  className="px-4 py-2.5 text-xs font-mono font-medium bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl transition disabled:opacity-50"
                >
                  {ragLoading ? '...' : 'Search'}
                </button>
              </div>

              {ragResults.length > 0 && (
                <div className="space-y-3 mt-4 max-h-[300px] overflow-y-auto">
                  {ragResults.map((r, i) => (
                    <div key={i} className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg text-xs font-mono space-y-1">
                      <div className="flex justify-between items-center text-[10px] text-slate-500 mb-1 border-b border-slate-800 pb-1">
                        <span className="truncate">{r.metadata?.source || r.source || 'Unknown'}</span>
                        <span className="text-cyan-500">Score: {r.score ? r.score.toFixed(3) : 'N/A'}</span>
                      </div>
                      <p className="text-slate-300 line-clamp-3 leading-relaxed">{r.page_content || r.content || r.text || JSON.stringify(r)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
    </div>
  );
}
