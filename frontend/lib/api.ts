import { TaskInput } from "./types";

export const BACKEND_HTTP_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function uploadFile(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${BACKEND_HTTP_URL}/upload`, { method: "POST", body: formData });
  if (!res.ok) throw new Error("Upload failed");
  const data: { path: string } = await res.json();
  return data.path;
}

export async function submitTask(input: Omit<TaskInput, "task_id">): Promise<string> {
  const res = await fetch(`${BACKEND_HTTP_URL}/task`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error("Task start failed");
  const data: { task_id: string } = await res.json();
  return data.task_id;
}

export async function getModels(): Promise<any[]> {
  const res = await fetch(`${BACKEND_HTTP_URL}/models`);
  if (!res.ok) throw new Error("Failed to fetch models");
  return res.json();
}

export async function saveModels(models: any[]): Promise<void> {
  const res = await fetch(`${BACKEND_HTTP_URL}/models`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(models),
  });
  if (!res.ok) throw new Error("Failed to save models");
}

export async function getManagerModel(): Promise<string> {
  const res = await fetch(`${BACKEND_HTTP_URL}/settings/manager-model`);
  if (!res.ok) throw new Error("Failed to fetch manager model");
  const data = await res.json();
  return data.manager_model || "deepseek-r1:8b";
}

export async function saveManagerModel(managerModel: string): Promise<void> {
  const res = await fetch(`${BACKEND_HTTP_URL}/settings/manager-model`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ manager_model: managerModel }),
  });
  if (!res.ok) throw new Error("Failed to save manager model");
}

// ---- Knowledge Base / RAG APIs ----

export async function getKnowledgeFiles(): Promise<any[]> {
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/files`);
  if (!res.ok) throw new Error('Failed to fetch knowledge files');
  return res.json();
}

export async function uploadKnowledgeFile(file: File): Promise<any> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/upload`, { method: 'POST', body: formData });
  if (!res.ok) throw new Error('Failed to upload knowledge file');
  return res.json();
}

export async function deleteKnowledgeFile(filename: string): Promise<void> {
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/files/${encodeURIComponent(filename)}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete knowledge file');
}

export async function reindexKnowledge(): Promise<any> {
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/reindex`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to reindex knowledge base');
  return res.json();
}

export async function queryKnowledge(query: string, topK: number = 5): Promise<any> {
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) throw new Error('Failed to query knowledge base');
  return res.json();
}

export async function getEmbeddingConfig(): Promise<any> {
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/embedding-config`);
  if (!res.ok) throw new Error('Failed to fetch embedding config');
  return res.json();
}

export async function saveEmbeddingConfig(config: any): Promise<void> {
  const res = await fetch(`${BACKEND_HTTP_URL}/knowledge/embedding-config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
  if (!res.ok) throw new Error('Failed to save embedding config');
}

// ---- Conversation History APIs ----

export async function getConversations(): Promise<any[]> {
  const res = await fetch(`${BACKEND_HTTP_URL}/conversations`);
  if (!res.ok) throw new Error("Failed to fetch conversations");
  return res.json();
}

export async function saveConversationAPI(conv: any): Promise<void> {
  const res = await fetch(`${BACKEND_HTTP_URL}/conversations/${conv.id}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(conv),
  });
  if (!res.ok) throw new Error("Failed to save conversation");
}

export async function deleteConversationAPI(convId: string): Promise<void> {
  const res = await fetch(`${BACKEND_HTTP_URL}/conversations/${convId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete conversation");
}
