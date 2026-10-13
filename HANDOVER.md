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

## 当前板面（已验证，两种模式）

```
# 不带数据表（历史默认）
规则总数: 28   有测试: 28   通过: 28   未通过: []   退步: []   未覆盖: []
gold-spec: 23/23   gold-quotes: skipped   gold-build: 23/23 (20 mods, 3 skipped)

# PARTSPEC_DATASHEETS=~/datasheets（2026-10-13 起首次可用，引文层真实点亮）
gold-quotes: 23/23 (vendor-rebuilt, name kept: lm358_soic8)
```

板面 28/28 全绿的含义：每条规则都有测试或金标套件，`未覆盖` 历史首次为空。引文层首次以实数
运行：23/23 全部通过（此前只有 skipped）。

## 数据表（2026-10-13 抓取）

- 位置：`~/datasheets`（仓库外，23 份 PDF，`.gitignore` 不管但刻意不入库）。
- 获取：`scripts/fetch_datasheets.py`（提交历史见 `[audit]` 相关提交），按各 gold 的
  `datasheet.url` 抓取并逐份校验 sha256：直连 22/23，`cp2102n` 走 Wayback 哈希命中，
  `lm358` 为厂商同 revision 重建版（字节不可恢复，引文全过）——回退语义见 ISSUES.md
  “数据表获取状态与厂商重建版回退”一节，三面（audit/check_gold/api.validate）一致有声。
- 重取：`.venv/bin/python scripts/fetch_datasheets.py [--wayback] [--force]`。

## 继续时的三件事（按优先级）

1. **MPN-001 结案（数据表已就位，阻塞解除）**：`~/datasheets` 已在盘上。逐案核对 6 个 gold 的
   mpn 与数据表 addendum 的 orderable（`ads1115_vssop10`、`ina219_soic8`、`tlc555_soic8`、
   `tps54202_sot23`、`txs0108e_tssop20`，加 `ads1015_vssop10` 的兄弟对照）。A（按 MUST 改 gold）
   走 [GOLD] 协议 + 重跑受影响 round 的 `evals/score.py`；B（逃生条款）需逐案确认"未印"并补
   review.md 证据。裁定后同步 tests/test_rules.py 的 MPN-001 硬编码表与 scoring 的 mpn 缺位。
2. **新一轮抽取记分（round 6）**：引文层已实数，`evals/score.py --extracted DIR --datasheets
   ~/datasheets` 可跑真实 quotes 列。用 `scripts/loop.sh` 同款 headless 方式对新模型跑几个 case，
   看规则集是否真的约束出免修可用 spec（round 5 基线：4/10）。
3. **循环的下一形态**：板面对非绿板有效；现在是绿板 + PDF 就位，循环的"未通过"列表为空。
   若要以循环推进上面两件事，把目标写进 `scripts/prompts/round.md` 的选项（round.md 目前只从
   板面缺口选目标）。

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
