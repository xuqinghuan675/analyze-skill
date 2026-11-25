"""All fixtures are deliberately fictional and run in temporary directories."""
import tempfile
import unittest
from pathlib import Path
import research_gate as g

def evidence(i,fact,value=None,unit="text",kind="primary",artifact=None):
    row={"id":f"E{i}","source_kind":kind,"publisher":"SYNTHETIC TEST ONLY",
         "url":f"https://example.invalid/fictional/{i}","locator":f"table {i}, row 1",
         "available_at":"2025-12-31T12:00:00+00:00","retrieved_at":"2026-01-02T12:00:00+00:00",
         "period":"fictional FY2025","fact":fact,"unit":unit,"independence_group":f"fixture{i}"}
    if value is not None:row["value"]=value
    if artifact:row.update(artifact=artifact,url="local:"+artifact)
    return row

def gap(i,topic="company.cash",material=True):
    return {"id":f"G{i}","topic":topic,"question_id":"Q1","material":material,
            "reason":"Synthetic missing record","attempts":[{"query":"synthetic source table and alternate source","result":"fictional data absent"}]}

def fixture(root):
    # Frozen V4 fixture: exercise backward compatibility through current validator.
    root.mkdir(parents=True)
    g.write_json(root/"manifest.json",{"version":4,"id":root.name,"routes":["company"],"created_at":g.now()})
    for p in ("sources","data","analysis","_gate","_history"):(root/p).mkdir()
    ds=g.templates(["company"])
    ds[0].update(object="Fictional Example Company",question="How does profit respond to pricing?",as_of="2026-01-01T00:00:00+00:00",
                 horizon="FY2026",decision="Assess economic driver, no trade",scope="Illustrative numerical case only",exclusions="Not a real company or live investment")
    ds[0]["questions"]=[{"id":"Q1","question":"How much operating profit under different margins?","critical":True,"success":"Explain margins and calculate scenarios"}]
    ds[1]["evidence"]=[evidence(1,"Fictional revenue: 100",100,"USDm"),evidence(2,"Fictional cost: 60",60,"USDm"),
      evidence(3,"Fictional disclosure and legal entity"),evidence(4,"Fictional cash and debt"),evidence(5,"Fictional contract terms"),evidence(6,"Fictional share price and shares")]
    # Each route topic gets an explicit entry.
    for row,n in zip(ds[1]["coverage"],[3,1,2,4,5,6]):
        row.update(status="supported",refs=[f"E{n}"],finding=f"Fictional coverage for {row['topic']}")
    ds[2]["metrics"]=[{"id":"M1","question_id":"Q1","name":"Contribution margin","definition":"Revenue less variable costs, divided by revenue",
      "unit":"ratio","rule":"(revenue-cost)/revenue","observation":"Illustrative historical gross contribution 0.4","benchmark":"Compare alternative cost structures",
      "interpretation":"Operating margin may rise with better pricing","alternative":"Higher input prices could offset gains",
      "distinguishing_evidence":"Read contract and cost schedule","next_question":"Can pricing be adjusted in the contract?","refs":["E1","E2"]}]
    ds[3]["hypotheses"]=[{"id":"H1","question_id":"Q1","claim":"Margins depend on pass-through","mechanism":"Contract pricing affects retained incremental revenue",
      "competing_explanation":"Cost growth could absorb revenue growth","falsifier":"A fixed-price contract with rising input costs would weaken the claim",
      "test_plan":"Read contract pricing and expense allocation","refs":["M1","E2"]}]
    (root/"sources"/"contract.txt").write_text("SYNTHETIC FIXTURE ONLY: fictional adjustable prices.",encoding="utf-8")
    ds[4]["evidence"]=[evidence(7,"Fictional adjustable price provision",artifact="sources/contract.txt"),
                       evidence(8,"Fictional variable cost schedule")]
    ds[4]["followups"]=[
      {"id":"F1","question_id":"Q1","hypothesis_id":"H1","parent_id":None,"question":"Can pricing be adjusted in the contract?",
       "investigation":"Read fictional contract paragraph","finding":"Fictional annual adjustment","refs":["E7"],"next_question":"How much cost remains variable?"},
      {"id":"F2","question_id":"Q1","hypothesis_id":"H1","parent_id":"F1","question":"How much cost remains variable?",
       "investigation":"Read fictional cost schedule","finding":"Margin depends on variable cost","refs":["E8","E2"],"next_question":"What margin range is plausible?"}]
    ds[4]["mechanisms"]=[{"question_id":"Q1","hypothesis_id":"H1","edges":[{"from":"adjustable price","to":"operating margin","direction":"positive if cost unchanged",
      "lag":"one year","condition":"customer accepts price changes","status":"hypothesis","refs":["E7","E8"]}],"implication":"Model conditional margins, not guaranteed profit"}]
    ds[5]["assumptions"]=[{"id":f"A{i}","name":kind+" assumed margin","unit":"ratio","basis":"Fictional scenario parameter informed by cost schedule","sensitivity":"Profit changes proportionally","value":v,"refs":["E8","H1"]} for i,(kind,v) in enumerate([("base",.2),("upside",.3),("downside",.1)],1)]
    ds[5]["calculations"]=[{"id":f"C{i}","question_id":"Q1","expression":"revenue * margin","variables":{"revenue":{"value":100,"unit":"USDm","ref":"E1"},
      "margin":{"value":v,"unit":"ratio","ref":f"A{i}"}},"expected":round(100*v,8),"unit":"USDm","interpretation":"Fictional forecast operating profit"} for i,v in enumerate([.2,.3,.1],1)]
    for row in ds[5]["route_outputs"]:
        if row["required_kind"]=="quantitative":row.update(status="measured",finding="Synthetic calculation fixture",refs=["C1"])
        else:row.update(status="grounded",finding="Synthetic governance fixture",refs=["E5"])
    ds[5]["model_coverage"]=[{"question_id":"Q1","refs":["C1","C2","C3"],"interpretation":"Scenario calculations"}]
    ds[5]["scenarios"]=[{"question_id":"Q1","kind":kind,"metric":"operating profit","unit":"USDm","horizon":"FY2026","driver":f"assumed margin {v}","outcome":f"Fictional operating profit {100*v}","value":round(100*v,8),"refs":[f"C{i}",f"A{i}"]} for i,(kind,v) in enumerate([("base",.2),("upside",.3),("downside",.1)],1)]
    ds[6]["countercases"]=[{"question_id":"Q1","strongest_case":"Costs may rise faster than prices","search_or_recheck":"Compare fictional contract adjustment and cost schedule",
        "finding":"Pass-through is conditional","refs":["E7","E8","C3"],"verdict":"weakened","response":"Keep downside and state assumption"}]
    ds[6]["checks"]=[{"name":k,"status":"pass","finding":f"Synthetic verification of {k} using explicit fixture","refs":["E1","E7","C1"]} for k in g.CHECKS]
    ds[7]["answers"]=[{"question_id":"Q1","kind":"derived","conclusion":"Fictional base-case operating profit 20 USDm",
        "explanation":"Revenue 100 times assumed margin 0.2","refs":["E1","A1","C1","H1","F2"],"confidence":"medium",
        "invalidation":"If margin differs from scenario, recompute","next_observation":"Next contract repricing"}]
    ds[7].update(limitations="Synthetic example only, no actual market evidence",decision="Conditional illustrative assessment",next_step="Check the next fictional filing")
    for f,d in zip(g.FILES,ds):g.write_json(root/f,d)
    (root/"report.md").write_text("# SYNTHETIC TEST, NOT RESEARCH\n\n"+
      "\n\n".join("## "+h+"\n"+v for h,v in zip(g.HEADINGS,[
       "[Q1] Conditional illustrative result [C1].","Revenue [E1], assumption [A1], cost investigation [F2].",
       "Mechanism [H1], formula calculation [C1].","Base, upside, downside [C1] [C2] [C3].",
       "Synthetic contract and cost schedule [E7] [E8].","Recompute if margin or contract changes."]))+"\n",encoding="utf-8")
    return ds

class GateTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)/"fixture"
        self.ds=fixture(self.root)
    def tearDown(self): self.t.cleanup()
    def put(self,i):g.write_json(self.root/g.FILES[i],self.ds[i])
    def advance_to(self,n):
        for i in range(n):
            r=g.advance(self.root);self.assertEqual(r["gate"],f"G{i}")
    def blocked(self,n):
        self.advance_to(n)
        with self.assertRaises(g.GateError):g.advance(self.root)
        self.assertFalse(g.receipt_path(self.root,n).exists())
    def test_complete(self):
        self.advance_to(8)
        self.assertEqual(g.status(self.root)["status"],"COMPLETE")
        self.assertEqual(g.status(self.root)["verified_gates"],8)
    def test_blank_template_blocked(self):
        other=Path(self.t.name)/"empty";g.init(other,["market"])
        self.assertFalse(g.status(other)["ready"])
        with self.assertRaises(g.GateError):g.advance(other)
    def test_cannot_skip(self):
        self.assertEqual(g.advance(self.root)["gate"],"G0")
        self.assertEqual(g.status(self.root)["next"],"G1")
    def test_duplicate_init(self):
        with self.assertRaises(g.GateError):g.init(self.root,["market"])
    def test_missing_route_coverage(self):
        self.ds[1]["coverage"].pop();self.put(1);self.blocked(1)
    def test_secondary_only_not_supported(self):
        self.ds[1]["evidence"][0]["source_kind"]="secondary";self.put(1);self.blocked(1)
    def test_fake_reference(self):
        self.ds[2]["metrics"][0]["refs"]=["E999"];self.put(2);self.blocked(2)
    def test_future_data(self):
        self.ds[1]["evidence"][0]["available_at"]="2026-01-02T00:00:00+00:00";self.put(1);self.blocked(1)
    def test_naive_timestamp(self):
        self.ds[0]["as_of"]="2026-01-01T00:00:00";self.put(0);self.blocked(0)
    def test_identical_explanations(self):
        h=self.ds[3]["hypotheses"][0];h["competing_explanation"]=h["claim"];self.put(3);self.blocked(3)
    def test_broken_followup_chain(self):
        self.ds[4]["followups"][1]["question"]="Unrelated question";self.put(4);self.blocked(4)
    def test_missing_second_layer(self):
        self.ds[4]["followups"].pop();self.put(4);self.blocked(4)
    def test_no_new_investigation(self):
        self.ds[4]["followups"][1]["refs"]=["E7"];self.put(4);self.blocked(4)
    def test_wrong_arithmetic(self):
        self.ds[5]["calculations"][0]["expected"]=999;self.put(5);self.blocked(5)
    def test_unverified_input(self):
        self.ds[5]["calculations"][0]["variables"]["revenue"]["value"]=200;self.put(5);self.blocked(5)
    def test_wrong_unit(self):
        self.ds[5]["calculations"][0]["variables"]["revenue"]["unit"]="USDk";self.put(5);self.blocked(5)
    def test_formula_security(self):
        with self.assertRaises(g.GateError):g.arithmetic("__import__('os').system('echo hi')",{})
    def test_missing_route_output(self):
        self.ds[5]["route_outputs"].pop();self.put(5);self.blocked(5)
    def test_quantitative_route_output_needs_math(self):
        self.ds[5]["route_outputs"][0].update(status="grounded",refs=["E1"]);self.put(5);self.blocked(5)
    def test_route_exclusion_must_be_declared(self):
        self.ds[5]["route_outputs"][0].update(status="out_of_scope",exclusion="Not declared");self.put(5);self.blocked(5)
    def test_missing_scenario(self):
        self.ds[5]["scenarios"].pop();self.put(5);self.blocked(5)
    def test_fake_scenario_value(self):
        self.ds[5]["scenarios"][0]["value"]=999;self.put(5);self.blocked(5)
    def test_review_missing_check(self):
        self.ds[6]["checks"].pop();self.put(6);self.blocked(6)
    def test_report_missing_citation(self):
        p=self.root/"report.md";p.write_text(p.read_text(encoding="utf-8").replace("[F2]",""),encoding="utf-8");self.blocked(7)
    def test_material_gap_partial(self):
        self.ds[1]["gaps"]=[gap(1)]
        for row in self.ds[1]["coverage"]:
            if row["topic"]=="company.cash":row.update(status="gap",refs=["G1"],finding="Fictional cash record not available")
        self.put(1);self.advance_to(8)
        r=g.status(self.root);self.assertEqual(r["status"],"PARTIAL");self.assertEqual(r["material_gaps"],["G1"])
    def test_resolved_gap_complete(self):
        self.ds[1]["gaps"]=[gap(1)]
        for row in self.ds[1]["coverage"]:
            if row["topic"]=="company.cash":row.update(status="gap",refs=["G1"],finding="Fictional cash initially missing")
        self.put(1)
        self.ds[4]["evidence"].append(evidence(9,"Fictional cash record found in alternate report"))
        self.ds[4]["resolved_gaps"]=[{"gap_id":"G1","refs":["E9"],"explanation":"Alternate report supplies missing record"}]
        self.put(4);self.advance_to(8);self.assertEqual(g.status(self.root)["status"],"COMPLETE")
    def test_unresolved_countercase_partial(self):
        self.ds[6]["countercases"][0]["verdict"]="unresolved";self.put(6);self.advance_to(8)
        self.assertEqual(g.status(self.root)["status"],"PARTIAL")
    def test_changed_prior_stage_stale(self):
        self.advance_to(2);self.ds[1]["evidence"][0]["fact"]="Changed";self.put(1)
        with self.assertRaisesRegex(g.GateError,"STALE"):g.status(self.root)
    def test_changed_raw_artifact_stale(self):
        self.advance_to(5);(self.root/"sources"/"contract.txt").write_text("changed",encoding="utf-8")
        with self.assertRaisesRegex(g.GateError,"STALE"):g.advance(self.root)
    def test_changed_report_stale(self):
        self.advance_to(8);p=self.root/"report.md";p.write_text(p.read_text(encoding="utf-8")+"\nchanged",encoding="utf-8")
        with self.assertRaisesRegex(g.GateError,"STALE"):g.status(self.root)
    def test_premature_completion(self):
        g.write_json(self.root/"completion.json",{"status":"COMPLETE"})
        with self.assertRaisesRegex(g.GateError,"STALE"):g.advance(self.root)
    def test_forged_completion(self):
        self.advance_to(8);g.write_json(self.root/"completion.json",{"status":"COMPLETE"})
        with self.assertRaisesRegex(g.GateError,"STALE"):g.status(self.root)
    def test_rewind_archive(self):
        self.advance_to(8);r=g.rewind(self.root,5,"Synthetic changed assumption")
        self.assertTrue((Path(r["archive"])/"completion.json").is_file())
        self.assertFalse((self.root/"completion.json").exists())
        self.assertEqual(g.status(self.root)["next"],"G5")
        self.advance_to_from(5,8)
        self.assertEqual(g.status(self.root)["status"],"COMPLETE")
    def advance_to_from(self,start,end):
        for i in range(start,end):self.assertEqual(g.advance(self.root)["gate"],f"G{i}")

if __name__=="__main__":unittest.main(verbosity=2)
