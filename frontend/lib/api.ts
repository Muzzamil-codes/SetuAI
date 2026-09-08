import { TaskInput } from "./types";

const BACKEND_HTTP_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export async function uploadFile(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BACKEND_HTTP_URL}/upload`, {
    method: "POST",
    body: formData,
  });

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
