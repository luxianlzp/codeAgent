Git 仓库地址：https://github.com/luxianlzp/codeAgent.git

Code Agent 是一个自研简化版 coding agent，提供 CLI 和 Windows 桌面 GUI。
核心 loop、工具系统、沙箱和 GUI 调度均自行实现。模型只输出 JSON action，本地程序负责解析、执行工具、回传 observation，并循环决策直到 finish 或 max_steps。

运行方式：
cd agent
python -m pip install -r requirements.txt
python -m pip install -e . --no-build-isolation

配置环境变量或本地 .env：
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
真实 API key 不提交到仓库和视频中。

运行 CLI：
code-agent --workspace ../examples/demo_workspace "Create hello.py and run it."

运行 GUI：
code-agent-gui

特色功能：
1. 自研 agent loop：模型请求、JSON action 解析、工具调用、结果回传、继续决策和停止条件形成完整闭环。
2. 本地工具系统：支持 list_files、read_file、write_file、run_command；写文件记录 diff，命令执行捕获 stdout、stderr、exit code。
3. Windows GUI 工作台：支持项目/对话管理、Max Steps、Skills 选择、输入框 Skill 标签、执行过程折叠、工具详情展开、终端风格命令输出。
4. 实时 trace 与历史：记录模型请求、工具调用、工具结果、完成和错误；GUI 任务结束后保存到 .code-agent/runs，可恢复历史对话。
5. CLI/GUI 复用同一 Agent Core，GUI 后台线程运行 agent。
6. Markdown 最终结果：完成消息支持 Markdown 和代码块高亮，便于阅读与演示。
7. 记忆分层：当前 loop 是工作记忆，同一 GUI 对话历史压缩为短期记忆，.code-agent/memory.md 作为长期项目记忆，支持连续任务上下文。
8. 安全限制：文件访问限制在 workspace 内；拦截 rm、del、format、shutdown、git reset、git clean、Remove-Item 等危险命令；Skills 和 memory 不绕过沙箱。

项目结构：
core 负责 Agent loop、配置、事件和记忆；
llm 负责 OpenAI 兼容模型客户端；
tools 负责工具注册、文件工具和命令工具；
workspace 负责路径沙箱；
skills 负责 Skill 发现和加载；
gui 负责 PySide6/QML 桌面端。
tests 存放核心、工具、CLI、GUI 历史和记忆相关测试，
examples 提供演示 workspace。

Agent 结构与设计思想：
整体按“用户任务 -> CLI/GUI -> Agent Core -> LLM Client -> Tool Registry -> 本地文件/命令”的链路拆分。
Agent Core 不直接写界面，GUI 不直接做模型决策；
模型只产生下一步动作，本地工具负责真实执行。
这样可以让 CLI 和 GUI 复用同一核心，也便于展示 trace、限制权限和测试 agent loop。

测试：
cd agent
python -m pytest

