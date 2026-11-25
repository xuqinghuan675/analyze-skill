"""Synthetic V5 integration tests; no real market claims or live transactions."""
import tempfile
import unittest
from pathlib import Path
import research_gate as g
import research_linkage as l
from test_research_gate import fixture as v4_fixture, evidence, gap

def fixture(root):
    ds=v4_fixture(root)
    anchors=["company"]; routes=l.expand(anchors)
    g.write_json(root/"manifest.json",{"version":5,"id":root.name,"routes":routes,"primary_routes":anchors,"created_at":g.now()})
    templates=l.extend_templates(g.templates(routes),anchors)
    ds[0]["routes"]=routes;ds[0]["primary_routes"]=anchors
    ds[0]["route_scope"]=templates[0]["route_scope"]
    for row in ds[0]["route_scope"]:
        r=row["route"]
        row.update(entity=f"Fictional {r} entity",focus=f"Synthetic {r} economic mechanism",decision_impact=f"Test contribution of {r} to valuation")
    route_ref={"company":"E1","product":"E10","industry":"E11","policy":"E12","market":"E13","expectation":"E14"}
    for row in ds[1]["evidence"]+ds[4]["evidence"]:
        row["topics"]=list(g.topic_ids(["company"]))
    for i,r,v,u in [(10,"product",1.2,"ratio"),(11,"industry",.9,"ratio"),(12,"policy",.95,"ratio"),(13,"market",1000,"USDm"),(14,"expectation",1200,"USDm")]:
        row=evidence(i,f"Fictional {r} value {v}",v,u)
        row["topics"]=list(g.topic_ids([r]))
        ds[1]["evidence"].append(row)
    existing={x["topic"]:x for x in ds[1]["coverage"]}
    ds[1]["coverage"]=[]
    for row in templates[1]["coverage"]:
        r=l.route_of(row["topic"])
        ds[1]["coverage"].append(existing.get(row["topic"],dict(row,status="supported",refs=[route_ref[r]],finding=f"Synthetic {row['topic']} evidence")))
    ds[2]["metrics"][0]["route"]="company"
    for i,r in enumerate([x for x in routes if x!="company"],2):
        ds[2]["metrics"].append(dict(ds[2]["metrics"][0],id=f"M{i}",route=r,name=f"Fictional {r} metric",
            refs=[route_ref[r]],observation=f"Synthetic {r} observation",next_question=f"How does {r} enter the model?"))
    ds[4]["linkages"]=templates[4]["linkages"]
    for row in ds[4]["linkages"]:
        a,b,_,_=l.LINKS[row["id"]]
        row.update(status="hypothesis",driver=f"Fictional {a} driver",target_variable=f"Fictional {b} variable",
            mechanism=f"Conditional {a} to {b} effect",lag="Fictional one-year period",conditions="Synthetic scenario assumptions",
            falsifier="If the fictional driver has no effect, reject link",from_refs=[route_ref[a]],to_refs=[route_ref[b]])
    def calc(i,expr,unit,result,vals):
        ds[5]["calculations"].append({"id":f"C{i}","question_id":"Q1","expression":expr,"variables":{
           name:{"ref":ref,"value":value,"unit":u} for name,ref,value,u in vals},
           "expected":result,"unit":unit,"interpretation":"Synthetic model calculation only"})
    calc(4,"revenue * adoption","USDm",120,[("revenue","E1",100,"USDm"),("adoption","E10",1.2,"ratio")])
    calc(5,"expanded * pricing","USDm",108,[("expanded","C4",120,"USDm"),("pricing","E11",.9,"ratio")])
    calc(6,"revenue / price","ratio",.108,[("revenue","C5",108,"USDm"),("price","E13",1000,"USDm")])
    calc(7,"price / forecast","ratio",1000/1200,[("price","E13",1000,"USDm"),("forecast","E14",1200,"USDm")])
    calc(8,"forecast / price - 1","ratio",.2,[("forecast","E14",1200,"USDm"),("price","E13",1000,"USDm")])
    calc(9,"fundamentals / pricing","ratio",.108/(1000/1200),[("fundamentals","C6",.108,"ratio"),("pricing","C7",1000/1200,"ratio")])
    calc(10,"price_factor * policy_factor","ratio",.855,[("price_factor","E11",.9,"ratio"),("policy_factor","E12",.95,"ratio")])
    calc_ref={"company":"C1","product":"C4","industry":"C5","policy":"C10","market":"C6","expectation":"C7"}
    ds[5]["route_outputs"]=templates[5]["route_outputs"]
    for row in ds[5]["route_outputs"]:
        r=l.route_of(row["topic"])
        if row["required_kind"]=="quantitative":row.update(status="measured",refs=[calc_ref[r]],finding="Synthetic route-specific calculation")
        else:row.update(status="grounded",refs=[route_ref[r]],finding="Synthetic route-specific source")
    model_refs={"L1":["C4"],"L2":["C5"],"L3":["E12","E11"],"L4":["C6"],"L5":["C7"],"L6":["C8"]}
    ds[5]["linkage_models"]=templates[5]["linkage_models"]
    for row in ds[5]["linkage_models"]:
        k=row["link_id"];row.update(status="grounded" if k=="L3" else "measured",refs=model_refs[k],
           effect="Synthetic conditional change",parameter_or_constraint="Explicit synthetic model or policy constraint")
    ds[6]["integration_review"]=templates[6]["integration_review"]
    for row in ds[6]["integration_review"]:
        a,b,_,_=l.LINKS[row["link_id"]]
        row.update(counterexample="Fictional demand/price relation may reverse",actual_recheck="Read fixture inputs and recompute",
            refs=[route_ref[a],route_ref[b]],verdict="checked",response="Keep assumptions conditional")
    synrefs=["C9","C4","C5","C6","C7","C8","E12","E11"]
    ds[7]["synthesis"]=dict(templates[7]["synthesis"],refs=synrefs,integrated_result="Synthetic revenue yield adjusted by forecast price ratio",
        decision_trace="Product adoption and industry price affect revenue and market-relative metric",
        what_changes_it="Changed synthetic pricing or adoption",opportunity_cost="Compare a fictional passive baseline",
        risk_boundary="Synthetic no-trade example")
    ds[7]["answers"][0]["refs"]+=["C9"]
    p=root/"report.md";p.write_text(p.read_text(encoding="utf-8")+"\n## Synthetic integration\n"+ " ".join("["+x+"]" for x in list(l.LINKS)+synrefs)+"\n",encoding="utf-8")
    for n,d in zip(g.FILES,ds):g.write_json(root/n,d)
    return ds

class LinkageTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)/"fixture"
        self.ds=fixture(self.root)
    def tearDown(self):self.t.cleanup()
    def put(self,i):g.write_json(self.root/g.FILES[i],self.ds[i])
    def through(self,n):
        for i in range(n):self.assertEqual(g.advance(self.root)["gate"],f"G{i}")
    def blocked(self,n):
        self.through(n)
        with self.assertRaises(g.GateError):g.advance(self.root)
        self.assertFalse(g.receipt_path(self.root,n).exists())
    def test_init_expands_all_anchors(self):
        for r in l.ROUTES:
            root=Path(self.t.name)/r
            result=g.init(root,[r]);self.assertEqual(set(result["linked_routes"]),set(l.ROUTES))
            self.assertEqual(len(g.read_json(root/g.FILES[1])["coverage"]),31)
            self.assertEqual(len(g.read_json(root/g.FILES[5])["route_outputs"]),24)
    def test_integrated_complete(self):
        self.through(8);r=g.status(self.root);self.assertEqual(r["version"],5);self.assertEqual(r["status"],"COMPLETE")
    def test_stock_cannot_skip_product(self):
        for x in self.ds[0]["route_scope"]:
            if x["route"]=="product":x.update(depth="screened",exclusion="Not a real company or live investment")
        self.put(0);self.blocked(0)
    def test_missing_route_scope(self):
        self.ds[0]["route_scope"].pop();self.put(0);self.blocked(0)
    def test_mislabelled_evidence(self):
        for row in self.ds[1]["coverage"]:
            if row["topic"]=="product.user":row["refs"]=["E1"]
        self.put(1);self.blocked(1)
    def test_core_gap_material(self):
        self.ds[1]["gaps"].append(gap(1,topic="product.user",material=False))
        for row in self.ds[1]["coverage"]:
            if row["topic"]=="product.user":row.update(status="gap",refs=["G1"])
        self.put(1);self.blocked(1)
    def test_missing_route_metric(self):
        self.ds[2]["metrics"]=[m for m in self.ds[2]["metrics"] if m["route"]!="industry"]
        self.put(2);self.blocked(2)
    def test_missing_link(self):
        self.ds[4]["linkages"].pop();self.put(4);self.blocked(4)
    def test_wrong_endpoint_evidence(self):
        self.ds[4]["linkages"][0]["from_refs"]=["E1"];self.put(4);self.blocked(4)
    def test_reused_same_calc_does_not_link(self):
        self.ds[5]["linkage_models"][0]["refs"]=["C1"];self.put(5);self.blocked(5)
    def test_quantitative_link_not_prose(self):
        self.ds[5]["linkage_models"][0].update(status="grounded",refs=["E10","E1"]);self.put(5);self.blocked(5)
    def test_wrong_route_output_calculation(self):
        for row in self.ds[5]["route_outputs"]:
            if row["topic"]=="output.product.user_roi":row["refs"]=["C1"]
        self.put(5);self.blocked(5)
    def test_missing_integration_review(self):
        self.ds[6]["integration_review"].pop();self.put(6);self.blocked(6)
    def test_synthesis_missing_link_result(self):
        self.ds[7]["synthesis"]["refs"].remove("C8");self.put(7);self.blocked(7)
    def test_synthesis_without_integrated_answer(self):
        self.ds[7]["answers"][0]["refs"].remove("C9");self.put(7);self.blocked(7)
    def test_missing_integration_can_be_partial(self):
        self.ds[6]["gaps"].append(gap(1,topic="integration",material=True));self.put(6)
        self.ds[7]["answers"][0]["refs"].remove("C9")
        self.ds[7]["answers"][0]["refs"].append("G1")
        self.ds[7]["synthesis"]["refs"].append("G1");self.put(7)
        p=self.root/"report.md";p.write_text(p.read_text(encoding="utf-8")+"\n[G1] Synthetic gap.\n",encoding="utf-8")
        self.through(8);self.assertEqual(g.status(self.root)["status"],"PARTIAL")

if __name__=="__main__":unittest.main(verbosity=2)
