#!/usr/bin/env python3
"""The browser decline fitter.

The whole point is where it runs. The fit happens on the visitor's machine,
so production history is never uploaded and there is no server that could
retain it. That is not a policy promise, it is an absence of capability, and
it is worth saying plainly on the page.
"""

TITLE = "Fit your own well"

DESCRIPTION = (
    "Paste a well's monthly production and get a decline curve fitted properly: "
    "per producing day, on the logarithm of rate, with a terminal switch and an "
    "honest refusal when the fit is unsound. Runs in your browser, uploads nothing."
)

HEAD_EXTRA = """
<script defer src="/decline.js"></script>"""

BODY = r"""
  <section class="thesis article">
    <div class="crumb">Tool &middot; Decline fitter</div>
    <h1>Paste a well. Find out whether your forecast survives contact with it.</h1>
    <p class="standfirst">
      The same engine behind the Powder River Basin study, running here instead
      of on our machines. It fits per producing day, on the logarithm of rate,
      switches to a terminal decline before estimating recovery, and refuses to
      give you a number when the fit does not deserve one.
    </p>
    <div class="costline">
      Nothing you paste leaves this page. There is no server to send it to.
    </div>
  </section>

  <div class="block">
    <div class="rail"><b>Input</b><span>Monthly production</span></div>
    <div class="col">
      <p class="prose" style="color:var(--ink-2); margin-bottom:16px;">
        One row per month. Two columns is enough, volume and producing days,
        and a date column is accepted and ignored. Commas, tabs or spaces.
        Header row optional.
      </p>
      <textarea id="input" class="paste" spellcheck="false"
        placeholder="month, oil bbl, producing days&#10;2021-01, 21689, 30&#10;2021-02, 18447, 28&#10;2021-03, 16022, 31"></textarea>
      <div class="ctl" style="margin-top:14px;">
        <div class="ctlgrp">
          <button id="run" type="button">Fit this well</button>
          <button id="demo" type="button">Load an example</button>
          <button id="clear" type="button">Clear</button>
        </div>
      </div>
      <div class="opts">
        <label>Economic limit
          <input id="limit" type="number" value="5" min="0.1" step="0.1"> per day</label>
        <label>Terminal decline
          <input id="terminal" type="number" value="6" min="0" max="90" step="0.5"> % a year</label>
        <label><input id="dropfirst" type="checkbox" checked> drop the flowback month</label>
      </div>
      <div id="note" class="detail" style="display:none;"></div>
    </div>
  </div>

  <div class="block" id="resultblock" style="display:none;">
    <div class="rail"><b>Result</b><span>The fit</span></div>
    <div class="col">
      <div id="verdict"></div>
      <div class="mapwrap" style="margin-top:18px;">
        <svg id="chart" viewBox="0 0 760 380" role="img"
             aria-label="Production history and fitted decline curve"></svg>
      </div>
      <div class="legend" id="chartlegend"></div>
      <div class="tbl" style="margin-top:22px;">
        <table id="params"></table>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Method</b><span>What it does differently</span></div>
    <div class="col prose">
      <p>
        <b>Rate per producing day.</b> If you give it producing days, it divides
        by them. A well down for eleven days did not decline, it was off, and a
        fitter that cannot tell the difference forecasts your downtime forward
        as reservoir behaviour.
      </p>
      <p>
        <b>The flowback month dropped.</b> The first partial month is choked and
        cleaning up. It is not on the trend that governs everything after it.
      </p>
      <p>
        <b>Fitted on the logarithm of rate.</b> Production spans two orders of
        magnitude across a well's life. A fit on raw rate is dominated by the
        first six months and effectively ignores the tail, which is where the
        reserve lives.
      </p>
      <p>
        <b>A terminal switch before any recovery number.</b> A hyperbolic with
        an exponent near or above one barely converges when integrated forever,
        and exponents that high are ordinary early in life. Without the switch
        a well fitted at 1.4 books sixty percent more oil than it will deliver.
      </p>
      <p>
        <b>It refuses.</b> If the exponent lands on its bound, the search hit a
        wall rather than found an answer, and you get told that instead of a
        number. Most fitters report the number.
      </p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Limits</b><span>What this is not</span></div>
    <div class="col prose">
      <p>
        This fits one well to one curve. It does not know your costs, your
        working interest, your downtime causes or whether the well is under
        injection, and a decline curve cannot describe a well under injection at
        all. On the Powder River Basin study it refused 174 of 1,368 wells for
        exactly that kind of reason.
      </p>
      <p>
        The engine here is the same code as the study, checked line for line
        against it: both implementations are run over the same cases and must
        agree to within one part in a million before either ships.
      </p>
      <p style="margin-top:24px;">
        <a href="/powder-river-basin/">See what it found across 1,459 wells</a>,
        or <a href="/contact/">have us run it properly on your asset</a>.
      </p>
    </div>
  </div>

<style>
.paste { width:100%; min-height:190px; box-sizing:border-box; padding:14px 16px;
  font-family:var(--f-data); font-size:13px; line-height:1.6;
  background:var(--paper-2); color:var(--ink); border:1px solid var(--rule);
  resize:vertical; }
.paste:focus { outline:none; border-color:var(--rust); }
.opts { display:flex; flex-wrap:wrap; gap:12px 28px; margin-top:16px;
  font-family:var(--f-data); font-size:12px; color:var(--ink-2); }
.opts label { display:flex; align-items:center; gap:8px; }
.opts input[type=number] { width:70px; padding:4px 6px; font-family:var(--f-data);
  font-size:12px; background:var(--paper-2); color:var(--ink);
  border:1px solid var(--rule); }
.verdict { border-left:2px solid var(--rust); padding:14px 18px;
  font-family:var(--f-data); font-size:14px; line-height:1.7; }
.verdict.bad { border-left-color:#b0574a; }
.verdict b { color:var(--ink); }
</style>

<script>
(function () {
  function $(id) { return document.getElementById(id); }
  function el(n, a) {
    var e = document.createElementNS("http://www.w3.org/2000/svg", n);
    for (var k in a) e.setAttribute(k, a[k]);
    return e;
  }
  function fmt(n, d) {
    return n.toLocaleString(undefined, {maximumFractionDigits: d === undefined ? 0 : d});
  }

  // Columns are guessed rather than demanded, because nobody's export looks
  // like anybody else's. A date column is recognised and skipped; of the
  // numbers that remain, the largest is volume and a value at or under 31 is
  // producing days.
  function parse(text) {
    var rows = [], skipped = 0;
    text.split(/\r?\n/).forEach(function (line) {
      var s = line.trim();
      if (!s) return;
      var cells = s.split(/[,;\t]|\s{2,}/).map(function (c) { return c.trim(); })
                   .filter(function (c) { return c !== ""; });
      if (cells.length === 1) cells = s.split(/\s+/);
      var nums = [];
      cells.forEach(function (c) {
        if (/^\d{4}[-\/]\d{1,2}([-\/]\d{1,2})?$/.test(c)) return;   // a date
        if (/^\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4}$/.test(c)) return;     // a date
        var v = parseFloat(c.replace(/[,$]/g, ""));
        if (!isNaN(v) && isFinite(v)) nums.push(v);
      });
      if (!nums.length) { skipped++; return; }
      var vol = nums[0], days = null, i;
      for (i = 0; i < nums.length; i++) if (nums[i] > vol) vol = nums[i];
      for (i = 0; i < nums.length; i++) {
        if (nums[i] !== vol && nums[i] > 0 && nums[i] <= 31) { days = nums[i]; break; }
      }
      rows.push({volume: vol, days: days});
    });
    return {rows: rows, skipped: skipped};
  }

  function series(rows, dropFirst) {
    var used = rows.filter(function (r) { return r.volume > 0; });
    if (dropFirst && used.length > 1) used = used.slice(1);
    var t = [], q = [], anyDays = false;
    used.forEach(function (r, i) {
      var d = (r.days && r.days > 0) ? r.days : 30.4375;
      if (r.days && r.days > 0) anyDays = true;
      t.push(i / 12.0);
      q.push(r.volume / d);
    });
    return {t: t, q: q, anyDays: anyDays, n: used.length};
  }

  function chart(t, q, f, limit) {
    var svg = $("chart");
    svg.innerHTML = "";
    var padL = 62, padR = 18, padT = 18, padB = 34;
    var W = 760 - padL - padR, H = 380 - padT - padB;

    var tMax = Math.max(t[t.length - 1] * 1.35, t[t.length - 1] + 1);
    var all = q.slice();
    var curve = [], steps = 160, i, x, y;
    for (i = 0; i <= steps; i++) {
      var tt = tMax * i / steps;
      var v = Decline.rate(tt, f.qi, f.Di_nominal, f.b);
      if (v < limit * 0.5) break;
      curve.push([tt, v]);
      all.push(v);
    }
    var qMax = Math.max.apply(null, all);
    var qMin = Math.max(Math.min.apply(null, all), limit * 0.5, 0.01);

    // Log scale on rate. On a linear axis the tail is a flat line against the
    // axis and the fit looks perfect whatever it is doing.
    function px(tt) { return padL + (tt / tMax) * W; }
    function py(v) {
      var lo = Math.log(qMin), hi = Math.log(qMax);
      return padT + H - (Math.log(Math.max(v, qMin)) - lo) / (hi - lo) * H;
    }

    // Decade lines alone disappear whenever the data spans less than a factor
    // of ten, which is most wells over a few years. Step through 1, 2 and 5
    // times each power instead, so there is always something to read against.
    var ticks = [], p10 = Math.floor(Math.log10(qMin));
    for (var e = p10; e <= Math.ceil(Math.log10(qMax)); e++) {
      [1, 2, 5].forEach(function (mult) {
        var v = mult * Math.pow(10, e);
        if (v >= qMin && v <= qMax * 1.01) ticks.push(v);
      });
    }
    if (ticks.length < 2) ticks = [qMin, Math.sqrt(qMin * qMax), qMax];
    for (var gi = 0; gi < ticks.length; gi++) {
      var g = ticks[gi];
      y = py(g);
      svg.appendChild(el("line", {x1: padL, y1: y, x2: padL + W, y2: y,
        stroke: "var(--rule-2)", "stroke-width": 1}));
      var lbl = el("text", {x: padL - 8, y: y + 4, "text-anchor": "end",
        "font-family": "var(--f-data)", "font-size": 10, fill: "var(--ink-3)"});
      lbl.textContent = fmt(g);
      svg.appendChild(lbl);
    }
    // One label per year gets crowded past a decade of history.
    var yrStep = Math.max(1, Math.ceil(tMax / 12));
    for (var yr = 0; yr <= tMax; yr += yrStep) {
      x = px(yr);
      svg.appendChild(el("line", {x1: x, y1: padT, x2: x, y2: padT + H,
        stroke: "var(--rule-2)", "stroke-width": 1, opacity: 0.5}));
      var xl = el("text", {x: x, y: padT + H + 20, "text-anchor": "middle",
        "font-family": "var(--f-data)", "font-size": 10, fill: "var(--ink-3)"});
      xl.textContent = yr;
      svg.appendChild(xl);
    }

    var d = curve.map(function (p, i) {
      return (i ? "L" : "M") + px(p[0]).toFixed(1) + " " + py(p[1]).toFixed(1);
    }).join(" ");
    svg.appendChild(el("path", {d: d, fill: "none", stroke: "var(--rust)",
      "stroke-width": 2}));

    for (i = 0; i < t.length; i++) {
      svg.appendChild(el("circle", {cx: px(t[i]), cy: py(q[i]), r: 2.6,
        fill: "none", stroke: "var(--ink-2)", "stroke-width": 1}));
    }

    y = py(limit);
    if (y > padT && y < padT + H) {
      svg.appendChild(el("line", {x1: padL, y1: y, x2: padL + W, y2: y,
        stroke: "var(--ink-3)", "stroke-width": 1, "stroke-dasharray": "4,3"}));
    }

    var ax = el("text", {x: padL + W / 2, y: 374, "text-anchor": "middle",
      "font-family": "var(--f-data)", "font-size": 10, fill: "var(--ink-3)"});
    ax.textContent = "years on production";
    svg.appendChild(ax);

    $("chartlegend").innerHTML =
      '<span><i class="sw" style="background:none;border:none;' +
      'border-top:2px solid var(--rust);height:0"></i>fitted curve</span>' +
      '<span><i class="sw" style="border-radius:50%;width:12px;' +
      'background:transparent"></i>your data</span>' +
      '<span><i class="sw" style="background:none;border:none;' +
      'border-top:1px dashed var(--ink-3);height:0"></i>economic limit</span>' +
      '<span style="color:var(--ink-3)">rate per producing day, log scale</span>';
  }

  function run() {
    var parsed = parse($("input").value);
    var note = $("note");
    if (parsed.rows.length < 5) {
      note.style.display = "block";
      note.innerHTML = "<b>Not enough rows.</b> Found " + parsed.rows.length +
        " with a number on them. Paste at least five months.";
      $("resultblock").style.display = "none";
      return;
    }

    var s = series(parsed.rows, $("dropfirst").checked);
    var limit = parseFloat($("limit").value) || 5;
    var terminal = (parseFloat($("terminal").value) || 0) / 100;

    var msgs = ["Read <b>" + parsed.rows.length + "</b> rows" +
      (parsed.skipped ? ", skipped " + parsed.skipped + " without numbers" : "") +
      ", used <b>" + s.n + "</b>."];
    msgs.push(s.anyDays
      ? "Producing days found, so rate is per producing day."
      : "<b>No producing days column.</b> Assuming a full month, which reads " +
        "downtime as decline. Add one if you have it.");
    note.style.display = "block";
    note.innerHTML = msgs.join("<br>");

    var f;
    try {
      f = Decline.fit(s.t, s.q);
    } catch (e) {
      $("resultblock").style.display = "none";
      note.innerHTML += "<br><b>Could not fit:</b> " + e.message;
      return;
    }

    var unsound = f.b_pinned_to_bound || f.r2_log < 0.5;
    var v = $("verdict");
    v.className = "verdict" + (unsound ? " bad" : "");
    if (unsound) {
      v.innerHTML = "<b>This fit is not sound, and no recovery number is " +
        "offered.</b><br>" +
        (f.b_pinned_to_bound
          ? "The hyperbolic exponent landed on its bound, which means the " +
            "search hit a wall rather than found an answer. That usually means " +
            "the rate rises somewhere, which no decline curve can describe: " +
            "wells added to a total, a return from downtime, or a well under " +
            "injection."
          : "The fit quality is " + f.r2_log.toFixed(3) + " on log rate, which " +
            "is too poor to build a forecast on.");
    } else {
      var e = Decline.eur(f, limit, 0, terminal);
      var eRaw = Decline.eur(f, limit, 0, null);
      var over = eRaw > 0 ? (eRaw - e) / eRaw * 100 : 0;
      v.innerHTML = "<b>Estimated recovery " + fmt(e) + "</b> down to " +
        fmt(limit, 1) + " a day." +
        (over > 1 ? "<br>Without the terminal switch this curve would have " +
          "booked " + fmt(eRaw) + ", which is <b>" + fmt(over, 0) +
          "% higher</b> than it will deliver." : "");
    }

    var rows = [
      ["Initial rate", fmt(f.qi, 1) + " per day"],
      ["Hyperbolic exponent, b", f.b.toFixed(3) +
        (f.b_pinned_to_bound ? " &mdash; pinned to its bound" : "")],
      ["Nominal decline", f.Di_nominal.toFixed(3) + " per year"],
      ["Secant effective decline", (f.De_secant * 100).toFixed(1) + "%"],
      ["Tangent effective decline", (f.De_tangent * 100).toFixed(1) + "%"],
      ["Fit quality on log rate", f.r2_log.toFixed(3)],
      ["Months used", String(f.n)]
    ];
    $("params").innerHTML = "<tr><th>Parameter</th><th>Value</th></tr>" +
      rows.map(function (r) {
        return "<tr><td>" + r[0] + "</td><td>" + r[1] + "</td></tr>";
      }).join("");

    $("resultblock").style.display = "";
    chart(s.t, s.q, f, limit);
  }

  function ready() {
    if (typeof Decline === "undefined") return setTimeout(ready, 100);
    $("run").onclick = run;
    $("clear").onclick = function () {
      $("input").value = "";
      $("note").style.display = "none";
      $("resultblock").style.display = "none";
    };
    $("demo").onclick = function () {
      // A synthetic well, not a real one. Generated from a known curve so the
      // fitted parameters come back close to the ones it was built from.
      var lines = ["month, oil bbl, producing days"];
      var qi = 820, Di = 2.1, b = 1.25;
      for (var m = 0; m < 42; m++) {
        var days = m === 0 ? 14 : (m % 9 === 0 ? 24 : 30);
        var r = Decline.rate(m / 12.0, qi, Di, b);
        var noise = 1 + (Math.sin(m * 2.1) * 0.06);
        var y = 2022 + Math.floor(m / 12), mo = (m % 12) + 1;
        lines.push(y + "-" + (mo < 10 ? "0" : "") + mo + ", " +
                   Math.round(r * days * noise) + ", " + days);
      }
      $("input").value = lines.join("\n");
      run();
    };
  }
  ready();
})();
</script>
"""
