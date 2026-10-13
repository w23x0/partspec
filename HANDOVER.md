# 交接（HANDOVER）

状态截至 2026-10-13，分支 `next`。本文件是“继续开始”的入口：新会话先读它，再运行 `./scripts/audit.sh`。

## 刚完成的事（2026-10-13，分支 `next`）

- **SRC-006 立项并落地**：round 1 独立审计的候选规则"引文必须支撑所记数值"已成 MUST 规则。
  `check_quote_value_support`（`src/kicad_partspec/verify/spec_checks.py`）对每个 `extracted`
  维度要求：引文带数字时，min/nom/max 至少有一个出现在引文中（英寸引文 ×25.4 换算，容差 2%）；
  无数字引文 = 字母行（`HE L Lp v w y`）不查；`inferred` 维度不查。登记 `spec/rules.json`
  SRC-006，正文见 `reference.md` 括号值段之后，测试 `tests/test_rules.py::test_SRC_006_*`。
  257 条 gold 维度零失败。连带修正：`test_SCH_005_a_zero_minimum_is_allowed` 的夹具引文
  （`e 0.95` 不支撑被改写后的 0.0/0.5/1.0，改为 `e 0.0-1.0`，断言未动）。
  残留口子记在 ISSUES.md 该条 settled 注记（纯字母引文仍可谎报，需 PDF 才能收掉）。

此前（2026-10-12，提交 `abc572c` 与 `7bd1def`）落地了宪法/规则登记/审计板面/循环驱动（原文保留）：

- `AGENTS.md`：宪法（工作循环、红线、Gold 修改仲裁协议、审计分层、架构约定）。
- `spec/rules.json`：规则登记表（`MPN/PIN/STAT/SCH/SRC/DIM/LAND/GEN`，MUST/SHOULD），索引
  `skills/partspec/reference.md`。
- `tests/test_rules.py`：用例名即 rule-id；SCH/SRC 是穿过真实检查器的夹具测试，其余是对 23 个 gold
  的语料测试。措辞守卫仍在 `tests/test_skill_*.py`，不计入审计。
- `scripts/audit.sh`（实现 `scripts/audit.py`）：唯一进度指标。板面 = 规则计数 +
  `gold-spec` / `gold-quotes` / `gold-build` 三套件；上一板存 `.audit/last.json`（已 gitignore）。
- `scripts/loop.sh` + `scripts/prompts/`：无人值守循环，每轮独立分支，绿板即停，无进展熔断。
- `spec/ISSUES.md`：Spec 争议登记处。

## 当前板面（已验证）

```
规则总数: 28   有测试: 27   通过: 27   未通过: []   退步: []
未覆盖:   [DIM-004]
gold-spec: 23/23   gold-quotes: skipped   gold-build: 23/23 (20 mods, 3 skipped)
```

全量：`609 passed, 27 skipped`，ruff 干净。mypy 在 `tests/` 有 55 个既有报错（stash 基线同样 55，
非本轮引入；`src/` 干净）。

## 继续时的三件事（按优先级）

1. **点亮引文层**：PDF 不在仓库。挂上数据表目录后跑
   `./scripts/audit.sh --datasheets DIR`（或设 `PARTSPEC_DATASHEETS`），`gold-quotes` 应从
   `skipped` 变为实数。预期全绿；若某 case 引文失败，按仲裁协议处理，不得改测试绕开。
   PDF 就位后还可收掉 SRC-006 的纯字母引文口子（74hc595 `lead_length`，见 ISSUES.md）。
2. **DIM-001 / DIM-004 的毕业判定**（需人类拍板）：DIM-001 已有规则测试
   （印刷区间落 min+max），剩登记表措辞补"两个叠印数字"形态；DIM-004 三个 gold 与
   reference.md 正面冲突，立案在 ISSUES.md，未裁定前刻意不写测试，板面持续 `未覆盖`。
3. **未决的 open 议题**：ISSUES.md 里 MPN-001、PIN-001、PIN-004、SCH-007、DIM-003、LAND-001、
   PIN-005 六条均待人类（多数需要 PDF 或改既有断言，勿自行拍板）。

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
