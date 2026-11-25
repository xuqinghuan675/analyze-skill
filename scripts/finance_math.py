"""Deterministic research helpers; all monetary inputs use one consistent unit.
Not a data source or a trading engine. Percentages are decimal fractions.
"""
import math
from collections.abc import Sequence

def cagr(start:float,end:float,years:float)->float:
    if start<=0 or end<=0 or years<=0: raise ValueError("CAGR needs positive values and years")
    return (end/start)**(1/years)-1

def fcff(ebit:float,tax_rate:float,da:float,capex:float,delta_nwc:float)->float:
    if not 0<=tax_rate<=1:raise ValueError("Invalid tax rate")
    return ebit*(1-tax_rate)+da-capex-delta_nwc

def wacc(equity:float,debt:float,ke:float,kd:float,tax_rate:float)->float:
    if equity<0 or debt<0 or equity+debt<=0 or not 0<=tax_rate<=1:raise ValueError("Invalid capital structure")
    return (equity*ke+debt*kd*(1-tax_rate))/(equity+debt)

def dcf(cash_flows:Sequence[float],discount_rate:float,terminal_growth:float,*,terminal_fcf:float|None=None,nonoperating_assets:float=0,debt:float=0,other_claims:float=0,shares:float|None=None)->dict:
    """End-of-year discounting. terminal_fcf is normalized year N cash flow before growth."""
    if not cash_flows or discount_rate<=terminal_growth or discount_rate<=-1 or terminal_growth<=-1: raise ValueError("Need cash flows and WACC > terminal growth")
    if shares is not None and shares<=0: raise ValueError("Shares must be positive")
    base=cash_flows[-1] if terminal_fcf is None else terminal_fcf
    if base<=0:raise ValueError("Normalize stable-period FCF before applying perpetuity")
    pv_forecast=sum(f/(1+discount_rate)**i for i,f in enumerate(cash_flows,1))
    tv=base*(1+terminal_growth)/(discount_rate-terminal_growth)
    pv_tv=tv/(1+discount_rate)**len(cash_flows)
    ev=pv_forecast+pv_tv
    eq=ev+nonoperating_assets-debt-other_claims
    return {"pv_forecast":pv_forecast,"terminal_value":tv,"pv_terminal":pv_tv,"enterprise_value":ev,"equity_value":eq,"per_share":None if shares is None else eq/shares,"terminal_fraction":pv_tv/ev if ev>0 else None}

def required_future_revenue(current_price:float,shares_at_exit:float,years:float,target_cagr:float,exit_pe:float,net_margin:float)->dict:
    """Reverse exit-multiple model, ignoring distributions. Accounts for future dilution."""
    if min(current_price,shares_at_exit,years,exit_pe,net_margin)<=0 or target_cagr<=-1:raise ValueError("Invalid valuation assumptions")
    target_price=current_price*(1+target_cagr)**years
    target_equity=target_price*shares_at_exit
    profit=target_equity/exit_pe
    return {"required_share_price":target_price,"required_equity_value":target_equity,"required_net_profit":profit,"required_revenue":profit/net_margin}

def dcf_sensitivity(cash_flows,discount_rates,terminal_growths,**kwargs):
    return [{"discount_rate":r,"terminal_growth":g,"valuation":dcf(cash_flows,r,g,**kwargs) if r>g else None} for r in discount_rates for g in terminal_growths]

def expected_return(scenarios:Sequence[tuple[float,float]])->float:
    """(probability, net return) of mutually exclusive and exhaustive scenarios."""
    if not scenarios or any(p<0 or p>1 for p,_ in scenarios) or not math.isclose(sum(p for p,_ in scenarios),1,rel_tol=0,abs_tol=1e-9):raise ValueError("Scenario probabilities must sum to one")
    return sum(p*r for p,r in scenarios)

def statement_checks(assets,liabilities,equity,opening_cash,ocf,icf,financing_cf,closing_cash,fx_other=0,tolerance=1e-6):
    balance_error=assets-liabilities-equity
    cash_error=opening_cash+ocf+icf+financing_cf+fx_other-closing_cash
    return {"balance_error":balance_error,"cash_error":cash_error,"pass":abs(balance_error)<=tolerance and abs(cash_error)<=tolerance}

def bond_price_change(modified_duration:float,convexity:float,delta_yield:float)->float:
    return -modified_duration*delta_yield+0.5*convexity*delta_yield**2
