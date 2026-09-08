export interface TaskInput {
  task_id?: string;
  modality: "text" | "image" | "file";
  content: string;
  context: Record<string, unknown>;
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
  type: "docx" | "xlsx" | "pptx";
  filename: string;
  path: string;
}

export interface TraceEvent {
  task_id: string;
  step: StepType;
  payload: Record<string, any>;
  timestamp: string;
}