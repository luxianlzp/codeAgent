# Code Agent

一个自研的简化版 coding agent。当前第一阶段先实现 CLI 最小闭环，后续会加入前后端分离 Web GUI。

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
- 输出结构化 trace，便于 CLI 展示和后续 Web GUI 复用。

## 安装

在你自己的 conda 环境中安装依赖：

```powershell
cd backend
python -m pip install -r requirements.txt
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
