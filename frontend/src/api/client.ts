import type { CreateRunRequest, CreateRunResponse, RunSnapshot } from "../types/agent";

export class ApiClient {
  constructor(private readonly baseUrl: string) {}

  async health(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async createRun(request: CreateRunRequest): Promise<CreateRunResponse> {
    const response = await fetch(`${this.baseUrl}/api/runs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Create run failed: HTTP ${response.status}`);
    }
    return response.json();
  }

  async getRun(runId: string): Promise<RunSnapshot> {
    const response = await fetch(`${this.baseUrl}/api/runs/${encodeURIComponent(runId)}`);
    if (!response.ok) {
      throw new Error(`Fetch run failed: HTTP ${response.status}`);
    }
    return response.json();
  }
}
