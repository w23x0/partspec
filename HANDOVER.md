# 交接（HANDOVER）

状态截至 2026-10-14，分支 `next`。本文件是“继续开始”的入口：新会话先读它，再运行 `./scripts/audit.sh`。

## 刚完成的事（2026-10-14，分支 `next`）

- **MPN-001 结案（读法 A，`4a7058c` [GOLD]）**：全 corpus 机械扫描（token-boundary + 各厂商
  ordering 表解析）发现 23 gold 里 13 个 mpn 是 device name / TI 通配形式而非印刷 orderable
  （超出审计员点名的 6 个：lm358/ne555 共用了“LM358 无后缀即可订购”的伪前提；drv8871、
  uln2003a、ina226、pca9306、24lc256、mcp23008 的 review 原本无 mpn 段）。13 个 fix 全部
  走 [GOLD] 协议（页码 + 逐字行 + 选择理由在各 review.md），5 个保留（Nexperia Type 1、
  Silabs 表内、ST 解码器拼装、rp2040/atmega328p 走 escape 条款）。测试表 3→16 项，
  6 个文件/单元名夹具随 lm358 迁移，`evals/runs/mpn001_goldfix_rescore.md` 记录重跑：
  mpn 零记分影响。**至此 ISSUES.md 里 round 1 的 10 条议题全部 settled。**
- **数据表就位（2026-10-13）**：23 份 PDF 抓取到 `~/datasheets`，`scripts/fetch_datasheets.py`
  可重跑；引文层首次实数运行 `gold-quotes: 23/23`（lm358 为厂商同 revision 重建版，回退语义
  见 ISSUES.md）。此前九轮（SRC-006/DIM-004/SCH-007/LAND-001/PIN-005/DIM-001/PIN-004/
  DIM-003/PIN-001）见 git log fa3e0a5…0ed7907。

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

1. **round 6 真实记分（首次带 quotes 的 round）**：数据表与引文层都就位，
   `evals/score.py --extracted <dir> --datasheets ~/datasheets` 现在评 quotes 列。
   按 round 5 同款方式（headless agent + 空目录 + 单份 PDF + 本仓 plugin）跑几个
   case，回答唯一还悬着的问题：这套规则集是否真的约束出免修可用 spec
   （round 5 基线 4/10，且当时 quotes 未评）。注意新基线：DIM-004 检查器会让记了
   括号值的 run 直接 `spec_failures`。
2. **循环的下一形态**：`scripts/prompts/round.md` 目前只从板面缺口选目标，板面全绿 +
   ISSUES 清空后循环无事可做。要循环推进上面两件事，需把目标写进 round.md 的选项。
3. **自产深度候选题**（都需新设计，不是遗留）：SRC-006 的纯字母引文口子（74hc595
   `lead_length`，收它要改该 gold 引文）、双单位引文换算口径、扩 gold 集到未覆盖的
   封装族（QFP/BGA/DIP 大间距）。

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
