# Contributing / 贡献指南

Thanks for helping improve **Awesome Interactive Model**!  
感谢帮助完善本列表！

This file is bilingual. English first, 中文在后。

---

## English

### What to add

We welcome:

- New **interactive** speech / Omni models (especially full-duplex, dual-system, think-while-*, harness / agentic, streaming omni, embodied).
- Benchmarks and datasets tagged by **interaction layer**.
- Industry API updates with **dates** and verified **deprecations**.
- Fixes to wrong arXiv IDs, dead links, or openness status.

Out of scope (unless clearly boundary-marked): generic ASR/TTS catalogs, non-interactive audio tagging, price lists.

### Entry format

Edit YAML under `data/entries/` (do **not** hand-edit generated `README.md` / `README_zh.md`).

```yaml
- id: unique-kebab-id
  name: ShortName
  title: Full paper or product title (English)
  date: "2026-09"          # YYYY-MM preferred
  venue: "ICLR'26"         # optional
  org: "Org"               # optional
  status: open_weights     # open_weights | code_only | closed | paper_only
  star: false              # true only for highly representative items
  links:
    arxiv: https://arxiv.org/abs/xxxx.xxxxx
    web: https://...
    code: https://github.com/...
    hf: https://huggingface.co/...
    blog: https://...
    docs: https://...
    data: https://...
  sections: [duplex-multistream]   # see data/sections.yaml ids
  note_en: "One-line mechanism note when useful."
  note_zh: "有用时写一行机制说明。"
```

**Rules**

1. Prefer **mechanism** sections; add Industry sections only for vendor products.
2. Status must match evidence: demos / “coming soon” → `paper_only` or `closed`, not `open_weights`.
3. Same logical project = one `id`; list multiple `sections` instead of duplicating.
4. `name`, `title`, `venue`, and `note_en` must be in English (the build fails on Chinese characters in these fields); put Chinese notes in `note_zh`.
5. No prices.

### Rebuild & checks

```bash
python3 scripts/dedupe_entries.py   # if you merged names
python3 scripts/build_readme.py
python3 scripts/verify_arxiv.py
python3 scripts/check_links.py
# optional HTTP probe:
python3 scripts/check_links.py --http --limit 80
```

### PR checklist

- [ ] Valid YAML; `build_readme.py --check-only` passes
- [ ] Correct `sections` ids from `data/sections.yaml`
- [ ] Links resolve; arXiv ID matches the paper
- [ ] Status icon justified in PR description if non-obvious
- [ ] No commit secrets / personal data

---

## 中文

### 欢迎补充的内容

- 新的**交互式**语音 / Omni 模型（尤其全双工、大小脑双系统、边听边想、harness / agentic、流式 Omni、具身）。
- 按**交互层**标注的 benchmark 与数据集。
- 带**日期**与已核实**停用**信息的产业 API 更新。
- 错误 arXiv ID、失效链接或开放状态的修正。

一般不收录（除非明确标为边界）：普通 ASR/TTS 目录、非交互音频标签、价格表。

### 条目格式

请改 `data/entries/` 下的 YAML（**不要**手改生成的 `README.md` / `README_zh.md`）。字段见上方英文示例。

**约定**

1. 优先按**机制**归类；仅厂商产品再加 Industry 小节。
2. 状态须有证据：演示 /「即将发布」→ `paper_only` 或 `closed`，不要标 `open_weights`。
3. 同一项目一个 `id`；用多个 `sections` 跨节复用，不要复制条目。
4. `name`、`title`、`venue`、`note_en` 必须是英文（含中文字符时构建会报错）；中文说明写在 `note_zh`。
5. 不写价格。

### 重建与检查

同上英文命令。提交前请确保 `build_readme.py --check-only` 通过。

### PR 检查清单

- [ ] YAML 合法；schema 检查通过
- [ ] `sections` 使用 `data/sections.yaml` 中的 id
- [ ] 链接可访问；arXiv 与论文一致
- [ ] 状态非显然时在 PR 说明依据
- [ ] 无密钥与个人隐私

---

## License

Contributions are accepted under [CC0-1.0](LICENSE). By opening a PR you agree to dedicate your contribution to the public domain under CC0.
