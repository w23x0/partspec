# 项目宪法

本文件对每个新会话生效。把它当流程读，把红线当禁令读。

# 项目目标

`kicad-partspec` 为模型或人工提供可追溯的电路设计基础工具：数据表证据整理 → 带页码与引文的 PartSpec →
KiCad 符号与封装 → 明确约束的参考电路检查。优先解决漏看图纸、型号/封装绑定错误、调用过碎、交接不清和接线错误。

进度以可用能力和具体问题的解决为准。`./scripts/audit.sh` 衡量已有抽取规则与 gold 的一致性，不是产品进度的唯一指标。
不把新模型发布当作必须跑真实实验的理由；模型选择与跑分不是本项目默认工作。

# Spec 与测试在哪

| 层 | 位置 | 说明 |
|---|---|---|
| Spec（权威散文） | `skills/partspec/reference.md` | 抽取规则的唯一正文。**不要另建第二处 spec**；登记表只是索引 |
| 规则登记表 | `spec/rules.json` | 每条规则的 `id`、`level`（MUST/SHOULD）、声明、正文位置；审计据此算"规则总数/未覆盖" |
| 规则测试 | `tests/test_rules.py` | 每个测试函数以 `test_<RULE-ID>_<slug>` 命名，审计按节点名归属规则 |
| 语料（被判题标准） | `evals/cases/*/spec.gold.json` | 历史金标准，`review.md` 记录每案裁决；数量以目录为准 |
| 措辞守卫 | `tests/test_skill_*.py` | 钉住 reference.md 的关键定义与历史裁决文字，防无人值守改写漂移；有检查器的规则不重复钉。**不是**规则测试，审计不计数 |
| 检查器单测 | `tests/test_spec_checks.py` 等 | 检查器属性（一次性报错、消息可操作、CLI 退出码） |
| 工作流接口 | `skills/partspec/workflows.md` | 证据包、批量任务、电路约束的输入输出约定；不重定义抽取规则 |
| 项目交付接口 | `skills/partspec/project.md` | 一份清单串联元件与电路，汇总证据、待办、BOM、库索引和前后差异 |

rule-id 格式 `<模块>-<三位数字>`，模块：`MPN` `PIN` `STAT` `SCH`（spec 结构） `SRC`（引文校验） `DIM` `LAND` `GEN`（生成/加载）。

# 默认工作流程

1. 依据用户的实际痛点确定本次交付，读受影响的实现和接口约定；涉及抽取语义时再读对应规则和测试。
2. 完成可直接使用的实现、CLI/MCP 入口、示例和必要说明，避免只增加调研或路线图。
   同一项完整改造连续推进；阶段完成只作进度更新，不把每个新增工具当成一次最终交付让用户反复催促。
3. 只运行与改动直接相关、数量适当的局部检查。用户明确限制验证范围时遵从；未执行的检查写明 `not_run`，不能宣称通过。
4. 全量审计、真实 PDF/gold 验证、KiCad 加载、端到端测试、模型评估和无人值守循环，由用户明确要求或任务范围明确包含时运行。
5. 报告实际交付、实际做过的检查和仍需复核的边界。需求完成即停止，不为了刷新板面继续跑循环。
6. 发现抽取 Spec 矛盾或歧义 → 写入 `spec/ISSUES.md`；没有明确授权时不要自行裁决。

若用户要求规则修复/全量审计，再按板面的未通过、退步、未覆盖逐项修复，并确认相关套件不退步。规则类提交使用
`[RULE-ID] 简述`；工作流功能提交使用对应功能名称，不虚构 rule-id。

# 红线（违反任何一条等于任务失败）

- 禁止为了让测试通过而修改、弱化、跳过 `tests/test_rules.py` 中已有的断言——它就是本仓库的 conformance 测试。
- 禁止针对测试输入硬编码、特判、按 case 名或文件名分支。
- 禁止吞掉错误、降低断言强度、把失败降级成警告。
- 禁止删除或跳过测试；唯一例外是措辞守卫（`tests/test_skill_*.py`）可按人类确认增删。`skipif` 仅限环境缺失（无 `pdftotext`、无 `kicad-cli`、无 `PARTSPEC_DATASHEETS`）。
- 实现必须对"同类但不同的输入"也成立。**把散文断言（`assert "..." in REFERENCE`）当行为验证是作弊**——措辞守卫钉文字，规则测试钉行为，两者不可互相顶替。
- 改已有抽取 conformance 断言、规则等级或 Spec 正文，需在 `spec/ISSUES.md` 记录依据并获得人类授权；
  已有明确授权无需重复询问。新增工具的测试和接口清单应随功能正常维护，不能借此弱化已有抽取约束。
- 页面预览/OCR 不等于原 PDF 文本引文；引文匹配不等于几何或型号绑定正确；连通性/参数检查不等于电路功能或制造通过。
- 批量任务失败必须可见；新证据包和批量输出保留先前产物，不能用覆盖或删除历史结果掩盖失败。

# Gold 修改仲裁协议（本仓库特有）

`evals/cases/*/spec.gold.json` 是被判题标准，历史上确实纠正过多次（round 4/5 合计 9 处，MPN-001 又 13 处）。
允许修改，但必须满足两条，缺一即作弊：

1. **重跑**：改完后重跑受影响 round 的 `python evals/score.py --extracted …`，确认已有运行不被单方面洗分。这条没有例外。
2. **可追溯**：改了什么、依据哪一页哪句话，写进 `[GOLD]` 提交 message 或该 case 的 `review.md`（引文必须过 `check_quotes`），二选一即可。

# 按需审计的分层

- **确定性层**：规则测试（`tests/test_rules.py`）、`gold-spec`（`verify_spec`）、`gold-build`（生成 + `kicad-cli` 加载）。
  这三层决定退出码。
- **评估层**：`gold-quotes`（引文按页校验，需要数据表 PDF：`./scripts/audit.sh --datasheets DIR` 或
  `PARTSPEC_DATASHEETS`；PDF 不在仓库里，缺失时该层打印 `skipped` 且不影响退出码）；`python evals/score.py`（对模型抽取打分，
  非确定性，只在评估轮次跑）。
- 在明确启用的评估任务中，使用"确定性层不退步 + 评估层分数不降"双闸；它不替代其他功能的验收。

# 架构约定

- `src/` layout，hatchling 打包；`scripts/` 只放审计与驱动，**不 import `src`**。
- 模块边界：`spec/`（模型+加载） → `sexpr/`（读写） → `gen/`（符号/封装生成） → `verify/`（spec/引文/符号/封装/kicad-cli 五层检查）
  → `api.py`（CLI 与 MCP 共用的操作） → `cli.py` / `mcp_server.py`。检查只追加 `Finding`，不抛异常。
- `documents.py` 整理/渲染证据；`review.py` 生成复核清单；`workflow.py` 编排批量任务；`circuit.py` 检查显式网表约束。
  `decisions.py` 将复核记录绑定到内容版本；`netlist.py` 导入已有 KiCad XML 网表，保持物理引脚和装配状态。
  `project.py` 统一编排与发布；`project_reports.py` 负责汇总、BOM、库索引和差异。运行范围必须显式，停用检查不算修复失败。
  文件/工具操作的预期异常由 API 转为 findings；电路检查不自动调用外部程序。
- 测试分层见上表；新抽取规则先进 `spec/rules.json` 和 `tests/test_rules.py`，再动实现。普通接口功能不虚增抽取规则。
- 生成的符号面向 KiCad 9 文件格式；可选 KiCad 加载工具缺失时警告并报告未执行。
  明确要求 PDF 渲染而缺少渲染依赖时报告失败，可选择 `prepare --preview-limit 0` 只整理文本。

# 独立审计

仅在用户明确启用独立审计或无人值守审计循环时，按 `AUDIT_EVERY` 轮（默认 5）把
`scripts/prompts/independent_audit.md` 原样交给**另一个**模型实例跑（只读，不改代码），
报告落 `.audit/reports/`。它找四类问题：Spec 矛盾/歧义、测试没覆盖的边界（给具体输入）、疑似针对测试的硬编码（给文件和行号）、
实现与 Spec 不一致。每条标注严重程度和 rule-id。

# 显式启用无人值守规则修复循环

以下是按需使用的维护工具，不是每次开发会话的启动流程：

```bash
AGENT_CMD="claude -p" MAX_ROUNDS=20 STALL_LIMIT=3 ./scripts/loop.sh
```

每轮独立分支（`audit/round-N`）、跑一轮工作循环、跑审计、按板面摘要提交，`未通过: []` 且无退步即停。
`AGENT_CMD` 换成任何无头 agent 命令；循环本身不理解 agent，只理解审计板面。
