# 金融研究精选资料库（2026-11-25）

原则：优先选原始披露、维护明确的工具、可解释公式和可追溯数据。GitHub 星数、漂亮页面、长报告、收益宣传都不是研究质量。每个新来源先看文档、实际输入输出、测试、许可证和数据时效，再决定使用；引用具体版本或提交号。以下是本轮实际查阅公开项目说明与方法文件后的筛选，不是已经运行整套第三方项目的声明。

## 一级：事实和一手数据
| 来源 | 地址 | 如何使用 |
|---|---|---|
| SEC EDGAR 官方 API | https://www.sec.gov/search-filings/edgar-application-programming-interfaces | CIK→历史申报元数据、标准化 XBRL facts；定位 filing accession 和原文 |
| EdgarTools | https://github.com/dgunning/edgartools | 读取 10-K/10-Q/8-K/20-F、XBRL 三表、重大事项、内幕人/持股表；原件优先 |
| EdgarTools 快速指引 | https://github.com/dgunning/edgartools/blob/main/docs/quick-guide.md | 检索公司、申报、财务表与原始文本 |
| FRED / ALFRED | https://fred.stlouisfed.org/docs/api/fred/alfred.html | 宏观时间序列、首次发布与修订版本；历史研究还原当时已知信息 |
| 美国联储 | https://www.federalreserve.gov/ | FOMC 声明、SEP、发布会、会议纪要、H.4.1 资产负债表 |
| BLS / BEA / Treasury | https://www.bls.gov/ ; https://www.bea.gov/ ; https://home.treasury.gov/ | 通胀、就业、GDP/PCE、收益率和财政数据 |
| CFTC | https://www.cftc.gov/MarketReports/CommitmentsofTraders/index.htm | 按品种及参与者类别的期货持仓；注明滞后与覆盖范围 |

EDGAR 公开数据接口无需密钥。请求需遵守 SEC fair access、设置合适 User-Agent、限速、缓存、失败退避；不绕过访问限制。CompanyFacts 的标准化聚合不能替代原始披露上下文；公司自定义标签、非 GAAP、分部/地域、合同和重大附注要直接查 filing。历史分析按披露可获得日期过滤，而非只看报告期末。FRED 最新修订数不作为历史可知数据，用 ALFRED 或首发公告。

## 二级：专业金融研究方法
| 项目 | 已核实资料 | 采用部分 |
|---|---|---|
| Anthropic financial-services | https://github.com/anthropics/financial-services | 覆盖研究、可比公司、财报分析、三表模型、估值、研究观点维护；根据任务选择，不强制报告长度或使用指定商业数据库 |
| 财报更新工作流 | https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/commands/earnings.md | 实际结果、此前预期、解释差异、指引修订，更新预测与估值 |
| 研究观点追踪 | https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/equity-research/skills/thesis-tracker/SKILL.md | 关键假设与催化事件、反证、研究版本变更 |
| DCF 建模 | https://github.com/anthropics/financial-services/blob/main/plugins/vertical-plugins/financial-analysis/skills/dcf-model/SKILL.md | 预测参数独立、现金流折现、敏感性和计算一致性 |
| FinRobot | https://github.com/AI4Finance-Foundation/FinRobot | 将财务计算交给确定性代码，Agent 做解释；证据和结果保留计算链，不引入整套大型 Agent/UI 系统 |
| Damodaran 教授（NYU Stern） | https://pages.stern.nyu.edu/adamodar/New_Home_Page/spreadsh.htm | 估值模型选择、资本成本、再投资、金融企业/高增长等特殊估值 |
| Damodaran 行业数据 | https://pages.stern.nyu.edu/adamodar/New_Home_Page/data.html | 各行业/地区利润率、风险、资本回报、估值及历史版本，用于校准参数；记录数据日期和统计口径 |

不采用仅按新闻情绪或技术指标打分的自动荐股系统，不把未经验证的 LLM 观点或回测收益当作证据。OpenBB 此次查到其原 GitHub 组织已宣布停止运营/资产移交，暂不作为新依赖。部分开源金融项目依赖付费数据源或 API；本 Skill 先使用官方公开数据，可授权接入更高质量的数据，缺数据明确标注。

## 三级：视频学习
- https://github.com/jdepoix/youtube-transcript-api ：直接读公开可获取字幕，不转录音频。
- https://github.com/yt-dlp/yt-dlp ：备选字幕读取路径，启用 skip-download；不用不明第三方字幕站。
- 老周横眉频道 https://www.youtube.com/channel/UCFDMMIHbtRdrVhHlGXVzApA ：训练追问、理解指标及商业/经济机制。将观点与客观事实区分；视频中的数字回到监管或统计原件。
- 本轮实际直接字幕测试见 video/captions/latest_run.json。历史识别片段仍保留来源标签，不称为作者字幕。

## 维护规则
新知识写进指标手册或专题研究路径，至少包含定义、现实机制、证据字段、替代解释、适用条件及反例。优先补能改变真实结论的知识，不为扩展条数而新增内容。外部代码不自动安装、不自动执行仓库脚本，独立评估依赖和许可证后再接入。
