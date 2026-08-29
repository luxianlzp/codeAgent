# Code Agent 项目要求对照与差距分析

> 更新时间：2026-08-29
> 依据文件：`推免考核题目学生版.pdf`

## 一、题目要求摘要

根据题目 PDF 的可辨识内容，项目需要完成一个自研的简化版 coding agent。它应通过模型与用户交互，自主读取和写入文件、执行本地命令，并通过 agent loop 根据工具结果继续决策，直到完成任务或达到停止条件。

主要约束和交付要求如下：

1. 核心逻辑需要自行设计和实现，不能直接套用现成的 agent 产品、agent 框架或 SDK，例如 LangChain、LlamaIndex、OpenAI Agents SDK、Claude Agent SDK、AutoGen、CrewAI 等。
2. 可以使用模型编程 API、API 客户端库、OpenAI 兼容接口或模型原生 tool calling 接口，但不能使用 Code Interpreter、Files API 等托管执行或托管文件能力。
3. 主要逻辑应包含对话历史、工具调用、文件读写、本地命令执行、循环决策和终止机制。
4. 需要保留 Git 提交历史，并提交 Git 仓库地址。
5. 需要提供 README.txt，内容包括仓库地址、运行方式、功能说明、设计说明和安全限制等；PDF 中要求 README 控制在约 1000 字以内。
6. 需要提供不超过 2 分钟、MP4 格式且不超过 200 MB 的演示视频，展示 agent 完成一个真实编程任务的过程。
7. API key 只能通过环境变量或本地未入库配置文件提供，不能出现在仓库、README、视频或最终提交材料中。
8. 最终提交物为包含 README.txt 和视频文件的 ZIP 压缩包，并通过题目指定的表单提交。
9. 需要准备项目说明和答辩，能够解释 agent loop、工具调用、停止条件以及关键设计决策。

PDF 文件本身共 2 页。当前环境的文本提取对中文字体存在编码问题，因此本文件对 PDF 要求采用可辨识内容的归纳表述；涉及最终提交时限、表单地址等信息，应再人工打开原 PDF 核对一次。

## 二、当前项目状态

### 2.1 项目定位和代码结构

项目已经从前后端实验结构收敛为单体 Python 项目，主代码位于 `agent/`。当前没有依赖 Web 前端或额外后端服务。

主要结构：

```text
agent/
├─ src/code_agent/
│  ├─ core/       # Agent loop、配置、消息、事件和结果
│  ├─ llm/        # OpenAI 兼容客户端
│  ├─ tools/      # 工具注册、文件工具、命令工具
│  ├─ workspace/  # workspace 沙箱
│  ├─ skills/     # Skill 发现、加载和引用解析
│  ├─ gui/        # PySide6 桌面 GUI
│  └─ cli.py      # CLI 入口
└─ tests/         # 核心模块和 CLI 测试
```

### 2.2 已完成能力

- CLI 已形成完整的模型决策 -> 工具执行 -> 工具结果回传 -> 继续决策闭环。
- 已实现 `list_files`、`read_file`、`write_file`、`run_command` 和 `finish`。
- 已实现最大步骤数、命令超时、基础错误处理和停止机制。
- 文件访问受到 workspace 沙箱限制，避免任意访问 workspace 外部路径。
- 命令工具会拦截一批明显危险命令。
- 支持 OpenAI 兼容 API、`.env` 配置和环境变量优先级。
- 支持交互模式、JSON trace、trace 文件、verbose 和 no-color 输出。
- 已抽象 `Agent`、`LLMClient`、`ToolRegistry`、`Workspace`、`TraceEvent` 和 `AgentRunResult`。
- 已有 fake LLM 相关测试，可绕过真实模型验证 agent loop。
- 已增加 Skill 机制，并支持 CLI 和 GUI 中显式选择或通过 `@skill-name` 引用。
- Windows GUI 已具备项目、对话、workspace、Max Steps、Model、输入框、后台线程、实时事件流和详情展开功能。
- GUI 当前支持空状态、状态栏、Tool Call/Tool Result 卡片和任务完成后隐藏中间执行过程。
- 根 README、项目状态和计划文档已经基本覆盖安装、配置、CLI、GUI、Skills、安全和测试说明。
- Git 提交历史完整，当前分支为 `main`，并与 `origin/main` 同步。

### 2.3 当前工作区状态

当前工作区存在未提交修改，主要是 GUI 美化和执行过程显示相关调整：

- `agent/src/code_agent/gui/main_window.py`
- `agent/src/code_agent/gui/styles.py`
- `agent/src/code_agent/gui/widgets/chat_panel.py`
- `agent/src/code_agent/gui/widgets/composer.py`
- `agent/src/code_agent/gui/widgets/task_panel.py`

此外，`examples/demo2/index.html` 当前也有一个已有的未提交修改，需要在最终提交前确认是否属于最终演示内容。

## 三、与题目要求的差距

| 要求 | 当前状态 | 差距 / 风险 | 优先级 |
|---|---|---|---|
| 自研 agent loop | 已完成 | 暂未发现使用禁止的 agent 框架；最终答辩需能清楚讲解 | 高 |
| 文件读写和本地命令执行 | 已完成 | 需要用真实演示任务验证完整链路 | 高 |
| workspace 安全边界 | 已完成基础能力 | 需要在演示和 README 中明确说明限制与危险命令拦截 | 高 |
| CLI 独立运行 | 已完成 | 当前环境尚未完成最终依赖安装和实测 | 高 |
| Windows GUI | 基本完成 | 当前机器缺少 PySide6，尚未完成真实窗口启动和分辨率验证 | 高 |
| 工具调用过程展示 | 已完成基础展示 | 需要在真实运行中确认完成后只显示最终输出、错误仍可见 | 中 |
| 测试 | 有测试文件 | 当前 Python 环境没有 pytest，完整测试尚未执行 | 高 |
| README.txt | 当前为 `README.md` | 题目明确要求 README.txt；需要生成最终提交版，并控制长度 | 高 |
| Git 仓库地址 | 尚未确认最终提交文档 | README 中需要填写最终 GitHub/Gitee 地址 | 高 |
| 演示视频 | 尚未制作 | 需要录制真实编程任务，控制在 2 分钟和 200 MB 内 | 高 |
| 最终 ZIP | 尚未制作 | 需要包含 README.txt 和 MP4，并检查不包含 API key、缓存和无关文件 | 高 |
| 答辩准备 | 尚未形成独立材料 | 需要准备 agent loop、工具设计、停止条件和安全边界说明 | 中 |
| 截止时间核对 | PDF 中有明确截止时间 | 由于中文文本提取乱码，最终提交前应人工核对 PDF 的日期和时区 | 高 |

## 四、建议的收尾顺序

### 第一优先级：环境和功能验收

1. 在目标 conda 环境安装 `agent/requirements.txt`。
2. 执行 `python -m pytest`，修复失败测试。
3. 启动 `code-agent-gui`，至少验证 1920x1080 和笔记本尺寸下的布局。
4. 使用 `examples/demo_workspace` 或 `examples/demo2` 完成一次真实任务：读取项目、修改文件、运行命令、处理结果并结束。
5. 确认任务完成后中间执行卡片隐藏，最终输出和错误信息显示正常。

### 第二优先级：提交材料

1. 决定是否保留当前 5 个 GUI 文件的未提交修改，并提交一个清晰的 Git commit。
2. 检查 `examples/demo2/index.html` 的未提交修改，确认是否属于演示成果。
3. 创建符合题目要求的 `README.txt`，补充最终 Git 仓库地址。
4. 检查仓库和 README 中没有真实 API key、`.env` 或敏感日志。
5. 录制不超过 2 分钟的 MP4 演示视频，重点呈现：

   ```text
   用户任务 -> Agent 决策 -> Tool Call -> Tool Result -> 文件/命令结果 -> 完成
   ```

6. 将 README.txt 和视频放入最终 ZIP，检查文件大小、格式和内容后再提交表单。

### 第三优先级：答辩准备

- 能用 1 分钟说明整体架构和 agent loop。
- 能解释为什么 GUI 使用后台线程，以及 GUI 如何复用核心 Agent。
- 能解释 workspace 沙箱、危险命令拦截和 API key 管理。
- 能说明模型只负责决策，实际文件和命令操作由本地工具执行。
- 准备一个工具失败后模型根据错误结果继续修正的例子。

## 五、结论

项目的核心实现已经基本达到题目要求，当前主要差距集中在最终验收和交付材料，而不是 Agent Core 的缺失。最需要优先处理的是：在正确环境中完成 pytest 和 GUI 实测、确认 GUI 未提交修改、生成题目要求的 README.txt、录制演示视频并制作最终 ZIP。

截至本次检查，项目可以视为“功能开发基本完成，处于提交前验收阶段”。
