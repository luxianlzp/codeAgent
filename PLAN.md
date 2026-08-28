# Coding Agent 项目计划

## 目标

独立设计并实现一个简化版编程智能体（coding agent）。它通过与大语言模型交互，自主完成编程任务，例如读取文件、写入文件、执行命令、根据执行结果继续修正，最终给出完成结果。

项目支持两种入口：

- CLI：优先实现，用来验证 agent 核心能力。
- Windows GUI：后续实现，作为本地桌面客户端，用来更直观地展示对话、工具调用、命令输出和文件变更。

核心要求是：CLI 和 Windows GUI 共用同一套 agent 核心逻辑，GUI 只是交互层，不依赖现成 agent 产品或 agent 框架。

## 总体架构

```text
用户任务
  ↓
CLI / Windows GUI Client
  ↓
Agent Core
  ↓
LLM Client
  ↓
Tool Registry
  ↓
本地文件系统 / 命令执行
```

## 阶段计划

### 第一阶段：CLI 版 agent 跑通

目标：从命令行输入一个编程任务，让 agent 能完成基本的“模型决策 -> 工具执行 -> 结果回传 -> 继续决策”循环。

需要实现：

- 读取用户任务。
- 管理 system prompt、用户消息、模型回复和工具结果。
- 调用 OpenAI 兼容模型 API。
- 支持基础工具：
  - `read_file`：读取工作区文件。
  - `write_file`：写入工作区文件。
  - `list_files`：列出工作区文件。
  - `run_command`：在工作区执行命令。
- 解析模型返回的 action。
- 根据 action 调用对应工具。
- 将工具执行结果加入上下文。
- 支持 `finish` 结束任务。
- 设置最大轮数、命令超时和基础错误处理。

验收标准：

- 能通过 CLI 输入一个真实编程任务。
- agent 能至少完成一次文件读取、文件写入或命令执行。
- agent 能在完成后主动停止。
- 工具错误会反馈给模型，而不是直接崩溃。

### 第二阶段：抽象 agent loop

目标：把第一阶段的逻辑拆成清晰模块，方便 CLI 和 Windows GUI 复用。

需要拆出：

- `Agent`：负责主循环。
- `LLMClient`：负责模型 API 调用。
- `ToolRegistry`：负责工具注册和分发。
- `Workspace`：负责工作目录安全限制。
- `TraceEvent`：记录每一步执行日志。
- `Config`：统一管理模型、API 地址、最大轮数、超时时间等配置。

验收标准：

- CLI 入口只负责解析参数和展示结果。
- agent 核心可以被 Python 代码直接调用。
- 每一步工具调用都有结构化 trace 记录。
- 测试可以绕过真实模型，使用 fake LLM 验证 agent loop。

### 第三阶段：Windows 桌面 GUI

目标：构建一个 Windows 本地桌面 GUI 客户端。GUI 直接复用 Python agent core，不通过 Web 前后端通信，也不把 agent 决策逻辑写进界面层。

推荐布局：

```text
顶部：Code Agent、当前模型、运行状态
左侧：项目侧边栏、workspace 选择、max steps、新对话
右侧顶部：当前对话标题和运行状态
右侧主区域：对话式 agent 事件流
右侧底部：固定任务输入框和发送按钮
消息详情：工具参数、命令输出、文件 diff、错误信息默认隐藏，点击 Details 展开
```

需要实现：

- `code-agent-gui` 启动 Windows 桌面客户端。
- GUI 主线程只负责界面展示和用户交互。
- `AgentWorker` 后台线程运行 `Agent.run(task, on_event=...)`。
- `TraceEvent` 通过 Qt signal 实时发送回主线程。
- 支持选择 workspace 目录。
- 支持输入任务、设置 max steps、点击 Run。
- 以对话流展示工具类型、状态、输出摘要和最终回复。
- 工具参数、stdout、stderr、diff 和错误信息默认隐藏，需要时展开查看。
- 任务结束后展示最终回答。

验收标准：

- Windows GUI 能完成和 CLI 相同的 demo 任务。
- GUI 能实时展示 agent 的执行过程。
- GUI 运行时界面不冻结。
- GUI 代码中不包含 agent 决策逻辑。
- 关闭 GUI 后，CLI 仍然可独立运行。

### 第四阶段：README 和视频准备

目标：准备最终提交材料，突出项目设计和演示效果。

README.txt 需要包含：

- Git 仓库地址。
- API key 配置方式。
- CLI 运行方式。
- Windows GUI 运行方式。
- 核心功能说明。
- 设计亮点说明。
- 安全限制说明。

视频建议结构：

1. 简短展示项目结构和 README。
2. 运行 CLI 或 Windows GUI。
3. 输入一个真实编程任务。
4. 展示 agent 自动读写文件、执行命令、处理错误或完成测试。
5. 简要解释 agent loop、工具系统和安全边界。
6. 强调 GUI 只是交互层，核心 agent 逻辑为自研实现。

## 推荐文件结构

```text
code-agent/
├─ README.txt
├─ PLAN.md
├─ .env.example
├─ .gitignore
│
├─ backend/
│  ├─ pyproject.toml
│  ├─ src/
│  │  └─ code_agent/
│  │     ├─ __init__.py
│  │     ├─ cli.py
│  │     │
│  │     ├─ core/
│  │     │  ├─ __init__.py
│  │     │  ├─ agent.py
│  │     │  ├─ config.py
│  │     │  ├─ events.py
│  │     │  ├─ messages.py
│  │     │  └─ prompts.py
│  │     │
│  │     ├─ llm/
│  │     │  ├─ __init__.py
│  │     │  ├─ base.py
│  │     │  └─ openai_client.py
│  │     │
│  │     ├─ tools/
│  │     │  ├─ __init__.py
│  │     │  ├─ base.py
│  │     │  ├─ registry.py
│  │     │  ├─ filesystem.py
│  │     │  └─ shell.py
│  │     │
│  │     ├─ workspace/
│  │     │  ├─ __init__.py
│  │     │  └─ sandbox.py
│  │     │
│  │     └─ gui/
│  │        ├─ __init__.py
│  │        ├─ app.py
│  │        ├─ main_window.py
│  │        ├─ worker.py
│  │        ├─ styles.py
│  │        └─ widgets/
│  │           ├─ __init__.py
│  │           ├─ task_panel.py
│  │           ├─ chat_panel.py
│  │           ├─ trace_panel.py      # 旧版三栏 trace，可保留为备用
│  │           └─ detail_panel.py     # 旧版详情面板，可保留为备用
│  │
│  └─ tests/
│     ├─ test_agent_loop.py
│     ├─ test_gui_worker.py
│     ├─ test_tool_registry.py
│     └─ test_workspace_sandbox.py
│
└─ examples/
   └─ demo_workspace/
      └─ README.md
```

## 核心模块设计

### `core/agent.py`

负责 agent 主循环：

```text
while step < max_steps:
    1. 组装上下文消息
    2. 调用模型
    3. 解析模型 action
    4. 如果 action 是 finish，则结束
    5. 否则调用本地工具
    6. 记录工具结果
    7. 将工具结果加入上下文
    8. 进入下一轮
```

### `llm/openai_client.py`

只负责模型调用，不包含 agent 决策逻辑。

职责：

- 从环境变量读取 API key。
- 支持 OpenAI 兼容 API base URL。
- 发送 messages 和工具说明。
- 返回模型原始响应或标准化后的 action。

### `tools/registry.py`

负责工具注册和调用。

职责：

- 保存工具名称到工具实现的映射。
- 校验工具名称是否存在。
- 调用工具并捕获异常。
- 返回统一格式的工具结果。

### `tools/filesystem.py`

提供文件系统工具。

工具：

- `read_file`
- `write_file`
- `list_files`

所有路径都必须经过 workspace sandbox 校验。

### `tools/shell.py`

提供命令执行工具。

要求：

- 命令在指定工作区内执行。
- 有超时时间。
- 捕获 stdout、stderr 和 exit code。
- 对危险命令做基础限制或提示。

### `workspace/sandbox.py`

负责工作区安全边界。

要求：

- 所有文件路径必须解析到工作区内部。
- 禁止访问工作区外路径。
- 处理 `..`、绝对路径、符号链接等风险。
- 提供统一的路径解析函数。

### `core/events.py`

定义结构化 trace event。

示例事件：

```text
user_message
model_response
tool_call
tool_result
error
finish
```

这些事件同时服务于 CLI 日志、Windows GUI 展示和视频演示。

### `gui/app.py`

负责创建 Windows GUI 应用入口。

职责：

- 初始化 Qt 应用。
- 加载样式。
- 创建并展示 `MainWindow`。
- 作为 `code-agent-gui` 命令入口。

### `gui/main_window.py`

负责主窗口布局和事件绑定。

职责：

- 构建左侧控制栏和右侧对话主区域。
- 读取用户输入的 task、workspace、max steps。
- 启动和管理 `AgentWorker`。
- 接收 worker 发来的 trace event 并更新 UI。
- 任务完成或出错后恢复按钮状态。

### `gui/worker.py`

负责后台运行 agent。

职责：

- 在独立线程里创建 `Agent`、`LLMClient`、`ToolRegistry` 和 `Workspace`。
- 调用 `Agent.run(task, on_event=...)`。
- 将 `TraceEvent` 通过 Qt signal 发送给主线程。
- 将最终 `AgentRunResult` 或错误通过 signal 返回主线程。

### `gui/widgets/`

负责拆分界面组件。

组件：

```text
task_panel.py    # 任务输入、workspace 选择、运行按钮
chat_panel.py    # 对话式 agent 事件流，详情默认折叠
trace_panel.py   # 旧版 agent trace 时间线，可保留为备用
detail_panel.py  # 旧版详情面板，可保留为备用
```

GUI 组件只处理展示和交互，不直接调用模型 API，不直接执行文件或命令工具。

说明：此前尝试过的 `frontend/` Web 原型暂时作为实验产物保留，不作为当前主线。当前 GUI 主线切换为 Windows 桌面客户端。

## 技术栈建议

- 语言：Python
- CLI：`argparse` 或 `Typer`
- Windows GUI：`PySide6-Essentials` / Qt for Python
- 模型调用：OpenAI 兼容 API
- 测试：`pytest`

## 风险点

- 不要使用 LangChain、LlamaIndex、OpenAI Agents SDK、AutoGen、CrewAI 等 agent 框架。
- 不要调用 Code Interpreter、Files API 等 API 服务端托管执行能力。
- API key 只能通过环境变量或本地未入库配置文件提供。
- README 和视频中不要出现 API key。
- GUI 不能只是包装现成 agent 产品，必须调用本项目自研的 agent core。
- GUI 主线程不能直接运行 agent loop，避免界面冻结。
- 截止时间后不要再向公开仓库推送新提交。

## 推荐优先级

1. 先实现 CLI 最小闭环。
2. 加入 workspace sandbox。
3. 加入 trace event。
4. 写基础测试。
5. 再实现 Windows GUI。
6. 最后整理 README 和视频演示脚本。
