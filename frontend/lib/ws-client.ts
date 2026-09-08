import { TraceEvent } from "./types";

export function connectWebSocket(
  taskId: string,
  onEvent: (event: TraceEvent) => void,
  onError?: (err: Event) => void
): () => void {
  const wsUrl = process.env.NEXT_PUBLIC_WS_URL || `ws://localhost:8000/trace/${taskId}`;
  const ws = new WebSocket(wsUrl);

  ws.onmessage = (message) => {
    try {
      const data: TraceEvent = JSON.parse(message.data);
      onEvent(data);
    } catch (err) {
      console.error("JSON parse error:", err);
    }
  };

  if (onError) ws.onerror = onError;

  return () => {
    if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
      ws.close();
    }
  };
}