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

## 安装

在你自己的 conda 环境中安装依赖：

```bash
cd backend
python -m pip install -r requirements.txt
```

## 配置

复制 `.env.example` 中的变量到本地环境中，至少需要：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

不要把真实 API key 提交到仓库。

## 运行 CLI

```bash
cd backend
PYTHONPATH=src python -m code_agent.cli --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

如果希望使用 `code-agent` 命令，可以额外安装本地包：

```bash
python -m pip install -e .
code-agent --workspace ../examples/demo_workspace "Create a hello.py file that prints hello, then run it."
```

## 测试

```bash
cd backend
python -m pytest
```
