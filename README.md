# Code Agent

Code Agent 是一个自研的简化版 coding agent。它可以接收用户的自然语言编程任务，调用大语言模型进行下一步决策，并通过本地工具读取文件、写入文件、执行命令，再把工具结果回传给模型继续推理，直到任务完成或达到停止条件。

项目提供两种入口：

- CLI：适合快速运行、调试和保存完整 trace。
- Windows 桌面 GUI：适合演示 agent 执行过程、查看工具调用、管理项目和对话历史。

CLI 和 GUI 共用同一套 Agent Core。GUI 只负责界面展示、用户交互、后台线程调度和历史加载，不包含模型决策逻辑，也不直接实现文件或命令工具。

## 项目特色

- 自研 agent loop：没有使用 LangChain、LlamaIndex、AutoGen、CrewAI、OpenAI Agents SDK 等现成 agent 框架。
- 本地工具执行：支持列目录、读文件、写文件和执行本地命令，模型只负责产生 action，实际操作由本地工具完成。
- 结构化工具协议：模型必须返回 JSON action，程序解析后调用工具，并把 observation 再交给模型。
- Workspace 沙箱：文件读写限制在用户选择的 workspace 内，避免访问项目外文件。
- 危险命令拦截：对删除、格式化、关机、破坏性 git 命令等进行基础拦截。
- CLI/GUI 双入口：同一个 Agent Core 可以在命令行和桌面客户端中复用。
- 实时 trace：每一步模型请求、action、工具调用、工具结果和最终回答都会生成结构化事件。
- 任务历史持久化：GUI 任务结束后自动保存运行记录，下次打开同一项目可以恢复历史对话。
- Skills：支持 workspace 级可复用指令，适合把测试偏好、代码审查习惯等注入 agent。
- 记忆分层：实现工作记忆、短期记忆和长期项目记忆，支持连续任务上下文。
- Markdown 最终结果：GUI 的完成结果支持 Markdown 渲染和代码块高亮，便于阅读。

## 目录结构

```text
codeAgent/
├─ agent/
│  ├─ src/code_agent/
│  │  ├─ core/       # Agent loop、配置、事件、记忆和运行结果
│  │  ├─ llm/        # OpenAI 兼容模型客户端
│  │  ├─ tools/      # 工具基类、注册表、文件工具、命令工具
│  │  ├─ workspace/  # workspace 路径沙箱
│  │  ├─ skills/     # Skill 发现、加载和引用解析
│  │  └─ gui/        # PySide6 / QML 桌面客户端
│  ├─ tests/         # 自动化测试
│  ├─ pyproject.toml
│  └─ requirements.txt
├─ examples/         # 示例 workspace
├─ README.md
├─ PLAN.md
├─ PROJECT_STATUS.md
└─ .env.example
```

## 核心原理

Agent 的主循环位于 `agent/src/code_agent/core/agent.py`，流程如下：

```text
1. 组装 system prompt、用户任务、skills 和记忆上下文
2. 调用 OpenAI 兼容模型接口
3. 解析模型返回的 JSON action
4. 如果 action 是 finish，则结束任务
5. 如果 action 是工具调用，则执行本地工具
6. 将工具结果作为 observation 加入上下文
7. 进入下一轮，直到完成或达到 max_steps
```

模型输出示例：

```json
{"action":"read_file","args":{"path":"calculator.py"}}
```

程序解析后会在当前 workspace 内读取文件，再把读取结果回传给模型。模型随后可以继续决定写文件、运行测试，或用 `finish` 给出最终结果。

## 安装

推荐在 conda 环境中安装依赖：

```powershell
cd agent
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
```

安装本地包后会提供两个命令：

```text
code-agent
code-agent-gui
```

## 配置

复制 `.env.example` 为本地 `.env`，然后填入真实配置：

```powershell
Copy-Item ../.env.example .env
```

`.env` 至少包含：

```bash
OPENAI_API_KEY=sk-your-real-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

CLI 和 GUI 会自动读取项目根目录、`agent` 目录或当前运行目录下的 `.env` 文件。系统环境变量优先级更高，不会被 `.env` 覆盖。真实 API key 不应提交到仓库，也不应出现在 README、视频或运行日志中。

## 运行 CLI

单次任务：

```powershell
cd agent
code-agent --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

交互模式：

```powershell
code-agent --interactive --workspace ../examples/demo_workspace
```

进入后直接输入任务，输入 `:q`、`:quit`、`exit` 或 `quit` 退出。

保存完整运行 trace：

```powershell
code-agent --trace-file traces/run.json --workspace ../examples/demo_workspace "Fix calculator.py and run tests."
```

查看完整 JSON trace：

```powershell
code-agent --json-trace --workspace ../examples/demo_workspace "List files and summarize the project."
```

展开模型响应、工具参数、diff 和命令输出：

```powershell
code-agent --verbose --workspace ../examples/demo_workspace "Review calculator.py and run focused tests."
```

不安装本地包时，也可以临时设置 `PYTHONPATH`：

```powershell
$env:PYTHONPATH="src"
python -m code_agent.cli --workspace ../examples/demo_workspace "Create hello.py."
```

## 运行 Windows GUI

安装依赖和本地包后：

```powershell
cd agent
code-agent-gui
```

或使用模块方式启动：

```powershell
$env:PYTHONPATH="src"
python -m code_agent.gui.app
```

GUI 支持：

- 新建项目并选择 workspace。
- 在项目下创建多个对话。
- 选择 Skills，并在输入框下方显示当前选中的 Skill。
- 设置最大 agent 步数。
- 实时查看用户任务、模型请求、agent action、工具调用、工具结果和最终回答。
- 任务完成后默认折叠中间过程，只保留用户任务和最终结果。
- 点击“显示过程”复盘完整执行过程。
- 点击“查看详情”展开工具参数、命令输出、文件 diff 或错误详情。
- 使用后台 `QThread + AgentWorker` 运行 agent，避免 GUI 主线程卡顿。
- 保存 GUI 任务历史，并在下次打开同一 workspace 时自动加载。

## Skills

Skill 是 workspace 下的一段可复用 Markdown 指令，用于给 agent 补充某类任务的工作偏好。默认目录：

```text
.code-agent/skills/
```

创建 Skill 模板：

```powershell
code-agent --workspace ../examples/demo_workspace --add-skill python-review
```

支持两种文件形式：

```text
.code-agent/skills/python-review/SKILL.md
.code-agent/skills/python-review.md
```

查看可用 Skills：

```powershell
code-agent --workspace ../examples/demo_workspace --list-skills
```

运行时显式启用：

```powershell
code-agent --workspace ../examples/demo_workspace --skill python-review "Review calculator.py and run tests."
```

也可以在任务文本里引用：

```powershell
code-agent --workspace ../examples/demo_workspace "Use @python-review to review calculator.py."
```

Skill 只作为模型提示词注入，不会执行任意 Python 代码，也不会绕过 workspace 沙箱和工具规则。

## 记忆分层

项目实现了轻量级上下文记忆机制：

- 工作记忆：当前 agent loop 内的用户任务、模型 action 和工具 observation 会保存在本次运行上下文中，支持模型连续决策。
- 短期记忆：GUI 同一对话里的前几轮任务会从 `raw_events` 压缩成摘要，包含任务、最终结果、工具调用和相关文件。用户继续提问时，这段摘要会注入给模型。
- 长期记忆：如果 workspace 下存在 `.code-agent/memory.md`，CLI 和 GUI 会读取其中的项目级约定、常用命令、目录说明或注意事项，并作为长期项目记忆注入。

长期记忆示例：

```markdown
# Project Memory

- Preferred test command: python -m pytest
- Main source directory: agent/src/code_agent
- GUI uses PySide6 and QML
- Do not commit .env files or generated .exe files
```

这样可以支持同一对话中的连续任务，例如用户先让 agent 修复测试，再追问“再加一个 divide 函数”，模型能够获得上一轮任务和相关文件背景，同时避免把完整日志无限追加到上下文中。

## 工具系统

默认工具包括：

- `list_files`：列出 workspace 内文件和目录。
- `read_file`：读取 workspace 内 UTF-8 文本文件。
- `write_file`：写入 workspace 内 UTF-8 文本文件，并生成 unified diff。
- `run_command`：在 workspace 内执行本地 shell 命令，捕获 stdout、stderr 和 exit code。
- `finish`：模型主动结束任务并返回最终说明。

每个工具返回统一的 `ToolResult`，包含成功状态、用户可读消息和结构化数据。Agent 不直接操作文件系统或命令行，而是通过 `ToolRegistry` 分发工具调用。

## 安全限制

- 文件路径必须通过 `Workspace.resolve()` 校验，最终路径必须位于当前 workspace 内。
- `run_command` 的工作目录固定为当前 workspace。
- 命令执行有超时时间，避免任务无限阻塞。
- 阻止明显危险的命令，例如 `rm`、`del`、`erase`、`rmdir`、`format`、`shutdown`、`reboot`、`diskpart`、`git reset`、`git clean`、PowerShell `Remove-Item` 等。
- API key 只通过环境变量或本地未提交的 `.env` 文件提供。
- Skills 和 memory 都只是提示词内容，不拥有绕过工具和沙箱的权限。

## Trace 与历史

Agent 运行时会产生结构化 `TraceEvent`，常见事件包括：

- `user_message`
- `context`
- `skill`
- `model_request`
- `model_delta`
- `model_response`
- `action`
- `tool_call`
- `tool_result`
- `finish`
- `error`

CLI 可以直接打印这些事件，也可以通过 `--json-trace` 或 `--trace-file` 保存完整 JSON。GUI 会把事件转换为对话流卡片，并在任务结束后保存到 workspace 的 `.code-agent/runs/` 目录。

## 测试

运行自动化测试：

```powershell
cd agent
python -m pytest
```

当前测试覆盖：

- Agent loop 和停止条件。
- 模型 action 解析。
- 工具注册和调用。
- 文件读写与 workspace 沙箱。
- 命令执行基础行为。
- CLI 输出和 trace。
- Skills 加载与引用。
- GUI 历史持久化。
- Markdown 最终结果渲染。
- 记忆上下文构造。
