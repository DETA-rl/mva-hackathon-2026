"""The step graph for a tier: what would run, with declared resources, inputs, outputs and dependencies."""
from __future__ import annotations

import json

from replicate.registry import deps_of, rule_status, select, topo_order
from replicate.steps import PROVIDER, root_missing


def build_plan(cfg, tier="quick", only=None, with_deps=False):
    selected = select(tier, only, with_deps)
    order = topo_order()
    rules = rule_status(cfg)
    produced = set()
    rows = []
    for s in order:
        if s.id in selected and s.kind in ("script", "harness"):
            bad_rules = [r for r in s.rules if not rules.get(r, {}).get("ok")]
            if s.network and not cfg.allow_network:
                action = "REFUSED (network step; allow_network is false)"
            elif bad_rules:
                action = "REFUSED (rule file " + ", ".join(bad_rules) + (
                    " not shipped; available to organisers on request)" if all(
                        rules[r].get("not_shipped") and rules[r].get("observed") is None for r in bad_rules)
                    else " does not match its sha256)")
            else:
                have = dict.fromkeys(produced | set(cfg.intermediates))
                miss = [k for k in s.needs if k not in have]
                roots = sorted(set().union(*(root_missing(k, have) for k in miss))) if miss else []
                action = "run" if not miss else "NOT RUN (needs " + ", ".join(miss) + "; depends on " + ", ".join(
                    f"{r} from {PROVIDER[r]}" for r in roots) + ": see check for how to obtain it)"
        elif s.id in selected:
            action = {"placeholder": "NOT RUN (placeholder)", "external": "NOT RUN (external: replicate/EXTERNAL_STEPS.md)"}[s.kind]
        else:
            action = "NOT RUN (" + ("full tier" if s.tier == "full" and tier == "quick" else "not selected") + ")"
        if action == "run":
            produced |= set(s.provides)
        d = s.describe()
        d.update(depends_on=deps_of(s), action=action)
        rows.append(d)
    runs = [r for r in rows if r["action"] == "run"]
    totals = {"steps": len(rows), "to_run": len(runs), "disk_gb": round(sum(r["disk_gb"] for r in runs), 2),
              "max_ram_gb": max([r["ram_gb"] for r in runs] or [0]),
              "max_vram_gb": max([r["vram_gb"] for r in runs if r["gpu"]] or [0]),
              "gpu_steps": [r["id"] for r in runs if r["gpu"]], "network_steps": [r["id"] for r in runs if r["network"]]}
    return {"tier": tier, "totals": totals, "steps": rows}


def _num(v, width, places):
    return "n/r".rjust(width) if v is None else f"{v:{width}.{places}f}"


def render(plan):
    L = [f"Plan, tier {plan['tier']}: {plan['totals']['to_run']} of {plan['totals']['steps']} steps would run; "
         f"disk budget {plan['totals']['disk_gb']} GB, largest RAM {plan['totals']['max_ram_gb']} GB, "
         f"largest VRAM {plan['totals']['max_vram_gb']} GB",
         "", f"{'step':24s} {'tier':5s} {'gpu':>4s} {'vram':>5s} {'ram':>5s} {'disk':>6s} {'net':>3s}  "
             f"{'depends on':38s} action", "-" * 140]
    for r in plan["steps"]:
        L.append(f"{r['id']:24s} {r['tier']:5s} {('yes' if r['gpu'] else 'no'):>4s} {_num(r['vram_gb'], 5, 0)} "
                 f"{_num(r['ram_gb'], 5, 1)} {_num(r['disk_gb'], 6, 2)} {('yes' if r['network'] else 'no'):>3s}  "
                 f"{', '.join(r['depends_on'])[:38]:38s} {r['action']}")
    L += ["", "n/r: not recorded. Inputs, outputs, register entry and measured runtime per step: results/plan.json "
              "(or --json).",
          "External steps are not run by the harness; their procedures are in replicate/EXTERNAL_STEPS.md."]
    return "\n".join(L)


def mermaid(plan):
    L = ["graph TD"]
    for r in plan["steps"]:
        for d in r["depends_on"]:
            L.append(f"  {d.replace('-', '_')} --> {r['id'].replace('-', '_')}")
    return "\n".join(L)


def to_json(plan):
    return json.dumps(plan, indent=1)
