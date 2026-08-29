# Code Agent 当前项目状态

## 项目定位

项目是一个自研简化版 coding agent，不再保留前端/后端拆分叙事。当前主代码目录已从 `backend/` 改为：

```text
agent/
```

`frontend/` Web 实验代码已经删除。

## 当前目录

```text
D:\code\se\CodeAgent\codeAgent
├─ agent/
│  ├─ pyproject.toml
│  ├─ requirements.txt
│  ├─ README.md
│  ├─ src/code_agent/
│  └─ tests/
├─ examples/
├─ README.md
├─ PLAN.md
├─ PROJECT_STATUS.md
├─ .env.example
├─ .gitignore
└─ 推免考核题目学生版.pdf
```

## 已完成能力

CLI 最小闭环已经完成：

- 读取用户任务。
- 调 OpenAI 兼容接口。
- 模型输出 JSON action。
- 执行工具：
  - `list_files`
  - `read_file`
  - `write_file`
  - `run_command`
  - `finish`
- 工具结果回传给模型继续决策。
- workspace 沙箱限制文件访问。
- 支持 `.env` 自动读取。
- 支持交互模式 `--interactive/-i`。
- 支持 `--json-trace`、`--trace-file`、`--verbose`、`--no-color`。

## 桌面 GUI 当前状态

当前 GUI 位于：

```text
agent/src/code_agent/gui/
```

入口：

```powershell
cd agent
code-agent-gui
```

或：

```powershell
cd agent
$env:PYTHONPATH="src"
python -m code_agent.gui.app
```

当前 GUI 已有：

- PySide6-Essentials 桌面客户端。
- 左侧项目列表。
- 项目创建时选择项目文件夹。
- 项目下创建对话。
- 右侧对话流。
- 顶部当前对话标题和运行状态。
- 底部输入框。
- 后台 `QThread + AgentWorker` 执行 agent。
- trace event 通过 Qt signal 回主线程展示。
- 工具详情通过 `Details` 折叠。

## 最近 UI 调整

已经做过这些较稳定的 UI 调整：

- 初始窗口从 `1360x840` 调小到 `1120x720`。
- 设置最小窗口 `900x600`。
- 底部输入框缩小。
- 项目文件夹设置后不再提供修改按钮。
- README/PLAN 中删除 Web 前端、前后端残留表述。
- `.gitignore` 加入 `logs/`。

## 不稳定点

有两个 GUI 方向尝试过，但因为引发或伴随闪退，建议暂时不要继续沿用：

1. 任务结束后自动隐藏上方模型执行过程。
2. 为减少闪烁而改 `Details` 懒加载、`QTimer.singleShot` 延迟滚动等。

你已经回退到上次修改，因此下一步建议从稳定 GUI 基线继续，不要先碰这些刷新/隐藏优化。

## 已知问题

GUI 在 agent 输出过程中，新增步骤时会偶尔出现“小窗口闪一下”。

初步判断原因是：

- 每个消息卡片都会提前创建隐藏的 `QPlainTextEdit` 作为 `Details`。
- Qt 在 Windows 上新增 widget、布局重算、隐藏控件时可能短暂绘制。
- 流式/逐步输出会放大这个刷新现象。

但之前直接优化这块导致闪退，因此建议后续用更保守方案：

- 不再频繁创建复杂 `QWidget` 卡片。
- 改成单个 `QTextBrowser` 或 `QPlainTextEdit` 渲染事件流。
- 或者只在任务结束后统一渲染最终结果，过程放到独立日志面板。

## 文档状态

根 README 已经改成中性项目说明，运行路径使用：

```powershell
cd agent
```

不再出现 `frontend/`、Web 前端说明、前后端通信说明。

唯一可能搜到的 `build-backend` 是 `pyproject.toml` 的 Python 打包标准字段，不是项目结构残留，不建议修改。

## 测试状态

当前 Codex shell 不一定是你的 `codeAgent` conda 环境，因此完整测试需要在本地 conda 环境执行：

```powershell
cd D:\code\se\CodeAgent\codeAgent\agent
conda activate codeAgent
python -m pytest
```

此前语法检查结果：

```text
agent/src/code_agent
agent/tests
共 37 个 Python 文件可正常解析
```

