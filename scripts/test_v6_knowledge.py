import json
import unittest
from pathlib import Path
from source_plan import build_plan, load_registry, DOMAINS
from advanced_finance_math import *

class SourcePlanTests(unittest.TestCase):
    def test_registry(self):
        self.assertEqual(len(load_registry()), 55)
    def test_all_six(self):
        self.assertEqual(set(build_plan(["company"])["six_domain_questions"]), set(DOMAINS))
    def test_company_route(self):
        p = build_plan(["company"])
        self.assertIn("references/specialists/advanced/expectations-moat.md", p["manuals"])
        self.assertIn("references/specialists/advanced/management-capital-quality.md", p["manuals"])
    def test_crypto_route(self):
        p = build_plan(["market"], ["crypto"])
        self.assertIn("references/specialists/advanced/crypto-onchain-deep.md", p["manuals"])
        self.assertIn("references/specialists/advanced/empirical-research.md", p["manuals"])
    def test_unavailable_separate(self):
        p = build_plan(["policy"])
        self.assertIn("Y06", [e["id"] for e in p["unavailable_sources"]])
        self.assertNotIn("Y06", [e["id"] for b in p["source_candidates"].values() for e in b])
    def test_invalid_route_and_tag(self):
        with self.assertRaises(ValueError): build_plan(["invalid"])
        with self.assertRaises(ValueError): build_plan(["market"], ["invalid"])

class AdvancedFinanceTests(unittest.TestCase):
    def test_economic_profit(self):
        self.assertAlmostEqual(economic_profit(20, 100, .08), 12)
    def test_fx(self):
        self.assertAlmostEqual(fx_total_return(.10, -.05), .045)
    def test_debt(self):
        self.assertAlmostEqual(debt_ratio_next(1, .04, .02, .01), 1.04 / 1.02 - .01)
    def test_duration(self):
        self.assertAlmostEqual(duration_convexity_return(5, 40, .01), -.048)
    def test_credit(self):
        self.assertAlmostEqual(expected_credit_loss(.02, .5, 100), 1)
        with self.assertRaises(ValueError): expected_credit_loss(2,.5,100)
    def test_spread(self):
        self.assertAlmostEqual(spread_bps(99,101), 200)
        with self.assertRaises(ValueError): spread_bps(101,99)
    def test_execution_both_sides(self):
        self.assertAlmostEqual(implementation_shortfall("buy",100,[(101,2)],.5)["cost"], 2.5)
        self.assertAlmostEqual(implementation_shortfall("sell",100,[(99,2)],.5)["cost"], 2.5)
    def test_brier(self):
        self.assertAlmostEqual(brier_score([.8,.2],[1,0]), .04)
        with self.assertRaises(ValueError): brier_score([.8],[1,0])
    def test_capacity(self):
        self.assertAlmostEqual(effective_capacity(10,100,5,.8,.9),3600)
    def test_asml_historical(self):
        b = segment_bridge({"logic":13.2,"memory":8.6,"service":6.5},{"logic":16.1,"memory":8.4,"service":8.2})
        self.assertAlmostEqual(b["total_change"],4.4)
        self.assertAlmostEqual(b["change"]["service"],1.7)
        self.assertAlmostEqual(8.2/b["after_total"],.250764526,places=7)
    def test_svb_historical(self):
        self.assertEqual(91321-76169,15152)
        self.assertAlmostEqual((91321-76169)/16004,.9467633092)
        self.assertAlmostEqual(173109/189203-1,-.0850620761827,places=10)
