# V5 专家方法学习档案（2026-11-25）

> 历史学习记录。链接与原创方法总结公开，完整第三方字幕、媒体和本地采集回执不随 GitHub 仓库分发；需要原文时通过来源链接或可选字幕工具获取。
选择标准：公开可核查原件、清晰机制、可验证数据、能转化成实际研究步骤。专家的历史成绩、观点、粉丝数不是事实的替代品；不模仿荐股与带单。以下区分实际阅读、字幕取得和仅筛选候选。

## 一手投资者及学术课程
| 来源与阅读范围 | 吸收方法 | 对应环节 |
|---|---|---|
| Berkshire Hathaway 1986、1992、1996 股东信相关章节；https://www.berkshirehathaway.com/letters/letters.html | 所有者收益扣必要维护投入；新增资本回报高于成本才创造价值；能力圈、持续竞争优势、价格和资本配置 | G2/G4/G5，owner-capital.md |
| Aswath Damodaran NYU 课程资料 https://pages.stern.nyu.edu/~adamodar/；估值视频 https://www.youtube.com/watch?v=LYGYvN5LUbA（完整短篇字幕） | 价值与价格区分、现金流/增长/风险、故事转为数字、动手估值而非精确假象 | L1/L2/L4/L5 |

## 中文与英文视频：本批实际获取原字幕
保存于 video/captions/<视频ID>/captions.json 及 transcript.txt；批次回执 video/captions/batch_03.json。中文为作者字幕，英文为平台现有自动字幕；不下载音视频、不运行语音识别模型。以下是实际研究选段，不把已下载等同全文阅读。时间为字幕最后起始时点近似，不保证视频完整覆盖。
| 作者/主题及链接 | 记录 | 实际学习与转化 |
|---|---|---|
| 小Lin说·利率 https://youtu.be/u3Q9BpZOhP8 | 569条，约16:50，中文人工；阅读0至约800秒相关段落 | 时间价值、风险与期限利差、央行短端与市场长端、融资/需求/折现传导；用曲线与信用利差交叉检验，不能按降息标题判涨跌 |
| 小Lin说·美联储 https://youtu.be/iGz2uWl-kGc | 805条，约25:33，中文人工；阅读600–760及1010–1170秒相关段落 | 治理与政策工具、QE/taper区别、资产负债表传导；会员银行权利、财政汇款和利润要查法定制度及官方报表，拒绝“印钱全部流向股市”的简化推断 |
| Damodaran·估值 https://youtu.be/LYGYvN5LUbA | 144条，约4:56，英语自动；读完短篇字幕 | 将商业叙事对应到现金流、增长和风险；不混淆相对定价和内在价值 |
| Ben Felix·投资教训 https://youtu.be/MOjS2zuQMdo | 213条，约7:00，英语自动；阅读约125–420秒 | 价格已包含预期，比较过程与结果、因子风险、成本及分散；风险溢价不是无条件回报 |
| Patrick Boyle·私人信贷 https://youtu.be/8Qc5U00IiAk | 628条，约26:48，英语自动；阅读0–645、700–920、1100–1350秒相关段落 | 浮息贷款、赎回与资产期限错配、PIK账面与现金利息、估值和流动性；案例指控不作事实，查基金条款、BDC财报、IMF风险研究 |
本批5个全部成功，2359条字幕，最后起始时间合计约81分钟。既有老周横眉学习档案保留，见 video-case-lessons.md。字幕里的术语、事实和数字仍需原件核对。

## 播客与商业个案
- Acquired / Costco：https://www.acquired.fm/episodes/costco 。阅读公开文字稿的会员模式、低加价、规模采购与库存/供应商条款段落。把产品价值主张→重复购买与会员费用→经营利润→现金转换，和官方 10-K 交叉。不可把会员收入/经营利润直接说成会员业务净利润贡献。
- Business Breakdowns / ASML：官方节目站 https://www.joincolossus.com/episodes 。阅读 ASML 节目摘要及公开文字稿开头，学习光刻设备物理约束→晶圆客户产能/先进制程→设备销售、装机服务与利润；未听完。需核对公司分部、交付、客户及出口许可。
- Rational Reminder：https://rationalreminder.ca/ 。阅读因子投资相关节目公开文本片段，结合 Kenneth French 数据库检验风险暴露、机会成本与因子定义；不以播客判断代替实证。
- 中文候选（仅筛选栏目与节目摘要，未称完整收听）：商业就是这样、晚点聊 LateTalk。后续学习应按具体行业/商业机制检索，并记录节目链接、原文位置和所读范围；没有文字稿不冒充已读。

## GitHub、机构与专业原始来源
| 来源 | 用法与边界 |
|---|---|
| https://github.com/py-why/dowhy | 因果建模、识别、估计、反驳四步；不替代识别假设 |
| https://github.com/microsoft/qlib | 时点数据、模型实验和可复现工作流；未安装或回测 |
| https://github.com/bashtage/arch | ARCH/时间序列、区块自助抽样；需适合数据结构 |
| https://github.com/ranaroussi/quantstats | 绩效口径与回撤；期间统计不能当逐笔统计 |
| https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html | 因子和基准原始定义，按版本/日期保存 |
| https://www.cboe.com/optionsinstitute/ ; https://www.optionseducation.org/ | 合约、Greeks及衍生品风险 |
| https://www.federalreserve.gov/ ; https://www.bis.org/statistics/ ; https://www.imf.org/en/Publications/WEO | 货币政策、信用、宏观、跨境与金融稳定 |
| https://www.isc.hbs.edu/strategy/business-strategy/Pages/the-five-forces.aspx ; https://www.bea.gov/industry/input-output-accounts-data ; https://comtradeplus.un.org/ | 竞争结构、产业链投入产出与贸易 |
| https://www.ifrs.org/issued-standards/list-of-standards/ ; https://www.sec.gov/edgar/search/ | 会计定义、披露与原始数据 |
| https://github.com/DefiLlama/dimension-adapters ; https://docs.uniswap.org/ | 链上费用收入、协议规则，读定义与版本 |
本轮阅读公开文档、目录及相关章节；没有将外部框架安装到电脑，也未声称执行其全部算法。

## 迭代规则
新材料必须产出“原始链接及读取范围—研究动作—所需证据—计算/反证—适用边界—更新哪个专业手册”。不按作者名气堆清单。金融资料进入 G1 时必须重新验证数据时间与口径；G2 负责掌握指标，G4/G5 必须把知识落实为调查和模型。专家观点与投资结论分离，允许相互冲突；寻找可以判别解释的证据。
