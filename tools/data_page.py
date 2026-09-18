#!/usr/bin/env python3
"""The data page: what is held, where it came from, and where it runs out.

The site has always shown conclusions and never the material behind them. A
reader cannot weigh a finding without knowing how much data stands under it,
which is why the coverage table here is as prominent as the row counts and
says plainly how thin some of it is.
"""

TITLE = "What is in the store, and where it runs out"

DESCRIPTION = (
    "Every record behind this site: how many, from which public source, under "
    "what licence, and the coverage gaps. Built from Wyoming, Montana and "
    "federal filings."
)

BODY = r"""
  <section class="thesis article">
    <div class="crumb">Data</div>
    <h1>Everything here is a public filing, and some of it is thin.</h1>
    <p class="standfirst">
      This is the material the studies and the models are built from. The row
      counts are the easy part. The coverage table underneath them is the
      honest part, because a figure computed from 15% of wells is not the same
      claim as one computed from 97%.
    </p>
  </section>

  <div class="block">
    <div class="rail"><b>Held</b><span>Record counts</span></div>
    <div class="col">
      <div class="tbl"><table id="tables"><tbody></tbody></table></div>
      <p class="detail" id="tracenote"></p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Coverage</b><span>Of the wells held</span></div>
    <div class="col">
      <h2>What is known about each well, and what is not.</h2>
      <div class="tbl"><table id="coverage"><tbody></tbody></table></div>
      <div class="prose">
        <p id="covnote"></p>
        <p>
          The thin rows are not oversights. A lateral length can only be
          measured where a directional survey was filed and is machine
          readable, and two thirds of the surveys in these counties exist only
          as scanned images. Spud date is not published on any layer the state
          serves. Those are limits of the record, and every figure drawn from
          those fields carries them.
        </p>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Sources</b><span>And their terms</span></div>
    <div class="col">
      <h2>Nothing enters the store until its licence has been read.</h2>
      <p class="prose" style="color:var(--ink-2); margin-bottom:20px;">
        Free to download is not the test. One well-known commercial dataset is
        free to read and forbidden to build on, which would have been an
        expensive thing to discover after the fact. Each source below carries
        the finding made when its terms were read, and the publisher's own
        disclaimer travels with the data into anything published from it.
      </p>
      <div id="sources"></div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Loads</b><span>Most recent</span></div>
    <div class="col">
      <div class="tbl"><table id="loads"><tbody></tbody></table></div>
      <p class="detail">
        Every row in the store records which retrieval it came from, so any
        figure on this site can be traced back to a fetch on a date.
      </p>
    </div>
  </div>
"""

STYLE = r"""
.srcbox { border-top: 1px solid var(--rule); padding: 18px 0; }
.srcbox h3 { font-size: 15px; margin-bottom: 4px; }
.srcbox .tag { font-family: var(--f-data); font-size: 10px; letter-spacing: .14em;
  text-transform: uppercase; padding: 2px 7px; border: 1px solid var(--rule); margin-left: 8px; }
.srcbox .ok { color: var(--draft); border-color: var(--draft); }
.srcbox .no { color: var(--ink-3); }
.srcbox p { font-size: 14px; color: var(--ink-2); margin-top: 8px; }
.bar { display: inline-block; height: 7px; background: var(--redline); vertical-align: middle; }
.barwrap { display: flex; align-items: center; gap: 9px; }
"""

SCRIPT = r"""
(function () {
  var el = function (id) { return document.getElementById(id); };
  if (!el("tables")) return;
  fetch(DATA + "/inventory.json").then(function (r) { return r.json(); }).then(function (d) {
    var n = function (v) { return v.toLocaleString(); };

    var t = el("tables").querySelector("tbody");
    t.innerHTML = "<tr><th>Record</th><th>Source</th><th>Rows</th></tr>" +
      d.tables.map(function (r) {
        return "<tr><td>" + r.label + "</td><td>" + r.source +
               "</td><td>" + n(r.rows) + "</td></tr>";
      }).join("");

    var traced = d.tables.filter(function (r) { return r.traced !== null; });
    var tr = traced.reduce(function (a, r) { return a + r.traced; }, 0);
    var tot = traced.reduce(function (a, r) { return a + r.rows; }, 0);
    el("tracenote").textContent =
      n(tr) + " of " + n(tot) + " rows record which retrieval they came from. " +
      "Generated " + d.generated + ".";

    var c = el("coverage").querySelector("tbody");
    c.innerHTML = "<tr><th>Known for</th><th>Wells</th><th>Share</th></tr>" +
      d.coverage.map(function (row) {
        var pct = d.wells ? (100 * row[1] / d.wells) : 0;
        return "<tr><td>" + row[0] + "</td><td>" + n(row[1]) +
               "</td><td><span class='barwrap'><span class='bar' style='width:" +
               Math.max(1, pct).toFixed(0) + "px'></span>" + pct.toFixed(0) + "%</span></td></tr>";
      }).join("");
    el("covnote").textContent =
      "Of " + n(d.wells) + " wells held. Coverage is what the filings contain, " +
      "not what was collected: where a share is low, the states' records are thin.";

    el("sources").innerHTML = d.sources.map(function (s) {
      return "<div class='srcbox'><h3>" + s.name +
        "<span class='tag " + (s.status === "usable" ? "ok" : "no") + "'>" +
        s.status + "</span></h3>" +
        "<p><b>" + (s.agency || "") + "</b></p>" +
        "<p>" + (s.licence || "") + "</p>" +
        (s.disclaimer ? "<p><i>" + s.disclaimer + "</i></p>" : "") + "</div>";
    }).join("");

    var l = el("loads").querySelector("tbody");
    l.innerHTML = "<tr><th>Source</th><th>What</th><th>Rows</th><th>When</th></tr>" +
      d.loads.map(function (r) {
        return "<tr><td>" + r.source + "</td><td>" + (r.note || "") + "</td><td>" +
               (r.rows === null ? "&mdash;" : n(r.rows)) + "</td><td>" +
               (r.started || "").slice(0, 10) + "</td></tr>";
      }).join("");
  }).catch(function () {
    el("tracenote").textContent = "The inventory could not be loaded.";
  });
})();
"""

BODY = "".join([BODY, "<style>", STYLE, "</style>",
                "<script>", SCRIPT, "</script>"])
