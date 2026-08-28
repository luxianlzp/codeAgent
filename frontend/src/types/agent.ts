export type TraceKind =
  | "user_message"
  | "step"
  | "model_request"
  | "model_response"
  | "action"
  | "tool_call"
  | "tool_result"
  | "finish"
  | "error";

export type RunStatus = "idle" | "running" | "finished" | "max_steps" | "error";

export interface TraceEvent {
  kind: TraceKind | string;
  message: string;
  data: Record<string, unknown>;
  timestamp: number;
}

export interface AgentRunResult {
  status: Exclude<RunStatus, "idle" | "running">;
  final_message: string;
  events: TraceEvent[];
}

export interface CreateRunRequest {
  task: string;
  workspace: string;
  max_steps?: number;
}

export interface CreateRunResponse {
  run_id: string;
  status: RunStatus;
}

export interface RunSnapshot {
  run_id: string;
  status: RunStatus;
  final_message?: string;
  events: TraceEvent[];
}
