"""V6 transparent finance formulas; all rates are decimal, not percentages."""
import math

def _finite(*xs):
    if not all(math.isfinite(x) for x in xs):
        raise ValueError("finite inputs required")

def economic_profit(nopat, capital, wacc):
    _finite(nopat, capital, wacc)
    if capital <= 0 or wacc < 0:
        raise ValueError("positive capital and nonnegative WACC required")
    return nopat - capital * wacc

def fx_total_return(asset_return, fx_return):
    _finite(asset_return, fx_return)
    if asset_return < -1 or fx_return <= -1:
        raise ValueError("invalid simple return")
    return (1 + asset_return) * (1 + fx_return) - 1

def debt_ratio_next(debt_ratio, interest_rate, nominal_growth, primary_surplus_ratio, other_adjustments=0):
    _finite(debt_ratio, interest_rate, nominal_growth, primary_surplus_ratio, other_adjustments)
    if debt_ratio < 0 or interest_rate < -1 or nominal_growth <= -1:
        raise ValueError("invalid debt or rate")
    return debt_ratio * (1 + interest_rate) / (1 + nominal_growth) - primary_surplus_ratio + other_adjustments

def duration_convexity_return(modified_duration, convexity, yield_change):
    _finite(modified_duration, convexity, yield_change)
    return -modified_duration * yield_change + 0.5 * convexity * yield_change ** 2

def expected_credit_loss(pd, lgd, exposure):
    _finite(pd, lgd, exposure)
    if not 0 <= pd <= 1 or not 0 <= lgd <= 1 or exposure < 0:
        raise ValueError("PD and LGD in [0,1], nonnegative exposure")
    return pd * lgd * exposure

def spread_bps(bid, ask):
    _finite(bid, ask)
    if not 0 < bid <= ask:
        raise ValueError("positive uncrossed quote required")
    return (ask - bid) / ((ask + bid) / 2) * 10000

def implementation_shortfall(side, decision_price, executions, fees=0):
    """Executed quantity only; add unfilled quantity opportunity cost separately."""
    if side not in ("buy", "sell") or decision_price <= 0:
        raise ValueError("invalid side or price")
    _finite(decision_price, fees)
    sign = 1 if side == "buy" else -1
    cost, quantity = fees, 0
    for price, size in executions:
        _finite(price, size)
        if price <= 0 or size <= 0:
            raise ValueError("positive prices and sizes required")
        cost += sign * (price - decision_price) * size
        quantity += size
    if not quantity:
        raise ValueError("no executed quantity")
    return {"cost": cost, "bps": cost / (quantity * decision_price) * 10000}

def brier_score(probabilities, outcomes):
    ps, ys = list(probabilities), list(outcomes)
    if not ps or len(ps) != len(ys):
        raise ValueError("nonempty paired samples required")
    for p, y in zip(ps, ys):
        _finite(p, y)
        if not 0 <= p <= 1 or y not in (0, 1):
            raise ValueError("invalid probability or outcome")
    return sum((p-y)**2 for p,y in zip(ps,ys)) / len(ps)

def effective_capacity(devices, hours, rate, availability, first_pass_yield):
    _finite(devices, hours, rate, availability, first_pass_yield)
    if min(devices, hours, rate) < 0 or not 0 <= availability <= 1 or not 0 <= first_pass_yield <= 1:
        raise ValueError("invalid capacity inputs")
    return devices * hours * rate * availability * first_pass_yield

def segment_bridge(before, after):
    if set(before) != set(after) or not before:
        raise ValueError("matching nonempty segments required")
    _finite(*before.values(), *after.values())
    change = {k: after[k] - before[k] for k in before}
    return {"before_total": sum(before.values()), "after_total": sum(after.values()),
            "change": change, "total_change": sum(change.values())}
