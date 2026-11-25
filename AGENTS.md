# ANALYZE 项目 Agent 强制入口（V6 知识库 / V5 验收）

所有进入本项目执行研究的 Agent（Codex、Claude Code、网页 Agent 及子 Agent）必须先读取 SKILL.md、WORKFLOW.md 、WORKFLOW_SCHEMA.md、references/cross-domain.md 及当前任务对应研究手册。研究任务必须使用 scripts/research_gate.py，禁止仅写一份报告冒充执行完毕。

## 六域联动（不得绕过）
- 新任务 init 自动扩展六域；--routes 是主入口。股票必须联动产品、行业、公司、市场与预期，政策影响也须调查或有证据地筛除。
- G1 原始证据主题标签，G2 活跃域指标卡，G4 L1–L6 双端证据，G5 实际依赖计算，G6 反证，G7 综合核心回答与机会成本/风险边界全部必做。用 references/cross-domain.md 选择专业手册，禁止只拼六段摘要。
- 未解决的重大联动缺口只能 PARTIAL；旧 V4 任务可按 V4 核验，但不得声称 V5 完成。

## V6 专业取证要求
- G0 后/G1 前读取 references/knowledge/field-intelligence.md 与 advanced-index.md，并运行 scripts/source_plan.py 选择主入口及专业主题；实际阅读适用手册，将关键线索追到原件。不得将计划、名人观点、字幕或仓库 README 当作数据。
- 需要专业深化时使用 references/specialists/advanced/ 九个手册，实际产物进入现有 G1–G7；检查器仍用 schema 5，旧任务不重置。只学习或维护 Skill 时无需创建投资研究任务。
- X/YouTube/博客/官方信/GitHub 按问题取舍，不凑数量，不冒充全文阅读或工具实测。新方法必须落到指标、可验证假设、计算或反证。

## 不可跳过的顺序
G0 研究契约 → G1 原始证据 → G2 指标解码 → G3 假设与竞争解释 → G4 穿透调查 → G5 模型与情景 → G6 反证检查 → G7 决策与交付。

- 开始新任务先 init；已有任务先 status，按未通过的第一个关卡恢复。不得为同一研究无故重建目录或删除旧成果。
- 每关实际执行研究动作，填写对应 JSON 与附件，再执行 advance。只有返回 PASS 才能推进。关卡缺证据时，按指引补查；真实不可获取的资料标记 gap，记录尝试及影响，结论降为 PARTIAL。
- 不得手改 _gate/ 回执、completion.json、检查器或其测试以制造通过。修改已通过的阶段须用 rewind，保留旧回执，重新核对受影响的后续阶段。
- 必须先查可访问的一手资料，并围绕异常指标连续追问；禁止只浏览摘要、只搬运研报、用新闻数量填充深度，或编造数据/引用/子 Agent。
- 报告不是唯一产物。交付以真实研究资料、模型、各阶段验收记录和 status/verify 结果为准。没有 COMPLETE 的报告只能按 PARTIAL 或 IN_PROGRESS 交付。
- 研究是分析，不自动交易、不操作未授权账户。只为用户要求的研究展开工作；维护 Skill、普通问答、读旧报告不强制创建研究任务。当前工作区外的 Agent 只有读取本入口并调用检查器才受此工作流约束。
