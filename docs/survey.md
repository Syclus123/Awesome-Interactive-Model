# Interactive Models for Voice and Omni Agents: A Working Survey

**As of:** 2026-10-06  
**Companion list:** [Awesome Interactive Model](../README.md) · [中文版](survey_zh.md)

This note accompanies the curated list. It is a *working* survey: opinionated about taxonomy, deliberately short on exhaustive paper reviews, and aligned with the position that **categories are compositional roles, not an evolution ladder**.

---

## 1. What counts as an Interactive Model?

We treat **interaction** as the joint control of three quantities:

1. **Content** — what to say or act.
2. **Timing** — when to speak, listen, backchannel, barge in, or stay silent.
3. **Task state** — how an underlying task progresses (tools, memory, physical action).

A system that only streams TTS after a complete user utterance is *streaming*, not necessarily *interactive* in this sense. Conversely, a cascade with a strong turn detector can be highly interactive without being end-to-end.

**Omni** here means audio–vision (and usually text) sharing one interaction timeline. Speech-only systems are included when they innovate on timing or task control.

---

## 2. Timeline of paradigms (compressed)

| Period | What changed | Representative signals |
|--------|--------------|------------------------|
| ≤2023 | Speech LLMs as S2T/S2S generators; duplex mostly engineered | SpeechGPT, AudioPaLM; call-center VAD stacks |
| 2024 | Native duplex audio LMs; first open multi-stream systems | Moshi / Helium, MiniCPM-Duplex, GPT-4o Voice |
| 2025 | Omni + streaming video; think-while-*; agentic voice | Qwen2.5-Omni, VideoLLM-online / MMDuet, MoshiRAG, Step-Audio tool channels |
| 2025–2026 | Dual-system products & open dual stacks; harness language | GPT-Live + Responses, Gemini Live Extended Thinking, Realtime-Venus / Gander, Qwen-Live-Harness |
| 2026 Q3 | Vendor GA / deprecation churn; duplex eval maturation | GPT-Live GA; gpt-realtime deprecate; Nova 2.5 Sonic; Full-Duplex-Bench v2 / τ-Voice |

The point is not that each row *replaces* the previous one. Engineered duplex still ships the majority of production voice agents. Dual-system and harness layers increasingly *sit on top of* either cascades or native duplex front-ends.

---

## 3. Design axes

### 3.1 Who controls timing?

- **Engineered:** VAD, end-of-turn classifiers, FSMs, barge-in policies outside the LM.
- **Learned:** multi-stream codecs, time-division / chunk interleaving, state tokens (`speak` / `listen` / `wait`).

Both can achieve low latency. Learned sync tends to capture backchannels and overlaps more naturally; engineered sync is easier to audit and hot-fix.

### 3.2 How are thinking and speaking scheduled?

| Pattern | Sketch | Typical home |
|---------|--------|--------------|
| Think-then-speak | Finish user turn → reason → reply | Turn-based SLMs / Omni |
| Think-while-listen/speak | Use listen/speak time for causal compute in one timeline | STITCH, SHANKS, CT-SDLM, Mini-Omni-Reasoner |
| Async dual-system | Fast front-end + slow back-end with injection | Brain–cerebellum products & open stacks |

### 3.3 What can the model affect?

Speech-only → tools / RAG / UI actions (**harness**) → physical actuators (**embodied**). Agentic capability is orthogonal to duplex: a half-duplex model can be deeply agentic; a duplex model can refuse tools.

### 3.4 Modality

Speech-only vs Omni. Streaming video adds a *proactive when-to-speak* problem that speech duplex does not fully cover.

---

## 4. Paradigm comparison (not a ranking)

### 4.1 Turn-based speech & Omni LLMs

**Strengths:** mature training recipes, strong content quality, easy eval via S2T proxies.  
**Limits:** timing and barge-in are bolted on; “streaming TTS” is often mistaken for duplex.

### 4.2 Full-duplex (engineered vs learned)

Follow FD-SLM / DuplexSurvey taxonomies:

- **Engineered sync** — controller or cascade (Neural-FSM, FlexDuo, FireRedChat, Unmute…).
- **Learned multi-stream** — Moshi-family, dGSLM, PersonaPlex, Voila….
- **Learned TDM / chunk / state tokens** — MiniCPM-Duplex/o, OmniFlatten, SALMONN-omni, BayLing-Duplex….

**Openness note:** many “open duplex” releases are weights-only without the realtime transport stack; mark 🔓 vs 🧩 carefully.

### 4.3 Brain–cerebellum dual systems

Fast front-end keeps the floor; slow back-end reasons / calls tools; results **re-enter** the live conversation.

**Critical distinction:** *Thinker–Talker* (semantic vs acoustic modules inside one model) is **not** dual-system. Dual-system requires concurrency + feedback across two control loops.

Open stacks (Realtime-Venus, Gander, DuplexOmni, SALMONN-duo, KAME, MoshiRAG…) make the interface inspectable. Closed products (GPT-Live, Gemini Live Extended Thinking, Qwen-Audio realtime lines, Grok Voice Think Fast, TML Interaction-Small…) expose only API contracts—document what is public.

### 4.4 Think-while-listening / speaking

Single-timeline causal compute during listen/speak. Complements dual-system: one can think-while *and* escalate to a brain.

### 4.5 Agentic models & harness

A **harness** organizes context, tools, permissions, task state, and result delivery *around* the front-end. Native tool channels (Step-Audio 2, Stream RAG, UITron-Speech…) and external harnesses (qwen-audio-agent, Venus/Gander runtimes, Chat-Supervisor patterns, voice-driven coding CLIs) should be listed separately: one is model capability, the other is systems software.

### 4.6 Streaming Omni & proactive vision

Continuous video forces *whether/when to speak* without a query. Lineage: VideoLLM-online, MMDuet, Dispider, StreamBridge, LiveCC, plus duplex Omni assistants.

### 4.7 Embodied interaction

Full-duplex speech+action (ELLSA, VITA-E, RoboEgo…) and dual-system VLAs that accept mid-task language corrections (Hi Robot, Helix, GR00T N1, RoboOS…). Co-speech gesture / digital humans sit in the boundary zone unless they close the listen–speak–act loop.

---

## 5. Evaluation: measure the layer you claim

| Layer | Ask | Traps |
|-------|-----|-------|
| Timing | Can it barge-in / backchannel with correct latency? | TTS-simulated user audio overstates robustness |
| State | Mid-turn corrections & recovery | Text chat proxies miss acoustic overlap |
| Content | Instruction / knowledge in speech | Half-duplex S2T leaderboards ≠ duplex skill |
| Agents | Tool success under spoken noise & partial turns | Ignoring harness policy hides failures |
| Proactivity | Speak without query at the right moment | Over-talking looks “helpful” but fails UX |
| Omni | Align speech acts with video events | Frame sampling hides continuous-time errors |

Report **input setting** every time: real human · TTS · half-duplex S2T · true full-duplex streaming.

Benchmarks in the list are grouped accordingly (Full-Duplex-Bench family, EchoChain, τ-Voice, ProVoice-Bench, StreamingBench / OVO-Bench, …). Methodology papers (e.g. recent duplex-eval surveys) belong under *Evaluation Methodology*.

---

## 6. Industry landscape (snapshot 2026-10-06)

- **OpenAI:** GPT-Live GA (2026-09-10); prior gpt-realtime / mini on deprecation path. Dual-system flavour via Live + Responses / supervisor patterns.
- **Google:** Gemini Live family with extended thinking options; media streaming APIs.
- **Alibaba / Qwen:** Omni open weights + realtime product lines (Audio 3.1 / Omni realtime variants)—track which are API-only.
- **ByteDance / Seed:** SeedRealtime and related speech agents.
- **Amazon:** Nova 2.5 Sonic GA (2026-10-05).
- **Others:** xAI Grok Voice Think Fast; TML Interaction-Small; numerous regional realtime APIs.

Prices are intentionally omitted. Deprecations are recorded only when vendor docs confirm them.

---

## 7. Open problems

1. **Unified duplex+agent metrics** — timing, state, and tool success under one protocol.
2. **Open dual-system interfaces** — standard message types for inject / cancel / summarize between cerebellum and brain.
3. **Harness safety** — permissions and side effects while audio is still playing.
4. **Data** — real dual-channel, multi-party, barge-in-rich corpora with licenses that allow training.
5. **Omni proactivity** — when *not* to speak in continuous video.
6. **Embodied barge-in** — language corrections that safely preempt motor policies.
7. **Evidence hygiene** — “coming soon”, gated weights, and demo-only duplex should not be labelled 🔓.

---

## 8. How to use the Awesome list

- Prefer section placement by **mechanism**, then skim Industry for product dates.
- Read 🔓/🧩/🔒/📄 before assuming reproducibility.
- For dual-system / harness / closed products, read the one-line mechanism note.
- Rebuild after YAML edits: `python3 scripts/build_readme.py`.

Contributions: [CONTRIBUTING.md](../CONTRIBUTING.md).
