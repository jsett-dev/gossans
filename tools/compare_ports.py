#!/usr/bin/env python3
"""Check that public/decline.js and tools/decline.py give the same answers.

Two implementations of the same maths will drift apart the moment one is
edited alone, and a browser tool that disagrees with the study on the same
well is worse than no browser tool. So this runs both over the same cases and
fails loudly on any disagreement.

Needs node on the path.

    python tools/compare_ports.py
"""

import json
import math
import random
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import decline  # noqa: E402

TOLERANCE = 1e-6


def cases():
    """Clean curves, noisy curves, and the shapes that break a fitter."""
    random.seed(20260911)
    out = []

    for qi, Di, b in [(900, 2.2, 1.0), (500, 1.1, 0.5), (1500, 3.0, 1.4),
                      (300, 0.8, 0.0), (750, 2.5, 1.8)]:
        t = [i / 12.0 for i in range(1, 61)]
        q = [decline.rate(x, qi, Di, b) for x in t]
        out.append(("clean b=%.1f" % b, t, q))

    # Noise, because real production is never on the curve.
    t = [i / 12.0 for i in range(1, 49)]
    q = [decline.rate(x, 800, 2.0, 1.2) * (1 + random.uniform(-0.25, 0.25))
         for x in t]
    out.append(("noisy", t, q))

    # A rate that rises, which no decline curve can describe. The fitter should
    # pin the exponent, and both ports should pin it identically.
    t = [i / 12.0 for i in range(1, 37)]
    q = [100 + 5 * i for i in range(1, 37)]
    out.append(("rising rate", t, q))

    # Very short history, right at the minimum.
    t = [i / 12.0 for i in range(1, 6)]
    q = [decline.rate(x, 600, 1.5, 0.9) for x in t]
    out.append(("five points", t, q))

    # A near-flat tail, where the terminal switch does the work.
    t = [i / 12.0 for i in range(1, 121)]
    q = [decline.rate(x, 400, 0.3, 1.6) for x in t]
    out.append(("flat tail", t, q))

    return out


JS_RUNNER = """
const fs = require("fs");
const D = require(%s).Decline || global.Decline;
// Cases arrive on stdin: a command line argument would hit the Windows
// length limit on anything but a toy payload.
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
const out = cases.map(c => {
  try {
    const f = D.fit(c.t, c.q);
    return {
      name: c.name, ok: true,
      qi: f.qi, Di: f.Di_nominal, b: f.b,
      de: f.De_secant, r2: f.r2_log, pinned: f.b_pinned_to_bound,
      eur: D.eur(f, 5.0, 0.0, 0.06),
      eur_raw: D.eur(f, 5.0, 0.0, null)
    };
  } catch (e) { return {name: c.name, ok: false, error: String(e.message)}; }
});
process.stdout.write(JSON.stringify(out));
"""


def run_js(payload):
    js = ROOT / "public" / "decline.js"
    runner = ROOT / "tools" / "_compare_runner.js"
    runner.write_text(JS_RUNNER % json.dumps(str(js).replace("\\", "/")),
                      encoding="utf-8")
    try:
        proc = subprocess.run([_node(), str(runner)],
                              input=json.dumps(payload),
                              capture_output=True, text=True)
        if proc.returncode != 0:
            raise SystemExit("node failed:\n" + proc.stderr)
        return json.loads(proc.stdout)
    finally:
        runner.unlink(missing_ok=True)


def _node():
    for name in ("node", "node.exe"):
        try:
            subprocess.run([name, "--version"], capture_output=True, check=True)
            return name
        except Exception:
            continue
    raise SystemExit("node is not on the path; cannot compare the ports")


def main():
    payload, expected = [], []
    for name, t, q in cases():
        payload.append({"name": name, "t": t, "q": q})
        try:
            f = decline.fit(t, q)
            expected.append({
                "name": name, "ok": True,
                "qi": f["qi"], "Di": f["Di_nominal"], "b": f["b"],
                "de": f["De_secant"], "r2": f["r2_log"],
                "pinned": f["b_pinned_to_bound"],
                "eur": decline.eur(f, 5.0, terminal_effective=0.06),
                "eur_raw": decline.eur(f, 5.0, terminal_effective=None),
            })
        except ValueError as e:
            expected.append({"name": name, "ok": False, "error": str(e)})

    got = run_js(payload)
    failures = []

    print("%-16s %10s %8s %7s %10s %9s" %
          ("CASE", "qi", "Di", "b", "EUR", "AGREE"))
    for py, js in zip(expected, got):
        if py["ok"] != js["ok"]:
            failures.append("%s: one port raised and the other did not" % py["name"])
            print("%-16s %s" % (py["name"], "MISMATCH on success/failure"))
            continue
        if not py["ok"]:
            print("%-16s %s" % (py["name"], "both refused, as expected"))
            continue

        worst = 0.0
        for key in ("qi", "Di", "b", "de", "r2", "eur", "eur_raw"):
            a, bv = py[key], js[key]
            if math.isinf(a) and math.isinf(bv):
                continue
            scale = max(1.0, abs(a))
            worst = max(worst, abs(a - bv) / scale)
        if py["pinned"] != js["pinned"]:
            failures.append("%s: pinned flag differs" % py["name"])
        if worst > TOLERANCE:
            failures.append("%s: worst relative difference %.2e" % (py["name"], worst))

        print("%-16s %10.2f %8.4f %7.4f %10.0f %9s" % (
            py["name"], py["qi"], py["Di"], py["b"], py["eur"],
            "yes" if worst <= TOLERANCE and py["pinned"] == js["pinned"]
            else "NO (%.1e)" % worst))

    print()
    if failures:
        for f in failures:
            print("FAIL:", f)
        raise SystemExit(1)
    print("Both ports agree to within %g on every case." % TOLERANCE)


if __name__ == "__main__":
    main()
