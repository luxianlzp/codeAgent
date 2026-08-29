# Code Agent 项目整体状态

> 更新时间：2026-08-29
> 当前分支：`main`

## 一、总体结论

项目已经完成一个自研简化版 coding agent 的核心闭环，目前处于“功能基本完成、提交前验收和材料整理”阶段。

核心能力已经具备，主要剩余工作集中在：目标环境中的完整测试、Windows GUI 实机验证、最终 README.txt、演示视频、压缩包和答辩准备。

## 二、项目定位

项目是一个不依赖现成 agent 框架的 Python coding agent，提供 CLI 和 Windows 桌面 GUI 两种入口。CLI 与 GUI 共用同一套 Agent Core，GUI 只负责界面展示、用户交互和后台任务调度。

项目不再采用前端/后端拆分结构，主代码目录为 `agent/`，原 Web 前端实验代码已经删除。

## 三、当前代码结构

```text
codeAgent/
├─ agent/
│  ├─ src/code_agent/
│  │  ├─ core/       # Agent loop、配置、消息、事件和运行结果
│  │  ├─ llm/        # OpenAI 兼容模型客户端
│  │  ├─ tools/      # 工具基类、注册表、文件工具、命令工具
│  │  ├─ workspace/  # workspace 路径和沙箱限制
│  │  ├─ skills/     # Skill 发现、加载和引用解析
│  │  ├─ gui/        # PySide6 Windows 桌面客户端
│  │  └─ cli.py      # CLI 入口
│  ├─ tests/         # Agent、CLI、工具、沙箱、Skills 等测试
│  ├─ pyproject.toml
│  └─ requirements.txt
├─ examples/         # demo_workspace 和 demo2
├─ README.md
├─ PLAN.md
├─ PROJECT_STATUS.md
├─ PROJECT_GAP_ANALYSIS.md
├─ .env.example
└─ 推免考核题目学生版.pdf
```

## 四、已完成能力

### Agent Core

- 用户任务读取和对话上下文管理。
- 模型请求、响应、Action 解析和 agent loop。
- 模型决策 -> 工具调用 -> 工具结果回传 -> 继续决策的完整循环。
- `finish` 主动结束任务，达到最大步骤数时停止。
- 工具异常和模型错误能够回传，不会直接导致主循环无提示崩溃。
- 结构化 `TraceEvent` 支持 `user_message`、`model_request`、`tool_call`、`tool_result`、`finish`、`error` 等事件。

### 工具和安全

- `list_files`：列出 workspace 文件。
- `read_file`：读取 workspace 内文件。
- `write_file`：写入 workspace 内文件并记录 diff。
- `run_command`：在 workspace 中执行命令，捕获 stdout、stderr 和退出码。
- 所有文件路径经过 workspace 沙箱校验，限制访问 workspace 外部路径。
- 对 `rm`、`del`、`format`、`shutdown`、`git reset`、`git clean`、PowerShell `Remove-Item` 等明显危险命令进行拦截。

### CLI

- 支持单次任务和 `--interactive/-i` 交互模式。
- 支持 `--json-trace`、`--trace-file`、`--verbose`、`--no-color`。
- 支持从项目根目录、`agent` 目录或当前运行目录读取 `.env`。
- 提供 `code-agent` 命令和模块启动方式。

### Skills

- 支持 workspace 下 `.code-agent/skills/` 中的 Skill。
- 支持 `SKILL.md` 和单文件 Skill。
- 支持 CLI 参数指定 Skill，也支持任务中的 `@skill-name` 引用。
- GUI 支持通过 Skill 选择窗口加载 Skill。
- Skill 只作为模型指令注入，不绕过工具和 workspace 安全规则。

### Windows GUI

- 使用 PySide6-Essentials 构建桌面客户端。
- 支持项目创建、项目文件夹选择和项目下多对话管理。
- 左侧显示对话历史、当前项目、Workspace、Max Steps 和 Model。
- 主区域展示用户任务、Agent 回复、Action、Tool Call、Tool Result 和最终输出。
- Tool Call/Tool Result 使用独立卡片，并显示 Running、Success 或 Error 状态。
- 支持无对话空状态和示例任务。
- 支持底部多行任务输入框、发送按钮和 Skill 选择。
- 通过 `QThread + AgentWorker` 在后台运行 Agent，避免阻塞 GUI 主线程。
- Trace event 通过 Qt signal 回传主线程实时展示。
- 任务完成后隐藏中间执行过程，只保留最终输出；错误事件仍然显示。
- 底部状态栏显示 Connected、Running、Finished、Model 和当前 Step 等状态。
- GUI 仅调用 Agent Core，不包含模型决策、文件操作或命令执行逻辑。

## 五、文档和 Git 状态

- 根目录 `README.md` 已覆盖安装、配置、CLI、GUI、Skills、安全限制和测试方式。
- `PLAN.md` 记录了项目目标、架构、阶段计划、验收标准和风险点。
- `PROJECT_GAP_ANALYSIS.md` 已根据题目 PDF 对照项目完成度和提交差距。
- Git 提交历史保留，当前分支为 `main`，此前提交已同步到 `origin/main`。
- 当前检查时工作区新增了未跟踪文件 `PROJECT_GAP_ANALYSIS.md`；提交前应确认是否一起提交。

## 六、验证情况

已完成：

- GUI Python 文件语法解析通过，共检查 12 个 GUI Python 文件。
- `git diff --check` 通过。
- 已进行代码结构和 GUI 事件流检查。

尚未完成：

- 当前 Codex shell 没有 `conda`、`pytest` 和 `PySide6`，因此尚未在目标环境执行完整 `pytest`。
- 尚未在真实 Windows Qt 环境启动 GUI 并完成 1920x1080、笔记本分辨率下的视觉检查。
- 尚未用真实 API 完成一次从任务输入到文件修改、命令执行、工具结果回传和最终结束的完整录制验证。

建议在目标环境执行：

```powershell
cd D:\code\se\CodeAgent\codeAgent\agent
conda activate codeAgent
python -m pip install -r requirements.txt
python -m pytest
code-agent-gui
```

## 七、与考核要求的差距

依据 `推免考核题目学生版.pdf`，项目核心实现已经基本符合要求，剩余差距主要是交付和验收：

| 项目 | 当前状态 | 后续工作 |
|---|---|---|
| 自研 Agent Core | 已完成 | 准备答辩说明 |
| 文件读写和命令执行 | 已完成 | 用真实任务完整验证 |
| Agent loop 和停止条件 | 已完成 | 准备演示和答辩材料 |
| Git 提交历史 | 已保留 | 最终提交前确认历史和远端地址 |
| README.txt | 尚未生成 | 从 README.md 整理符合题目要求的 README.txt，并控制篇幅 |
| Git 仓库地址 | 待最终确认 | 写入 README.txt |
| 演示视频 | 尚未制作 | 录制不超过 2 分钟、200 MB 的 MP4 |
| 最终 ZIP | 尚未制作 | 包含 README.txt 和视频，排除 API key、缓存和无关文件 |
| 完整测试 | 待目标环境执行 | 安装依赖后运行 pytest |
| GUI 实机验证 | 待完成 | 检查启动、布局、溢出、遮挡和执行流程 |
| 答辩准备 | 待整理 | 准备架构、工具调用、安全边界和失败恢复说明 |

API key 管理已经按要求采用环境变量或本地 `.env`，但最终提交前仍需再次扫描仓库、README、日志和视频，确保没有泄露真实 key。

## 八、提交前推荐顺序

1. 在目标 conda 环境安装依赖并执行完整测试。
2. 启动 GUI，验证常见分辨率和一次完整 demo 任务。
3. 确认任务完成后中间执行过程隐藏，最终输出、错误和详情行为正确。
4. 检查所有未提交文件，确认 GUI 修改和 `PROJECT_GAP_ANALYSIS.md` 是否应提交。
5. 确认最终 Git 仓库地址。
6. 创建符合题目要求的 `README.txt`。
7. 录制 2 分钟以内的真实任务演示视频。
8. 检查敏感信息、视频格式、视频大小和 ZIP 内容。
9. 准备答辩讲解：

   ```text
   用户任务 -> Agent 决策 -> Tool Call -> Tool Result -> 文件/命令结果 -> 完成
   ```

10. 生成最终 ZIP 并按题目要求提交。

## 九、最终判断

当前项目不是核心功能缺失，而是已经进入交付前收尾阶段。Agent Core、工具系统、沙箱、CLI、Skills 和 GUI 主流程均已实现；最重要的剩余事项是完成目标环境验证，并补齐 README.txt、演示视频、最终 ZIP 和答辩材料。
