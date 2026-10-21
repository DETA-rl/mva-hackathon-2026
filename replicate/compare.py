"""Observed vs expected, one metric at a time, with an explicit tolerance per metric."""
from __future__ import annotations

PASS, FAIL, NC, MISSING = "PASS", "FAIL", "NOT COMPARABLE", "NOT OBSERVED"


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _round(x, k):
    # Python's round() on the float; the scripts print with format(), which also rounds half to even on the binary value.
    return float(f"{x:.{k}f}")


def _sigfig(x, k):
    if x == 0:
        return 0.0
    return float(f"{x:.{k - 1}e}")


def _eq_num(o, e, fn):
    if isinstance(e, (list, tuple)):
        return isinstance(o, (list, tuple)) and len(o) == len(e) and all(_eq_num(a, b, fn) for a, b in zip(o, e))
    if isinstance(e, dict):
        return isinstance(o, dict) and set(o) == set(e) and all(_eq_num(o[k], e[k], fn) for k in e)
    if _num(e) and _num(o):
        return fn(o, e)
    return o == e


def check(observed, expected, tol):
    """Return True if `observed` matches `expected` under tolerance `tol`."""
    if tol in (None, "exact"):
        return _eq_num(observed, expected, lambda o, e: o == e)
    if tol == "set":
        return sorted(map(str, observed)) == sorted(map(str, expected))
    if tol == "subset":
        return set(map(str, expected)) <= set(map(str, observed))
    if isinstance(tol, dict):
        if "round" in tol:
            k = int(tol["round"])
            return _eq_num(observed, expected, lambda o, e: _round(o, k) == _round(e, k))
        if "sigfig" in tol:
            k = int(tol["sigfig"])
            return _eq_num(observed, expected, lambda o, e: _sigfig(o, k) == _sigfig(e, k))
        if "abs" in tol:
            a = float(tol["abs"])
            return _eq_num(observed, expected, lambda o, e: abs(o - e) <= a + 1e-12)
        if "rel" in tol:
            r = float(tol["rel"])
            return _eq_num(observed, expected, lambda o, e: abs(o - e) <= r * abs(e) + 1e-12)
        if "lt" in tol:
            return _num(observed) and observed < float(tol["lt"])
        if "le" in tol:
            return _num(observed) and observed <= float(tol["le"])
    raise ValueError(f"unknown tolerance {tol!r}")


def describe_tol(tol):
    if tol in (None, "exact"):
        return "exact"
    if isinstance(tol, str):
        return tol
    k, v = next(iter(tol.items()))
    return {"round": f"equal after rounding to {v} decimals", "sigfig": f"equal at {v} significant figures",
            "abs": f"|obs - exp| <= {v}", "rel": f"relative difference <= {v}", "lt": f"observed < {v}",
            "le": f"observed <= {v}"}.get(k, str(tol))


def compare_metrics(spec_metrics, observed: dict, exact_ok: bool):
    """exact_ok: every input/artifact listed in exact_if matched its expected sha256."""
    rows = []
    for m in spec_metrics:
        name = m["name"]
        tol = m.get("tol", "exact")
        alt = m.get("tol_alt")
        row = {"metric": name, "expected": m.get("expected"), "source": m.get("source", ""),
               "tolerance": describe_tol(tol)}
        if name not in observed:
            row.update(observed=None, verdict=MISSING)
            rows.append(row)
            continue
        o = observed[name]
        row["observed"] = o
        if exact_ok:
            ok = check(o, m.get("expected"), tol)
            row["verdict"] = PASS if ok else FAIL
        elif alt is not None:
            ok = check(o, m.get("expected"), alt)
            row["tolerance"] = describe_tol(alt) + " (inputs differ from ours)"
            row["verdict"] = PASS if ok else FAIL
        else:
            row["verdict"] = NC
            row["tolerance"] += " (not applied: an input differs from ours)"
        rows.append(row)
    extra = [{"metric": k, "observed": v, "expected": None, "verdict": "INFO", "source": "", "tolerance": ""}
             for k, v in observed.items() if k not in {m["name"] for m in spec_metrics}]
    return rows, extra


def step_status(rows):
    if not rows:
        return "NO EXPECTED VALUES"
    v = {r["verdict"] for r in rows}
    if FAIL in v or MISSING in v:
        return FAIL
    if NC in v:
        return "INCONCLUSIVE"
    return PASS
