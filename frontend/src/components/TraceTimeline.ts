import type { TraceEvent } from "../types/agent";

export class TraceTimeline {
  private readonly root: HTMLElement;
  private readonly list: HTMLElement;
  private readonly empty: HTMLElement;
  private events: TraceEvent[] = [];
  private selectedIndex = -1;

  constructor(onSelect: (event: TraceEvent | null) => void) {
    this.root = document.createElement("section");
    this.root.className = "timeline-panel";
    this.root.innerHTML = `
      <div class="panel-header">
        <div>
          <h2>Run Trace</h2>
          <p>Live agent events</p>
        </div>
      </div>
      <div class="empty-state">No events yet</div>
      <ol class="timeline"></ol>
    `;
    this.list = this.root.querySelector<HTMLElement>(".timeline")!;
    this.empty = this.root.querySelector<HTMLElement>(".empty-state")!;
    this.list.addEventListener("click", (event) => {
      const target = (event.target as HTMLElement).closest<HTMLButtonElement>("button[data-index]");
      if (!target) return;
      const index = Number(target.dataset.index);
      this.selectedIndex = index;
      this.render(onSelect);
      onSelect(this.events[index] ?? null);
    });
  }

  element(): HTMLElement {
    return this.root;
  }

  setEvents(events: TraceEvent[], onSelect: (event: TraceEvent | null) => void): void {
    this.events = events;
    if (this.selectedIndex >= this.events.length) {
      this.selectedIndex = this.events.length - 1;
    }
    this.render(onSelect);
  }

  append(event: TraceEvent, onSelect: (event: TraceEvent | null) => void): void {
    this.events.push(event);
    this.selectedIndex = this.events.length - 1;
    this.render(onSelect);
    onSelect(event);
  }

  clear(onSelect: (event: TraceEvent | null) => void): void {
    this.events = [];
    this.selectedIndex = -1;
    this.render(onSelect);
    onSelect(null);
  }

  private render(onSelect: (event: TraceEvent | null) => void): void {
    this.empty.hidden = this.events.length > 0;
    this.list.innerHTML = "";
    for (const [index, event] of this.events.entries()) {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.index = String(index);
      button.className = index === this.selectedIndex ? "timeline-item selected" : "timeline-item";
      button.innerHTML = `
        <span class="event-dot ${event.kind}"></span>
        <span class="event-copy">
          <span class="event-kind">${labelForKind(event.kind)}</span>
          <span class="event-message">${escapeHtml(summaryForEvent(event))}</span>
        </span>
        <span class="event-time">${formatTime(event.timestamp)}</span>
      `;
      item.append(button);
      this.list.append(item);
    }
    if (this.selectedIndex >= 0) {
      onSelect(this.events[this.selectedIndex] ?? null);
    }
  }
}

function labelForKind(kind: string): string {
  const labels: Record<string, string> = {
    user_message: "User",
    model_request: "Model",
    model_response: "Model response",
    action: "Action",
    tool_call: "Tool call",
    tool_result: "Tool result",
    finish: "Finish",
    error: "Error",
  };
  return labels[kind] ?? kind;
}

function summaryForEvent(event: TraceEvent): string {
  if (event.kind === "tool_call") {
    const args = event.data.args;
    if (isRecord(args)) {
      if (event.message === "write_file") {
        const content = String(args.content ?? "");
        return `${event.message} ${String(args.path ?? "")} (${content.split("\n").length} lines)`;
      }
      if (event.message === "run_command") {
        return `${event.message} ${String(args.command ?? "")}`;
      }
      if ("path" in args) {
        return `${event.message} ${String(args.path)}`;
      }
    }
  }
  if (event.kind === "tool_result" && isRecord(event.data.data)) {
    const data = event.data.data;
    if (typeof data.exit_code === "number") {
      return `exit_code=${data.exit_code}`;
    }
    if (typeof data.path === "string") {
      return `${data.path} ${data.changed ? "changed" : "unchanged"}`;
    }
    if (typeof data.count === "number") {
      return `listed ${data.count} entries`;
    }
  }
  return event.message;
}

function formatTime(timestamp: number): string {
  if (!timestamp) return "";
  return new Date(timestamp * 1000).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function escapeHtml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}
