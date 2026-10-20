# 语音与 Omni 交互模型精炼报告

**截至：** 2026-10-19  
**配套列表：** [Awesome Interactive Model（中文）](../README_zh.md) · [English](survey.md)

本文配合 curated 列表阅读。这是一份精炼报告：在分类上有明确立场，不对每篇论文做穷尽评述，并坚持——**类别描述的是组成关系，不是进化阶梯**。

---

## 1. 什么算 Interactive Model？

我们将 **交互** 定义为对三个量的联合控制：

1. **内容** — 说什么 / 做什么。
2. **时机** — 何时说、听、附和、打断或保持沉默。
3. **任务状态** — 底层任务如何推进（工具、记忆、物理动作）。

仅在用户说完后流式 TTS 的系统是 *streaming*，未必是此处意义上的 *interactive*。反之，带强轮次检测的级联可以高度交互，却不是端到端。

此处的 **Omni** 指音视频（通常含文本）共享同一交互时间轴。纯语音系统只要在时机或任务控制上有创新，同样收录。

---

## 2. 范式时间线（压缩）

| 时期 | 变化 | 代表性信号 |
|------|------|------------|
| ≤2023 | 语音大模型多为 S2T/S2S 生成器；双工多为工程化 | SpeechGPT、AudioPaLM；呼叫中心 VAD 栈 |
| 2024 | 原生双工音频 LM；首批开放多流系统 | Moshi / Helium、MiniCPM-Duplex、GPT-4o Voice |
| 2025 | Omni + 流式视频；边听边想；语音 agentic | Qwen2.5-Omni、VideoLLM-online / MMDuet、MoshiRAG、Step-Audio 工具通道 |
| 2025–2026 | 双系统产品与开放双栈；harness 话语普及 | GPT-Live + Responses、Gemini Live Extended Thinking、Realtime-Venus / Gander、Qwen-Live-Harness |
| 2026 Q3 | 厂商 GA / 停用更替；双工评测成熟 | GPT-Live GA；gpt-realtime 停用；Nova 2.5 Sonic；Full-Duplex-Bench v2 / τ-Voice |

重点不是后一行*取代*前一行。工程化双工仍承载多数生产语音 Agent。双系统与 harness 层越来越多地*叠在*级联或原生双工前台之上。

---

## 3. 设计轴

### 3.1 时机由谁控制？

- **Engineered：** VAD、句末分类器、FSM、打断策略在 LM 之外。
- **Learned：** 多流 codec、时分 / 分块交错、状态 token（`speak` / `listen` / `wait`）。

两者都能做到低延迟。Learned 同步更易自然建模附和与重叠；Engineered 同步更易审计与热修。

### 3.2 思考与说话如何调度？

| 模式 | 示意 | 常见归属 |
|------|------|----------|
| 先想后说 | 听完 → 推理 → 回复 | 轮次式 SLM / Omni |
| 边听/边说边想 | 在同一时间轴上利用听/说时段做因果计算 | STITCH、SHANKS、CT-SDLM、Mini-Omni-Reasoner |
| 异步双系统 | 快速前台 + 慢速后台并回流 | 大小脑产品与开放栈 |

### 3.3 模型能影响什么？

仅语音 → 工具 / RAG / UI 动作（**harness**） → 物理执行器（**具身**）。Agentic 能力与双工正交：半双工也可深度 agentic；双工也可不接工具。

### 3.4 模态

纯语音 vs Omni。流式视频额外带来*主动 when-to-speak* 问题，语音双工并不能完全覆盖。

---

## 4. 范式对照（不是排行）

### 4.1 轮次式语音与 Omni 大模型

**优势：** 训练配方成熟，内容质量强，可用 S2T 代理评测。  
**局限：** 时机与打断多为外挂；「流式 TTS」常被误认为双工。

### 4.2 全双工（engineered vs learned）

沿用 FD-SLM / DuplexSurvey 分类：

- **Engineered 同步** — 控制器或级联（Neural-FSM、FlexDuo、FireRedChat、Unmute…）。
- **Learned 多流** — Moshi 系、dGSLM、PersonaPlex、Voila…。
- **Learned 时分 / 分块 / 状态 token** — MiniCPM-Duplex/o、OmniFlatten、SALMONN-omni、BayLing-Duplex…。

**开放度提示：** 许多「开放双工」只有权重、没有实时传输栈；请仔细区分 🔓 与 🧩。

### 4.3 大小脑双系统

快速前台维持发言权；慢速后台推理 / 调工具；结果**重新进入**实时对话。

**关键区分：** *Thinker–Talker*（同一模型内语义 vs 声学模块）**不是**双系统。双系统要求两个控制环的并发与反馈。

开放栈（Realtime-Venus、Gander、DuplexOmni、SALMONN-duo、KAME、MoshiRAG…）使接口可检查。闭源产品（GPT-Live、Gemini Live Extended Thinking、Qwen-Audio 实时线、Grok Voice Think Fast、TML Interaction-Small…）只暴露 API 契约——只记录公开信息。

### 4.4 边听边想 / 边说边想

单时间轴上在听/说期间做因果计算。可与双系统互补：既能边听边想，也能升级到「大脑」。

### 4.5 Agentic 模型与 harness

**Harness** 在前台周围组织上下文、工具、权限、任务状态与结果投递。原生工具通道（Step-Audio 2、Stream RAG、UITron-Speech…）与外部 harness（qwen-audio-agent、Venus/Gander 运行时、Chat-Supervisor 模式、语音驱动编程 CLI）应分开列出：前者是模型能力，后者是系统软件。

### 4.6 流式 Omni 与主动视觉

连续视频迫使模型在无提问时决定是否/何时发言。谱系：VideoLLM-online、MMDuet、Dispider、StreamBridge、LiveCC，以及双工 Omni 助手。

### 4.7 具身交互

全双工语音+动作（ELLSA、VITA-E、RoboEgo…）与可接受任务中语言纠正的双系统 VLA（Hi Robot、Helix、GR00T N1、RoboOS…）。共语手势 / 数字人若不闭合听–说–做环路，放在边界区。

---

## 5. 评测：测你所声称的那一层

| 层 | 该问什么 | 常见陷阱 |
|----|----------|----------|
| 时机 | 能否以正确延迟打断 / 附和？ | TTS 模拟用户音频夸大鲁棒性 |
| 状态 | 轮中纠正与恢复 | 文本聊天代理测不到声学重叠 |
| 内容 | 语音指令 / 知识 | 半双工 S2T 榜 ≠ 双工能力 |
| Agent | 噪声与部分轮次下的工具成功 | 忽略 harness 策略会掩盖失败 |
| 主动性 | 无提问时在正确时刻发言 | 「话多」看似有帮助，实则伤体验 |
| Omni | 语音行为与视频事件对齐 | 抽帧会掩盖连续时间错误 |

每次都要报告 **输入设置**：真人 · TTS · 半双工 S2T · 真正全双工流式。

列表中的 benchmark 按此分组（Full-Duplex-Bench 系列、EchoChain、τ-Voice、ProVoice-Bench、StreamingBench / OVO-Bench…）。评测方法论论文放在 *Evaluation Methodology*。

---

## 6. 产业快照（2026-10-19）

- **OpenAI：** GPT-Live GA（2026-09-10）；GPT-Live-1.1 产品上线（2026-10-15），API 增加原生 Decisions 委派与 prompt-to-voice；原 gpt-realtime / mini 进入停用路径。
- **Google：** Gemini Live 家族与 extended thinking；媒体流式 API（10 月上旬无新 Live 模型，仍为 3.8 Live）。
- **阿里 / 通义：** Omni 开放权重 + 实时产品线（Audio 3.1 / Omni realtime 变体）——需区分哪些仅 API。
- **字节 / Seed：** SeedRealtime 及相关语音 Agent。
- **Amazon：** Nova 2.5 Sonic GA（2026-10-05）；Strands Bidi Agents GA（2026-10-05）。
- **Microsoft：** MAI-Voice-2.1 / Flash 与 MAI-Transcribe-2-Streaming（2026-10-01），面向级联语音智能体。
- **其他：** xAI Grok Voice 3.0（2026-10-14；latest 别名）；Sesame 智能体助手（2026-10-06）；Hume 宣布 EVI/TTS 停服（访问截止 2026-11-13）；TML Interaction-Small；诸多区域实时 API。

故意不写价格。停用信息仅在厂商文档确认后记录。

---

## 7. 开放问题

1. **统一的双工+Agent 指标** — 在同一协议下测时机、状态与工具成功。
2. **开放双系统接口** — 小脑与大脑之间 inject / cancel / summarize 的标准消息类型。
3. **Harness 安全** — 音频仍在播放时的权限与副作用。
4. **数据** — 真实双通道、多方、富打断语料，且许可允许训练。
5. **Omni 主动性** — 连续视频中何时*不该*说话。
6. **具身打断** — 能安全抢占运动策略的语言纠正。
7. **证据卫生** — 「即将发布」、门禁权重、仅 demo 的双工不应标成 🔓。

---

## 8. 如何使用 Awesome 列表

- 先按 **机制** 找章节，再扫产业全景看产品日期。
- 假定可复现前先看 🔓/🧩/🔒/📄。
- 双系统 / harness / 闭源产品请读一行机制说明。
- 改 YAML 后重建：`python3 scripts/build_readme.py`。

贡献指南：[CONTRIBUTING.md](../CONTRIBUTING.md)。
