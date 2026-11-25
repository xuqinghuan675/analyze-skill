# V4 工作流参考与采用决策

本轮实际查阅原始项目说明/具体文件及专业标准。仅吸收可迁移方法，不安装外部 Agent 框架，不将开源项目中的自评当作真实研究成绩。

| 来源 | 阅读入口 | 吸收进 ANALYZE 的设计 |
|---|---|---|
| Anthropic Financial Services，initiating-coverage | https://github.com/anthropics/financial-services/tree/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage ; https://raw.githubusercontent.com/anthropics/financial-services/main/plugins/vertical-plugins/equity-research/skills/initiating-coverage/SKILL.md | 将研究、建模、估值与报告分开，前一阶段真实产物验收后才能进入下一阶段；本项目不强制每项人工确认或固定图表格式。 |
| Stanford STORM | https://github.com/stanford-oval/storm | 从多个视角形成问题，依据来源不断提出后续问题；本项目加上实际父子问题和证据引用，而非模拟专家意见。 |
| LangChain Open Deep Research | https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/deep_researcher.py ; https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/prompts.py | 研究契约、分解独立工作包、比较缺口与剩余研究价值；查阅时该仓库已归档，借鉴设计，不接入其运行依赖。 |
| FinanceBench | https://github.com/patronus-ai/financebench | 金融问答应绑定原文件、证据位置与解释，采用证据 ID、页/表/字段、事实与结论对应。 |
| FinQA | https://github.com/czyssrs/FinQA | 原始表格/文字证据与可执行数学步骤一起验证；采用受限算术复算与输入来源约束。 |
| CFA Institute V(A) | https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a | 独立充分的研究基础、模型的条件和局限、风险情景、第三方数据可信度；据此确定反证和模型门槛。 |
| CFA Institute V(B) | https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-b | 区分事实与意见，交付重大风险、局限与依据。 |
| CFA Institute V(C) | https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-c | 留存原始研究、模型参数和结果；落实为结构文件、回执哈希、回退归档。 |
| Aswath Damodaran, Narrative and Numbers | https://pages.stern.nyu.edu/adamodar/New_Home_Page/numbers%26narrative.htm ; https://pages.stern.nyu.edu/adamodar/New_Home_Page/narrative/yourstory.htm | 把商业叙事转成可观察驱动和量化参数，测试叙事，持续依据事实修正模型。 |

不照搬：第三方仓库对报告字数、字体和固定排版的要求；无条件依赖付费接口；把多轮调用等同于质量；把研究主管的自由宣布结束当作验收。ANALYZE 的八关、覆盖主题、JSON 格式、回执与错误回退为针对本项目的新设计。相关视频与此前金融参考仍在 video-case-lessons.md、finance/source-library.md 中；本轮未新增视频转录。
