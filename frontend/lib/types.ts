export interface TaskInput {
  task_id?: string;
  modality: "text" | "image" | "file";
  content: string;
  context: Record<string, unknown>;
  model_override?: string;
}

export type StepType =
  | "classify"
  | "plan"
  | "tool_call"
  | "verify_pass"
  | "verify_fail"
  | "retry"
  | "generate"
  | "done"
  | "error";

export interface ArtifactRef {
  type: "docx" | "xlsx" | "pptx" | "py" | "txt" | "md" | "code";
  filename: string;
  path: string;
}

export interface TraceEvent {
  task_id: string;
  step: StepType;
  payload: Record<string, any>;
  timestamp: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  taskId?: string;
  traceEvents?: TraceEvent[];
  artifacts?: ArtifactRef[];
  isStreaming?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  model: string;
}