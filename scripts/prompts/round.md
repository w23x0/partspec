按 AGENTS.md 的工作循环执行（连续推进，直到板面不再变化）：

1. 运行 ./scripts/audit.sh，读取板面的 未通过 / 退步 / 未覆盖 列表。
2. 从中选一条规则，或同一模块下的一批，作为本步目标。
3. 阅读 skills/partspec/reference.md 中该规则的正文，以及 tests/test_rules.py 中对应的测试。
4. 实施最小改动：实现、修 gold（必须遵守 AGENTS.md 的 Gold 修改仲裁协议两条），或澄清规则文字。
   - 禁止硬编码、特判、按 case 名或文件名分支。
   - 禁止修改、弱化或跳过 tests/test_rules.py 的既有断言；要改测试或 Spec，写入 spec/ISSUES.md 并停下来。
   - 禁止删测试、吞错误、把失败降级为警告。
5. 重新运行 ./scripts/audit.sh，确认：目标规则通过；未通过与退步列表不差于本步开始前；
   gold-spec / gold-build 全套通过。
6. 提交本步改动，commit message 以 [RULE-ID] 开头；gold 改动以 [GOLD] 开头并附证据摘要。
7. 回到第 1 步；板面不再变化就停（未通过: [] 且无退步时，下一步是评估层，不是继续磨规则）。
8. 如果 Spec 有矛盾或歧义，写入 spec/ISSUES.md，不要自行决定，直接结束。

板面不退步比多修一条规则更重要。
