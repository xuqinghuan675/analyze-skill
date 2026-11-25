"""ANALYZE V5: cross-domain, deterministic research gate. Python 3.10+."""
import argparse
import ast
import datetime as dt
import hashlib
import json
import math
import operator
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlparse
import research_linkage as linkage

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
VERSION = 5
FILES = ["00_scope.json","01_evidence.json","02_metrics.json","03_hypotheses.json",
         "04_investigation.json","05_model.json","06_review.json","07_decision.json"]
NAMES = ["研究契约","原始证据","指标解码","假设与竞争解释","穿透调查","模型与情景","反证检查","决策与交付"]
TOPICS = {
    "industry": {"chain":"产业链和交易关系","demand":"终端需求及真实使用","supply":"产能库存价格与供给","profit":"成本与利润池","competition":"竞争/替代和周期"},
    "company": {"filings":"原始披露及主体","revenue":"业务/客户与收入驱动","cost":"成本利润及增量","cash":"现金债务与资本投入","commitment":"合同承诺/治理/风险","price":"市场价格/股本及估值基准"},
    "product": {"user":"用户及真实任务","alternative":"替代品和验证","price":"价格与付费行为","economics":"单位经济与交付","retention":"留存/复购和壁垒"},
    "policy": {"text":"原文/版本/适用及生效","execution":"执行部门与实际进度","budget":"预算/限制/处罚","exposure":"受益受损主体","baseline":"反事实与历史对照"},
    "market": {"rules":"标的及交易/定价规则","price":"价格与供需","liquidity":"流动性与成本","participants":"参与者、持仓或交易流","regime":"历史/当前市场状态"},
    "expectation": {"event":"事件与可知时间","consensus":"事前共识","pricing":"市场隐含预期","drivers":"独立基本面驱动","reaction":"历史及其他影响因素"},
}
ROUTE_OUTPUTS = {
    "industry": {"value_chain":("真实交易与价值链","grounded"),"supply_demand":("可售供给、终端需求与供需缺口","quantitative"),"profit_pool":("单位经济与利润分配","quantitative"),"cycle":("周期、瓶颈及利润迁移条件","grounded")},
    "company": {"financial_bridge":("收入、利润和现金流的驱动桥接","quantitative"),"cash_commitments":("现金、债务、合同与资金缺口","quantitative"),"governance":("控制权、治理与关键约束","grounded"),"valuation":("合理价值与当前价格隐含门槛","quantitative")},
    "product": {"tasks":("真实任务、用户和替代品","grounded"),"user_roi":("用户成本收益及付费意愿","quantitative"),"unit_economics":("提供方单位经济及获客回收","quantitative"),"retention":("真实留存、切换成本与可交付性","grounded")},
    "policy": {"legal":("原文、效力、执行主体与时间","grounded"),"transmission":("行为激励和利益传导","grounded"),"impact":("覆盖规模、预算与边际经济影响","quantitative"),"trigger":("实施瓶颈、反事实与后续验证","grounded")},
    "market": {"structure":("交易制度与边际定价机制","grounded"),"liquidity":("交易/交付成本与流动性","quantitative"),"baseline":("基准、状态条件与可验证表现","quantitative"),"regime":("行情状态、规律约束与失效","grounded")},
    "expectation": {"surprise":("事前共识与独立预期差","quantitative"),"pricing":("价格隐含预期或可验证代理","quantitative"),"catalyst":("兑现时点、驱动与条件","grounded"),"reaction":("情景价格反应及成本后赔率","quantitative")},
}
CHECKS = ["source","units","as_of","causality","contrary","model"]
HEADINGS = ["结论","证据与指标","机制与计算","情景","反证与限制","失效与下一步"]
PLACEHOLDER = {"tbd","todo","待填","待补充","未知待查","placeholder","...","未填写","n/a","na","none","null"}

class GateError(Exception): pass
def require(condition, message):
    if not condition: raise GateError(message)
def filled(v, name):
    require(isinstance(v,str) and bool(v.strip()) and v.strip().lower() not in PLACEHOLDER, f"{name}: fill actual content")
    return v.strip()
def fields(row, keys, name):
    require(isinstance(row,dict),f"{name}: expected object")
    for k in keys: filled(row.get(k),f"{name}.{k}")
def arr(row,k,where):
    v=row.get(k)
    require(isinstance(v,list),f"{where}.{k}: expected array")
    return v
def flag(v,name):
    require(type(v) is bool,f"{name}: expected true/false")
    return v
def stamp(v,name):
    filled(v,name)
    try: t=dt.datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError: raise GateError(f"{name}: ISO 8601 datetime required")
    require(t.tzinfo is not None and t.utcoffset() is not None,f"{name}: timezone required")
    return t
def number(x,name):
    require(type(x) in (int,float) and math.isfinite(x),f"{name}: finite number required")
    return x
def uid(row,prefix,seen):
    require(isinstance(row,dict),f"{prefix}: expected object")
    x=row.get("id")
    require(isinstance(x,str) and re.fullmatch(prefix+r"[1-9]\d*",x),f"{prefix}: invalid id {x}")
    require(x not in seen,f"duplicate id: {x}")
    return x
def ref_list(v,allowed,name,empty=False):
    require(isinstance(v,list) and (empty or len(v)>0),f"{name}: references required")
    require(all(isinstance(x,str) and x in allowed for x in v),f"{name}: unknown reference")
    require(len(set(v))==len(v),f"{name}: duplicate reference")
    return v
def read_json(p):
    try:
        x=json.loads(p.read_text(encoding="utf-8-sig"))
        require(isinstance(x,dict),f"{p.name}: expected JSON object")
        return x
    except (OSError,ValueError) as e: raise GateError(f"{p.name}: {e}") from e
def write_json(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile("w",encoding="utf-8",dir=p.parent,delete=False) as f:
        tmp=Path(f.name)
        json.dump(x,f,ensure_ascii=False,indent=2,allow_nan=False)
        f.write("\n")
    tmp.replace(p)
def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""): h.update(chunk)
    return h.hexdigest()
def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def relfile(root,relative):
    require(isinstance(relative,str) and bool(relative), "artifact path required")
    rel=Path(relative)
    require(not rel.is_absolute() and ".." not in rel.parts, f"unsafe artifact path {relative}")
    p=(root/rel).resolve()
    require(p.is_relative_to(root.resolve()) and p.is_file(),f"artifact missing/outside task: {relative}")
    require(p.stat().st_size>0,f"empty artifact: {relative}")
    return p
def topic_ids(routes): return {f"{r}.{k}":v for r in routes for k,v in TOPICS[r].items()}
def output_ids(routes): return {f"output.{r}.{k}":v for r in routes for k,v in ROUTE_OUTPUTS[r].items()}
def blank_evidence():
    return {"id":"E1","source_kind":"","publisher":"","url":"","locator":"","available_at":"","retrieved_at":"","period":"","fact":"","unit":"","independence_group":""}
def blank_gap():
    return {"id":"G1","topic":"","question_id":"","material":True,"reason":"","attempts":[{"query":"","result":""}]}
def templates(routes):
    return [
      {"object":"","question":"","as_of":"","horizon":"","decision":"","scope":"","exclusions":"","routes":routes,"questions":[{"id":"Q1","question":"","critical":True,"success":""}]},
      {"evidence":[],"gaps":[],"coverage":[{"topic":t,"label":label,"status":"","refs":[],"finding":""} for t,label in topic_ids(routes).items()]},
      {"metrics":[{"id":"M1","question_id":"Q1","name":"","definition":"","unit":"","rule":"","observation":"","benchmark":"","interpretation":"","alternative":"","distinguishing_evidence":"","next_question":"","refs":[]}]},
      {"hypotheses":[{"id":"H1","question_id":"Q1","claim":"","mechanism":"","competing_explanation":"","falsifier":"","test_plan":"","refs":[]}]},
      {"evidence":[],"gaps":[],"resolved_gaps":[],"followups":[{"id":"F1","question_id":"Q1","hypothesis_id":"H1","parent_id":None,"question":"","investigation":"","finding":"","refs":[],"next_question":""},{"id":"F2","question_id":"Q1","hypothesis_id":"H1","parent_id":"F1","question":"","investigation":"","finding":"","refs":[],"next_question":""}],"mechanisms":[{"question_id":"Q1","hypothesis_id":"H1","edges":[{"from":"","to":"","direction":"","lag":"","condition":"","status":"hypothesis","refs":[]}],"implication":""}]},
      {"evidence":[],"gaps":[],"resolved_gaps":[],"assumptions":[],"calculations":[],"model_artifacts":[],"route_outputs":[{"topic":t,"label":label,"required_kind":kind,"status":"","question_id":"Q1","finding":"","refs":[],"exclusion":""} for t,(label,kind) in output_ids(routes).items()],"model_coverage":[{"question_id":"Q1","refs":[],"interpretation":""}],"scenarios":[{"question_id":"Q1","kind":kind,"metric":"","unit":"","horizon":"","driver":"","outcome":"","value":None,"refs":[]} for kind in ("base","upside","downside")]},
      {"evidence":[],"gaps":[],"resolved_gaps":[],"countercases":[{"question_id":"Q1","strongest_case":"","search_or_recheck":"","finding":"","refs":[],"verdict":"","response":""}],"checks":[{"name":c,"status":"","finding":"","refs":[]} for c in CHECKS]},
      {"answers":[{"question_id":"Q1","kind":"","conclusion":"","explanation":"","refs":[],"confidence":"","invalidation":"","next_observation":""}],"limitations":"","decision":"","next_step":""}
    ]

class Context:
    def __init__(self,root,manifest):
        self.root=root; self.routes=manifest["routes"]; self.topics=topic_ids(self.routes)
        self.version=manifest["version"]; self.anchors=manifest.get("primary_routes",self.routes)
        self.asof=None; self.scope={}; self.questions={};self.ev={};self.gaps={};self.resolved=set()
        self.metrics={};self.hyp={};self.follow={};self.assumptions={};self.calcs={}
        self.artifacts=set();self.unresolved_review=False;self.unknown=False
    def refs(self): return set(self.ev)|set(self.gaps)|set(self.metrics)|set(self.hyp)|set(self.follow)|set(self.assumptions)|set(self.calcs)
    def source_refs(self):return set(self.ev)|set(self.gaps)
    def q(self,x):
        require(x in self.questions,f"unknown question {x}");return x
    def critical(self):return {k for k,r in self.questions.items() if r["critical"]}
    def covered(self,rows,label,all_questions=False):
        required=set(self.questions) if all_questions else self.critical()
        covered={r.get("question_id") for r in rows}
        require(required<=covered,f"{label}: missing questions {sorted(required-covered)}")
    def material_gaps(self): return [k for k,r in self.gaps.items() if r["material"] and k not in self.resolved]
    def conclusion(self): return "PARTIAL" if self.material_gaps() or self.unresolved_review or self.unknown else "COMPLETE"

def append_sources(ctx,data,stage):
    for e in arr(data,"evidence",stage):
        x=uid(e,"E",ctx.ev)
        fields(e,["source_kind","publisher","url","locator","available_at","retrieved_at","period","fact","unit","independence_group"],x)
        require(e["source_kind"] in ("primary","secondary"),f"{x}: source_kind primary/secondary")
        url=e["url"]
        if url.startswith("local:"):
            local=url.removeprefix("local:")
            require(e.get("artifact")==local,f"{x}: local source must match artifact")
        else:
            u=urlparse(url);require(u.scheme in ("http","https") and bool(u.netloc),f"{x}: valid source URL required")
        available=stamp(e["available_at"],x+".available_at")
        retrieved=stamp(e["retrieved_at"],x+".retrieved_at")
        require(available<=ctx.asof,f"{x}: future information after as_of")
        require(available<=retrieved,f"{x}: retrieved before available")
        if e.get("value") is not None: number(e["value"],x+".value")
        if e.get("artifact"):ctx.artifacts.add(relfile(ctx.root,e["artifact"]))
        ctx.ev[x]=e
    for g in arr(data,"gaps",stage):
        x=uid(g,"G",ctx.gaps)
        fields(g,["topic","reason"],x)
        if g.get("question_id"):ctx.q(g["question_id"])
        flag(g.get("material"),x+".material")
        attempts=arr(g,"attempts",x);require(attempts,f"{x}: actual retrieval attempt required")
        for a in attempts: fields(a,["query","result"],x+".attempt")
        ctx.gaps[x]=g
    if stage!="G1":
        for item in arr(data,"resolved_gaps",stage):
            g=item.get("gap_id");require(g in ctx.gaps and g not in ctx.resolved,"resolution must reference an unresolved gap")
            refs=ref_list(item.get("refs"),set(ctx.ev),g+".resolution")
            require(any(ctx.ev[x]["source_kind"]=="primary" for x in refs),f"{g}: primary evidence required for resolution")
            filled(item.get("explanation"),g+".explanation")
            ctx.resolved.add(g)

OPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Pow:operator.pow}
def arithmetic(expression,variables):
    require(len(expression)<=500,"formula too long")
    try: tree=ast.parse(expression,mode="eval")
    except SyntaxError as e:raise GateError("invalid arithmetic formula") from e
    require(sum(1 for _ in ast.walk(tree))<=100,"formula too complex")
    used=set()
    def walk(node):
        if isinstance(node,ast.Constant):return number(node.value,"constant")
        if isinstance(node,ast.Name):
            require(node.id in variables,f"unknown variable {node.id}");used.add(node.id);return variables[node.id]
        if isinstance(node,ast.UnaryOp) and type(node.op) in (ast.UAdd,ast.USub):
            n=walk(node.operand);return n if isinstance(node.op,ast.UAdd) else -n
        if isinstance(node,ast.BinOp) and type(node.op) in OPS:
            a,b=walk(node.left),walk(node.right)
            if isinstance(node.op,ast.Pow):require(abs(b)<=100,"exponent outside supported range")
            try: return number(OPS[type(node.op)](a,b),"formula result")
            except (ArithmeticError,ValueError,TypeError) as e:raise GateError(f"formula: {e}") from e
        raise GateError("formula contains forbidden expression; use arithmetic only")
    value=walk(tree.body)
    require(used==set(variables),"unused or unbound formula variables")
    return value

def _validate_base_stage(i,d,c):
    if i==0:
        fields(d,["object","question","as_of","horizon","decision","scope","exclusions"],"G0")
        require(d.get("routes")==c.routes,"routes differ from init manifest")
        c.asof=stamp(d["as_of"],"as_of"); c.scope=d
        for q in arr(d,"questions","G0"):
            x=uid(q,"Q",c.questions);fields(q,["question","success"],x);flag(q.get("critical"),x+".critical");c.questions[x]=q
        require(c.critical(),"G0: at least one critical question required")
    elif i==1:
        append_sources(c,d,"G1")
        rows=arr(d,"coverage","G1");seen=set()
        for row in rows:
            fields(row,["topic","status","finding"],"coverage")
            t=row["topic"];require(t in c.topics and t not in seen,f"coverage: unknown/duplicate topic {t}");seen.add(t)
            refs=ref_list(row.get("refs"),c.source_refs(),t)
            if row["status"]=="supported" or (c.version==5 and row["status"]=="screened"):
                require(any(x in c.ev and c.ev[x]["source_kind"]=="primary" for x in refs),f"{t}: supported requires primary evidence")
            elif row["status"]=="gap":
                require(any(x in c.gaps and c.gaps[x]["topic"]==t for x in refs),f"{t}: matching gap required")
            else:raise GateError(f"{t}: status must be supported or gap")
        require(seen==set(c.topics),f"G1: missing coverage {sorted(set(c.topics)-seen)}")
    elif i==2:
        rows=arr(d,"metrics","G2")
        for m in rows:
            x=uid(m,"M",c.metrics);c.q(m.get("question_id"))
            fields(m,["name","definition","unit","rule","observation","benchmark","interpretation","alternative","distinguishing_evidence","next_question"],x)
            require(m["interpretation"].strip()!=m["alternative"].strip(),f"{x}: alternative must differ")
            ref_list(m.get("refs"),c.source_refs(),x);c.metrics[x]=m
        c.covered(rows,"G2")
    elif i==3:
        rows=arr(d,"hypotheses","G3")
        for h in rows:
            x=uid(h,"H",c.hyp);c.q(h.get("question_id"))
            fields(h,["claim","mechanism","competing_explanation","falsifier","test_plan"],x)
            require(h["claim"].strip()!=h["competing_explanation"].strip(),f"{x}: competing explanation must differ")
            refs=ref_list(h.get("refs"),c.source_refs()|set(c.metrics),x)
            require(any(r in c.metrics and c.metrics[r]["question_id"]==h["question_id"] for r in refs),f"{x}: link the relevant metric card")
            c.hyp[x]=h
        c.covered(rows,"G3")
    elif i==4:
        old_refs=c.source_refs()
        append_sources(c,d,"G4")
        new_refs=c.source_refs()-old_refs
        rows=arr(d,"followups","G4");depth={}
        for f in rows:
            x=uid(f,"F",c.follow);q=c.q(f.get("question_id"));h=f.get("hypothesis_id")
            require(h in c.hyp and c.hyp[h]["question_id"]==q,f"{x}: invalid hypothesis")
            fields(f,["question","investigation","finding","next_question"],x)
            refs=ref_list(f.get("refs"),c.source_refs(),x)
            require(f["question"].strip()!=f["next_question"].strip(),f"{x}: next question must differ")
            p=f.get("parent_id")
            if p is None:
                metric_questions={c.metrics[m]["next_question"].strip() for m in c.hyp[h]["refs"] if m in c.metrics}
                require(f["question"].strip() in metric_questions or f["question"].strip()==c.hyp[h]["test_plan"].strip(),f"{x}: root must follow metric next_question or hypothesis test_plan")
                depth[x]=1
            else:
                require(p in c.follow and c.follow[p]["question_id"]==q and c.follow[p]["hypothesis_id"]==h,f"{x}: invalid previous followup")
                require(c.follow[p]["next_question"].strip()==f["question"].strip(),f"{x}: question must match previous next_question")
                require(c.follow[p]["investigation"].strip()!=f["investigation"].strip(),f"{x}: duplicate investigation")
                require(set(refs)-set(c.follow[p]["refs"]),f"{x}: child requires at least one additional evidence/gap reference")
                depth[x]=depth[p]+1
            c.follow[x]=f
        for q in c.critical():
            require(any(c.follow[f]["question_id"]==q and n>=2 for f,n in depth.items()),f"{q}: need two linked investigation levels")
            require(any(f["question_id"]==q and set(f["refs"])&new_refs for f in rows),f"{q}: G4 must add newly investigated evidence or a documented gap")
        mechanisms=arr(d,"mechanisms","G4");c.covered(mechanisms,"G4 mechanisms")
        for m in mechanisms:
            q=c.q(m.get("question_id"));h=m.get("hypothesis_id")
            require(h in c.hyp and c.hyp[h]["question_id"]==q,"mechanism invalid hypothesis")
            filled(m.get("implication"),"mechanism.implication")
            edges=arr(m,"edges","mechanism");require(edges,"mechanism requires edges")
            for e in edges:
                fields(e,["from","to","direction","lag","condition","status"],"edge")
                require(e["from"]!=e["to"],"edge cannot be self-loop")
                require(e["status"] in ("hypothesis","supported"),"edge status")
                refs=ref_list(e.get("refs"),c.source_refs()|set(c.follow),"edge")
                if e["status"]=="supported":require(any(x in c.ev for x in refs),"supported mechanism needs source evidence")
    elif i==5:
        append_sources(c,d,"G5")
        for a in arr(d,"assumptions","G5"):
            x=uid(a,"A",c.assumptions)
            fields(a,["name","unit","basis","sensitivity"],x);number(a.get("value"),x+".value")
            ref_list(a.get("refs"),c.source_refs()|set(c.hyp),x);c.assumptions[x]=a
        for item in arr(d,"calculations","G5"):
            x=uid(item,"C",c.calcs);c.q(item.get("question_id"))
            fields(item,["expression","unit","interpretation"],x)
            vals=item.get("variables");require(isinstance(vals,dict) and vals,f"{x}: sourced variables required")
            sources={**c.ev,**c.assumptions,**c.calcs};numbers={}
            for name,v in vals.items():
                require(isinstance(name,str) and name.isidentifier(),f"{x}: invalid variable name")
                fields(v,["unit","ref"],x+"."+name)
                source=sources.get(v["ref"]);require(source is not None,f"{x}: unknown numeric input ref {v['ref']}")
                n=number(v.get("value"),x+"."+name)
                expected=number(source.get("value",source.get("expected")),v["ref"])
                require(math.isclose(n,expected,rel_tol=1e-9,abs_tol=1e-9) and v["unit"]==source["unit"],f"{x}: input value/unit differs from {v['ref']}")
                numbers[name]=n
            result=arithmetic(item["expression"],numbers)
            expected=number(item.get("expected"),x+".expected")
            require(math.isclose(result,expected,rel_tol=1e-6,abs_tol=1e-8),f"{x}: computed {result} != claimed {expected}")
            c.calcs[x]=item
        for a in arr(d,"model_artifacts","G5"):
            fields(a,["path","role","run_or_check"],"model artifact");c.artifacts.add(relfile(c.root,a["path"]))
        coverage=arr(d,"model_coverage","G5");c.covered(coverage,"G5")
        for m in coverage:
            q=c.q(m.get("question_id"));filled(m.get("interpretation"),"model coverage")
            refs=ref_list(m.get("refs"),set(c.calcs)|set(c.gaps),"model coverage")
            require(any(x in c.calcs and c.calcs[x]["question_id"]==q or x in c.gaps and c.gaps[x].get("question_id")==q and x not in c.resolved for x in refs),f"{q}: calculation or explicit matching unresolved gap required")
        required_outputs=output_ids(c.routes);output_seen=set()
        for o in arr(d,"route_outputs","G5"):
            fields(o,["topic","status","finding"],"route output");t=o["topic"];q=c.q(o.get("question_id"))
            require(t in required_outputs and t not in output_seen,f"unknown/duplicate route output {t}");output_seen.add(t)
            expected_kind=required_outputs[t][1]
            if o["status"]=="out_of_scope":
                exclusion=filled(o.get("exclusion"),t+".exclusion")
                require(exclusion in c.scope["exclusions"],f"{t}: exclusion must be declared in G0")
                ref_list(o.get("refs"),c.refs(),t,empty=True)
            else:
                refs=ref_list(o.get("refs"),c.refs(),t)
                if o["status"]=="gap":
                    require(any(x in c.gaps and c.gaps[x]["topic"]==t and x not in c.resolved and c.gaps[x].get("question_id")==q for x in refs),f"{t}: matching unresolved gap required")
                elif o["status"]=="measured":
                    require(any(x in c.calcs and c.calcs[x]["question_id"]==q for x in refs),f"{t}: measured requires calculation for same question")
                elif o["status"]=="grounded":
                    require(expected_kind=="grounded",f"{t}: quantitative output requires calculation or gap")
                    require(any(x in c.ev and c.ev[x]["source_kind"]=="primary" for x in refs),f"{t}: grounded requires primary evidence")
                else:raise GateError(f"{t}: invalid route output status")
        require(output_seen==set(required_outputs),f"missing route outputs {sorted(set(required_outputs)-output_seen)}")
        rows=arr(d,"scenarios","G5");seen={}
        for s in rows:
            q=c.q(s.get("question_id"));fields(s,["kind","metric","unit","horizon","driver","outcome"],"scenario")
            require(s["kind"] in ("base","upside","downside"),"invalid scenario kind")
            refs=ref_list(s.get("refs"),c.refs(),"scenario")
            if s.get("value") is None:
                require(any(x in c.gaps and x not in c.resolved and c.gaps[x].get("question_id")==q for x in refs),f"{q}: qualitative scenario needs a matching unresolved quantification gap")
            else:
                n=number(s["value"],"scenario.value")
                require(any(x in c.calcs and c.calcs[x]["question_id"]==q and c.calcs[x]["unit"]==s["unit"] and math.isclose(n,c.calcs[x]["expected"],rel_tol=1e-6,abs_tol=1e-8) for x in refs),f"{q}: numeric scenario must match a calculated result and unit")
            k=(q,s["kind"]);require(k not in seen,f"duplicate scenario {k}");seen[k]=s
        for q in c.critical():
            items=[seen.get((q,k)) for k in ("base","upside","downside")]
            require(all(items),f"{q}: base/upside/downside scenarios required")
            require(len({(s["metric"],s["unit"],s["horizon"]) for s in items})==1,f"{q}: inconsistent scenario basis")
    elif i==6:
        append_sources(c,d,"G6")
        rows=arr(d,"countercases","G6");c.covered(rows,"G6")
        for r in rows:
            c.q(r.get("question_id"));fields(r,["strongest_case","search_or_recheck","finding","verdict","response"],"countercase")
            ref_list(r.get("refs"),c.refs(),"countercase")
            require(r["verdict"] in ("supported","weakened","unresolved"),"countercase verdict")
            if r["verdict"]=="unresolved":c.unresolved_review=True
            else:require(any(x in c.ev for x in r["refs"]),"resolved countercase needs actual source evidence")
        seen=set()
        for r in arr(d,"checks","G6"):
            fields(r,["name","status","finding"],"review check");k=r["name"]
            require(k in CHECKS and k not in seen,"invalid/duplicate review check");seen.add(k)
            require(r["status"] in ("pass","limited"),f"{k}: use pass/limited")
            ref_list(r.get("refs"),c.refs(),k)
            if r["status"]=="limited":c.unresolved_review=True
        require(seen==set(CHECKS),f"missing review checks {sorted(set(CHECKS)-seen)}")
    elif i==7:
        fields(d,["limitations","decision","next_step"],"G7")
        rows=arr(d,"answers","G7");c.covered(rows,"G7",True);seen=set();required_refs=set()
        for a in rows:
            q=c.q(a.get("question_id"));require(q not in seen,"duplicate answer");seen.add(q)
            fields(a,["kind","conclusion","explanation","confidence","invalidation","next_observation"],q)
            require(a["kind"] in ("fact","derived","inference","unknown"),f"{q}: invalid answer kind")
            require(a["confidence"] in ("high","medium","low","unknown"),f"{q}: invalid confidence")
            refs=ref_list(a.get("refs"),c.refs(),q);required_refs.update(refs);required_refs.add(q)
            if a["kind"]=="fact":require(any(x in c.ev and c.ev[x]["source_kind"]=="primary" for x in refs),f"{q}: fact needs primary source")
            elif a["kind"]=="derived":require(any(x in c.calcs and c.calcs[x]["question_id"]==q for x in refs),f"{q}: derived answer needs computed result")
            elif a["kind"]=="inference":require(any(x in c.hyp and c.hyp[x]["question_id"]==q for x in refs) and any(x in c.ev for x in refs),f"{q}: inference needs hypothesis and source")
            else:
                require(any(x in c.gaps and x not in c.resolved for x in refs),f"{q}: unknown answer needs unresolved gap")
                c.unknown=True
            if a["confidence"] in ("low","unknown"):c.unknown=True
        report=relfile(c.root,"report.md");s=report.read_text(encoding="utf-8-sig")
        for h in HEADINGS:
            match=re.search(r"(?m)^## "+re.escape(h)+r"\s*$",s)
            require(match,f"report missing section {h}")
            tail=s[match.end():].split("\n## ",1)[0].strip()
            filled(tail,"report "+h)
        cited=set(re.findall(r"\[([QEGMHFAC][1-9]\d*)\]",s))
        require(cited<=c.refs()|set(c.questions),f"report invalid references {sorted(cited-(c.refs()|set(c.questions)))}")
        require(required_refs<=cited,f"report missing answer references {sorted(required_refs-cited)}")
        c.artifacts.add(report)

def validate_stage(i,d,c):
    _validate_base_stage(i,d,c)
    linkage.check_stage(i,d,c,sys.modules[__name__])

def manifest_for(root):
    m=read_json(root/"manifest.json")
    require(m.get("version") in (4,VERSION),"unsupported manifest version")
    rs=m.get("routes")
    require(isinstance(rs,list) and rs and len(rs)==len(set(rs)) and all(x in TOPICS for x in rs),"invalid routes")
    if m["version"]==5:
        anchors=m.get("primary_routes")
        require(isinstance(anchors,list) and anchors and len(anchors)==len(set(anchors)) and all(x in TOPICS for x in anchors),"invalid primary routes")
        require(rs==linkage.expand(anchors),"V5 requires all six linked routes")
    require(m.get("id")==root.name,"manifest id mismatch")
    return m
def init(root,routes):
    require(routes and all(x in TOPICS for x in routes) and len(routes)==len(set(routes)),"choose valid distinct routes")
    require(not root.exists(),"task already exists; use status")
    root.mkdir(parents=True)
    anchors=list(routes);routes=linkage.expand(anchors)
    write_json(root/"manifest.json",{"version":VERSION,"id":root.name,"routes":routes,"primary_routes":anchors,"created_at":now()})
    for name,d in zip(FILES,linkage.extend_templates(templates(routes),anchors)):write_json(root/name,d)
    for p in ("sources","data","analysis","_gate","_history"):(root/p).mkdir()
    (root/"report.md").write_text("# 研究报告（待完成）\n\n"+"\n\n".join("## "+h+"\n待填" for h in HEADINGS)+"\n",encoding="utf-8")
    return {"status":"IN_PROGRESS","next":"G0","file":FILES[0],"task":str(root),"primary_routes":anchors,"linked_routes":routes}

def receipt_path(root,i):return root/"_gate"/f"G{i}.json"
def snapshot(root,i,c):
    ps={root/"manifest.json",*(root/f for f in FILES[:i+1]),*c.artifacts}
    return {p.relative_to(root).as_posix():digest(p) for p in sorted(ps)}
def inspect(root):
    m=manifest_for(root);c=Context(root,m);passed=0
    for i,name in enumerate(FILES):
        p=receipt_path(root,i)
        if not p.exists():
            require(not any(receipt_path(root,j).exists() for j in range(i+1,len(FILES))),"STALE: noncontiguous receipts; rewind")
            break
        rec=read_json(p)
        require(rec.get("version")==c.version and rec.get("stage")==i and rec.get("status")=="PASS","STALE: malformed receipt; rewind")
        require(rec.get("files",{}).get("manifest.json")==digest(root/"manifest.json"),"STALE: manifest changed; rewind or new task")
        for rel,h in rec.get("files",{}).items():
            require(digest(relfile(root,rel))==h,f"STALE: {rel} changed; rewind")
        validate_stage(i,read_json(root/name),c)
        require(rec.get("files")==snapshot(root,i,c),f"STALE: G{i} snapshot mismatch; rewind")
        if i:require(rec.get("prior_receipt")==digest(receipt_path(root,i-1)),"STALE: receipt chain mismatch")
        passed+=1
    return c,passed

def completion(root,c):
    return {"version":c.version,"task":root.name,"status":c.conclusion(),"material_gaps":c.material_gaps(),
            "unresolved_review":c.unresolved_review,"unknown_or_low_confidence":c.unknown,
            "report_sha256":digest(root/"report.md"),"last_receipt_sha256":digest(receipt_path(root,7)),
            "verified_gates":8}
def status(root,check_next=True):
    c,p=inspect(root)
    if p==8:
        expected=completion(root,c)
        require(read_json(root/"completion.json")==expected,"STALE: completion record mismatch; rewind G7")
        return expected
    require(not (root/"completion.json").exists(),"STALE: premature completion record")
    result={"status":"IN_PROGRESS","passed":p,"next":f"G{p}","name":NAMES[p],"file":FILES[p]}
    if check_next:
        try:validate_stage(p,read_json(root/FILES[p]),c);result["ready"]=True
        except (GateError,KeyError,TypeError,AttributeError,OverflowError) as e:result["ready"]=False;result["blocker"]=str(e)
    return result
def advance(root):
    c,p=inspect(root)
    if p==8:return status(root)
    require(not (root/"completion.json").exists(),"STALE: premature completion record")
    validate_stage(p,read_json(root/FILES[p]),c)
    rec={"version":c.version,"stage":p,"status":"PASS","checked_at":now(),"prior_receipt":None if p==0 else digest(receipt_path(root,p-1)),"files":snapshot(root,p,c)}
    write_json(receipt_path(root,p),rec)
    if p==7:
        final=completion(root,c);write_json(root/"completion.json",final)
        return {"gate":"G7","gate_result":"PASS",**final}
    return {"gate":f"G{p}","gate_result":"PASS","status":"IN_PROGRESS","next":f"G{p+1}","file":FILES[p+1]}
def rewind(root,stage,reason):
    require(0<=stage<8,"stage must be 0..7");filled(reason,"rewind reason")
    manifest_for(root)
    dest=root/"_history"/(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")+f"-G{stage}")
    dest.mkdir(parents=True,exist_ok=False)
    for i in range(stage,8):
        if (root/FILES[i]).is_file():shutil.copy2(root/FILES[i],dest/FILES[i])
        p=receipt_path(root,i)
        if p.exists():shutil.copy2(p,dest/p.name);p.unlink()
    for f in ("report.md","completion.json"):
        if (root/f).is_file():shutil.copy2(root/f,dest/f)
    if (root/"completion.json").exists():(root/"completion.json").unlink()
    write_json(dest/"rewind.json",{"stage":stage,"reason":reason,"archived_at":now()})
    return {"status":"REWOUND","next":f"G{stage}","archive":str(dest)}

def main():
    if hasattr(sys.stdout,"reconfigure"):sys.stdout.reconfigure(encoding="utf-8")
    ap=argparse.ArgumentParser(description=__doc__)
    subs=ap.add_subparsers(dest="cmd",required=True)
    for name in ("init","status","advance","verify","rewind"):
        p=subs.add_parser(name);p.add_argument("id")
        if name=="init":p.add_argument("--routes",required=True)
        if name=="rewind":p.add_argument("stage",type=int);p.add_argument("--reason",required=True)
    args=ap.parse_args()
    try:
        require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,95}",args.id) is not None,"task id: letters/digits/_/- only")
        root=RESEARCH/args.id
        require(root.resolve().is_relative_to(RESEARCH.resolve()),"unsafe task directory")
        if args.cmd=="init": result=init(root,args.routes.split(","))
        elif args.cmd=="rewind":result=rewind(root,args.stage,args.reason)
        elif args.cmd=="advance":result=advance(root)
        else:result=status(root)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0 if args.cmd!="verify" or result["status"]=="COMPLETE" else 3
    except (GateError,OSError,KeyError,ValueError,TypeError,AttributeError,OverflowError) as e:
        error=str(e)
        print(json.dumps({"status":"STALE" if "STALE:" in error else "BLOCKED","error":error},ensure_ascii=False,indent=2))
        return 2
if __name__=="__main__":sys.exit(main())
