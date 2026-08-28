import type { TraceEvent } from "./types/agent";

export function sampleTrace(): TraceEvent[] {
  const now = Date.now() / 1000;
  return [
    event("user_message", "生成一个冒泡排序代码", {}, now),
    event("model_request", "Calling model", { step: 1 }, now + 0.3),
    event("action", "list_files", { args: { path: "." } }, now + 0.8),
    event("tool_call", "list_files", { args: { path: "." } }, now + 0.9),
    event("tool_result", "ok: (empty)", { tool: "list_files", ok: true, data: { count: 0, entries: [] } }, now + 1.0),
    event("model_request", "Calling model", { step: 2 }, now + 1.4),
    event(
      "action",
      "write_file",
      { args: { path: "bubble_sort.py", content: "def bubble_sort(items):\n    return sorted(items)\n" } },
      now + 2.1,
    ),
    event(
      "tool_call",
      "write_file",
      { args: { path: "bubble_sort.py", content: "def bubble_sort(items):\n    return sorted(items)\n" } },
      now + 2.2,
    ),
    event(
      "tool_result",
      "ok: Created bubble_sort.py",
      {
        tool: "write_file",
        ok: true,
        data: {
          path: "bubble_sort.py",
          created: true,
          changed: true,
          diff: "--- /dev/null\n+++ b/bubble_sort.py\n@@\n+def bubble_sort(items):\n+    return sorted(items)\n",
        },
      },
      now + 2.4,
    ),
    event("model_request", "Calling model", { step: 3 }, now + 2.8),
    event("action", "run_command", { args: { command: "python bubble_sort.py" } }, now + 3.2),
    event("tool_call", "run_command", { args: { command: "python bubble_sort.py" } }, now + 3.3),
    event(
      "tool_result",
      "ok: exit_code=0\nstdout:\n[1, 2, 3]",
      { tool: "run_command", ok: true, data: { exit_code: 0, stdout: "[1, 2, 3]\n", stderr: "" } },
      now + 3.6,
    ),
    event("finish", "冒泡排序代码已生成并验证通过。", {}, now + 4.0),
  ];
}

function event(kind: string, message: string, data: Record<string, unknown>, timestamp: number): TraceEvent {
  return { kind, message, data, timestamp };
}
