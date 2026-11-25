"""V5 integration gates layered on the eight-stage validator.
All six lenses are considered; core dependencies cannot be dropped.
The checks enforce structure/provenance, not the truth of a narrative.
"""
ROUTES=("industry","company","product","policy","market","expectation")
# Direction describes an analytical transmission, not an assertion of causation.
LINKS={
 "L1":("product","company","用户任务/支付/用量/单位成本 → 企业经营与现金流","quantitative"),
 "L2":("industry","company","行业供需/竞争/成本曲线 → 公司价格、份额与回报","quantitative"),
 "L3":("policy","industry","法律/监管/宏观约束 → 产能、需求、成本与竞争","grounded"),
 "L4":("company","market","企业盈利/现金/融资/权益 → 资产价值与市场供需","quantitative"),
 "L5":("market","expectation","成交价格/期限/仓位 → 隐含预期与共识比较","quantitative"),
 "L6":("expectation","market","新信息与事前预期差 → 价格、风险与兑现路径","quantitative"),
}
CORE={
 "company":{"company","product","industry","market","expectation"},
 "industry":{"industry","product","company","market"},
 "product":{"product","industry","company"},
 "policy":{"policy","industry","company","market"},
 "market":{"market","expectation","industry"},
 "expectation":{"expectation","market"},
}
def expand(anchors):
    return list(dict.fromkeys([*anchors,*ROUTES]))
def core(anchors):
    return set().union(*(CORE[x] for x in anchors))
def extend_templates(ds,anchors):
    ds[0]["primary_routes"]=list(anchors)
    ds[0]["route_scope"]=[{"route":r,"depth":"primary" if r in anchors else "linked",
          "entity":"","question_id":"Q1","focus":"","decision_impact":"","exclusion":""} for r in expand(anchors)]
    ds[2]["metrics"]=[dict(ds[2]["metrics"][0],id=f"M{i}",route=r) for i,r in enumerate(expand(anchors),1)]
    ds[4]["linkages"]=[{"id":k,"from_route":a,"to_route":b,"label":label,"question_id":"Q1",
        "status":"","driver":"","target_variable":"","mechanism":"","lag":"","conditions":"",
        "falsifier":"","from_refs":[],"to_refs":[],"gap_refs":[]} for k,(a,b,label,_) in LINKS.items()]
    ds[5]["linkage_models"]=[{"link_id":k,"status":"","refs":[],"effect":"","parameter_or_constraint":""} for k in LINKS]
    ds[6]["integration_review"]=[{"link_id":k,"counterexample":"","actual_recheck":"","refs":[],"verdict":"","response":""} for k in LINKS]
    ds[7]["synthesis"]={"question_id":"Q1","link_ids":list(LINKS),"refs":[],"integrated_result":"","decision_trace":"","what_changes_it":"","opportunity_cost":"","risk_boundary":""}
    return ds

def evidence_topics(row,gate,c):
    topics=gate.arr(row,"topics",row["id"])
    valid=set(c.topics)|set(gate.output_ids(c.routes))
    gate.require(topics and all(isinstance(t,str) and t in valid for t in topics),f"{row['id']}: valid route evidence topics required")
    gate.require(len(topics)==len(set(topics)),f"{row['id']}: duplicate evidence topics")
def route_of(topic):
    return topic.split(".")[1] if topic.startswith("output.") else topic.split(".")[0]
def ancestry(refs,c,seen=None):
    # Transitive inputs. A qualitative source in an assumption is traceable,
    # but is not magically a measured numeric input.
    if seen is None:seen=set()
    found=set()
    for ref in refs:
        if ref in seen:continue
        seen.add(ref)
        if ref in c.ev:found.add(ref)
        elif ref in c.calcs:
            found|=ancestry([v["ref"] for v in c.calcs[ref]["variables"].values()],c,seen)
        else:
            row=c.assumptions.get(ref) or c.metrics.get(ref) or c.hyp.get(ref) or c.follow.get(ref)
            if row:found|=ancestry(row.get("refs",[]),c,seen)
    return found
def sources_for(refs,route,c,primary=True):
    return {x for x in ancestry(refs,c) if (not primary or c.ev[x]["source_kind"]=="primary")
            and any(route_of(t)==route for t in c.ev[x].get("topics",[]))}
def check_stage(i,d,c,g):
    if c.version!=5:return
    req=g.require;fields=g.fields;arr=g.arr;refs=g.ref_list
    if i==0:
        req(d.get("primary_routes")==c.anchors,"G0: primary routes mismatch")
        required=core(c.anchors);seen=set();c.route_scope={}
        for row in arr(d,"route_scope","G0"):
            fields(row,["route","depth","entity","focus","decision_impact"],"route scope")
            r=row["route"];req(r in ROUTES and r not in seen,"G0: duplicate/unknown route scope")
            seen.add(r);c.q(row.get("question_id"))
            depth=row["depth"];req(depth in ("primary","linked","screened"),f"{r}: invalid depth")
            if r in c.anchors:req(depth=="primary",f"{r}: anchor must be primary")
            if r in required:req(depth!="screened",f"{r}: core dependency cannot be screened out")
            if depth=="screened":
                exclusion=g.filled(row.get("exclusion"),r+".exclusion")
                req(exclusion in d["exclusions"],f"{r}: screen exclusion must be in G0")
            c.route_scope[r]=row
        req(seen==set(ROUTES),"G0: all six route scopes required")
    if i in (1,4,5,6):
        for row in arr(d,"evidence",f"G{i}"):evidence_topics(row,g,c)
    if i==1:
        c.route_evidence={r:set() for r in ROUTES}
        for row in d["coverage"]:
            t=row["topic"];r=route_of(t);rr=row["refs"]
            if row["status"] in ("supported","screened"):
                es={x for x in rr if x in c.ev and c.ev[x]["source_kind"]=="primary" and t in c.ev[x]["topics"]}
                req(es,f"{t}: require primary evidence explicitly tagged with this topic")
                if row["status"]=="screened":req(c.route_scope[r]["depth"]=="screened",f"{t}: only a screened route may screen evidence")
                c.route_evidence[r]|=es
            elif row["status"]=="gap":
                if r in core(c.anchors):
                    req(any(x in c.gaps and c.gaps[x]["topic"]==t and c.gaps[x]["material"] for x in rr),f"{t}: core evidence gap must be material")
    if i==2:
        present=set()
        for row in d["metrics"]:
            r=row.get("route")
            req(r in ROUTES,f"{row['id']}: metric needs an explicit route")
            rr=row["refs"]
            req(sources_for(rr,r,c) or any(x in c.gaps and route_of(c.gaps[x]["topic"])==r for x in rr),f"{row['id']}: metric needs evidence or gap for its route")
            present.add(r)
        active={r for r,v in c.route_scope.items() if v["depth"]!="screened"}
        req(active<=present,f"G2: missing metric/knowledge cards for {sorted(active-present)}")
    if i==4:
        c.links={};seen=set()
        for row in arr(d,"linkages","G4"):
            k=row.get("id");req(k in LINKS and k not in seen,"G4: invalid/duplicate linkage")
            seen.add(k);a,b,_,_=LINKS[k]
            req((row.get("from_route"),row.get("to_route"))==(a,b),f"{k}: link endpoints differ")
            q=c.q(row.get("question_id"))
            fields(row,["status","driver","target_variable","mechanism","lag","conditions","falsifier"],k)
            status=row["status"];req(status in ("supported","hypothesis","gap","immaterial"),f"{k}: invalid link status")
            fr=refs(row.get("from_refs"),c.source_refs(),k+".from_refs",empty=status=="gap")
            tr=refs(row.get("to_refs"),c.source_refs(),k+".to_refs",empty=status=="gap")
            gaps=refs(row.get("gap_refs"),set(c.gaps),k+".gap_refs",empty=True)
            f=sources_for(fr,a,c);t=sources_for(tr,b,c)
            if status=="gap":
                req(any(c.gaps[x]["topic"]=="link."+k and c.gaps[x].get("question_id")==q and c.gaps[x]["material"] and x not in c.resolved for x in gaps),f"{k}: missing material linkage gap")
            else:
                req(f and t and len(f|t)>=2,f"{k}: two distinct endpoint primary evidence records required")
                if status=="immaterial":
                    req(c.route_scope[a]["depth"]=="screened" or c.route_scope[b]["depth"]=="screened",f"{k}: core active link cannot be immaterial")
            c.links[k]=row
        req(seen==set(LINKS),"G4: all six cross-route links required")
    if i==5:
        c.linkmodels={};seen=set()
        for row in d["route_outputs"]:
            r=route_of(row["topic"]);status=row["status"]
            if status=="out_of_scope":
                # Full company research may exclude a genuinely irrelevant item
                # but not its core financial/product/industry work.
                req(c.route_scope[r]["depth"]=="screened" or row["topic"] not in {
                   "output.company.financial_bridge","output.company.valuation","output.product.tasks",
                   "output.product.user_roi","output.industry.supply_demand","output.industry.profit_pool"},f"{row['topic']}: protected output requires evidence/calculation or gap")
            elif status=="gap" and r in core(c.anchors):
                req(any(x in c.gaps and c.gaps[x]["topic"]==row["topic"] and c.gaps[x]["material"] for x in row["refs"]),f"{row['topic']}: core output gap must be material")
            elif status in ("measured","grounded"):
                req(sources_for(row["refs"],r,c),f"{row['topic']}: output must trace to its own route's primary evidence")
        for m in arr(d,"linkage_models","G5"):
            k=m.get("link_id");req(k in c.links and k not in seen,"G5: invalid/duplicate link model")
            seen.add(k);a,b,_,kind=LINKS[k];l=c.links[k]
            fields(m,["status","effect","parameter_or_constraint"],k+".model")
            rr=refs(m.get("refs"),c.refs(),k+".model.refs")
            status=m["status"]
            if status=="measured":
                req(l["status"] in ("supported","hypothesis","gap"),f"{k}: inactive link cannot be measured")
                cs=[x for x in rr if x in c.calcs and c.calcs[x]["question_id"]==l["question_id"]]
                f=set(l["from_refs"]);t=set(l["to_refs"])
                req(any((sources_for([x],a,c)&f) and (sources_for([x],b,c)&t) and len((sources_for([x],a,c)&f)|(sources_for([x],b,c)&t))>=2 for x in cs),f"{k}: calculation must consume BOTH named endpoint evidence records")
                if l["status"]=="gap":req(all(x in c.resolved for x in l["gap_refs"]),f"{k}: unresolved link gap")
            elif status=="grounded":
                req(kind=="grounded" and l["status"] in ("supported","hypothesis"),f"{k}: quantitative link needs calculation or gap")
                req(sources_for(rr,a,c)&set(l["from_refs"]) and sources_for(rr,b,c)&set(l["to_refs"]),f"{k}: grounded link must use both endpoints")
            elif status=="gap":
                req(any(x in c.gaps and c.gaps[x]["topic"]=="link."+k and c.gaps[x]["material"] and c.gaps[x].get("question_id")==l["question_id"] and x not in c.resolved for x in rr),f"{k}: missing model needs matching material gap")
            elif status=="immaterial":
                req(l["status"]=="immaterial" and (sources_for(rr,a,c)&set(l["from_refs"])) and (sources_for(rr,b,c)&set(l["to_refs"])),f"{k}: immaterial requires screened route and both evidence endpoints")
            else:raise g.GateError(f"{k}: invalid linkage model status")
            c.linkmodels[k]=m
        req(seen==set(LINKS),"G5: missing cross-route link models")
    if i==6:
        seen=set()
        for row in arr(d,"integration_review","G6"):
            k=row.get("link_id");req(k in c.linkmodels and k not in seen,"G6: invalid/duplicate integration review")
            seen.add(k)
            fields(row,["counterexample","actual_recheck","verdict","response"],k+".review")
            rr=refs(row.get("refs"),c.refs(),k+".review.refs")
            req(row["verdict"] in ("checked","unresolved"),f"{k}: integration review verdict")
            if row["verdict"]=="unresolved":c.unresolved_review=True
            else:
                a,b,_,_=LINKS[k];req(sources_for(rr,a,c) and sources_for(rr,b,c),f"{k}: review needs evidence from both endpoints")
        req(seen==set(LINKS),"G6: every cross-route link must be challenged")
    if i==7:
        s=d.get("synthesis");fields(s,["integrated_result","decision_trace","what_changes_it","opportunity_cost","risk_boundary"],"synthesis")
        q=c.q(s.get("question_id"));req(q in c.critical(),"synthesis needs critical question")
        ids=arr(s,"link_ids","synthesis");req(len(ids)==len(LINKS) and set(ids)==set(LINKS),"synthesis must account for all six links")
        rr=refs(s.get("refs"),c.refs(),"synthesis.refs")
        for k,m in c.linkmodels.items():
            req(set(rr)&set(m["refs"]),f"G7: synthesis must explicitly include the result/constraint of {k}")
        answer=next(x for x in d["answers"] if x["question_id"]==q)
        shared=set(rr)&set(answer["refs"])
        required={"company","product","industry"} if "company" in c.anchors else set(c.anchors)
        active={r for r,v in c.route_scope.items() if v["depth"]!="screened"}
        usable=set().union(*(set(m["refs"]) for m in c.linkmodels.values() if m["status"]=="measured"))
        def sufficient(x):
            # Include an actual cross-domain model in the answer's dependency DAG.
            # A reference list of unrelated numbers is not integration.
            if x not in c.calcs or c.calcs[x]["question_id"]!=q:return False
            route_set={r for r in active if sources_for([x],r,c)}
            todo=[x];visited=set()
            while todo:
                z=todo.pop()
                if z in visited:continue
                visited.add(z)
                if z in c.calcs:todo.extend(v["ref"] for v in c.calcs[z]["variables"].values())
            return required<=route_set and len(route_set)>=min(3,len(active)) and bool(visited&usable)
        if not any(sufficient(x) for x in shared):
            req(any(x in c.gaps and c.gaps[x]["topic"]=="integration" and c.gaps[x]["material"] and c.gaps[x].get("question_id")==q and x not in c.resolved for x in shared),"G7: integrated calculation must enter main answer, or explicit material integration gap")
        report=(c.root/"report.md").read_text(encoding="utf-8-sig")
        req(all(f"[{k}]" in report for k in LINKS),"G7: report must expose all six linkage IDs")
        req(all(f"[{x}]" in report for x in rr),"G7: report missing synthesis references")
