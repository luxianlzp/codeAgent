# Code Agent

一个自研的简化版 coding agent。项目提供命令行和 Windows 桌面客户端两种入口，二者共用同一套 agent 核心逻辑。

## 当前能力

- 管理 agent 对话上下文。
- 调用 OpenAI 兼容模型 API。
- 解析模型返回的 JSON action。
- 执行本地工具：
  - `list_files`
  - `read_file`
  - `write_file`
  - `run_command`
- 将工具结果回传给模型，继续下一轮决策。
- 支持最大轮数和命令超时。
- 限制文件访问在指定 workspace 内。
- 输出结构化 trace，便于 CLI 展示和桌面客户端复用。
- CLI 会边运行边输出事件，不需要等整个任务结束后才看到结果。

## 安装

在你自己的 conda 环境中安装依赖：

```powershell
cd agent
python -m pip install -r requirements.txt
```

如果要使用 `code-agent` 和 `code-agent-gui` 这两个命令，还需要在当前 conda 环境中安装本地包。每次新增或修改命令入口后，都建议重新执行一次：

```powershell
python -m pip install -e . --no-build-isolation
```

## 配置

复制 `.env.example` 为本地 `.env`，然后填入真实配置：

```powershell
Copy-Item ../.env.example .env
```

`.env` 至少需要：

```bash
OPENAI_API_KEY=sk-your-real-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

请把 `OPENAI_API_KEY` 改成真实 key，不能保留 `.env.example` 里的占位值。CLI 和桌面客户端会自动读取项目根目录、`agent` 目录或当前运行目录下的 `.env` 文件。已经存在的系统环境变量优先级更高，不会被 `.env` 覆盖。不要把真实 API key 提交到仓库。

## 运行 CLI

推荐先在当前 conda 环境中安装本地包：

```powershell
cd agent
python -m pip install -e . --no-build-isolation
code-agent --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

如果想连续输入多个任务，使用交互模式：

```powershell
code-agent --interactive --workspace ../examples/demo_workspace
```

进入后直接输入任务即可，输入 `:q` 退出。每个任务会重新启动一次 agent loop，但会复用同一个 workspace。

如果需要查看完整 JSON trace：

```powershell
code-agent --json-trace --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

如果想保存完整运行日志：

```powershell
code-agent --trace-file traces/run.json --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

默认输出会隐藏较长的模型原文和工具细节。如果需要展开 diff、命令输出等完整信息：

```powershell
code-agent --verbose --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

默认的人类可读输出会按事件类型着色。如果终端不支持颜色，或需要录制纯文本输出：

```powershell
code-agent --no-color --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

如果不想安装本地包，也可以临时设置 `PYTHONPATH` 后运行模块：

```powershell
$env:PYTHONPATH="src"
python -m code_agent.cli --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

macOS / Linux shell 对应写法：

```bash
PYTHONPATH=src python -m code_agent.cli --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

## Skills

Skill 是一段可复用的 Markdown 指令，用来给 agent 补充特定场景的工作方式。默认 skill 目录位于当前 workspace 下：

```text
.code-agent/skills/
```

可以创建一个新 skill 模板：

```powershell
code-agent --workspace ../examples/demo_workspace --add-skill python-review
```

生成的文件路径类似：

```text
../examples/demo_workspace/.code-agent/skills/python-review/SKILL.md
```

也可以手动添加 skill。支持两种形式：

```text
.code-agent/skills/python-review/SKILL.md
.code-agent/skills/python-review.md
```

查看当前 workspace 可用的 skill：

```powershell
code-agent --workspace ../examples/demo_workspace --list-skills
```

运行任务时可以显式指定 skill：

```powershell
code-agent --workspace ../examples/demo_workspace --skill python-review "Review calculator.py and run focused tests."
```

也可以在任务文本里用 `@skill-name` 指定。CLI 和桌面客户端都会识别这种写法：

```powershell
code-agent --workspace ../examples/demo_workspace "Use @python-review to review calculator.py."
```

当前 skill 只作为模型指令注入，不会执行任意 Python 代码，也不会绕过 workspace 文件访问限制和工具规则。

## 运行 Windows 桌面客户端

安装依赖并安装本地包后运行：

```powershell
cd agent
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
code-agent-gui
```

如果没有安装本地包，也可以临时通过模块方式启动：

```powershell
$env:PYTHONPATH="src"
python -m code_agent.gui.app
```

桌面客户端使用 PySide6 Qt Quick/QML 构建界面，支持新建项目、选择项目文件夹，并在项目下创建多个对话。输入任务后点击发送按钮，agent 会在后台线程执行，界面不会冻结；主区域以对话流形式实时展示用户任务、模型请求、action、工具调用和最终结果。工具参数、命令输出、文件 diff 或错误详情默认隐藏，点击消息里的“查看详情”才会展开。

输入框左上角的 `+` 按钮会打开 Skill 选择窗口，窗口中会列出当前项目工作目录下 `.code-agent/skills/` 里的所有 skill。勾选后发送任务，本次运行会自动加载这些 skill；仍然可以在任务文本里继续使用 `@skill-name`。

每次 GUI 任务结束后，运行记录会保存到当前 workspace 的 `.code-agent/runs/` 目录。记录包含任务标题、workspace、model、运行状态、最终输出、结构化 trace 和界面展示事件；下次打开同一项目时，左侧对话列表会自动加载最近的历史任务。

## 测试

```powershell
cd agent
python -m pytest
```

## 安全与日志

- `run_command` 会拦截明显危险的命令，例如 `rm`、`del`、`format`、`shutdown`、`git reset`、`git clean`、PowerShell `Remove-Item` 等。
- `write_file` 会在 trace 中记录 unified diff，便于 CLI 和桌面客户端展示文件变更。
- `--trace-file` 会保存完整结构化 JSON，适合调试和录制视频。
- `--verbose` 会显示完整模型响应和工具输出；默认模式只显示摘要。
- `--no-color` 可以关闭彩色输出；`--json-trace` 始终输出纯 JSON。
