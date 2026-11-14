**Claude Fable 5.2 与 AI 电路设计：资料核查及对 kicad-partspec 的启示**

检索日期：2026-11-14。用户提到的“Fiber 5.2”与本次找到的 **Claude Fable 5.2** 高度吻合：Anthropic 于 2026-11-09 发布该模型，并在同日发表电子原型设计实验。以下是资料研究与工程改进依据；本次没有调用 Fable 5.2 执行本仓库的抽取评估。

**方向调整（用户确认）：直接改进项目，不进行 Fable 实验、真实验证或端到端测试，只做少量局部检查。**
下文的公开实验属于资料来源。后续实现聚焦模型无关的证据整理、批量操作、复核交接和显式电路约束，
不把模型比较作为这些能力交付的前置条件。

最值得关注的是几何理解、主动返工和工具编程能力的共同改善。公开资料支持它已能在专用工具环境和少量人工指导下完成工作的电子原型；对任意数据表抽取的准确率、复杂电路设计的泛化能力以及量产可靠性，仍需要分别验证。

官方发布页给出的 API 名称为 `claude-fable-5-2`，常规价格为每百万输入 token 8 美元、输出 token 40 美元；fast mode 为 16/80 美元。[S1]

**已核实的结果及其口径**

| 结果 | 原始材料实际说明 | 可以支持的判断及限制 |
|---|---|---|
| 三款可工作的原型 | USB/Bluetooth 扬声器电话、家庭语音助手 hub、电池供电的虚拟宠物。模型完成规格、原理图、选件、布局布线、外壳、固件和 BOM；官方称每块板不到一天达到送制造状态，实物无需电路修改即工作。[S1][S2] | 有完整原型案例，且横跨电子、机械、软件。但案例由 Anthropic 与商业合作伙伴 Diode 共同完成，不是独立复现。 |
| PCB Gym：69%，Fable 5 为 25% | Diode 内部评估，将既有板子的布局去掉，让模型重新摆放和布线。[S2] | 比通用编程成绩更接近 PCB 任务；公开文章不足以还原样本组成、完整判分和全部运行记录，不能转换成任意新板子的成功率。 |
| BenchCAD 2.1：83.5/100 | Claude Code 工具环境；系统卡说明提供 shell、文件编辑和图像放大工具，**不限制总轮数或总 token 数**；100 个 Core 问题，五次运行的均分。[S3][S4] | 是模型加工具环境、计算预算的整体成绩，含部分得分，不是 83.5% 的设计完全成功。 |
| BenchCAD 2.1：75.4/100 | 系统卡称其为“without tools”，但仍会执行模型写出的代码并回传输出和渲染，最多 60 轮、50 万输出 token；基准网站归入标准 2.1 环境。[S3][S4] | 不是纯文本一次作答。和 83.5 的差异同时涉及工具与预算，不能把全部提升归因于一个因素。 |

BenchCAD 的六类任务中，T1–T5 涉及机械零件和装配，T6 是 **PCB 照片 → 原理图**。其综合分并不是“数据表 → PartSpec”或“自然语言 → 新电路板”的专项指标。[S5] 基准网站明确标注 Fable 数字来源为 Anthropic 系统卡；列在第三方榜单上并不会让这些数字成为第三方独立实测。网站也区分不同 harness、版本和预算，跨口径数字不宜直接排排名。

系统卡的具体证据位于 §8.13.2，PDF 第 232–234 页。其公布的 Opus 5.5 成绩为 49.0/65.3，Fable 5.1 为 36.3/44.4，分别对应协议环境/额外工具环境。[S3]

**开源软件的局限与可借鉴的处理方式**

1. **工具的调用粒度可能先成为瓶颈。** 官方报告中，Diode 暴露的 KiCad router 接口一次在两个点之间画一条线。面对 100 引脚连接器引出的长线，模型判断逐条指导的成本太高，于是约半小时写出网格寻路布线器，每条长线约一秒；发现音频时钟靠近 Ethernet 后又扩大敏感线间距。[S2] 这说明应提供批量操作、可计算的约束和快速反馈。这个案例描述的是特定接口和任务，不能据此认定 KiCad 全面缺少布线能力。

2. **能够生成文件，距离电路正确仍有多层检查。** 开源 Circuitron 的 README 明确记录过封装名幻觉，并建议禁用 footprint search 来避开不稳定路径；项目现已归档。[S10] 这些是该项目作者自己的已知限制，正好说明本仓库从可追溯数据表生成、再独立验证元件库的价值。可参考其故障记录，但不适合直接把旧工作流当可靠基线。

3. **能撤销局部方案，比持续堆补丁更有用。** 早期模型经常把板子做到“95% 完成但不可用”。Fable 5.2 的案例包括交换可互换引脚、重摆角落、反复拆线重布，以及优先处理 USB/Ethernet 差分线、供电和噪声敏感信号。[S2] 对工具层的启示是支持局部重做、设计快照和每次修改后的检查，保留修改前后的可审查结果。

4. **检查器需要表达工程条件。** Anthropic 与 Diode 在 2025 年的合作中，将参考电路要求写成 testbench，例如检查电源与地之间的电容总量至少为 22 µF，而不是限定只能出现某一个特定电容。[S6] 当前 Zener 的公开测试接口支持连通性、元件属性和拓扑路径检查，失败能带出源位置。[S7] 这适合将来的参考电路层；PartSpec 中抄录的引脚、尺寸和引文仍应遵守本项目现有的精确规则。

5. **几何 DRC 通过后仍存在工程判断。** 官方案例中，MEMS 麦克风下的走线即使满足 clearance，模型仍主动重布；它还检查外壳装配碰撞、天线禁布区域、信号回流路径，以及麦克风声孔长度带来的共振。[S2] 确定性检查覆盖哪些性质，需要逐项说清，不能把文件加载成功或几何 DRC 通过等同于完整产品验证。

6. **制造反馈可以推动修正，但不能随意消除报错。** 官方记录了修复六处过窄阻焊桥，以及把一个被模型认为是有意连接的地网报错排除。[S2] 后者在本仓库中不能照搬成“模型认为没问题就跳过检查”：应保存证据、找出规则或检查器的原因，并遵守 `AGENTS.md` 的裁决与修改流程。

**现在能实际复用的开源材料**

| 材料 | 可参考或复用的内容 | 对本仓库的适用边界 |
|---|---|---|
| Diode `pcb` / Zener | 基于 Starlark 的原理图 DSL、模块与依赖管理、生成 KiCad 布局、testbench 和电路图查询。[S7] | 可作为 PartSpec 元件产物的下游电路设计层。当前 README 要求布局使用 KiCad 10.x，本仓库目标是 KiCad 9 文件格式，接入时需要版本适配和实测。 |
| Diode 的 FreeRouting 集成 | 公开源码有本地 `KiCad → DSN → FreeRouting → SES → KiCad` 流程，固定 FreeRouting 2.3.0，启动本地 API server。[S8] | 是已存在的自动布线适配实现。不能把它等同于官方案例中模型临时写出的网格布线器；本次材料未确认后者以可直接复用的独立组件发布。 |
| BenchCAD 2.1 | 几何和电路图的确定性评分、版本化实验环境、重复运行、成本与 token 记录。[S5] | 适合参考评估设计；它不是 PartSpec conformance 测试的替代品。Core 数据需要申请访问，README 另提供 Public 集和少量示例。 |
| KiCad 官方 API 文档 | 官方为新插件推荐 IPC API，旧 PCB Python bindings 被标为 legacy。[S9] | 若扩展板级操作，应先确认所需操作在目标 KiCad 版本可用。现有文件生成与 CLI 验证仍有独立用途。 |

核对 Diode 源码时使用的提交为 `a9d007f0eada7d3e5cd5ac6349d0d1b13dc4e79a`。README 对 Diode 自有代码与文档声明 MIT，另有第三方许可说明；复用依赖时仍要分别核对。

**第三方资料怎么读**

- **Artificial Analysis：独立通用模型评测。** 截至本次检索，Fable 5.2 Max 的 Intelligence Index 为 65，平均每个该指数任务成本 26.54 美元。[S11] 这能说明强推理模式的成本量级，但该指数不是 PCB 专项评估，26.54 美元也不是做一块电路板的报价。
- **R&D World，2026-11-09：有价值的二次分析。** 文章区分官方硬件成绩和 Artificial Analysis 的独立测量，并指出 token 单价下降不一定意味着每个任务更便宜。[S12] 其原型成功和 PCB 分数仍来自 Anthropic/Diode，并没有独立制造复现。
- **Hacker News，2026-11-09 至 11 日：工程使用经验。** 评论关注布局返工、串扰/寄生/制造/BOM 之间的取舍，以及单项目 token 成本缺失。一位使用其他模型的用户提到，先设设计规则、再调用自动布线插件改善了其 KiCad 工作流，但当时还没完成装配。[S13] 这属于个人经验，不能作为 Fable 5.2 的性能证据。
- 搜索结果中也出现了 Adafruit 的跟进文章，但正文访问返回 403，因此没有将其内容作为事实依据。在本次检索到且读到的材料中，尚未找到独立团队公开复现 Fable 5.2 三款原型的完整工程、运行记录和实测结果。

官方自己明确写出限制：三个设备尚未完成电气验证、天线调谐、热测试或认证，也不是为量产而设计。工程师负责物理制造、装配和测试；模型没有直接连到这些设备。论文式可复现实验、初步原型功能和量产验证是不同的证据层次。[S2]

**对应到 kicad-partspec，本次落地的方向**

已有链路为 `数据表 PDF → 带页码与引文的 PartSpec → 确定性生成 → spec/引文/符号/封装/KiCad 加载检查`。
改进重点是让输入证据完整可见、一次处理多个页面或元件、把未做的检查和后续工作明确交接，并让参考电路要求可计算。
模型抽取仍可替换；本次不接入特定模型或新的布线器。

本仓库 round 6 已记录：124/124 引脚类型正确、239 条引文均能在页上找到，但只有 6/10 个运行满足当时 scorer 的 usable 定义。这些是历史运行的记录，不是本次重测，也不是 Fable 的结果。文档同时指出 gold 由模型编写、尚无人类全面复核，部分 usable 差异还涉及可选字段及评分口径。[L1]

| 本项目的问题 | 与外部报告的关系 | 工程改进 |
|---|---|---|
| 尺寸引线方向、长度/宽度/厚度混淆 | 几何和图像阅读能力值得支持 | `read-pages` 一次读取多页，提供高清图、裁剪、原始全文和带页码联系表。 |
| 铜焊盘、阻焊开窗、封装轮廓混淆 | 外部案例需要区分制造层面几何 | `review` 按来源页集中值、引文与检查指引，明确保留视觉复核状态。 |
| CID 字体/无可搜索数字导致漏看图页 | round 6 已出现此问题 | `prepare` 索引每一页，标记稀疏/损坏文本并优先预览；不以关键词缺失宣告无图纸。 |
| 同一 PDF 内多个型号、多个封装及图纸版本 | 需要明确文档与型号绑定 | 保存 PDF 哈希、型号/图纸搜索词和全页索引，拒绝混用不同 PDF 的证据包。 |
| 工具调用过碎、单个失败拖住整批 | 外部路由器案例暴露调用粒度问题 | `batch` 提供独立元件输出、失败清单和交接文件，保留成功结果。 |
| 多个工具仍需要手工串接，结果难以交付 | 工具粒度应覆盖完整工作单元 | `project` 用一份清单组织元件与电路，输出统一报告、证据、BOM 和库索引；前后比较明确区分输入变化与停用检查。 |
| 看似合理的接线与选件缺少可计算条件 | Diode testbench 将意图写成条件 | `circuit-check` 检查真实引脚号、重复接线、输出冲突、指定网间电容及耐压，返回计算值。 |
| 文件通过检查被误当成工程完成 | 外部原型也没有完成量产验证 | 交接分别记录实际检查、未执行项、推断值、封装阻碍和后续动作。 |

这些改动不声称提高了某个模型的准确率。原有抽取规则和 gold 保留；新工作流的检查范围按任务明确选择，
不默认执行模型调用、PDF 语料验证、KiCad 加载或全量端到端测试。具体接口与示例见
[工作流说明](../skills/partspec/workflows.md)和[项目入口](../README.md)。

前一阶段的资料调研曾按当时仓库流程执行审计，命令为（后续工程改动没有重跑此命令）：

```bash
PYTHONPATH=src ./scripts/audit.sh --datasheets /home/w23x/datasheets
```

有效结果：28 条规则全部有测试且通过，未通过/退步/未覆盖均为空；`gold-spec 28/28`、`gold-quotes 28/28`、`gold-build 28/28`，其中生成 25 个封装、跳过 3 个；引文层明确标记 LM358 使用厂商重建版本。最初未设置 `PYTHONPATH` 的运行发生测试收集错误，其板面数字没有作为有效结果使用。这里的审计说明现有确定性基线状态，不衡量本次调研的模型进步。

**来源**

- [S1] Anthropic，2026-11-09，[Introducing Claude Fable 5.2 and Claude Mythos 5.2](https://www.anthropic.com/claude-fable-and-mythos-5-2)。官方发布、模型 ID、价格和硬件原型概述。
- [S2] Anthropic，2026-11-09，[Testing Claude on real-world electronics design](https://www.anthropic.com/research/claude-electronics-design)。页面浏览器标题为 “Claude can design electronic prototypes from start to finish”；正文包括布线器、返工、DFM、人工参与及限制。
- [S3] Anthropic，2026-11-09，[Fable 5.2 / Mythos 5.2 System Card](https://www.anthropic.com/document/claude-fable-5-2-mythos-5-2-system-card)，§8.13.2，第 232–234 页；[本次读取的 PDF](https://assets.claude.com/27d60918d218125e7504bc7354c4b4626ec56b11.pdf)。
- [S4] [BenchCAD leaderboard](https://benchcad.com/leaderboard.html)，2026-11-14 查阅。区分标准和自定义 harness，Fable 成绩明确归于 Anthropic；图表读出的成本仅为估计。
- [S5] [BenchCAD 2.1 release](https://github.com/BenchCAD-org/benchcad-2-main/releases/tag/v2.1)、[README](https://github.com/BenchCAD-org/benchcad-2-main)、[评分定义](https://github.com/BenchCAD-org/benchcad-2-main/blob/v2.1/docs/METRICS.md)。
- [S6] Anthropic，2025-12-12，[Making Claude a better electrical engineer](https://claude.com/resources/articles/making-claude-a-better-electrical-engineer)。Diode 合作训练背景、数据表理解失败模式、参考电路 testbench。
- [S7] [Diode pcb / Zener](https://github.com/diodeinc/pcb)，[固定提交的 README](https://github.com/diodeinc/pcb/blob/a9d007f0eada7d3e5cd5ac6349d0d1b13dc4e79a/README.md)，[TestBench 文档](https://github.com/diodeinc/pcb/blob/a9d007f0eada7d3e5cd5ac6349d0d1b13dc4e79a/docs/pages/testing.mdx)。
- [S8] [Diode 本地 FreeRouting 适配源码](https://github.com/diodeinc/pcb/blob/a9d007f0eada7d3e5cd5ac6349d0d1b13dc4e79a/crates/pcbc/src/freerouting/mod.rs)。本次只读实现，没有安装或执行。
- [S9] [KiCad APIs and Bindings](https://dev-docs.kicad.org/en/apis-and-binding/)。
- [S10] [Circuitron README](https://github.com/Shaurya-Sethi/circuitron)。归档状态、封装名幻觉和依赖配置的已知局限，2026-11-14 查阅。
- [S11] [Artificial Analysis — Claude Fable 5.2](https://artificialanalysis.ai/models/claude-fable-5-2)，2026-11-14 查阅。
- [S12] Brian Buntz，R&D World，2026-11-09，[Anthropic says Fable 5.2 nearly doubles its predecessor’s hardware-design score…](https://www.rdworldonline.com/anthropic-says-fable-5-2-nearly-doubles-its-predecessors-hardware-design-score-token-prices-fell-20-but-the-cost-per-task-doubled-at-full-effort/)。
- [S13] [Hacker News 讨论](https://news.ycombinator.com/item?id=50429952)，尤其是关于工程取舍与成本的评论，以及 [先设设计规则的使用经验](https://news.ycombinator.com/item?id=50438532)。个人经历，非受控评测。
- [L1] 本仓库 [evals/README.md](../evals/README.md)，round 5/6 与评估限制；本次仓库起点 `4f491a5`。

检索先使用本机 SearXNG 网关；Google CSE/Yahoo 后端限流或报错，Bing 返回无关结果，因此这些结果不作为证据。之后通过新闻索引定位准确模型名，并直接核读官方页面、系统卡、开源仓库、基准网站及上述第三方资料。
