# V6 专项知识路由（在 V5 八关内执行）
新增九份进阶手册；原有八份与六类 playbooks 保留。先读主入口手册、cross-domain.md 与 metric-intelligence.md，再按题目调用下面的手册。scripts/source_plan.py 仅生成检索与阅读计划，不能替代取证/验收。
| 主题触发 | 进阶手册 | 强制深化产物 |
|---|---|---|
| valuation/expectation：估值、护城河、预期差 | references/specialists/advanced/expectations-moat.md | 反向价格条件、经济利润/增量资本回报、超额回报期限 |
| management/accounting：财报、管理层、股东信、并购 | references/specialists/advanced/management-capital-quality.md | 利润到可分配现金、承诺兑现表、资本用途桥 |
| macro/bank：利率、信用、银行、财政、汇率 | references/specialists/advanced/global-money-credit.md | 资产负债及现金到期桶、风险传导、同币种模型 |
| market/risk：盘口、期货、期权、流动性、风险 | references/specialists/advanced/risk-market-microstructure.md | 交易规则、点差/冲击/实现成本、压力情景 |
| industry/technology/energy：制造、芯片、AI、能源、商品 | references/specialists/advanced/industry-constraints.md | 有效产能/交付/库存、量价成本及瓶颈 |
| quant：实证、因果、回测、预测 | references/specialists/advanced/empirical-research.md | 识别假设、试验账、隔离样本、反证与成本 |
| product/business：创业、SaaS、平台、用户 | references/specialists/advanced/business-model-platforms.md | 用户任务、支付链、cohort、贡献毛利与现金约束 |
| policy：监管、关税、制度、跨境 | references/specialists/advanced/country-policy-legal.md | 原文及适用时点、执行主体、利益和量化影响 |
| crypto：BTC、ETH、DeFi、稳定币、永续 | references/specialists/advanced/crypto-onchain-deep.md | 实体/地址、现金归属、撮合及跨场所成本 |
 
## 重点问答的组合
- 股票/IPO：用户与商业模式 + 行业瓶颈 + 管理层资本配置 + 护城河/反向估值；若银行加货币信用，若科技加工程约束，若政策驱动加法规模块。必须连到当前证券价格和预期。
- 商品/能源：真实交付产能与供需平衡 + 合约/期限结构 + 政策 + 企业量价成本。若仅价格研究，仍评估六域实质关联。
- BTC/量化：微观结构 + 实证/样本外 + 链上经济 + 宏观/政策，区分可交易机制与长期价值假设，保持现货和衍生品口径。
- 宏观/事件：货币信用 + 法规执行 + 实证 + 市场隐含预期；固定发布时间，禁止事后信息回填。
- 创业/产品：实际客户预算与替代品 + 贡献现金/获客 + 产业议价与竞争 + 监管/成本和需求约束。
 
## 执行方法
在 G0 后/G1 前生成计划，例：
    python scripts\source_plan.py --routes company,industry --focus valuation,technology
可选 --output research/<ID>/sources/v6_source_plan.json（只创建新文件；已有计划需换文件名以保留历史）。程序按已有 registry 标签选择方法/线索/原件和候选工具；不可把来源计划当已读内容。计划给出全部六域的强制问题，避免选单域就屏蔽关联。实际选用的每份来源需进入本任务 E 或 lead_log；无效/无关来源可跳过并解释真正重大缺口。所有关键参数以任务时间点的真实原件为准。
