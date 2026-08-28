import { ApiClient } from "./api/client";
import { DetailPanel } from "./components/DetailPanel";
import { createTaskInput, type TaskInputValue } from "./components/TaskInput";
import { TraceTimeline } from "./components/TraceTimeline";
import { sampleTrace } from "./sampleTrace";
import "./styles/main.css";
import type { TraceEvent, RunStatus } from "./types/agent";

const initialValue: TaskInputValue = {
  task: "生成一个冒泡排序代码，并运行验证",
  workspace: "../examples/demo_workspace",
  maxSteps: 8,
  apiBaseUrl: "http://127.0.0.1:8000",
};

let events: TraceEvent[] = [];
let selectedEvent: TraceEvent | null = null;
let status: RunStatus = "idle";

const app = document.querySelector<HTMLDivElement>("#app");
if (!app) {
  throw new Error("Missing #app root");
}

const detailPanel = new DetailPanel();
const timeline = new TraceTimeline((event) => {
  selectedEvent = event;
  detailPanel.render(event);
});

const taskPanel = createTaskInput({
  initialValue,
  onRun: runWithApi,
  onDemo: runSampleTrace,
});

app.className = "app-shell";
app.append(taskPanel, timeline.element(), detailPanel.element());
setStatus("idle");

async function runWithApi(value: TaskInputValue): Promise<void> {
  if (!value.task) {
    pushLocalEvent("error", "Task is empty");
    return;
  }

  events = [];
  selectedEvent = null;
  timeline.clear(selectEvent);
  setStatus("running");

  const client = new ApiClient(value.apiBaseUrl);
  try {
    const healthy = await client.health();
    if (!healthy) {
      throw new Error("Backend is not available");
    }
    const run = await client.createRun({
      task: value.task,
      workspace: value.workspace,
      max_steps: value.maxSteps,
    });
    await pollRun(client, run.run_id);
  } catch (error) {
    setStatus("error");
    pushLocalEvent("error", error instanceof Error ? error.message : String(error));
  }
}

async function pollRun(client: ApiClient, runId: string): Promise<void> {
  let knownCount = 0;
  for (;;) {
    const snapshot = await client.getRun(runId);
    for (const event of snapshot.events.slice(knownCount)) {
      appendEvent(event);
    }
    knownCount = snapshot.events.length;
    setStatus(snapshot.status);
    if (snapshot.status !== "running") {
      return;
    }
    await sleep(600);
  }
}

function runSampleTrace(): void {
  events = [];
  selectedEvent = null;
  timeline.clear(selectEvent);
  setStatus("running");
  const trace = sampleTrace();
  let index = 0;
  const timer = window.setInterval(() => {
    appendEvent(trace[index]);
    index += 1;
    if (index >= trace.length) {
      window.clearInterval(timer);
      setStatus("finished");
    }
  }, 240);
}

function appendEvent(event: TraceEvent): void {
  events = [...events, event];
  timeline.append(event, selectEvent);
}

function pushLocalEvent(kind: string, message: string): void {
  appendEvent({
    kind,
    message,
    data: {},
    timestamp: Date.now() / 1000,
  });
}

function selectEvent(event: TraceEvent | null): void {
  selectedEvent = event;
  detailPanel.render(selectedEvent);
}

function setStatus(nextStatus: RunStatus): void {
  status = nextStatus;
  const pill = taskPanel.querySelector<HTMLElement>(".status-pill");
  if (!pill) return;
  pill.dataset.status = status;
  pill.textContent = statusLabel(status);
}

function statusLabel(value: RunStatus): string {
  const labels: Record<RunStatus, string> = {
    idle: "Idle",
    running: "Running",
    finished: "Finished",
    max_steps: "Max steps",
    error: "Error",
  };
  return labels[value];
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}
