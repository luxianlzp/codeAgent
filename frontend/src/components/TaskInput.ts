export interface TaskInputValue {
  task: string;
  workspace: string;
  maxSteps: number;
  apiBaseUrl: string;
}

interface TaskInputOptions {
  initialValue: TaskInputValue;
  onRun: (value: TaskInputValue) => void;
  onDemo: () => void;
}

export function createTaskInput(options: TaskInputOptions): HTMLElement {
  const section = document.createElement("section");
  section.className = "task-panel";
  section.innerHTML = `
    <div class="panel-header">
      <div>
        <h1>Code Agent</h1>
        <p>Local coding agent workspace</p>
      </div>
      <span class="status-pill" data-status="idle">Idle</span>
    </div>
    <label class="field">
      <span>Task</span>
      <textarea id="task-input" rows="7" placeholder="例如：生成一个冒泡排序代码，并运行验证"></textarea>
    </label>
    <label class="field">
      <span>Workspace</span>
      <input id="workspace-input" type="text" />
    </label>
    <div class="field-row">
      <label class="field">
        <span>Max steps</span>
        <input id="max-steps-input" type="number" min="1" max="30" />
      </label>
      <label class="field">
        <span>API base</span>
        <input id="api-base-input" type="text" />
      </label>
    </div>
    <div class="actions">
      <button id="run-button" type="button" class="primary">Run</button>
      <button id="demo-button" type="button">Sample trace</button>
    </div>
  `;

  const taskInput = section.querySelector<HTMLTextAreaElement>("#task-input")!;
  const workspaceInput = section.querySelector<HTMLInputElement>("#workspace-input")!;
  const maxStepsInput = section.querySelector<HTMLInputElement>("#max-steps-input")!;
  const apiBaseInput = section.querySelector<HTMLInputElement>("#api-base-input")!;
  const runButton = section.querySelector<HTMLButtonElement>("#run-button")!;
  const demoButton = section.querySelector<HTMLButtonElement>("#demo-button")!;

  taskInput.value = options.initialValue.task;
  workspaceInput.value = options.initialValue.workspace;
  maxStepsInput.value = String(options.initialValue.maxSteps);
  apiBaseInput.value = options.initialValue.apiBaseUrl;

  runButton.addEventListener("click", () => {
    options.onRun({
      task: taskInput.value.trim(),
      workspace: workspaceInput.value.trim(),
      maxSteps: Number(maxStepsInput.value || options.initialValue.maxSteps),
      apiBaseUrl: apiBaseInput.value.trim(),
    });
  });

  demoButton.addEventListener("click", options.onDemo);

  return section;
}
