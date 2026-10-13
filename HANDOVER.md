# 交接（HANDOVER）

状态截至 2026-10-13，分支 `next`。本文件是“继续开始”的入口：新会话先读它，再运行 `./scripts/audit.sh`。

## 刚完成的事（2026-10-13，分支 `next`，10 个提交 fa3e0a5…0ed7907）

用户明确不再代为裁定，授权主会话自行推动后，round 1 独立审计的 9 条议题全部办完，
仅 MPN-001 因缺数据表 PDF 保持 open（见下）。按提交顺序：

1. **SRC-006**（新 MUST）：`check_quote_value_support`——引文带数字时 `extracted` 维度
   至少有一个 min/nom/max 被引文数字支撑（英寸 ×25.4，容差 2%）；无数字引文=字母行、
   `inferred`=人工标记，均不查。257 条 gold 维度零失败。
2. **DIM-004**（[GOLD] 86234b9 + 规则 55541f1，读法 A）：三个 gold 删除 parentheses-only
   `lead_thickness`，各 review.md 补证据，重跑记录 `evals/runs/dim004_goldfix_rescore.md`；
   `check_reference_dimensions` 让规则首次有机械执行者。
3. **SCH-007**（efc48fd，读法 A）：loader 不再把整数引脚号转字符串，直接 schema 失败；
   已确认 gold 与 runs 无整数引号，历史记分不动。
4. **LAND-001**（fdb478d，读法 A）：正文补"三件套"规则 + 新 `check_land_set` 检查器。
5. **PIN-005**（4fe5f49）：电源名语料测试从 11 个硬写名改为轨道名谓词（词干+前缀+
   A/B 后缀+配对），VBUS/EP/PAD/DAP 刻意不收并注明理由。
6. **DIM-001**（e594970）：登记表补堆叠形态；RANGE_QUOTE 接受混合端点（`0.9 - 1`），
   纯整数端点仍排除（gold 里 `0 -8` 是脚角度，实测 11 处）。
7. **PIN-004**（7889271，读法 A）：孤立电源 group "可选"回归规则本意，测试改为两种读法
   都过；README round-2 段同步纠错。
8. **DIM-003**（467b670，读法 a）：GAGE PLANE 禁区=带标注的值本身，正文补口径与正例；
   读法 (b) 与 spans 表矛盾的理由写进 ISSUES.md。
9. **PIN-001**（0ed7907，读法 B）：exposed pad 用引脚表印刷词（PAD/DAP/EP），gold 不动、
   记分不动。

在此之前，同一轮还完成了宪法/登记/审计板面/循环驱动的落地（abc572c、7bd1def）。

## 当前板面（已验证）

```
规则总数: 28   有测试: 28   通过: 28   未通过: []   退步: []
未覆盖:   []
gold-spec: 23/23   gold-quotes: skipped   gold-build: 23/23 (20 mods, 3 skipped)
```

全量：`639 passed, 27 skipped`，ruff 干净。mypy 在 `tests/` 有 55 个既有报错（stash 基线同样 55，
非本轮引入；`src/` 干净）。

板面 28/28 全绿的含义：每条规则都有测试或金标套件，`未覆盖` 历史首次为空。

## 继续时的三件事（按优先级）

1. **点亮引文层**：PDF 不在仓库。挂上数据表目录后跑
   `./scripts/audit.sh --datasheets DIR`（或设 `PARTSPEC_DATASHEETS`），`gold-quotes` 应从
   `skipped` 变为实数。预期全绿；若某 case 引文失败，按仲裁协议处理，不得改测试绕开。
   PDF 就位后还可收掉 SRC-006 的纯字母引文口子（74hc595 `lead_length`，见 ISSUES.md）。
2. **MPN-001（唯一 open 议题，硬阻塞于 PDF）**：6 个 gold 的 mpn 不是印刷 orderable
   （`ADS1115IDGS`/`INA219AxD`/`TLC555xD`/`TPS54202`/`TXS0108EPW` 一类）。两种读法都需逐案
   核对数据表 addendum：A 按 MUST 改 6 个 gold 的 mpn（走 [GOLD] 协议 + 重跑受影响 round 记分），
   B 确认数据表确实没印该 orderable 后启用逃生条款并补 review 证据。PDF 到位前无法裁定。
3. **无人值守循环**：板面 28/28 全绿、无未覆盖，`AGENT_CMD="claude -p" MAX_ROUNDS=20
   STALL_LIMIT=3 ./scripts/loop.sh` 现在从绿板出发；后续轮次的自然候选（都需新证据或新设计，
   不是 ISSUES 遗留）：新规则候选题（如"双单位引文须给换算"）、每轮一次的独立审计再跑。

## 无人值守启动方式

```bash
AGENT_CMD="claude -p" MAX_ROUNDS=20 STALL_LIMIT=3 ./scripts/loop.sh
```

`AGENT_CMD` 可换任何无头 agent。循环只认板面；每轮提交信息形如 `[audit] round N: 25/27 passing; 未通过: [...]`。
工作树脏时循环拒绝启动（`ALLOW_DIRTY=1` 可强制）。

## 环境事实

- 虚拟环境 `.venv/`（`python` 不在 PATH，用 `.venv/bin/python`）；`kicad-cli` 与 `pdftotext` 均已安装。
- 数据表 PDF 按 `evals/README.md` 的 revision + SHA-256 获取，不放仓库。
- 分支：`next`（当前），另有 `w/r3writeup`、`w/r4fix`、`w/r5fix`、`main`、`legacy`。
