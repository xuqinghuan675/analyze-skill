---
name: analyze
description: 深度金融与商业研究 Skill。用于股票/IPO、公司、行业、产品、宏观政策、加密市场及预期差研究；追溯原始证据，解读指标，联动六域，建立可复算模型并执行八关验收。Use for evidence-driven investment, business, industry and market research.
metadata:
  short-description: 穿透式金融与商业研究
---

# ANALYZE · V6

面向投资与创业的穿透式研究 Skill：从真实需求、供需、资金、合同、政策和市场价格推导独立结论。研究质量以证据、计算和反证为准，不以搜索数量、报告长度或收益承诺为准。

## 立即使用

直接调用 `$analyze 研究 <对象>：<核心问题>`。本文件所在目录是 ANALYZE 根目录；命令在该目录运行，使用可用 Python 3.10+。不得要求用户逐关批准；不得擅自操作真实资金或账户。

1. 读取 [WORKFLOW.md](WORKFLOW.md)、[WORKFLOW_SCHEMA.md](WORKFLOW_SCHEMA.md)、[完整研究方法](references/research-method.md) 和 [六域联动](references/cross-domain.md)。
2. 选择主入口（company / industry / product / policy / market / expectation），创建唯一任务 ID：
   `python scripts/research_gate.py init <ID> --routes company`。已有任务先 `status <ID>`，不得重建。自动扩展六域，股票研究不可省略产品、行业、公司、市场与预期。
3. G0 锁定对象、研究截点、决策、关键问题、六域关联。执行 `python scripts/research_gate.py advance <ID>` 逐关验收。
4. G0 后/G1 前运行 `python scripts/source_plan.py --routes company --focus valuation,technology`，按实际对象替换路由与专题。阅读 [多源取证](references/knowledge/field-intelligence.md)、[专项路由](references/knowledge/advanced-index.md)、[指标解码](references/metric-intelligence.md) 及返回的适用手册。原始来源库只导航；X、YouTube、博客、官方信、GitHub 用来发现线索和学习方法，事实回到一手原件。
5. 完成八关，每关保存实际产物再 `advance <ID>`。不得跳关、手改回执、伪造证据、用截点后的信息、重复同一查询冒充深入研究。
6. 最终运行 `python scripts/research_gate.py verify <ID>`。只在 COMPLETE 时称完整验收；重大缺口 PARTIAL，未完成 IN_PROGRESS，变动 STALE，必要时 rewind。报告与证据保存在 `research/<ID>/`，默认不进入 Git。

## 八关与六域

| 关卡 | 实际成果 |
|---|---|
| G0 契约 | 问题、截点、边界及六域关联 |
| G1 原始证据 | 31个主题，原件定位、单位、时间、缺口 |
| G2 指标解码 | 定义、公式、现实意义、替代解释 |
| G3 假设 | 竞争解释、可证伪条件和调查动作 |
| G4 穿透 | 关键问题至少两层实查；六条联动有两端证据 |
| G5 模型 | 24项专项成果、联动计算、三情景、反向条件 |
| G6 反证 | 核对来源、因果、计算、最强反例 |
| G7 交付 | 综合判断、机会成本、风险、失效及下一观察 |

核心链路：产品与行业 → 公司经营和现金流；政策 → 行业；公司 → 市场价格；市场 ↔ 预期。定量结论必须让计算真正消耗相应原始证据，不能拼接六篇摘要。只有原件支持、明确不相关的非核心域可筛除；重大缺口如实记录。

## 专业工具与边界

- [六类研究手册](references/playbooks/) 与 [17份专业手册](references/specialists/)：按需要加载，不机械读取所有文件。
- [来源地图](references/knowledge/source-atlas.md) 与 [专家学习档案](references/expert-learning.md)：说明参考方法与阅读边界。
- `scripts/finance_math.py` 和 `scripts/advanced_finance_math.py`：可复算计算；复杂模型保存实际输入、公式/代码、运行结果。
- [视频字幕规程](references/video/caption-workflow.md)：优先直接读取已有字幕；无字幕记录缺口，不默认运行 ASR。
- 检查器验证结构、来源引用关系、可用时间、公式和文件完整性，不自动验证所有原文真实性、因果正确性或盈利能力。工具缺失时说明未验收；不虚称完整执行。仅学习/维护 Skill、普通问答、读取旧报告不需创建投资研究任务。

完整细节以 [WORKFLOW.md](WORKFLOW.md) 与 [完整研究方法](references/research-method.md) 为准。V6 是知识发布版本，验收 schema 仍为 V5，兼容既有任务。
