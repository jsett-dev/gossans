#!/usr/bin/env python3
"""Arps decline fitting, done the way /findings/decline-fitted-to-field-rate/
says it should be.

No dependencies. A coarse-to-fine grid search over the two nonlinear
parameters, with the initial rate solved analytically at each node, is fast
enough for a few thousand months and is a great deal easier to audit than a
solver whose failure modes you cannot see.

Time is in years throughout. Rate is whatever unit the input is in, per day.

    python tools/decline.py            # runs the self-test

The self-test is the point. It fits a known curve and recovers its parameters,
then reproduces the field-rate failure the site describes, so the claim on the
website is checkable rather than asserted.
"""

import csv
import io
import math
from collections import defaultdict

# Below this the hyperbolic is numerically indistinguishable from exponential.
B_EXPONENTIAL = 1e-6


# --------------------------------------------------------------------------
# The Arps relations
# --------------------------------------------------------------------------

def rate(t, qi, Di, b):
    """Instantaneous rate at time t years, from initial rate qi."""
    if b < B_EXPONENTIAL:
        return qi * math.exp(-Di * t)
    return qi * (1.0 + b * Di * t) ** (-1.0 / b)


def cumulative(qi, Di, b, q):
    """Volume produced between rate qi and rate q, in rate-units times years."""
    if Di <= 0:
        return float("inf")
    if b < B_EXPONENTIAL:
        return (qi - q) / Di
    if abs(b - 1.0) < B_EXPONENTIAL:
        return qi / Di * math.log(qi / q)
    return qi / ((1.0 - b) * Di) * (1.0 - (q / qi) ** (1.0 - b))


def secant_from_nominal(Di, b):
    """Nominal decline to secant effective annual decline.

    Secant effective is the plain observed drop over twelve months, and it is
    what type curves and investor decks quote. Nominal is what the equation
    above consumes. Confusing the two is /findings/decline-quoted-on-the-wrong-basis/.
    """
    return 1.0 - rate(1.0, 1.0, Di, b)


def nominal_from_secant(De, b):
    """Secant effective annual decline back to nominal."""
    if not 0.0 < De < 1.0:
        raise ValueError("secant effective decline must be between 0 and 1")
    if b < B_EXPONENTIAL:
        return -math.log(1.0 - De)
    return ((1.0 - De) ** (-b) - 1.0) / b


def tangent_from_nominal(Di):
    """Nominal to tangent effective annual decline. The third of the three."""
    return 1.0 - math.exp(-Di)


# --------------------------------------------------------------------------
# Fitting
# --------------------------------------------------------------------------

def _sse_log(t, q, Di, b):
    """Sum of squared error in log rate, with qi solved analytically.

    Fitting on the log of rate rather than on rate is deliberate. Production
    spans two orders of magnitude across a well's life, so a fit on raw rate is
    dominated by the first few months and effectively ignores the tail, which
    is where the reserve lives.
    """
    resid = []
    for ti, qq in zip(t, q):
        shape = rate(ti, 1.0, Di, b)
        if shape <= 0.0:
            return float("inf"), 0.0
        resid.append(math.log(qq) - math.log(shape))
    log_qi = sum(resid) / len(resid)
    sse = sum((r - log_qi) ** 2 for r in resid)
    return sse, math.exp(log_qi)


def fit(t, q, b_bounds=(0.0, 2.0), di_bounds=(0.05, 5.0), rounds=6, nodes=40):
    """Fit an Arps curve to (t years, rate) pairs.

    Returns a dict with qi, Di, b, the three decline bases, r2 on log rate and
    a flag when b lands on a bound, which means the search hit a wall rather
    than found an answer.
    """
    pairs = [(ti, qq) for ti, qq in zip(t, q) if qq is not None and qq > 0]
    if len(pairs) < 4:
        raise ValueError("need at least four positive rate points to fit")
    t = [p[0] for p in pairs]
    q = [p[1] for p in pairs]

    b_lo, b_hi = b_bounds
    d_lo, d_hi = di_bounds
    best = None

    for _ in range(rounds):
        for i in range(nodes + 1):
            b = b_lo + (b_hi - b_lo) * i / nodes
            for j in range(nodes + 1):
                Di = d_lo + (d_hi - d_lo) * j / nodes
                if Di <= 0:
                    continue
                sse, qi = _sse_log(t, q, Di, b)
                if best is None or sse < best[0]:
                    best = (sse, qi, Di, b)
        # Narrow the window around the incumbent and search again.
        _, _, Di, b = best
        b_span = (b_hi - b_lo) / nodes * 2
        d_span = (d_hi - d_lo) / nodes * 2
        b_lo, b_hi = max(b_bounds[0], b - b_span), min(b_bounds[1], b + b_span)
        d_lo, d_hi = max(di_bounds[0], Di - d_span), min(di_bounds[1], Di + d_span)

    sse, qi, Di, b = best
    log_q = [math.log(x) for x in q]
    mean = sum(log_q) / len(log_q)
    sst = sum((x - mean) ** 2 for x in log_q)
    r2 = 1.0 - sse / sst if sst > 0 else float("nan")

    tol = (b_bounds[1] - b_bounds[0]) / 1000.0
    pinned = b <= b_bounds[0] + tol or b >= b_bounds[1] - tol

    return {
        "qi": qi,
        "Di_nominal": Di,
        "b": b,
        "De_secant": secant_from_nominal(Di, b),
        "De_tangent": tangent_from_nominal(Di),
        "r2_log": r2,
        "n": len(q),
        "b_pinned_to_bound": pinned,
    }


def eur(params, q_limit, cum_to_date=0.0):
    """Estimated ultimate recovery down to an economic limit rate."""
    return cum_to_date + cumulative(
        params["qi"], params["Di_nominal"], params["b"], q_limit
    ) * 365.25


# --------------------------------------------------------------------------
# Preparing real production history
# --------------------------------------------------------------------------

def per_well_rate(months):
    """Normalise a field history to rate per producing well per day.

    months is a sequence of dicts with keys: t (years), volume, producing_days,
    well_count. Dividing by wells actually online, rather than wells drilled,
    is what stops an infill programme from looking like a reservoir doing
    something impossible.
    """
    out = []
    for m in months:
        wells = m.get("well_count") or 0
        days = m.get("producing_days") or 0
        if wells <= 0 or days <= 0:
            continue
        out.append((m["t"], m["volume"] / days / wells))
    return out


def segments(months, tolerance=0):
    """Split a history wherever the producing well count steps up.

    Wells brought online two years apart are different vintages with different
    completions. One curve cannot describe both, and asking it to is the whole
    of the first finding on the site.
    """
    breaks = []
    previous = None
    for i, m in enumerate(months):
        wells = m.get("well_count") or 0
        if previous is not None and wells > previous + tolerance:
            breaks.append(i)
        previous = wells
    spans = []
    start = 0
    for b in breaks + [len(months)]:
        if b - start >= 4:
            spans.append((start, b))
        start = b
    return spans


def read_monthly_csv(path, date_col="date", volume_col="oil",
                     days_col="producing_days", well_col="well_count"):
    """Read a monthly production export into the shape the functions above want.

    Column names differ between the Wyoming Data Explorer, a lease operating
    statement and whatever an operator keeps in a spreadsheet, so they are
    arguments rather than assumptions.
    """
    rows = []
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    if not rows:
        return []

    def num(v):
        try:
            return float(str(v).replace(",", "").strip())
        except (TypeError, ValueError):
            return None

    rows.sort(key=lambda r: r[date_col])
    months = []
    for i, r in enumerate(rows):
        months.append({
            "t": i / 12.0,
            "date": r[date_col],
            "volume": num(r.get(volume_col)) or 0.0,
            "producing_days": num(r.get(days_col)) or 0.0,
            "well_count": num(r.get(well_col)) or 0.0,
        })
    return months


def group_by_well(path, well_col="api", date_col="date", volume_col="oil",
                  days_col="producing_days"):
    """Split a well-level export into one history per well."""
    wells = defaultdict(list)
    with io.open(path, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            wells[r[well_col]].append(r)
    out = {}
    for api, rows in wells.items():
        rows.sort(key=lambda r: r[date_col])
        history = []
        for i, r in enumerate(rows):
            try:
                vol = float(str(r.get(volume_col, 0)).replace(",", "") or 0)
                days = float(str(r.get(days_col, 0)).replace(",", "") or 0)
            except ValueError:
                continue
            history.append({"t": i / 12.0, "volume": vol,
                            "producing_days": days, "well_count": 1})
        out[api] = history
    return out


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def _self_test():
    print("Recovering known parameters from a clean curve")
    true = {"qi": 900.0, "Di": 2.2, "b": 1.0}
    t = [i / 12.0 for i in range(1, 60)]
    q = [rate(ti, true["qi"], true["Di"], true["b"]) for ti in t]
    got = fit(t, q)
    print("  true   qi %7.1f  Di %5.3f  b %5.3f"
          % (true["qi"], true["Di"], true["b"]))
    print("  fitted qi %7.1f  Di %5.3f  b %5.3f  R2(log) %.5f"
          % (got["qi"], got["Di_nominal"], got["b"], got["r2_log"]))
    assert abs(got["qi"] - true["qi"]) / true["qi"] < 0.02
    assert abs(got["b"] - true["b"]) < 0.05
    assert got["r2_log"] > 0.999

    print()
    print("Decline basis conversions round-trip")
    for b in (0.0, 0.5, 1.0, 1.4):
        Di = 2.2
        De = secant_from_nominal(Di, b)
        back = nominal_from_secant(De, b)
        print("  b %.2f  nominal %.3f -> secant %.1f%% -> nominal %.3f"
              % (b, Di, De * 100, back))
        assert abs(back - Di) < 1e-6

    print()
    print("The field-rate failure the site describes")
    # Three wells online at month 0, three more added at month 12. Every well
    # follows the same true curve from its own first month.
    starts = [0, 0, 0, 12, 12, 12]
    months = []
    for m in range(1, 49):
        total = 0.0
        online = 0
        for s in starts:
            if m > s:
                total += rate((m - s) / 12.0, true["qi"], true["Di"], true["b"])
                online += 1
        # Time origin is the well's own age, so a recovered qi is comparable
        # against the true one. Getting this convention wrong shifts qi by a
        # month of decline and looks like a fitting error when it is not.
        months.append({"t": m / 12.0, "volume": total * 30.0,
                       "producing_days": 30.0, "well_count": online})

    field_t = [m["t"] for m in months]
    field_q = [m["volume"] / m["producing_days"] for m in months]
    bad = fit(field_t, field_q)
    print("  fitted to field rate    b %5.3f  R2(log) %6.3f  pinned %s"
          % (bad["b"], bad["r2_log"], bad["b_pinned_to_bound"]))

    normalised = per_well_rate(months)
    spans = segments(months)
    start, end = spans[0]
    seg = normalised[start:end]
    good = fit([p[0] for p in seg], [p[1] for p in seg])
    print("  per well, first segment b %5.3f  R2(log) %6.3f  qi %7.1f"
          % (good["b"], good["r2_log"], good["qi"]))
    assert abs(good["qi"] - true["qi"]) / true["qi"] < 0.02, "qi must come back"

    assert good["r2_log"] > bad["r2_log"], "normalising must improve the fit"
    assert abs(good["b"] - true["b"]) < 0.05, "per-well fit must recover b"
    print()
    print("  The field-rate fit is the wrong answer. The per-well fit is not.")
    print()
    print("All checks passed.")


if __name__ == "__main__":
    _self_test()
