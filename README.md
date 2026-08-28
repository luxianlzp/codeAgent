# Code Agent

一个自研的简化版 coding agent。当前已经实现 CLI 最小闭环，后续主线是 Windows 桌面 GUI。

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
- 输出结构化 trace，便于 CLI 展示和后续 Windows GUI 复用。
- CLI 会边运行边输出事件，不需要等整个任务结束后才看到结果。

## 安装

在你自己的 conda 环境中安装依赖：

```powershell
cd backend
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

请把 `OPENAI_API_KEY` 改成真实 key，不能保留 `.env.example` 里的占位值。CLI 会自动读取项目根目录、`backend` 目录或当前运行目录下的 `.env` 文件。已经存在的系统环境变量优先级更高，不会被 `.env` 覆盖。不要把真实 API key 提交到仓库。

## 运行 CLI

推荐先在当前 conda 环境中安装本地包：

```powershell
cd backend
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

## 测试

```powershell
cd backend
python -m pytest
```

## 运行 Windows GUI

当前主线 GUI 已切换为 PySide6-Essentials 桌面客户端。安装依赖并安装本地包后运行：

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation
code-agent-gui
```

如果没有安装本地包，也可以临时通过模块方式启动：

```powershell
$env:PYTHONPATH="src"
python -m code_agent.gui.app
```

GUI 可以交互运行：左侧是类似 Codex app 的项目侧边栏和运行设置，右侧顶部显示当前对话标题，底部是固定输入框。输入任务后点击右侧发送按钮，agent 会在后台线程执行，界面不会冻结；主区域以对话流形式实时展示用户任务、模型请求、action、工具调用和最终结果。工具参数、命令输出、文件 diff 或错误详情默认隐藏，点击消息里的 `Details` 才会展开。

## Web 前端说明

`frontend/` 是此前尝试过的 Web GUI 实验原型，当前不是主线运行方式。现在优先维护 `code-agent-gui` 这个 Windows 桌面客户端。

## CLI 安全与日志

- `run_command` 会拦截明显危险的命令，例如 `rm`、`del`、`format`、`shutdown`、`git reset`、`git clean`、PowerShell `Remove-Item` 等。
- `write_file` 会在 trace 中记录 unified diff，便于 CLI 展示和后续 GUI 展示文件变更。
- `--trace-file` 会保存完整结构化 JSON，适合调试、录制视频和后续前端复用。
- `--verbose` 会显示完整模型响应和工具输出；默认模式只显示摘要。
- `--no-color` 可以关闭彩色输出；`--json-trace` 始终输出纯 JSON。
