# 研究目录与交付模板

V4：WORKFLOW.md 与 WORKFLOW_SCHEMA.md 的八关 JSON 及 report.md 是正式验收格式。以下 CSV 与报告内容为辅助写作/导出参考；不要使用旧结构跳过关卡。

research/YYYY-MM-DD_对象/
  report.md
  evidence.csv
  assumptions.csv
  sources/（原文或链接索引，遵守访问与版权约束）
  data/（原始与处理后数据分目录）
  analysis/（公式、脚本、情景表、图）
  notes/（关键假设变动、失败解释）

## evidence.csv
claim_id,claim,source_type,publisher,source_url,document_version,published_at,available_at,as_of,period,page_section_field,raw_value,unit,definition,calculation,status,limitations

status 可为 verified（原件直接支持）、derived（由记录数据计算）、reported（二手转述）、hypothesis（机制假设）、unknown（缺失/矛盾）。同一命题多个来源分别记行。冲突优先比较时间、定义、范围、原始表格。不要用视频作者的判断标记成 verified。

## assumptions.csv
assumption_id,variable,unit,base,upside,downside,source_or_rationale,range,dependency,sensitivity,trigger_to_update

概率不是必填；无法估计时写 unknown。明确情景间相关性，不擅自将多个条件视为独立。

## report.md（标题与六个必需二级标题）
# 对象、截至日期与研究问题
## 结论
直接回答每项 Q；标注适用期限、最大未知与证据引用。
## 证据与指标
写原件、异常、指标口径、关键比较及证据链。每个重要数字链接至原件/表格及期间口径。
## 机制与计算
现金/产品/供需/制度/预期的传导，涉及谁、时间、条件、风险分配。数据、公式、参数、可复算代码或算式。
## 情景
基准、上行、下行，反向计算市场价格要求的条件（若相关）；判断是否能满足，注明非独立变量、估值/交易时间尺度。
## 反证与限制
最强相反解释、查验结果、仍未知的信息与影响。
## 失效与下一步
列推翻判断的证据、可测指标、阈值、下一观察、何时更新与风险边界。六个标题不能删；不适用的内容解释原因。

## 自查一次
确认核心事实来源与数字单位一致，财务/价格计算可复算，时间点没有泄漏，关键风险和失效条件与结论匹配；修正明显错误即交付。避免重复无意义检查。
