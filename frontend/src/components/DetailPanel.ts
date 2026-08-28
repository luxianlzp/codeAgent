import type { TraceEvent } from "../types/agent";

export class DetailPanel {
  private readonly root: HTMLElement;

  constructor() {
    this.root = document.createElement("section");
    this.root.className = "detail-panel";
    this.render(null);
  }

  element(): HTMLElement {
    return this.root;
  }

  render(event: TraceEvent | null): void {
    if (!event) {
      this.root.innerHTML = `
        <div class="panel-header">
          <div>
            <h2>Details</h2>
            <p>Select an event</p>
          </div>
        </div>
        <div class="empty-state">No event selected</div>
      `;
      return;
    }

    const body = renderEventBody(event);
    this.root.innerHTML = `
      <div class="panel-header">
        <div>
          <h2>${escapeHtml(event.kind)}</h2>
          <p>${escapeHtml(event.message)}</p>
        </div>
      </div>
      ${body}
    `;
  }
}

function renderEventBody(event: TraceEvent): string {
  if (event.kind === "tool_result" && isRecord(event.data.data)) {
    const data = event.data.data;
    if (typeof data.diff === "string" && data.diff) {
      return `<pre class="code-block diff">${escapeHtml(data.diff)}</pre>`;
    }
    if (typeof data.stdout === "string" || typeof data.stderr === "string") {
      return `
        <div class="kv">
          <span>Exit code</span>
          <strong>${escapeHtml(String(data.exit_code ?? ""))}</strong>
        </div>
        <pre class="code-block">${escapeHtml(String(data.stdout || data.stderr || "(no output)"))}</pre>
      `;
    }
  }

  if (event.kind === "tool_call" && isRecord(event.data.args)) {
    return `<pre class="code-block">${escapeHtml(JSON.stringify(event.data.args, null, 2))}</pre>`;
  }

  return `<pre class="code-block">${escapeHtml(JSON.stringify(event, null, 2))}</pre>`;
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
