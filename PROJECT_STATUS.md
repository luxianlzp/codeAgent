# Code Agent 项目整体状态

> 更新时间：2026-08-30
> 当前分支：`main`

## 一、总体结论

项目已经完成一个自研简化版 coding agent 的核心闭环，并且完成了 CLI、Skills、Windows 桌面 GUI、GUI 任务历史持久化、最终结果 Markdown 渲染和基础测试覆盖。

当前项目已经从“核心功能实现”进入“最终体验打磨和交付准备”阶段。下一步重点不再是重写 Agent Core，而是继续优化 GUI 细节、清理演示 workspace 产物、整理 README.txt、录制演示视频和准备答辩材料。

## 二、项目定位

Code Agent 是一个不依赖现成 agent 框架的 Python coding agent，提供 CLI 和 Windows 桌面 GUI 两种入口。

CLI 与 GUI 共用同一套 Agent Core。GUI 只负责界面展示、用户交互、任务调度、事件展示和历史记录加载，不直接包含模型决策、工具执行或 workspace 安全逻辑。

当前 GUI 的产品方向已经明确：不是传统 IDE，也不是普通聊天软件，而是一个以 Agent 任务执行为核心的桌面工作台。

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
│  │  ├─ gui/        # PySide6 / QML 桌面客户端
│  │  │  ├─ qml/     # QML 主界面
│  │  │  └─ markdown.py # GUI 最终结果 Markdown / 代码高亮渲染
│  │  └─ cli.py      # CLI 入口
│  ├─ tests/         # Agent、CLI、工具、沙箱、Skills、GUI 历史测试
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

- 支持用户任务读取、对话上下文构造和模型请求。
- 支持模型响应解析、Action 解析和 agent loop。
- 支持模型决策 -> 工具调用 -> 工具结果回传 -> 继续决策的完整循环。
- 支持 `finish` 主动结束任务，达到最大步骤数时停止。
- 工具异常和模型错误会转换为事件回传，不会无提示崩溃。
- 结构化 `TraceEvent` 已支持 `user_message`、`model_request`、`model_delta`、`tool_call`、`tool_result`、`finish`、`error` 等事件。

### 工具和安全

- `list_files`：列出 workspace 文件。
- `read_file`：读取 workspace 内文件。
- `write_file`：写入 workspace 内文件并记录 diff。
- `run_command`：在 workspace 中执行命令，捕获 stdout、stderr 和退出码。
- 所有文件路径经过 workspace 沙箱校验，限制访问 workspace 外部路径。
- 对 `rm`、`del`、`format`、`shutdown`、`git reset`、`git clean`、PowerShell `Remove-Item` 等危险命令进行拦截。

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
- Skill 选择弹窗已经做浅色现代化样式优化，支持清晰标题、说明、数量 badge、hover/selected 状态和应用/取消按钮。
- Skill 只作为模型指令注入，不绕过工具和 workspace 安全规则。

### Windows GUI

- 当前 GUI 入口使用 PySide6 Qt Quick/QML，命令为 `code-agent-gui`。
- 保留原有大致操作逻辑：新建项目、选择项目文件夹、项目下新建对话、选择 Skills、设置 Max Steps、输入任务并运行。
- 左侧 Sidebar 显示 Code Agent 名称、新建项目、项目列表、对话列表、workspace、Skills 和 Max Steps。
- 右侧主区域显示当前任务标题、当前项目、模型、运行状态、用户任务、Agent 输出、工具过程和最终结果。
- 底部 Prompt Composer 支持多行输入，显示当前项目和模型，发送按钮使用简洁箭头。
- Agent 在后台 `QThread + AgentWorker` 中运行，GUI 主线程只负责界面和信号处理。
- 模型流式输出通过 Qt signal 增量更新，并做了节流，避免频繁刷新导致明显卡顿。
- 任务完成后默认折叠中间执行过程，只展示用户任务、最终结果和错误；用户可以点击“显示过程”查看中间 Activity / Tool Call / Tool Result。
- Tool Result 详情默认隐藏，点击“查看详情”后展开；命令结果使用终端风格展示。
- 新建或切换项目后，标题区和输入框中的项目名会同步更新。
- 窗口尺寸已经调得更紧凑：默认约 `1040x700`，最小约 `780x540`。
- 用户输入的 Task 气泡已按内容收缩，避免短提示词占满主区域。
- 最终 `Completed / finish` 结果支持 Markdown 渲染和代码块高亮。
- Tool Call、Tool Result、Terminal 输出仍保持纯文本，避免命令输出被 Markdown 误解析。
- 已处理 Qt Quick Controls native style 自定义警告，当前使用 Basic style。
- 已处理 `Fixedsys` 字体警告来源，QML 终端字体改为更稳的 `Courier New`。

### 任务历史持久化

- GUI 任务完成或失败后，会将运行记录保存到当前 workspace 的 `.code-agent/runs/` 目录。
- 历史记录包含任务标题、workspace、model、max steps、状态、最终输出、选中的 Skills、界面事件和原始 trace。
- 下次打开同一项目时，左侧对话列表会自动加载最近历史任务。
- 同一个对话中连续提问时，会保留之前的问题和结果，不再被后一个任务覆盖。
- 新增 `RunHistoryStore`，并增加 GUI 历史相关测试。
- 新历史记录会保存 `summaryHtml`，因此最终结果中的 Markdown 代码块可以高亮展示。
- 旧历史记录没有 `summaryHtml` 字段，会回退为纯文本显示；当前不修这个兼容显示差异。

### 最终结果 Markdown / 代码高亮

- 新增 `agent/src/code_agent/gui/markdown.py`。
- `qml_bridge.py` 会为 `finish` 事件生成 `summaryHtml`。
- `Main.qml` 会优先渲染 `summaryHtml`，使用 Qt RichText 展示最终结果。
- 支持标题、列表、加粗、行内代码和 fenced code block。
- 代码块支持 `python`、`js/javascript`、`ts/typescript`、`html/xml/qml`、`css` 的轻量语法高亮。
- 新增 `agent/tests/test_gui_markdown.py`，覆盖 Markdown 渲染和 QML 事件 HTML 注入。

## 五、验证情况

已在当前 conda 环境完成完整测试：

```text
31 passed in 0.48s
```

覆盖范围包括：

- Agent loop
- CLI
- GUI 任务历史
- GUI 最终结果 Markdown / 代码高亮
- OpenAI 兼容客户端
- Skills
- Tool Registry
- Workspace sandbox

也已做过 QML 离屏启动检查，确认 QML 能加载，窗口尺寸配置能读取。

仍建议在真实 Windows 桌面环境中继续做人工验收：

```powershell
cd D:\code\se\CodeAgent\codeAgent\agent
conda activate codeAgent
python -m pytest
code-agent-gui
```

重点检查：

- 新建项目和切换项目是否符合预期。
- 连续提问后历史消息是否保留。
- 任务完成后中间过程是否默认折叠。
- “显示过程 / 隐藏过程”和“查看详情”是否好用。
- Skill 选择弹窗视觉是否协调。
- 不同窗口尺寸下是否有文字溢出、遮挡或过大空白。

## 六、当前 Git 工作区状态

当前存在未提交修改，主要分为三类：

### 应考虑提交的项目代码

- `README.md`
- `agent/src/code_agent/gui/qml/Main.qml`
- `agent/src/code_agent/gui/qml_bridge.py`
- `agent/src/code_agent/gui/widgets/skill_dialog.py`
- `agent/src/code_agent/gui/history.py`
- `agent/tests/test_gui_history.py`
- `agent/src/code_agent/gui/markdown.py`
- `agent/tests/test_gui_markdown.py`

这些修改主要对应 QML GUI、美化、历史持久化、最终结果 Markdown / 代码高亮、流式输出稳定性和测试修正。

### 演示 workspace 产物

- `examples/demo2/.code-agent/runs/`
- `examples/demo2/bubble-sort.html`
- `examples/demo2/bubble_sort.cpp`
- `examples/demo2/bubble_sort.exe`
- `examples/demo2/bubble_sort.py`
- `examples/demo2/index.html`
- `examples/demo2/quick_sort.py`
- `examples/demo2/whack-a-mole.html`

这些更像 GUI / Agent 真实运行时生成的 demo 文件。提交前需要决定哪些作为示例保留，哪些应删除或加入忽略规则。

### 需要额外确认

- 如果要展示“任务历史持久化”，可以保留一个干净的 `.code-agent/runs/` 示例；否则最终提交时建议不要把大量运行记录一起提交。
- `.exe` 文件通常不建议提交，除非明确作为演示材料。

## 七、与考核要求的差距

| 项目 | 当前状态 | 后续工作 |
|---|---|---|
| 自研 Agent Core | 已完成 | 准备答辩说明 |
| 文件读写和命令执行 | 已完成 | 继续用真实任务演示 |
| Agent loop 和停止条件 | 已完成 | 准备架构说明 |
| CLI | 已完成 | README.txt 中写清用法 |
| Skills | 已完成 | 演示中可选用一个 Skill 加分 |
| Windows GUI | 已完成并持续美化 | 做真实窗口验收和录屏 |
| 任务历史持久化 | 已完成 | 决定是否展示历史文件 |
| 最终结果 Markdown / 代码高亮 | 已完成 | 在真实 GUI 中人工检查显示效果 |
| 测试 | 当前 31 passed | 提交前再跑一次 |
| Git 提交历史 | 已保留 | 提交前清理工作区并 commit |
| README.txt | 尚未生成 | 从 README.md / 本文件整理 |
| Git 仓库地址 | 待最终确认 | 写入 README.txt |
| 演示视频 | 尚未制作 | 录制不超过 2 分钟、200 MB 的 MP4 |
| 最终 ZIP | 尚未制作 | 包含 README.txt 和视频，排除 API key、缓存和无关文件 |
| 答辩准备 | 待整理 | 准备架构、工具调用、安全边界和失败恢复说明 |

## 八、下一步推荐计划

1. 决定 GUI 当前样式是否冻结，避免继续大改界面导致新问题。
2. 在真实 Windows 窗口中完成一次完整 demo：新建项目 -> 输入任务 -> 查看执行过程 -> 查看最终结果 -> 重启后查看历史。
3. 清理 `examples/demo2` 中不需要提交的 demo 产物，特别是 `.exe` 和临时运行记录。
4. 再次执行 `python -m pytest`，确认仍然全绿。
5. 更新 README.md 中 GUI 和任务历史部分，确保与当前实现一致。
6. 生成符合题目要求的 `README.txt`，控制篇幅并写入 Git 仓库地址。
7. 录制 2 分钟以内演示视频，重点展示：

   ```text
   用户任务 -> Agent Thinking / Activity -> Tool Call -> Tool Result -> Markdown Completed -> 历史记录保留
   ```

8. 全仓库扫描敏感信息，确认没有 API key、日志、缓存或个人隐私路径泄露。
9. 创建最终 ZIP，包含 README.txt 和演示视频，排除无关缓存和大体积临时文件。
10. 准备答辩话术：强调自研 Agent Core、工具协议、workspace 沙箱、GUI 后台线程和历史持久化。

## 九、最终判断

当前项目核心已经比较完整：Agent Core、工具系统、workspace 安全、CLI、Skills、QML GUI、任务历史持久化和最终结果 Markdown / 代码高亮都已实现，并通过现有自动化测试。

后续最有价值的提升点是：稳定 GUI 体验、清理提交内容、补齐交付材料，并把演示视频录得清楚专业。项目现在适合进入下一步计划和最终验收准备。

## 十、新对话交接说明

如果开启新对话，可以直接基于以下事实继续：

- 项目路径：`D:\code\se\CodeAgent\codeAgent`。
- 现在暂时不做“自动测试 -> 修复 -> 再测试”的强制验证功能，该功能已由用户回退。
- GUI 保持浅色主题，不要改成深色，也不要大幅改变原有新建项目、项目列表、对话列表和底部输入框的操作逻辑。
- GUI 当前重点能力是：QML 界面、项目/对话管理、Skills 选择、执行过程折叠、Tool 详情展开、任务历史持久化、最终结果 Markdown / 代码高亮。
- 旧历史记录不会高亮，因为旧记录没有 `summaryHtml`；当前接受这个现状，不需要修。
- 提交前要注意 `examples/demo2/.code-agent/runs/` 里的运行记录属于 demo 产物，是否保留需要单独决定。
- 下一步适合做真实 GUI 人工验收、更新 README.txt、清理提交内容、录制演示视频和准备最终 ZIP。
