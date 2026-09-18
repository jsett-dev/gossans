#!/usr/bin/env python3
"""Study pages rendered from the studies the data pipeline wrote.

The pipeline's studies step writes one JSON file per study to
public/data/studies/, with the population it drew, the method in words, its
tables and its caveats. This turns each one into a page. Nothing on the page
is typed here: the words and the numbers are the study's own, so the page
cannot drift from the work.
"""

import html
import json
from pathlib import Path

SITE = Path(__file__).resolve().parent.parent / "public"
STUDIES = SITE / "data" / "studies"


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def num(v):
    if v is None:
        return "&ndash;"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, int):
        return "{:,}".format(v)
    if isinstance(v, float):
        return "{:,.1f}".format(v) if abs(v) >= 100 else "{:,.2f}".format(v).rstrip("0").rstrip(".")
    return esc(v)


def table(t):
    cols = t["columns"]
    head = "".join("<th>%s</th>" % esc(c["label"]) for c in cols)
    body = []
    for r in t["rows"]:
        cells = []
        for i, c in enumerate(cols):
            v = r.get(c["key"])
            cells.append("<td>%s</td>" % (esc(v) if i == 0 else num(v)))
        body.append("<tr>%s</tr>" % "".join(cells))
    note = ('<p class="tnote">%s</p>' % esc(t["note"])) if t.get("note") else ""
    return ('<h3>%s</h3>\n<div class="tbl"><table><tr>%s</tr>\n%s\n</table></div>\n%s'
            % (esc(t["title"]), head, "\n".join(body), note))


def bullets(items):
    return "<ul>\n%s\n</ul>" % "\n".join("  <li>%s</li>" % esc(x) for x in items)


def block(label, sub, inner, cls="col prose"):
    return ('  <div class="block">\n    <div class="rail"><b>%s</b><span>%s</span></div>\n'
            '    <div class="%s">\n%s\n    </div>\n  </div>\n' % (esc(label), esc(sub), cls, inner))


def body(s):
    pop = s.get("population", {})
    count = pop.get("count")
    parts = []
    parts.append(
        '  <section class="thesis article">\n'
        '    <div class="crumb"><a href="/studies/">Studies</a> &middot; %s</div>\n'
        "    <h1>%s</h1>\n"
        '    <p class="standfirst">%s</p>\n'
        '    <div class="costline">%s &middot; rebuilt %s &middot; every figure from public filings.</div>\n'
        "  </section>\n"
        % (esc(s.get("region", "").upper() or "region"), esc(s["title"]), esc(s["question"]),
           ("{:,} wells".format(count) if isinstance(count, int) else "population as stated"),
           esc(s.get("generated", ""))))
    parts.append(block("Found", "In one paragraph", "<p>%s</p>" % esc(s.get("summary", ""))))
    facts = ["<p>%s</p>" % esc(pop.get("description", ""))]
    extra = {k: v for k, v in pop.items() if k not in ("count", "description")}
    if extra:
        facts.append('<p class="costline">%s</p>' % " &middot; ".join(
            "%s %s" % (esc(k.replace("_", " ")), esc(v)) for k, v in extra.items()))
    parts.append(block("Population", "Who is counted", "\n".join(facts)))
    parts.append(block("Method", "How each number was made", bullets(s.get("method", []))))
    parts.append(block("Tables", "The numbers", "\n".join(table(t) for t in s.get("tables", [])),
                       cls="col"))
    parts.append(block("Caveats", "What this does not show", bullets(s.get("caveats", []))))
    src = ["<p>%s</p>" % esc(s.get("standing", ""))]
    for r in s.get("sources", []):
        line = "<b>%s</b>" % esc(r.get("agency") or r.get("name"))
        if r.get("attribution"):
            line += " &middot; " + esc(r["attribution"])
        if r.get("disclaimer"):
            line += ' <span class="dim">%s</span>' % esc(r["disclaimer"])
        src.append('<p class="srcline">%s</p>' % line)
    parts.append(block("Sources", "And their terms", "\n".join(src)))
    return "\n".join(parts)


def load():
    idx = STUDIES / "index.json"
    if not idx.exists():
        return []
    out = []
    for entry in json.loads(idx.read_text(encoding="utf-8")):
        f = STUDIES / (entry["slug"] + ".json")
        if f.exists():
            out.append(json.loads(f.read_text(encoding="utf-8")))
    return out


def pages():
    out = []
    for s in load():
        out.append({
            "url": "/studies/%s/" % s["slug"],
            "title": "%s | Gossans" % s["title"],
            "description": s["question"],
            "kicker": "Study &middot; rebuilt from the store",
            "priority": "0.9",
            "body": body(s),
        })
    return out


def index_rows():
    """Rows for the studies index: one per rebuilt study."""
    rows = []
    for s in load():
        count = s.get("population", {}).get("count")
        rows.append(
            '      <div class="rl">\n        <div>\n'
            '          <h3><a href="/studies/%s/">%s</a></h3>\n          <p>%s</p>\n        </div>\n'
            '        <div class="cost">%s<br>rebuilt %s</div>\n      </div>\n'
            % (esc(s["slug"]), esc(s["title"]), esc(s.get("summary", "")),
               ("{:,} wells".format(count) if isinstance(count, int) else "population as stated"),
               esc(s.get("generated", ""))))
    return "".join(rows)


HEAD_EXTRA = """<style>
.tnote { font-family:var(--f-data); font-size:12px; color:var(--ink-3); margin:0 0 22px; }
.srcline { font-family:var(--f-data); font-size:13px; line-height:1.7; }
.srcline .dim { color:var(--ink-3); }
.block .col h3 { margin:22px 0 8px; }
.block .col h3:first-child { margin-top:0; }
</style>"""
