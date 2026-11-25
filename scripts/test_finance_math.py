import math, unittest
from finance_math import *

class FinanceMathTests(unittest.TestCase):
    def test_cagr(self):
        self.assertAlmostEqual(cagr(100,121,2),.1)
    def test_fcff(self):
        self.assertEqual(fcff(100,.25,20,30,5),60)
    def test_wacc(self):
        self.assertAlmostEqual(wacc(80,20,.10,.05,.25),.0875)
    def test_perpetuity(self):
        v=dcf([10,10,10],.1,0)
        self.assertAlmostEqual(v['enterprise_value'],100)
    def test_ev_bridge(self):
        self.assertAlmostEqual(dcf([10],.1,0,nonoperating_assets=20,debt=30,other_claims=5,shares=10)['per_share'],8.5)
    def test_reverse_with_dilution(self):
        v=required_future_revenue(10,12,2,.1,20,.25)
        self.assertAlmostEqual(v['required_revenue'],29.04)
    def test_sensitivity(self):
        v=dcf_sensitivity([10,10],[.08,.1],[0,.02])
        self.assertEqual(len(v),4)
        self.assertGreater(v[0]['valuation']['enterprise_value'],v[2]['valuation']['enterprise_value'])
    def test_invalid_terminal(self):
        with self.assertRaises(ValueError): dcf([10],.1,.1)
    def test_expected(self):
        self.assertAlmostEqual(expected_return([(.5,.2),(.5,-.1)]),.05)
        with self.assertRaises(ValueError):expected_return([(.4,.3)])
    def test_statements(self):
        self.assertTrue(statement_checks(100,60,40,10,20,-15,2,17)['pass'])
        self.assertFalse(statement_checks(100,60,41,10,20,-15,2,17)['pass'])
    def test_duration(self):
        self.assertAlmostEqual(bond_price_change(5,0,.01),-.05)
if __name__=="__main__":unittest.main()
