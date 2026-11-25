# V5 结构字段与填写说明

先 init，程序为任务生成全部阶段空模板；再按 status 指出的当前关卡填写真正研究成果。不要把示例复制为真实研究数据。下方示例只说明结构，虚构公司、数字和地址不可用于真实研究。八关V4虚构测试示例在 scripts/test_research_gate.py 的 fixture()，V5完整联动虚构示例在 scripts/test_research_linkage.py，程序会在临时目录运行，不会污染 research/。

## 通用规则
- 字符串写具体内容，不用 TODO、待填、空字符串、N/A 代替研究；数组可按实际需要增删记录。研究缺口必须独立记录。
- Q=研究问题，E=证据，G=缺口，M=指标，H=假设，F=穿透调查，A=假设参数，C=计算结果；各前缀独立编号，同类 ID 唯一。
- 日期使用 ISO 8601 带时区的时间，例如 2025-12-31T16:00:00-05:00。as_of 是研究可知信息截点，不是资料下载时间。
- refs 是实际存在的 ID 数组；引用未取得的材料用 G，不创建假的 E。artifact 等相对路径以本任务目录为根。
- 证据及缺口在 G1/G4/G5/G6 追加；原始资料以新文件名保存新版本，已通过的阶段文件只能通过 rewind 修订。
- 同一研究目录的关卡推进由主 Agent 负责；多 Agent 各自采集证据、提交工作笔记，主 Agent 合并当前阶段后单独 advance。不要多个进程并发修改验收记录。

## G0：范围
manifest 记录任务 ID、主入口和自动扩展的六域。00_scope.json 的 questions 可以多项，至少一个 critical=true；每条 success 必须是具体可检验目标。scope 写实体、产品/政策版本、时间、比较对象和决策边界；exclusions 写明无关问题。问题范围由任务决定，不为了轻松通过而把用户核心问题标为非关键。

## G1 / G4 / G5 / G6：证据和缺口
证据数组内每项：
~~~json
{
  "id": "E1", "source_kind": "primary",
  "publisher": "示例主体", "url": "https://example.invalid/report",
  "locator": "表2第3行；对应附注",
  "available_at": "2025-12-31T12:00:00+00:00",
  "retrieved_at": "2026-01-02T12:00:00+00:00",
  "period": "FY2025", "fact": "虚构示例：营业收入100",
  "unit": "USDm", "value": 100,
  "independence_group": "report-2025",
  "artifact": "sources/report.txt"
}
~~~
value 可省略（文本或纯定性证据），artifact 可省略（无法合法保存原件时用可定位原链接）；本地源用 url="local:sources/report.txt" 且 artifact 相同。事实摘要不得含研究者未被原文支持的解释。证据来源、字段与数值同口径。

缺口：
~~~json
{
  "id": "G1", "topic": "company.commitment", "question_id": "Q1",
  "material": true, "reason": "关键合同到期数据缺失，无法测算现金需求",
  "attempts": [{"query": "已实际查询的具体报告或关键词", "result": "得到的真实结果"}]
}
~~~
material 依据用户问题和决策影响判断，不得为了 COMPLETE 把关键缺口标为 false。topic 必须与该缺口覆盖范围相符；后续新证据解决缺口时，在当前阶段 resolved_gaps 增加 {"gap_id":"G1","refs":["E9"],"explanation":"具体如何解决"}，需要原始证据。

G1 coverage 已按六域自动生成。每行的 status 为 supported（refs 有对应主题原件）、screened（仅筛除域且有原件）或 gap（refs 有同 topic 缺口），finding 必须说明已经取得什么、还缺什么和对问题的关系。报告、交易所、统计数据等的同源转述使用相同 independence_group。

## G2 / G3：指标与假设
沿模板补齐字段。M1 的 next_question 必须是实际需要继续查的问题。H1 的 refs 必须引用同 Q 的指标卡，另引用关键 E/G。competing_explanation 不是换词重复原主张。test_plan 写实际要查看的资料、比较和计算；falsifier 写什么事实会导致改判。

## G4：连续调查
每个关键 Q 至少两条关联 F。根 F1.question 必须等于 H 所引用指标的 next_question 或 H.test_plan；根 parent_id=null。F2.parent_id="F1"，F2.question 必须等于 F1.next_question。实际调查路径与证据需新增，子项至少含一条父项未使用的 E/G。每个关键问题至少新增一条 G4 中实际调查获得的证据/缺口，允许从同一原始文件的另一个表或附注取得。
mechanisms 列边，写 from/to、direction、lag、condition、refs。status=hypothesis 或 supported，后者至少有真实来源 E。不要把相关性写成已证实因果。

## G5：参数、公式、情景
assumptions 参数记录：
~~~json
{"id":"A1","name":"情景净利润率","value":0.2,"unit":"ratio","basis":"为何用该情景假设","sensitivity":"变化怎样影响结果","refs":["E2","H1"]}
~~~
数值应为数字，不是 "20%" 字符串；百分比用小数时 unit="ratio"，乘100显示百分数需明确计算/单位。

calculations 示例：
~~~json
{
  "id":"C1","question_id":"Q1","expression":"revenue * margin",
  "variables":{
    "revenue":{"value":100,"unit":"USDm","ref":"E1"},
    "margin":{"value":0.2,"unit":"ratio","ref":"A1"}
  },
  "expected":20,"unit":"USDm","interpretation":"基准预测利润，非已实现利润"
}
~~~
variables 中每个 ref 必须是数值来源 E/A 或前面已计算的 C；value 与 unit 必须完全对应。公式只允许有限算术表达式，不允许函数调用、导入、文件操作。复杂 DCF/回测等在 analysis/ 中运行真实程序，保存代码及结果，model_artifacts 每项包含 path、role、run_or_check（实际运行命令与输出摘要）。同时用 calculations 复算关键算式。检查器验证复杂附件存在/哈希，不会自行执行任意模型代码。

route_outputs 已按六域生成，每项保留 topic、required_kind、question_id、status、finding、refs；不能删除。measured 需要同 Q 的 C；grounded 仅用于要求定性证据的成果且需原始 E；gap 需同 Q、同 topic 的未解决 G；out_of_scope 需 exclusion 原样存在于 G0 exclusions 字段，并解释为何不影响用户研究目标。定量项不能用 grounded 绕过计算。
model_coverage 对每个关键问题引用其 C 或同 Q 未解决 G；写模型假设与局限。
scenarios 对每个关键问题填 base/upside/downside，metric、unit、horizon 一致，driver 写改变的驱动量及依据，outcome 写情景意义。数值情景 value 必须等于所引用 C 的结果，定性情景 value=null 且引用同 Q 未解决的量化缺口。定性研究可以在范围内给合理非重大量化缺口；不能故意把本应量化的投资判断降成定性猜测。

## G6：反证
countercases 每个关键 Q 一条或更多；strongest_case 写能真正威胁主结论的解释；search_or_recheck 写实际重查的证据或具体反方检验；finding 写结果；verdict=supported / weakened / unresolved（相反解释得到支持/被削弱/尚未解决），response 写主结论或模型如何处理。已解决的反方检查必须引用 E。supported 不意味着主结论自动成立；须根据反方支持程度改变判断。
checks 固定 source/units/as_of/causality/contrary/model；status=pass 或 limited，finding 与 refs 均不可空。source 检查原文、日期、同源/独立性以及冲突；model 核对复算、情景及真实运行结果；不确定就 limited。重大未知应在 G6 添加 G 或标明 unresolved，最后降级。

## G7：结论
answers 必须覆盖所有 Q（含非关键问题），每条 kind=fact / derived / inference / unknown，confidence=high / medium / low / unknown。fact 需原始 E，derived 需同 Q 的 C，inference 需同 Q 的 H 和真实 E，unknown 需未解决 G。confidence 低或未知则最终 PARTIAL。每条写 explanation、invalidation、next_observation，引用相关证据。
report.md 用六个必需小节（见 WORKFLOW.md），引用形式 [Q1] [E1] [H1] [C1] 等；全部 answers 的引用必须出现在报告中。引用正确并非证明叙述正确，仍需确保原文含义。完成后 advance 生成 completion.json；verify 对上游、原始附件、报告和回执重新核验，只有 COMPLETE 的退出码为 0。PARTIAL/IN_PROGRESS 验收退出码为 3，结构错误/被修改退出码为 2。用户可运行 status 查看细节。

## V5 新增字段（与 V4 字段同时填写）
- G0: primary_routes 与 manifest 主入口相同；route_scope 六项，每项 route、depth、entity、question_id、focus、decision_impact、exclusion。depth=primary/linked/screened；核心域及主入口不可屏蔽，screened 的 exclusion 必须出现在 G0 exclusions。详见 cross-domain.md 的核心依赖表。
- G1/G4/G5/G6: 每条 E 增加 topics 字符串数组，使用 init 生成的实际主题 ID 或 output.<route>.<key>；不可随意为无关证据打标签。G1 coverage 的 supported/screened 必须引用主题一致的 primary E；核心域 gap 为 material=true。
- G2: 每张指标卡加 route。所有活跃域至少一张有本域 E 或 G 支撑的卡。
- G4: linkages 六项保持生成的 L1–L6、from_route、to_route、question_id。填写 status=supported/hypothesis/gap/immaterial、driver、target_variable、mechanism、lag、conditions、falsifier、from_refs、to_refs、gap_refs。除 gap 外两端各自至少一个原始 E，且合计至少两个不同 E；gap 引用同 Q、topic=link.Lx、material=true 的未解决 G；immaterial 至少一端已经 screened。假设不宣称已证明因果。
- G5: linkage_models 六项，每项 link_id、status、refs、effect、parameter_or_constraint。measured 必须引用同Q计算 C，C 的依赖（包括上游 C/A）追溯到该 L 的两端指定原始 E；grounded 仅 L3，且双端原始证据对应；gap 同 Q、topic=link.Lx、material=true；immaterial 必须与 G4 状态一致并有双端证据。route_outputs 的 measured/grounded 还需本域原始证据祖先；核心输出 gap 必须重大；活跃域受保护的财务桥/估值/用户任务/ROI/供需/利润池不能排除。
- G6: integration_review 每条链接一项 link_id、counterexample、actual_recheck、refs、verdict=checked/unresolved、response；checked 引用两端原件；unresolved 导致 PARTIAL。
- G7: synthesis 包含一个关键 question_id、全部六个 link_ids、refs、integrated_result、decision_trace、what_changes_it、opportunity_cost、risk_boundary。refs 包括各条 L 模型结果/约束；和主问题 answer.refs 至少共用一个真正综合的 C，C 依赖包含联动计算及至少三个活跃域（不足三则全部），公司入口必须包含产品、行业、公司，其他入口包含其主入口。若无该模型，只能以共享未解决 material G（topic=integration，同Q）如实交付 PARTIAL。报告必须出现 [L1] 至 [L6] 和全部 synthesis.refs。
检查器仅核对结构、数值与证据依赖，语义是否正确、证据是否真实及因果是否成立由实际研究和反证决定；不得乱贴主题或将无关值相乘通过。V4 已有任务按旧 schema 核验。

## 流程中断
已有任务执行 status，按下一关恢复；如果修改封存文件，状态会报 STALE，先 rewind 到最早受影响阶段。rewind 归档旧阶段和回执、报告、完成凭证；大数据或原始文件不自动复制，因此研究员必须为原件版本保留不同路径，不覆盖旧原件。验收器不是权限隔离系统，严禁绕开检查器、直接改回执或伪造证据。
