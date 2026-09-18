#!/usr/bin/env python3
"""The 3D strata view: measured tops and wellbore paths, and nothing else.

Every 3D geology viewer draws smooth surfaces between wells. Those surfaces
are interpolation, and they are the most persuasive thing on the screen
precisely where the least is known. This one draws the measurements and stops.

So: a formation top is a mark at the depth an operator filed for it. A
wellbore is the path its filed directional survey describes, or a plain
vertical line when no survey exists, which is what the record supports and no
more. Nothing spans the space between two wells.

Camera controls are written here rather than pulled from a second library.
Drag to rotate, wheel to zoom, right-drag or shift-drag to pan.
"""

TITLE = "The strata in three dimensions, and where the surfaces stop"

DESCRIPTION = (
    "Formation tops and wellbore paths in the Powder River Basin, in 3D, built "
    "from Wyoming's and Montana's filings. Measurements by default. Interpolated surfaces can "
    "be switched on, and stop where well control does."
)

HEAD_EXTRA = """
<script defer
        src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>"""

HERO = r"""
  <section class="thesis article">
    <div class="crumb">Model &middot; Strata in three dimensions</div>
    <h1>The tops are measured. The surface between them is an argument.</h1>
    <p class="standfirst">
      Drag to rotate, scroll to zoom, hold shift to pan. Each mark is a
      formation top at the depth an operator filed for it. Each line is a
      wellbore. Interpolated surfaces can be switched on, and stop where the
      wells do. Where a well has a directional survey on file the path is the
      one it describes; where it has none the line is vertical, because that is
      all the record supports.
    </p>
  </section>

"""

PANE = r"""
  <div id="strata" class="pane">
    <div class="maprow">
      <div class="scenewrap">
        <canvas id="scene"></canvas>
        <div id="hud" class="hud">loading&hellip;</div>
        <div id="flabels" class="flabels" aria-hidden="true"></div>
        <div id="tip" class="tip" role="status"></div>
        <div id="credit" class="credit"></div>
        <div id="compass" class="compass" aria-hidden="true">
          <svg viewBox="-50 -50 100 100">
            <g id="rose">
              <circle r="38" fill="none" stroke="currentColor" stroke-opacity=".35"></circle>
              <path d="M0,-38 L7,-8 L0,-16 L-7,-8 Z" fill="#b7532e"></path>
              <path d="M0,38 L7,8 L0,16 L-7,8 Z" fill="none" stroke="currentColor"
                    stroke-opacity=".45"></path>
              <text x="0" y="-41" text-anchor="middle">N</text>
              <text x="44" y="4" text-anchor="middle">E</text>
              <text x="0" y="48" text-anchor="middle">S</text>
              <text x="-44" y="4" text-anchor="middle">W</text>
            </g>
          </svg>
        </div>
      </div>
      <div class="panel">
        <div id="wellcard" class="wellcard" hidden></div>
        <h3 class="withbtn">Wells <span id="wellcount" class="cnt"></span></h3>
        <div class="filters" id="filters"></div>
        <h3>View</h3>
        <div class="ctlgrp" id="ctl"></div>
        <h3>Layers</h3>
        <div class="lay3d" id="layers3d"></div>
        <h3 class="withbtn">Strata
          <button type="button" id="allstrata">Hide all</button></h3>
        <label class="lay3d"><input id="cu" type="checkbox">
          Combine benches into units</label>
        <div id="legend" class="legend3d"></div>
        <p class="orient" id="orient"></p>
        <p class="zoomhint">
          Drag to rotate, scroll to zoom, hold shift to pan. Click a wellhead
          to isolate that well and its pad. Each mark is a
          formation top at the depth an operator filed for it; each line is a
          wellbore, following its filed survey where one exists and vertical
          where none does. The ground is the USGS bare-earth elevation model
          on a <span class="t-step">&hellip;</span> grid, with the township
          lines laid on it, and it can wear a basemap: aerial imagery, the
          USGS topographic map, or OpenStreetMap. Hover a wellhead or a top
          for what it is. Every switch that changes what is drawn is in the
          legend below.
        </p>
      </div>
    </div>
    <p class="detail" id="note"></p>
  </div>
"""

NOTES = r"""
  <div class="block">
    <div class="rail"><b>Honesty</b><span>What is not here</span></div>
    <div class="col prose">
      <p>
        Surfaces are available and are off until you ask for them, because a
        surface joining one well's Niobrara top to the next well's is a
        statement about ground nobody drilled. Switched on, each one is a
        weighted average of the tops around it, and it is drawn only where
        there is well control: at least three tops within eight kilometres,
        the nearest within four. Everywhere else stays empty, which is why the
        surfaces have ragged edges and holes. Across ten formations, 17,251
        cells could be computed and 42,269 could not.
      </p>
      <p>
        Colour fades toward the page as the nearest well gets further away, so
        thinly supported ground looks thin. Inverse distance weighting is used
        rather than anything smoother on purpose: smoothness is the quality
        that makes an interpolated surface look like knowledge.
      </p>
      <p>
        Two other limits are worth stating plainly. <b id="nsurv"></b> of the
        wells here have no directional survey on file and are drawn as vertical
        lines, which is wrong for any horizontal well but is what the filings
        support. And the surveyed paths are thinned before they reach your
        browser, so a path is the shape of the filed survey rather than every
        station in it.
      </p>
      <p>
        A formation in the legend governs two things at once: the tops filed
        at that horizon, and the wells completed in it. They are the same
        subject seen twice - what a well passed through and what it was
        perforated in - and having them on separate switches meant a layer
        could be turned off while the wells producing from it stayed on the
        screen. Completions come from the filed producing intervals:
        <b id="c-prod">&hellip;</b> wells are matched to a formation drawn
        here, <b id="c-multi">&hellip;</b> of them completed in more than one,
        <b id="c-none">&hellip;</b> have no producing formation on file, and
        <b id="c-notdrawn">&hellip;</b> produce from something this view does
        not draw because too few tops were filed for it. The last two groups
        are not folded in with the rest; they have their own row, so no
        switch claims to control more than it does.
      </p>
      <p>
        The ground surface is the one surface here that is not an inference.
        It is the U.S. Geological Survey's bare-earth elevation model, built
        largely from airborne lidar and served at one metre, resampled onto a
        <span class="t-step">&hellip;</span> grid because what it is wanted for is a datum under a
        column of formation tops rather than a terrain analysis. Bare earth
        means the ground, not the trees or the buildings on it, and anything
        needing the real resolution should go to
        <a href="https://www.usgs.gov/3d-elevation-program">3DEP</a> rather
        than to this page.
      </p>
      <p>
        Having a measured ground makes the filings checkable against it. Well
        by well, across the <b id="e-n">&hellip;</b> wells with both a filed
        elevation and a grid cell under them, the two agree in the middle and
        not in the tails: the median difference is <b id="e-med">&hellip;</b>,
        the quartiles are <b id="e-q1">&hellip;</b> and <b id="e-q3">&hellip;</b>,
        and <b><span id="e-big">&hellip;</span> wells differ by more than
        100&nbsp;m</b>. A hundred metres is not a survey error. In those wells either the filed
        elevation or the surface coordinate the well is mapped at is wrong,
        and this site does not yet know which; the disagreement tracks neither
        survey coverage nor lateral length. They are drawn anyway, because
        leaving them out would be choosing the evidence.
      </p>
      <p>
        Each wellbore hangs from the elevation filed with its own tops rather
        than from this grid, even where the two disagree, because that is the
        datum those tops were computed from and a well has to be internally
        consistent before it is consistent with anything else.
        <b id="e-3dep">&hellip;</b> wells had no usable filed elevation and
        hang from the 3DEP ground instead.
      </p>
      <p>
        The township lines on that surface are the Bureau of Land Management's
        survey grid, draped by sampling the ground under each step along the
        line. In BLM's words these data are neither legal documents nor land
        surveys and must not be used as such, and putting them on a
        three-dimensional ground makes them look more like a boundary than
        ever, so it bears repeating: this is the survey grid drawn for
        reference, not a determination of anybody's corner.
      </p>
      <p>
        Vertical exaggeration is on by default because the basin is about a
        hundred kilometres across and a couple of kilometres deep, and at true
        scale the layers collapse into a line. Exaggeration distorts dip and
        thickness. The figure is shown above and can be set to 1.
      </p>
    </div>
  </div>
"""

# Standalone form, for any page that shows the scene on its own rather than
# paired with the map, where the pane needs its own block and heading.
_OPEN = r"""
  <div class="block">
    <div class="rail"><b>View</b><span>Measured tops</span><span>and wellbores</span></div>
    <div class="col">
      <h2>The same wells in three dimensions.</h2>
"""

_CLOSE = r"""
    </div>
  </div>
"""

SECTIONS = _OPEN + PANE + _CLOSE + NOTES

STYLE = r"""
.maprow .scenewrap { height: 560px; }
.scenewrap { position: relative; border: 1px solid var(--rule); background: var(--paper-2);
  height: min(70vh, 620px); overflow: hidden; }
.scenewrap canvas { display: block; width: 100%; height: 100%; touch-action: none; cursor: grab; }
.scenewrap canvas:active { cursor: grabbing; }
.compass { position: absolute; left: 12px; bottom: 12px; width: 78px; height: 78px;
  color: var(--ink-3); background: var(--paper); border: 1px solid var(--rule);
  border-radius: 50%; }
.compass svg { width: 100%; height: 100%; display: block; }
.compass text { font-family: var(--f-data); font-size: 13px; fill: currentColor; }
.orient { font-family: var(--f-data); font-size: 11px; line-height: 1.7;
  color: var(--ink-2); margin: 10px 0 0; }
.orient b { color: var(--ink); }
.hud { position: absolute; left: 12px; top: 12px; font-family: var(--f-data);
  font-size: 11px; line-height: 1.6; color: var(--ink-2); background: var(--paper);
  border: 1px solid var(--rule); padding: 8px 10px; max-width: 46ch; }
/* The legend sits in the panel with every other switch rather than floating
   over the scene, because a legend that covers only half the layers is not a
   legend. */
.legend3d { font-family: var(--f-data); font-size: 11px; max-height: 240px;
  overflow-y: auto; }
.legend3d button { display: flex; align-items: flex-start; gap: 7px; width: 100%;
  background: none; border: 0; padding: 3px 0; font: inherit; color: var(--ink-2);
  cursor: pointer; text-align: left; }
.legend3d button[aria-pressed="false"] { opacity: .35; }
.legend3d .sw { width: 11px; height: 11px; flex: none; margin-top: 3px; }
.panel h3.withbtn { display: flex; align-items: baseline; justify-content: space-between; }
.panel h3.withbtn button { font-family: var(--f-data); font-size: 9.5px;
  letter-spacing: .1em; text-transform: uppercase; background: none;
  border: 1px solid var(--rule); color: var(--ink-2); cursor: pointer;
  padding: 2px 6px; }
.panel h3.withbtn button:hover { border-color: var(--redline); color: var(--ink); }
.lay3d label { display: flex; align-items: center; gap: 7px; padding: 2px 0;
  cursor: pointer; font-family: var(--f-data); font-size: 11.5px; }
.lay3d input { flex: none; }
.lay3d input[type=range] { flex: 1; min-width: 0; }
/* Formation names drawn over the scene. Each sits at the middle of its own
   tops, so where a layer is not drawn there is no name for it either. */
.flabels { position: absolute; inset: 0; pointer-events: none; overflow: hidden; }
/* What the cursor is over. Drawn in the page, never in the scene. */
.tip { position: absolute; display: none; pointer-events: none; z-index: 5;
  font-family: var(--f-data); font-size: 11px; line-height: 1.55; color: var(--ink);
  background: var(--paper); border: 1px solid var(--rule); padding: 6px 9px;
  max-width: 36ch; }
.tip b { color: var(--ink); }
.tip .m { color: var(--ink-3); }
/* The basemap's credit, in the corner it belongs in, never hidden. */
.credit { position: absolute; right: 12px; bottom: 12px; font-family: var(--f-data);
  font-size: 10px; color: var(--ink-2); background: var(--paper);
  border: 1px solid var(--rule); padding: 2px 6px; pointer-events: none; }
.credit:empty { display: none; }
.lay3d select { font: inherit; font-size: 11px; border: 1px solid var(--rule);
  background: var(--paper); color: var(--ink); padding: 2px 4px; }
.panel .cnt { font-weight: 400; letter-spacing: 0; text-transform: none; color: var(--ink-3); }
.filters { font-family: var(--f-data); font-size: 11px; }
.filters details { border-top: 1px solid var(--rule); padding: 4px 0; }
.filters summary { cursor: pointer; color: var(--ink-2); letter-spacing: .08em;
  text-transform: uppercase; font-size: 10px; padding: 2px 0; }
.filters label { display: flex; align-items: center; gap: 6px; padding: 1px 0; }
.filters label .n { margin-left: auto; color: var(--ink-3); }
.filters .sym { width: 14px; height: 14px; flex: none; }
.filters input[type=number], .filters input[type=text], .filters select {
  font: inherit; font-size: 11px; border: 1px solid var(--rule); background: var(--paper);
  color: var(--ink); padding: 2px 4px; width: 100%; }
.filters .row { display: flex; gap: 6px; align-items: center; padding: 2px 0; }
.filters .row span { color: var(--ink-3); white-space: nowrap; }
.filters .act { display: flex; gap: 6px; padding: 8px 0 2px; }
.filters button, .wellcard button { font-family: var(--f-data); font-size: 10px;
  letter-spacing: .1em; text-transform: uppercase; background: none;
  border: 1px solid var(--rule); color: var(--ink-2); cursor: pointer; padding: 4px 8px; }
.filters button.go { background: var(--redline); border-color: var(--redline); color: #fff; }
.filters button:hover, .wellcard button:hover { color: var(--ink); border-color: var(--redline); }
.wellcard { border: 1px solid var(--redline); padding: 10px 11px; margin-bottom: 14px;
  font-family: var(--f-data); font-size: 11px; line-height: 1.55; }
.wellcard h4 { font-size: 12px; margin: 0 0 4px; color: var(--ink); }
.wellcard .m { color: var(--ink-3); }
.wellcard dl { margin: 6px 0; display: grid; grid-template-columns: auto 1fr; gap: 1px 8px; }
.wellcard dt { color: var(--ink-3); }
.wellcard dd { margin: 0; }
.wellcard ul { margin: 4px 0 6px; padding-left: 14px; }
.wellcard li a { color: var(--ink); cursor: pointer; text-decoration: underline dotted; }
.wellcard .act { display: flex; gap: 6px; margin-top: 8px; }
.flabel { position: absolute; transform: translate(-50%, -50%);
  font-family: var(--f-data); font-size: 10px; letter-spacing: .1em;
  text-transform: uppercase; color: var(--ink); background: var(--paper);
  border: 1px solid var(--rule); padding: 1px 5px; white-space: nowrap;
  display: none; }
.legend3d .n { margin-left: auto; color: var(--ink-3); padding-left: 8px; }
.legend3d .d { display: block; font-style: normal; color: var(--ink-3); font-size: 10px; }
.legend3d h4 { font-size: 10px; letter-spacing: .14em; text-transform: uppercase;
  color: var(--ink-3); margin: 0 0 6px; font-weight: 400; }
"""

SCRIPT = r"""
function gossansStrata() {
  var host = document.getElementById("scene");
  if (!host) return;
  var hud = document.getElementById("hud"), legend = document.getElementById("legend"),
      ctl = document.getElementById("ctl"), note = document.getElementById("note");

  function fail(msg) { hud.textContent = msg; }
  if (!window.THREE) { fail("The 3D library did not load, so this view cannot draw."); return; }

  var EXAG = 15, showPaths = true, onlySurveyed = false, showSurfaces = false;
  var groundMode = "relief", groundOpacity = 0.85, showGrid = true, showLabels = false;
  var heads = [], hasPathArr = null, topsPerWell = null, pendingPreset = null;
  var filt = null, isolated = -1, padSet = null, shownCount = 0;
  var showContours = false;
  var hiddenNone = false, labels = [], combine = false;
  var data = null, surf = null, terr = null, plss = null, hidden = {};
  var renderer, scene, camera, root, tops = [], lines = [], meshes = [];
  var gridLines = null;

  Promise.all([
    fetch("/data/strata.json").then(function (r) {
      if (!r.ok) throw new Error(r.status); return r.json(); }),
    // The surfaces are optional. If they fail to load the measured view still
    // works, which is the right way round for a layer that is inference.
    fetch("/data/surfaces.json").then(function (r) {
      return r.ok ? r.json() : null; }).catch(function () { return null; }),
    // The ground and the survey grid are both optional in the same way: if
    // either fails the measured view still stands, which is the right way
    // round for context around the measurements.
    fetch("/data/terrain.json").then(function (r) {
      return r.ok ? r.json() : null; }).catch(function () { return null; }),
    (function () {
      // Shared with the map on the same page, which wants the same megabyte.
      var g = window.gossansData = window.gossansData || {};
      if (!g.townships)
        g.townships = fetch("/data/plss_townships.geojson")
          .then(function (r) { return r.ok ? r.json() : null; });
      return g.townships.catch(function () { return null; });
    })()
  ]).then(function (both) {
    data = both[0]; surf = both[1]; terr = both[2]; plss = both[3]; build();
  }).catch(function () {
    fail("Could not load the strata data.");
  });

  function controls() {
    // What is in the scene is one list, in the legend. What is done to the
    // whole scene - how far it is stretched, which wells are in it at all,
    // where the camera sits - is here.
    ctl.innerHTML =
      '<label class="ctl">Vertical exaggeration <input id="ex" type="range" min="1" max="40" step="1" value="' + EXAG + '"> <b id="exv">' + EXAG + '&times;</b></label>' +
      '<label class="ctl"><input id="cs" type="checkbox"> Only wells with a survey</label>' +
      '<button class="ctl" id="reset" type="button">Reset view</button>';
    layers();
    document.getElementById("ex").addEventListener("input", function (e) {
      setExag(+e.target.value);
    });
    document.getElementById("cs").addEventListener("change", function (e) {
      onlySurveyed = e.target.checked; rebuild();
    });
    var cu = document.getElementById("cu");
    if (cu) cu.addEventListener("change", function (e) {
      combine = e.target.checked; drawLegend();
    });
    document.getElementById("allstrata").addEventListener("click", function () {
      // Hiding every formation leaves the wellbores, which is the useful
      // state: the holes on their own, with nothing draped on them.
      var anyShown = data.formations.some(function (f, i) { return !hidden[i]; });
      data.formations.forEach(function (f, i) { hidden[i] = anyShown; });
      this.textContent = anyShown ? "Show all" : "Hide all";
      drawLegend();
      applyVisible();
    });
    document.getElementById("reset").addEventListener("click", home);
  }

  // ---------------------------------------------------------- symbols
  // Drawn once each on a small canvas. Filled shapes for what produces,
  // hollow ones for what does not, in the palette the rest of the page uses.
  var SYMBOLS = {
    0: {shape: "circle",   fill: "#b7532e", name: "oil"},
    1: {shape: "triangle", fill: "#54606b", name: "gas"},
    2: {shape: "diamond",  fill: "#d18a4d", name: "coalbed methane"},
    3: {shape: "down",     fill: null,      name: "injection", stroke: "#23292f"},
    4: {shape: "cross",    fill: null,      name: "dry hole", stroke: "#23292f"},
    5: {shape: "square",   fill: "#4f6b78", name: "water"},
    6: {shape: "square",   fill: null,      name: "monitor", stroke: "#8a9098"},
    7: {shape: "circle",   fill: null,      name: "other", stroke: "#8a9098"}
  };
  var symbolCache = {};
  function symbol(type) {
    if (symbolCache[type]) return symbolCache[type];
    var d = SYMBOLS[type] || SYMBOLS[7], S = 32, c = document.createElement("canvas");
    c.width = c.height = S;
    var g = c.getContext("2d"), r = 11, m = S / 2;
    g.lineWidth = 3; g.strokeStyle = d.stroke || "#f7f4ef"; g.fillStyle = d.fill || "rgba(0,0,0,0)";
    g.beginPath();
    if (d.shape === "circle") g.arc(m, m, r, 0, Math.PI * 2);
    else if (d.shape === "triangle") { g.moveTo(m, m - r); g.lineTo(m + r, m + r * 0.8); g.lineTo(m - r, m + r * 0.8); g.closePath(); }
    else if (d.shape === "down") { g.moveTo(m, m + r); g.lineTo(m + r, m - r * 0.8); g.lineTo(m - r, m - r * 0.8); g.closePath(); }
    else if (d.shape === "diamond") { g.moveTo(m, m - r); g.lineTo(m + r, m); g.lineTo(m, m + r); g.lineTo(m - r, m); g.closePath(); }
    else if (d.shape === "square") g.rect(m - r * 0.85, m - r * 0.85, r * 1.7, r * 1.7);
    else if (d.shape === "cross") { g.arc(m, m, r, 0, Math.PI * 2); g.moveTo(m - r * 0.7, m - r * 0.7); g.lineTo(m + r * 0.7, m + r * 0.7); g.moveTo(m + r * 0.7, m - r * 0.7); g.lineTo(m - r * 0.7, m + r * 0.7); }
    if (d.fill) { g.fill(); g.strokeStyle = "#f7f4ef"; g.lineWidth = 2.5; g.stroke(); }
    else g.stroke();
    var tex = new THREE.CanvasTexture(c);
    symbolCache[type] = { tex: tex, url: c.toDataURL(), name: d.name };
    return symbolCache[type];
  }

  // Symbols shrink and fade as the camera pulls back, so fifty thousand of
  // them are a texture at basin scale and a legible mark at pad scale.
  function sizeHeads() {
    var size = Math.max(4, Math.min(14, 14 * 12000 / Math.max(dist, 1)));
    var op = Math.max(0.6, Math.min(1, 40000 / Math.max(dist, 1)));
    heads.forEach(function (h) { h.material.size = size; h.material.opacity = op; });
  }

  // ---------------------------------------------------------- filters
  // The facts a well carries, as filed, and a predicate over them. Product
  // is the one derived thing: which of oil, gas or water a well has mostly
  // reported, with gas counted at six thousand cubic feet to the barrel.
  function product(wi) {
    var W = data.wells, o = W.oil[wi], g = W.gas[wi] / 6, w = W.water[wi];
    if (!o && !g && !w) return 3;                 // nothing reported
    if (o >= g && o >= w) return 0;
    if (g >= o && g >= w) return 1;
    return 2;                                     // water only, or mostly
  }
  var PRODUCTS = ["mostly oil", "mostly gas", "mostly water", "nothing reported"];

  function passes(wi) {
    var W = data.wells, f = filt;
    if (f.type && !f.type[W.type[wi]]) return false;
    if (f.prod && !f.prod[product(wi)]) return false;
    if (f.traj && W.traj[wi] >= 0 && !f.traj[W.traj[wi]]) return false;
    if (f.state && !f.state[W.state[wi]]) return false;
    if (f.first0 && (!W.first[wi] || W.first[wi] < f.first0)) return false;
    if (f.first1 && (!W.first[wi] || W.first[wi] > f.first1)) return false;
    if (f.last0 && (!W.last[wi] || W.last[wi] < f.last0)) return false;
    if (f.oil && W.oil[wi] < f.oil) return false;
    if (f.gas && W.gas[wi] < f.gas) return false;
    if (f.op && (data.operators[W.op[wi]] || "").toUpperCase().indexOf(f.op) < 0) return false;
    if (f.sma !== undefined && f.sma !== null && W.sma[wi] !== f.sma) return false;
    return true;
  }

  function counts(key, n) {
    var W = data.wells, c = new Array(n).fill(0);
    for (var i = 0; i < W.api.length; i++) {
      var v = key === "prod" ? product(i) : W[key][i];
      if (v >= 0 && v < n) c[v]++;
    }
    return c;
  }

  function filters() {
    var box = document.getElementById("filters");
    if (!box || !data) return;
    var W = data.wells;
    function checks(name, labels, key) {
      var c = counts(key, labels.length);
      return '<details' + (key === "type" ? " open" : "") + '><summary>' + name + '</summary>' + labels.map(function (l, i) {
        var sym = key === "type" ? '<img class="sym" src="' + symbol(i).url + '" alt=""> ' : "";
        return c[i] ? '<label><input type="checkbox" data-f="' + key + '" value="' + i + '" checked> ' +
               sym + l + '<span class="n">' + c[i].toLocaleString() + '</span></label>' : "";
      }).join("") + "</details>";
    }
    var states = {};
    W.state.forEach(function (st) { states[st] = (states[st] || 0) + 1; });
    var years = W.first.filter(function (y) { return y > 0; });
    var y0 = years.length ? Math.min.apply(null, years) : 1900, y1 = years.length ? Math.max.apply(null, years) : 2030;
    var ops = data.operators.slice().sort();
    var smas = data.surface_agencies || [];
    box.innerHTML =
      checks("Type", data.types, "type") +
      checks("Product", PRODUCTS, "prod") +
      checks("Trajectory", data.trajectories, "traj") +
      '<details><summary>State</summary>' + Object.keys(states).sort().map(function (st) {
        return '<label><input type="checkbox" data-f="state" value="' + st + '" checked> ' + st +
               '<span class="n">' + states[st].toLocaleString() + '</span></label>'; }).join("") + '</details>' +
      '<details open><summary>Produced</summary>' +
      '<div class="row"><span>first</span><input type="number" id="f-first0" placeholder="' + y0 + '" min="' + y0 + '" max="' + y1 + '">' +
      '<span>to</span><input type="number" id="f-first1" placeholder="' + y1 + '" min="' + y0 + '" max="' + y1 + '"></div>' +
      '<div class="row"><span>still producing in</span><input type="number" id="f-last0" placeholder="any" min="' + y0 + '" max="' + y1 + '"></div>' +
      '<div class="row"><span>oil &ge;</span><input type="number" id="f-oil" placeholder="0" min="0" step="1000"><span>bbl</span></div>' +
      '<div class="row"><span>gas &ge;</span><input type="number" id="f-gas" placeholder="0" min="0" step="1000"><span>mcf</span></div>' +
      '</details>' +
      '<details open><summary>Company</summary>' +
      '<input type="text" id="f-op" list="f-ops" placeholder="operator contains&hellip;">' +
      '<datalist id="f-ops">' + ops.slice(0, 400).map(function (o) { return '<option value="' + o.replace(/"/g, "&quot;") + '">'; }).join("") + '</datalist>' +
      '</details>' +
      '<details><summary>Surface</summary>' + (smas.length
        ? '<select id="f-sma"><option value="">any surface</option>' + smas.map(function (a, i) {
            return '<option value="' + i + '">' + a + '</option>'; }).join("") + '</select>'
        : '<span class="m">Surface agency not yet loaded for this region.</span>') +
      '</details>' +
      '<div class="act"><button type="button" class="go" id="f-apply">Apply</button>' +
      '<button type="button" id="f-reset">Reset</button></div>';
    document.getElementById("f-apply").addEventListener("click", applyFilters);
    document.getElementById("f-reset").addEventListener("click", function () {
      filt = null; clearIsolate(false); filters(); rebuild();
    });
    box.querySelectorAll("input[type=number], input[type=text]").forEach(function (el) {
      el.addEventListener("keydown", function (e) { if (e.key === "Enter") applyFilters(); });
    });
  }

  function applyFilters() {
    var box = document.getElementById("filters"), f = {};
    function set(key) {
      var boxes = box.querySelectorAll('input[data-f="' + key + '"]');
      if (!boxes.length) return;
      var any = false, m = {};
      boxes.forEach(function (b) { if (b.checked) { m[b.value] = true; any = true; } });
      if (Object.keys(m).length < boxes.length) f[key] = m;
    }
    set("type"); set("prod"); set("traj"); set("state");
    var num = function (id) { var v = document.getElementById(id).value; return v === "" ? 0 : +v; };
    f.first0 = num("f-first0"); f.first1 = num("f-first1"); f.last0 = num("f-last0");
    f.oil = num("f-oil"); f.gas = num("f-gas");
    f.op = document.getElementById("f-op").value.trim().toUpperCase();
    var smaSel = document.getElementById("f-sma");
    f.sma = (smaSel && smaSel.value !== "") ? +smaSel.value : null;
    filt = f;
    clearIsolate(false);
    rebuild();
  }

  // ---------------------------------------------------------- isolate
  // One well and its pad: the wells within 250 m of it on the ground. The
  // camera goes to it, the ground round it wears tiles at pad scale, and the
  // panel says what the filings hold for it.
  function isolate(wi) {
    if (window.gossansDebug) console.debug("isolate", wi, new Error().stack.split(String.fromCharCode(10)).slice(2, 5).join(" <- "));
    var W = data.wells, nW = W.api.length;
    padSet = new Uint8Array(nW);
    var x = W.x[wi], y = W.y[wi], pad = [];
    for (var i = 0; i < nW; i++) {
      var dx = W.x[i] - x, dy = W.y[i] - y;
      if (dx * dx + dy * dy <= 250 * 250) { padSet[i] = 1; pad.push(i); }
    }
    // Fifteen times is right for a basin a hundred kilometres across and
    // wrong for a pad, where it turns a bench into a cliff. Three, while a
    // well is isolated, and back to what it was afterwards.
    if (isolated < 0) exagBefore = EXAG;
    setExag(3);
    isolated = wi;
    rebuild();
    target.set(x, y, (W.ground[wi] === null ? 0 : W.ground[wi]) * EXAG);
    dist = 2500; yaw = NORTH_UP; pitch = 1.0; place();
    markWell(wi);
    wellCard(wi, pad);
    if (history.replaceState) history.replaceState(null, "", "#well=" + W.api[wi]);
  }

  function clearIsolate(redraw) {
    if (isolated < 0 && !padSet) return;
    isolated = -1; padSet = null;
    unmark();
    setExag(exagBefore);
    var card = document.getElementById("wellcard");
    if (card) { card.hidden = true; card.innerHTML = ""; }
    if (redraw !== false) { rebuild(); home(); }
  }

  function wellCard(wi, pad) {
    var card = document.getElementById("wellcard");
    if (!card) return;
    var W = data.wells, ops = data.operators || [], forms = formationsOf(wi);
    var smas = data.surface_agencies || [];
    var yr = function (v) { return v ? v : "\u2014"; };
    card.innerHTML =
      "<h4>" + (W.name[wi] || "unnamed") + "</h4>" +
      '<span class="m">API ' + W.api[wi] + " &middot; " + W.state[wi] + "</span>" +
      "<dl>" +
      "<dt>Operator</dt><dd>" + (ops[W.op[wi]] || "\u2014") + "</dd>" +
      "<dt>Type</dt><dd>" + data.types[W.type[wi]] + (W.traj[wi] >= 0 ? ", " + data.trajectories[W.traj[wi]] : "") + "</dd>" +
      "<dt>Completed in</dt><dd>" + (forms.length ? forms.join(", ") : "not filed") + "</dd>" +
      "<dt>Produced</dt><dd>" + yr(W.first[wi]) + " to " + yr(W.last[wi]) + (W.months[wi] ? " (" + W.months[wi] + " months)" : "") + "</dd>" +
      "<dt>Reported</dt><dd>" + W.oil[wi].toLocaleString() + " bbl oil, " + W.gas[wi].toLocaleString() + " mcf gas, " + W.water[wi].toLocaleString() + " bbl water</dd>" +
      "<dt>Surface</dt><dd>" + (W.sma[wi] >= 0 ? smas[W.sma[wi]] : "agency not yet loaded") + "</dd>" +
      "<dt>Ground</dt><dd>" + Math.round(W.ground[wi]).toLocaleString() + " m, " + (W.datum[wi] === 1 ? "from 3DEP" : "as filed") + "</dd>" +
      "<dt>Tops</dt><dd>" + (topsPerWell[wi] || 0) + " drawn &middot; " + (hasPathArr[wi] ? "survey on file" : "no survey; vertical") + "</dd>" +
      "</dl>" +
      (pad.length > 1
        ? "<b>Pad</b> <span class=\"m\">" + (pad.length - 1) + " other well" + (pad.length > 2 ? "s" : "") + " within 250 m</span><ul>" +
          pad.filter(function (p) { return p !== wi; }).slice(0, 12).map(function (p) {
            return '<li><a data-wi="' + p + '">' + (W.name[p] || W.api[p]) + "</a> <span class=\"m\">" + data.types[W.type[p]] + "</span></li>";
          }).join("") + (pad.length > 13 ? "<li class=\"m\">and " + (pad.length - 13) + " more</li>" : "") + "</ul>"
        : "<span class=\"m\">No other well within 250 m.</span><br>") +
      '<span class="m gnote">Ground refines toward the camera from the one-metre model; the imagery is pinned to it tile by tile.</span>' +
      '<div class="act"><button type="button" id="w-all">Show all wells</button></div>';
    card.hidden = false;
    card.querySelectorAll("a[data-wi]").forEach(function (a) {
      a.addEventListener("click", function () { isolate(+a.getAttribute("data-wi")); });
    });
    document.getElementById("w-all").addEventListener("click", function () { clearIsolate(true); });
  }

  //: every layer in the scene, with the flag it sets and what it is called.
  var LAYERS = [
    {id: "ck", label: "Township grid", get: function () { return showGrid; },
     set: function (v) { showGrid = v; }},
    {id: "cp", label: "Wellbores", get: function () { return showPaths; },
     set: function (v) { showPaths = v; }},
    {id: "cl", label: "Formation labels", get: function () { return showLabels; },
     set: function (v) { showLabels = v; }},
    {id: "cc", label: "Contours", get: function () { return showContours; },
     set: function (v) { showContours = v; if (terrain) terrain.setContours(v); }},
    {id: "cf", label: "Interpolated surfaces", get: function () { return showSurfaces; },
     set: function (v) { showSurfaces = v; }}
  ];

  //: what the ground can wear. Terms read and recorded in the source
  //: register before any of these was used; the credit is drawn on the scene.
  var BASEMAPS = {
    off:     {label: "Off"},
    relief:  {label: "Shaded relief (3DEP)", credit: "Relief: USGS 3DEP"},
    osm:     {label: "OpenStreetMap", zmax: 19,
              url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
              credit: "&copy; OpenStreetMap contributors"},
    imagery: {label: "Aerial (USGS)", zmax: 16,
              url: "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}",
              credit: "Imagery: USDA, USGS The National Map"},
    topo:    {label: "Topographic (USGS)", zmax: 16,
              url: "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}",
              credit: "USGS The National Map: Topo"}
  };

  function layers() {
    var box = document.getElementById("layers3d");
    if (!box) return;
    var sel = '<label>Ground <select id="cgm">' + Object.keys(BASEMAPS).map(function (k) {
      return '<option value="' + k + '"' + (k === groundMode ? " selected" : "") + ">" +
             BASEMAPS[k].label + "</option>";
    }).join("") + "</select></label>";
    sel += '<label>Ground opacity <input id="cgo" type="range" min="0.2" max="1" step="0.05" value="' + groundOpacity + '"></label>';
    box.innerHTML = sel + LAYERS.map(function (L) {
      return '<label><input id="' + L.id + '" type="checkbox"' +
             (L.get() ? " checked" : "") + "> " + L.label + "</label>";
    }).join("");
    document.getElementById("cgm").addEventListener("change", function (e) {
      groundMode = e.target.value; applyGround();
    });
    document.getElementById("cgo").addEventListener("input", function (e) {
      groundOpacity = +e.target.value; applyGround();
    });
    LAYERS.forEach(function (L) {
      document.getElementById(L.id).addEventListener("change", function (e) {
        L.set(e.target.checked);
        if (L.id === "cf")
          hud.innerHTML = showSurfaces
            ? "Surfaces are <b>interpolated</b>: a weighted average of nearby filed "
              + "tops, not measurements. They stop where well control does."
            : "Measured tops and wellbores only. Nothing is drawn between wells.";
        applyVisible();
      });
    });
  }

  function build() {
    controls();
    filters();
    renderer = new THREE.WebGLRenderer({ canvas: host, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, 1, 10, 4000000);
    root = new THREE.Group();
    scene.add(root);
    rebuild();
    home();
    resize();
    addEventListener("resize", resize);
    // The pane may be hidden when this runs, in which case the canvas has no
    // size until the switcher shows it and calls this back.
    window.gossansViews = window.gossansViews || {};
    window.gossansViews.resize3d = function(){ resize(); home(); };
    // Where the camera is, for anyone checking the view from outside.
    // Put the camera somewhere: {dist, pitch, yaw, target: [x, y, z]}.
    window.gossansViews.look = function (v) {
      if (v.target) target.set(v.target[0], v.target[1], v.target[2]);
      if (v.dist !== undefined) dist = v.dist;
      if (v.pitch !== undefined) pitch = Math.max(0.05, Math.min(Math.PI - 0.05, v.pitch));
      if (v.yaw !== undefined) yaw = v.yaw;
      place();
    };
    window.gossansViews.camera = function () {
      return { dist: dist, pitch: pitch, yaw: yaw, isolated: isolated,
               target: [target.x, target.y, target.z] };
    };
    // The Surface tab is this same scene wearing a basemap with the strata
    // put away; the Three dimensions tab is the strata on shaded relief.
    window.gossansViews.preset3d = function (name) {
      if (!data) { pendingPreset = name; return; }
      if (name === "surface") {
        // Wellbores are underground; on a surface view they are haze. The
        // wellheads stay, faint, so a hover still names the well.
        groundMode = "imagery"; groundOpacity = 0.95; showLabels = false; showSurfaces = false;
        showGrid = true; showPaths = false;
        data.formations.forEach(function (f, i) { hidden[i] = true; });
        yaw = NORTH_UP; pitch = OVERHEAD;
      } else {
        groundMode = "relief"; groundOpacity = 0.6; showLabels = false; showPaths = true;
        data.formations.forEach(function (f, i) { hidden[i] = false; });
        yaw = NORTH_UP; pitch = OVERHEAD;
      }
      layers(); drawLegend(); syncAllButton(); applyGround(); applyVisible(); place();
    };
    var pp = pendingPreset || window.gossansViews.pendingPreset;
    pendingPreset = null; window.gossansViews.pendingPreset = null;
    if (pp) window.gossansViews.preset3d(pp);
    // A link straight to a well: #well=<API>, on arrival or later.
    window.gossansViews.isolate = function (api) {
      var wi = data.wells.api.indexOf(String(api));
      if (wi < 0) return false;
      if (groundMode === "relief" || groundMode === "off") { groundMode = "imagery"; layers(); applyGround(); }
      isolate(wi);
      return true;
    };
    function fromWellHash() {
      var mw = /^#well=(\d{10})$/.exec(location.hash);
      if (mw) window.gossansViews.isolate(mw[1]);
    }
    fromWellHash();
    addEventListener("hashchange", fromWellHash);
    bindCamera();
    renderer.setAnimationLoop(function () {
      renderer.render(scene, camera);
      placeLabels();
    });

    var c = data.counts;
    document.getElementById("nsurv").textContent = c.not_surveyed.toLocaleString();
    // The prose quotes the counts rather than carrying numbers that go
    // stale the first time the region or the filings change.
    [["c-prod", c.wells_with_producing_formation],
     ["c-multi", c.wells_completed_in_more_than_one_formation],
     ["c-none", c.wells_with_no_producing_formation_filed],
     ["c-notdrawn", c.wells_producing_from_a_formation_not_drawn]
    ].forEach(function (pair) {
      var el = document.getElementById(pair[0]);
      if (el && pair[1] !== undefined) el.textContent = pair[1].toLocaleString();
    });
    if (terr && terr.step_m) {
      var stepTxt = Math.round(terr.step_m) + " m";
      Array.prototype.forEach.call(document.querySelectorAll(".t-step"),
        function (el) { el.textContent = stepTxt; });
    }
    var ec = c.elevation_check || {};
    function m(v) { return v === null || v === undefined ? "?" : (v > 0 ? "+" : v < 0 ? "−" : "") + Math.abs(v).toFixed(0) + " m"; }
    [["e-n", (ec.wells || 0).toLocaleString()], ["e-med", m(ec.median_m)],
     ["e-q1", m(ec.q1_m)], ["e-q3", m(ec.q3_m)],
     ["e-big", (ec.beyond_100_m || 0).toLocaleString()],
     ["e-3dep", (c.datum_3dep || 0).toLocaleString()]
    ].forEach(function (pair) {
      var el = document.getElementById(pair[0]);
      if (el) el.textContent = pair[1];
    });
    note.textContent = "Generated " + data.generated + " from " +
      c.tops.toLocaleString() + " filed formation tops across " +
      c.wells.toLocaleString() + " wells. " + c.surveyed.toLocaleString() +
      " have a directional survey; " + c.not_surveyed.toLocaleString() + " do not. " +
      "Paths are thinned to " + c.path_points_kept_per_well + " stations each, dropping " +
      c.survey_stations_dropped_by_thinning.toLocaleString() + " stations. " +
      c.tops_dropped_rare_formation.toLocaleString() +
      " tops in formations with fewer than 25 records are not shown.";
  }

  function mid(a) {
    if (!a.length) return 0;
    var b = a.slice().sort(function (p, q) { return p - q; });
    return b[Math.floor(b.length / 2)];
  }

  function rebuild() {
    while (root.children.length) root.remove(root.children[0]);
    tops = []; lines = [];
    // Format 2: parallel arrays by well index, tops per formation, paths for
    // the surveyed few. One object per well was a megabyte for two and a
    // half thousand wells; the region has fifty thousand.
    var W = data.wells, nW = W.api.length;
    var hasPath = new Uint8Array(nW), pathOf = {};
    data.paths.forEach(function (pr) { hasPath[pr.w] = 1; pathOf[pr.w] = pr.p; });
    // What is drawn: an isolated well and its pad, or whatever passes the
    // filters. The survey-only switch applies on top of either.
    var pass = new Uint8Array(nW);
    shownCount = 0;
    for (var pi = 0; pi < nW; pi++) {
      var ok = padSet ? !!padSet[pi] : (!filt || passes(pi));
      if (ok && onlySurveyed && !hasPath[pi]) ok = false;
      pass[pi] = ok ? 1 : 0;
      if (ok) shownCount++;
    }
    function shown(wi) { return pass[wi] === 1; }
    var wc = document.getElementById("wellcount");
    if (wc) wc.textContent = shownCount.toLocaleString() + " of " + nW.toLocaleString();

    // Tops, one point cloud per formation so the legend can toggle them.
    var deepest = new Float32Array(nW).fill(Infinity), hasTop = new Uint8Array(nW);
    topsPerWell = new Uint16Array(nW);
    data.formations.forEach(function (f, fi) {
      var T = data.tops[fi], pts = [], pwi = [], pti = [];
      for (var i = 0; i < T.w.length; i++) {
        var wi = T.w[i], z = T.z[i];
        if (z < deepest[wi]) deepest[wi] = z;
        hasTop[wi] = 1;
        topsPerWell[wi]++;
        if (!shown(wi)) continue;
        pts.push(W.x[wi], W.y[wi], z);
        pwi.push(wi); pti.push(i);
      }
      if (!pts.length) return;
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
      // Sized in screen pixels, not world units. At 90 m across and a
      // camera 100 km away, every top rendered sub-pixel and the scene
      // came up blank.
      var m = new THREE.PointsMaterial({ color: f.colour, size: 3.5,
                                         sizeAttenuation: false });
      var p = new THREE.Points(g, m);
      // The middle of this formation's own tops, which is where its name is
      // written when labels are on.
      var xs = [], ys = [], zs = [];
      for (var q = 0; q < pts.length; q += 3) {
        xs.push(pts[q]); ys.push(pts[q + 1]); zs.push(pts[q + 2]);
      }
      p.userData = { formation: fi, anchor: [mid(xs), mid(ys), mid(zs)],
                     wi: pwi, ti: pti };
      p.renderOrder = -2; tops.push(p); root.add(p);
    });

    // A symbol at every wellhead, on the ground, one point cloud per type,
    // so the kind of well reads at the surface and a hover can name it.
    heads = [];
    var byType = {};
    for (var hw = 0; hw < nW; hw++) {
      if (!shown(hw) || W.ground[hw] === null) continue;
      var ty = W.type[hw];
      if (!byType[ty]) byType[ty] = { p: [], wi: [] };
      byType[ty].p.push(W.x[hw], W.y[hw], W.ground[hw]); byType[ty].wi.push(hw);
    }
    Object.keys(byType).forEach(function (ty) {
      var hg = new THREE.BufferGeometry();
      hg.setAttribute("position", new THREE.Float32BufferAttribute(byType[ty].p, 3));
      var pts = new THREE.Points(hg, new THREE.PointsMaterial({
        map: symbol(+ty).tex, size: 10, sizeAttenuation: false,
        transparent: true, alphaTest: 0.04, depthWrite: false }));
      var hxy = new Float32Array(byType[ty].wi.length * 2);
      for (var hq = 0; hq < byType[ty].wi.length; hq++) { hxy[hq * 2] = byType[ty].p[hq * 3]; hxy[hq * 2 + 1] = byType[ty].p[hq * 3 + 1]; }
      pts.userData = { heads: true, wi: byType[ty].wi, type: +ty, xy: hxy, lift: 0 };
      pts.renderOrder = 2; heads.push(pts); root.add(pts);
    });
    sizeHeads();
    hasPathArr = hasPath;

    // Wellbores, grouped by the formation each well was completed in, so a
    // formation switched off in the legend takes its producers with it. The
    // key is that formation's index, or "none" for a well completed in
    // something this view does not draw or with nothing on file at all.
    var byProd = {};
    function bucket(wi) {
      var k = W.prod[wi] >= 0 ? W.prod[wi] : "none";
      if (!byProd[k]) byProd[k] = { surveyed: [], vertical: [] };
      return byProd[k];
    }
    for (var wi = 0; wi < nW; wi++) {
      if (!shown(wi)) continue;
      var b = bucket(wi), x = W.x[wi], y = W.y[wi], gnd = W.ground[wi];
      if (hasPath[wi]) {
        var P = pathOf[wi];
        for (var i = 3; i < P.length; i += 3) {
          b.surveyed.push(P[i - 3], P[i - 2], P[i - 1], P[i], P[i + 1], P[i + 2]);
        }
        // Many surveys begin below the surface, some kilometres down,
        // because only the lateral was surveyed. The stem up to the ground
        // is drawn in the unsurveyed colour, because that is what it is.
        if (gnd !== null && gnd - P[2] > 30)
          b.vertical.push(x, y, gnd, P[0], P[1], P[2]);
      } else if (hasTop[wi]) {
        // From the ground it was drilled from down to the deepest top filed
        // for it. Vertical over the whole length is an assumption, and the
        // colour and the text both say the survey is missing.
        var top = (gnd !== null) ? gnd : deepest[wi];
        b.vertical.push(x, y, top, x, y, deepest[wi]);
      }
    }
    var pairs = [];
    Object.keys(byProd).forEach(function (k) {
      pairs.push([byProd[k].surveyed, "#54606b", k]);
      pairs.push([byProd[k].vertical, "#8a9098", k]);
    });
    pairs.forEach(function (pair) {
      if (!pair[0].length) return;
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(pair[0], 3));
      var l = new THREE.LineSegments(g, new THREE.LineBasicMaterial({
        color: pair[1], transparent: true, opacity: 0.7 }));
      l.userData = { prod: pair[2] };
      l.renderOrder = -2; lines.push(l); root.add(l);
    });

    buildSurfaces();
    // The ground and the grid cost real time to build and do not depend on
    // any of the switches that cause a rebuild, so they are built once and
    // put back afterwards.
    if (!terrain && terr) terrain = makeTerrain();
    if (terrain) root.add(terrain.group);
    if (gridLines) root.add(gridLines); else buildGrid();
    if (mark) root.add(mark);
    if (terrain) terrain.redrape();
    drawLegend();
    applyScale();
    applyVisible();
  }

  // One mesh per formation, built from the gridded surface. A cell is drawn
  // only where all four of its corners were computed, so the mesh stops at
  // the edge of well control instead of tapering into ground nobody drilled.
  // Colour is mixed toward the page background as the nearest control point
  // gets further away, so thin support looks thin.
  // ---------------------------------------------------------------- ground
  // Scene metres from the strata origin, which is where every other object in
  // this view is placed from.
  function metres() {
    return { lat: 111132.0,
             lon: 111320.0 * Math.cos(data.origin.lat * Math.PI / 180) };
  }

  // The 800 m grid, sampled by longitude and latitude. It is the base level
  // of the pyramid and the answer wherever no finer tile has arrived.
  function coarseAt(lon, lat) {
    if (!terr) return null;
    var fx = (lon - terr.min_lon) / terr.step_lon - 0.5;
    var fy = (lat - terr.min_lat) / terr.step_lat - 0.5;
    var ix = Math.floor(fx), iy = Math.floor(fy);
    if (ix < 0 || iy < 0 || ix >= terr.nx - 1 || iy >= terr.ny - 1) return null;
    var tx = fx - ix, ty = fy - iy;
    var a = terr.z[iy * terr.nx + ix], b = terr.z[iy * terr.nx + ix + 1],
        c = terr.z[(iy + 1) * terr.nx + ix], d = terr.z[(iy + 1) * terr.nx + ix + 1];
    if (a === null || b === null || c === null || d === null) return null;
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty;
  }

  // Height of the ground as drawn, at a scene point: the finest tile there.
  function terrainAt(x, y) {
    if (terrain) return terrain.at(x, y);
    var m = metres();
    return coarseAt(data.origin.lon + x / m.lon, data.origin.lat + y / m.lat);
  }

  // One elevation model, cut into a quadtree of web-mercator tiles that
  // refine toward the camera. The base level is cut from the grid on the
  // page; every finer level is fetched from the one-metre model for exactly
  // the tile's footprint, and a tile splits into four when it grows large on
  // screen. Each imagery tile is pinned to the terrain tile of the same
  // footprint, so photo and elevation cannot drift apart.
  var terrain = null;
  var TILE_N = 49, Z_BASE = 9, Z_MAX = 19, SPLIT = 0.45, INFLIGHT = 6;

  function makeTerrain() {
    var group = new THREE.Group(), tiles = {}, queue = [], inflight = 0;
    var m = metres(), frustum = new THREE.Frustum(), pm = new THREE.Matrix4();
    var base = [], pending = false, drapeTimer = null;
    var loader = new THREE.TextureLoader();
    loader.setCrossOrigin("anonymous");

    function key(z, x, y) { return z + "/" + x + "/" + y; }
    function bounds(z, x, y) {
      var n = 1 << z;
      var lat = function (yy) { return Math.atan(Math.sinh(Math.PI * (1 - 2 * yy / n))) * 180 / Math.PI; };
      return { lon0: x / n * 360 - 180, lon1: (x + 1) / n * 360 - 180, lat0: lat(y + 1), lat1: lat(y) };
    }
    function intervalFor(z) {
      return z <= 9 ? 100 : z <= 10 ? 50 : z <= 12 ? 20 : z <= 14 ? 10 : z <= 16 ? 5 : z <= 17 ? 2 : 1;
    }

    function makeTile(z, x, y, parent) {
      var b = bounds(z, x, y), k = key(z, x, y);
      var t = { z: z, x: x, y: y, key: k, b: b, parent: parent, children: null,
                state: "empty", node: null, dem: null, zmin: 0, zmax: 3000,
                cx: ((b.lon0 + b.lon1) / 2 - data.origin.lon) * m.lon,
                cy: ((b.lat0 + b.lat1) / 2 - data.origin.lat) * m.lat,
                size: (b.lon1 - b.lon0) * m.lon, tex: {}, used: 0 };
      if (parent) { t.zmin = parent.zmin; t.zmax = parent.zmax; }
      tiles[k] = t;
      return t;
    }

    // ---- geometry from a tile's own DEM, rows south to north
    function buildTile(t, dem) {
      var N = TILE_N, b = t.b, dlon = (b.lon1 - b.lon0) / (N - 1), dlat = (b.lat1 - b.lat0) / (N - 1);
      var cell = t.size / (N - 1);
      var lo = Infinity, hi = -Infinity, i, j, k;
      for (k = 0; k < dem.length; k++) { var v = dem[k]; if (!isNaN(v)) { if (v < lo) lo = v; if (v > hi) hi = v; } }
      if (!(hi >= lo)) return false;
      var skirt = 4 * N, nv = N * N + skirt;
      var pos = new Float32Array(nv * 3), ramp = new Float32Array(nv * 3), grey = new Float32Array(nv * 3), uv = new Float32Array(nv * 2);
      var glo = terr ? 900 : lo, ghi = terr ? 2800 : hi;
      for (j = 0; j < N; j++) for (i = 0; i < N; i++) {
        k = j * N + i;
        var lon = b.lon0 + i * dlon, lat = b.lat0 + j * dlat;
        var z = dem[k]; if (isNaN(z)) z = lo;
        pos[k * 3] = (lon - data.origin.lon) * m.lon; pos[k * 3 + 1] = (lat - data.origin.lat) * m.lat; pos[k * 3 + 2] = z;
        var mc = mercator(lon, lat), n = 1 << t.z;
        uv[k * 2] = mc[0] * n - t.x; uv[k * 2 + 1] = 1 - (mc[1] * n - t.y);
        var xw = dem[j * N + Math.max(0, i - 1)], xe = dem[j * N + Math.min(N - 1, i + 1)];
        var ys = dem[Math.max(0, j - 1) * N + i], yn = dem[Math.min(N - 1, j + 1) * N + i];
        if (isNaN(xw)) xw = z; if (isNaN(xe)) xe = z; if (isNaN(ys)) ys = z; if (isNaN(yn)) yn = z;
        var d = cell * 2, nxv = -(xe - xw) / d, nyv = -(yn - ys) / d, len = Math.sqrt(nxv * nxv + nyv * nyv + 1);
        var lit = (nxv * -0.55 + nyv * 0.55 + 0.63) / len, shade = 0.55 + 0.45 * Math.max(0, lit);
        var tt = Math.max(0, Math.min(1, (z - glo) / (ghi - glo)));
        ramp[k * 3] = (0.85 - 0.30 * tt) * shade; ramp[k * 3 + 1] = (0.77 - 0.24 * tt) * shade; ramp[k * 3 + 2] = (0.63 - 0.06 * tt) * shade;
        var g2 = 0.72 + 0.28 * Math.max(0, lit);
        grey[k * 3] = grey[k * 3 + 1] = grey[k * 3 + 2] = g2;
      }
      // Skirts: the edge ring again, dropped, so neighbouring tiles at a
      // different level do not show a crack of sky between them.
      var drop = Math.max(3, t.size * 0.03), sk = N * N, edges = [];
      for (i = 0; i < N; i++) edges.push(i);                       // south row
      for (j = 0; j < N; j++) edges.push(j * N + N - 1);           // east column
      for (i = N - 1; i >= 0; i--) edges.push((N - 1) * N + i);    // north row
      for (j = N - 1; j >= 0; j--) edges.push(j * N);              // west column
      for (k = 0; k < skirt; k++) {
        var src = edges[k], dst = sk + k;
        pos[dst * 3] = pos[src * 3]; pos[dst * 3 + 1] = pos[src * 3 + 1]; pos[dst * 3 + 2] = pos[src * 3 + 2] - drop;
        for (var c3 = 0; c3 < 3; c3++) { ramp[dst * 3 + c3] = ramp[src * 3 + c3]; grey[dst * 3 + c3] = grey[src * 3 + c3]; }
        uv[dst * 2] = uv[src * 2]; uv[dst * 2 + 1] = uv[src * 2 + 1];
      }
      var idx = [];
      for (j = 0; j < N - 1; j++) for (i = 0; i < N - 1; i++) {
        var q = j * N + i;
        idx.push(q, q + N, q + 1, q + 1, q + N, q + N + 1);
      }
      for (k = 0; k < skirt; k++) {
        var e0 = edges[k], e1 = edges[(k + 1) % skirt], s0 = sk + k, s1 = sk + (k + 1) % skirt;
        idx.push(e0, s0, e1, e1, s0, s1);
      }
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
      g.setAttribute("uv", new THREE.BufferAttribute(uv, 2));
      g.setIndex(idx);
      g.userData = { ramp: new THREE.BufferAttribute(ramp, 3), grey: new THREE.BufferAttribute(grey, 3), uv0: uv };
      g.setAttribute("color", g.userData.ramp);
      var mesh = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
        vertexColors: true, side: THREE.DoubleSide, transparent: true, opacity: groundOpacity,
        depthWrite: true, polygonOffset: true, polygonOffsetFactor: 2, polygonOffsetUnits: 2 }));
      mesh.renderOrder = 0;
      var node = new THREE.Group();
      node.add(mesh);
      node.userData = { mesh: mesh, lines: null, drop: drop };
      t.dem = dem; t.zmin = lo; t.zmax = hi; t.node = node; t.state = "ready";
      node.visible = false;
      group.add(node);
      buildContours(t);
      applyMode(t);
      scheduleDrape();
      return true;
    }

    // ---- contours per tile, by marching squares over its own DEM
    function buildContours(t) {
      var N = TILE_N, dem = t.dem, b = t.b, dlon = (b.lon1 - b.lon0) / (N - 1), dlat = (b.lat1 - b.lat0) / (N - 1);
      var interval = intervalFor(t.z), pts = [], cols = [];
      function X(i) { return (b.lon0 + i * dlon - data.origin.lon) * m.lon; }
      function Y(j) { return (b.lat0 + j * dlat - data.origin.lat) * m.lat; }
      var lo = t.zmin, hi = t.zmax;
      for (var level = Math.ceil(lo / interval) * interval; level <= hi; level += interval) {
        var shade = (level % (interval * 5) === 0) ? 0.25 : 0.55;
        for (var j = 0; j < N - 1; j++) for (var i = 0; i < N - 1; i++) {
          var a = dem[j * N + i], bb = dem[j * N + i + 1], c = dem[(j + 1) * N + i + 1], d = dem[(j + 1) * N + i];
          if (isNaN(a) || isNaN(bb) || isNaN(c) || isNaN(d)) continue;
          var idx = (a >= level ? 1 : 0) | (bb >= level ? 2 : 0) | (c >= level ? 4 : 0) | (d >= level ? 8 : 0);
          if (idx === 0 || idx === 15) continue;
          var e = {};
          if ((a >= level) !== (bb >= level)) e.b = [X(i + (level - a) / (bb - a)), Y(j)];
          if ((bb >= level) !== (c >= level)) e.r = [X(i + 1), Y(j + (level - bb) / (c - bb))];
          if ((d >= level) !== (c >= level)) e.t = [X(i + (level - d) / (c - d)), Y(j + 1)];
          if ((a >= level) !== (d >= level)) e.l = [X(i), Y(j + (level - a) / (d - a))];
          var pairs = {1: [["l", "b"]], 2: [["b", "r"]], 3: [["l", "r"]], 4: [["r", "t"]], 5: [["l", "t"], ["b", "r"]],
                       6: [["b", "t"]], 7: [["l", "t"]], 8: [["t", "l"]], 9: [["b", "t"]], 10: [["l", "b"], ["t", "r"]],
                       11: [["r", "t"]], 12: [["l", "r"]], 13: [["b", "r"]], 14: [["l", "b"]]}[idx];
          pairs.forEach(function (pr) {
            var p0 = e[pr[0]], p1 = e[pr[1]];
            if (!p0 || !p1) return;
            pts.push(p0[0], p0[1], level + 0.3, p1[0], p1[1], level + 0.3);
            cols.push(shade, shade, shade, shade, shade, shade);
          });
        }
      }
      if (!pts.length) return;
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
      g.setAttribute("color", new THREE.Float32BufferAttribute(cols, 3));
      var lines = new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.85 }));
      lines.renderOrder = 2;
      lines.visible = showContours;
      t.node.add(lines);
      t.node.userData.lines = lines;
    }

    // ---- what a tile wears
    function applyMode(t) {
      if (!t.node) return;
      var mesh = t.node.userData.mesh, g = mesh.geometry, mat = mesh.material;
      if (groundMode === "relief" || groundMode === "off") {
        g.setAttribute("color", g.userData.ramp); mat.map = null;
      } else {
        g.setAttribute("color", g.userData.grey);
        // Past the basemap's last zoom a tile wears its ancestor's image,
        // cropped to its own quarter of it, so the ground keeps refining
        // after the photographs stop.
        var bm = BASEMAPS[groundMode], d = Math.max(0, t.z - bm.zmax), f = 1 << d;
        var ax = t.x >> d, ay = t.y >> d, tk = groundMode + ":" + d;
        if (!t.tex[tk]) {
          var url = bm.url.replace("{z}", t.z - d).replace("{x}", ax).replace("{y}", ay);
          t.tex[tk] = loader.load(url, function () { t.tex[tk].loaded = true; applyMode(t); });
          t.tex[tk].anisotropy = 4;
        }
        if (t.tex[tk].loaded) { mat.map = t.tex[tk]; }
        else { mat.map = null; g.setAttribute("color", g.userData.ramp); }
        if (!g.userData.uvd) g.userData.uvd = {};
        if (!g.userData.uvd[d]) {
          var base = g.userData.uv0, arr = new Float32Array(base.length);
          var ox = t.x - ax * f, oy = t.y - ay * f;
          for (var q = 0; q < base.length / 2; q++) {
            arr[q * 2] = (base[q * 2] + ox) / f;
            arr[q * 2 + 1] = 1 - ((1 - base[q * 2 + 1]) + oy) / f;
          }
          g.userData.uvd[d] = new THREE.BufferAttribute(arr, 2);
        }
        g.setAttribute("uv", g.userData.uvd[d]);
      }
      mat.opacity = groundOpacity;
      mat.needsUpdate = true;
    }

    // ---- fetching, nearest first, a few at a time
    function request(t) {
      if (t.state !== "empty") return;
      t.state = "queued";
      if (t.z === Z_BASE) {
        var N = TILE_N, b = t.b, dlon = (b.lon1 - b.lon0) / (N - 1), dlat = (b.lat1 - b.lat0) / (N - 1), dem = new Float32Array(N * N);
        for (var j = 0; j < N; j++) for (var i = 0; i < N; i++) {
          var v = coarseAt(b.lon0 + i * dlon, b.lat0 + j * dlat);
          dem[j * N + i] = v === null ? NaN : v;
        }
        if (!buildTile(t, dem)) t.state = "failed";
        return;
      }
      queue.push(t);
      pump();
    }
    function pump() {
      if (inflight >= INFLIGHT || !queue.length) return;
      var cp = camera.position;
      queue.sort(function (p, q) {
        var dp = (p.cx - cp.x) * (p.cx - cp.x) + (p.cy - cp.y) * (p.cy - cp.y);
        var dq = (q.cx - cp.x) * (q.cx - cp.x) + (q.cy - cp.y) * (q.cy - cp.y);
        return dp - dq;
      });
      while (inflight < INFLIGHT && queue.length) fetchOne(queue.shift());
    }
    function fetchOne(t) {
      t.state = "loading"; inflight++;
      var N = TILE_N, b = t.b, hx = (b.lon1 - b.lon0) / (N - 1) / 2, hy = (b.lat1 - b.lat0) / (N - 1) / 2;
      var url = "https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/exportImage?" +
        "bbox=" + [b.lon0 - hx, b.lat0 - hy, b.lon1 + hx, b.lat1 + hy].join(",") + "&bboxSR=4326&imageSR=4326&size=" + N + "," + N +
        "&format=tiff&pixelType=F32&interpolation=RSP_BilinearInterpolation&f=image";
      var attempt = function (k) {
        return fetch(url).then(function (r) { return r.ok ? r.arrayBuffer() : null; }).catch(function () { return null; })
          .then(function (buf) {
            if (!buf && k > 0) return new Promise(function (res) { setTimeout(res, 1500); }).then(function () { return attempt(k - 1); });
            return buf;
          });
      };
      attempt(1).then(function (buf) {
        inflight--;
        if (!buf) { t.state = "failed"; pump(); return; }
        var r = readTiffF32(buf);
        if (r.w !== N || r.h !== N) { t.state = "failed"; pump(); return; }
        var dem = new Float32Array(N * N);
        for (var j = 0; j < N; j++) for (var i = 0; i < N; i++) {
          var z = r.z[(N - 1 - j) * N + i];
          dem[j * N + i] = (z > -500 && z < 4500) ? z : NaN;
        }
        if (!buildTile(t, dem)) t.state = "failed";
        pump();
        schedule();
      });
    }

    // ---- which tiles to show, from the camera
    function children(t) {
      if (t.children) return t.children;
      t.children = [];
      for (var dy = 0; dy < 2; dy++) for (var dx = 0; dx < 2; dx++)
        t.children.push(makeTile(t.z + 1, t.x * 2 + dx, t.y * 2 + dy, t));
      return t.children;
    }
    function box(t) {
      var half = t.size / 2, hy = ((t.b.lat1 - t.b.lat0) * m.lat) / 2;
      return new THREE.Box3(new THREE.Vector3(t.cx - half, t.cy - hy, t.zmin * EXAG - 50),
                            new THREE.Vector3(t.cx + half, t.cy + hy, t.zmax * EXAG + 50));
    }
    function hideTree(t) {
      if (t.node) t.node.visible = false;
      if (t.children) t.children.forEach(hideTree);
    }
    function visit(t, now) {
      var bx = box(t);
      if (!frustum.intersectsBox(bx)) { hideTree(t); return; }
      t.used = now;
      var cp = camera.position;
      var nx = Math.max(bx.min.x, Math.min(bx.max.x, cp.x)), ny = Math.max(bx.min.y, Math.min(bx.max.y, cp.y));
      var nz = Math.max(bx.min.z, Math.min(bx.max.z, cp.z));
      var d = Math.sqrt((nx - cp.x) * (nx - cp.x) + (ny - cp.y) * (ny - cp.y) + (nz - cp.z) * (nz - cp.z));
      var ratio = t.size / Math.max(d, 1);
      var shown = t.children && t.children.some(function (c) { return c.node && c.node.visible; });
      var want = t.z < Z_MAX && ratio > (shown ? SPLIT * 0.6 : SPLIT);
      if (t.state === "empty") request(t);
      if (want) {
        var kids = children(t), ready = true;
        kids.forEach(function (c) { if (c.state === "empty") request(c); if (c.state !== "ready") ready = false; });
        if (ready) {
          if (t.node) t.node.visible = false;
          kids.forEach(function (c) { visit(c, now); });
          return;
        }
      } else if (t.children) {
        t.children.forEach(hideTree);
      }
      if (t.node) t.node.visible = groundMode !== "off";
    }
    function update() {
      if (!camera || !base.length) return;
      camera.updateMatrixWorld();
      pm.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
      frustum.setFromProjectionMatrix(pm);
      var now = Date.now();
      base.forEach(function (t) { visit(t, now); });
      stitchAll();
      pump();
      evict(now);
    }

    // The level of whatever is drawn across a tile's edge: the same tile
    // key at the same level if it is visible, else the nearest visible
    // ancestor of that key. Null past the edge of the world.
    function visibleLevelAt(z, x, y) {
      var n = 1 << z;
      if (x < 0 || y < 0 || x >= n || y >= n) return null;
      for (var zz = z, xx = x, yy = y; zz >= Z_BASE; zz--, xx >>= 1, yy >>= 1) {
        var t = tiles[key(zz, xx, yy)];
        if (t && t.node && t.node.visible) return zz;
        if (t && t.children) continue;
        if (t) continue;
      }
      return null;
    }

    // Vertex indices along each edge, first to last, and the skirt slot
    // that mirrors each one.
    function edgeIndices(side) {
      var N = TILE_N, out = [];
      for (var i = 0; i < N; i++) {
        if (side === "s") out.push(i);
        else if (side === "e") out.push(i * N + N - 1);
        else if (side === "n") out.push((N - 1) * N + i);
        else out.push(i * N);
      }
      return out;
    }

    function stitchAll() {
      Object.keys(tiles).forEach(function (k) {
        var t = tiles[k];
        if (!t.node || !t.node.visible || !t.dem) return;
        var sides = { s: [t.x, t.y + 1], n: [t.x, t.y - 1], e: [t.x + 1, t.y], w: [t.x - 1, t.y] };
        var p = t.node.userData.mesh.geometry.getAttribute("position"), changed = false;
        var N = TILE_N, sk = N * N;
        Object.keys(sides).forEach(function (side) {
          var nb = visibleLevelAt(t.z, sides[side][0], sides[side][1]);
          var kdiff = nb === null ? 0 : Math.max(0, Math.min(4, t.z - nb));
          var idx = edgeIndices(side), step = 1 << kdiff;
          // Which slot of the skirt ring each edge vertex has: south row
          // first, then east, then north reversed, then west reversed.
          for (var i = 0; i < N; i++) {
            var vi = idx[i], z;
            if (kdiff === 0 || i % step === 0) {
              z = t.dem[vi];
              if (isNaN(z)) z = t.zmin;
            } else {
              var a = idx[i - (i % step)], b = idx[Math.min(N - 1, i - (i % step) + step)];
              var za = t.dem[a], zb = t.dem[b];
              if (isNaN(za)) za = t.zmin; if (isNaN(zb)) zb = t.zmin;
              z = za + (zb - za) * ((i % step) / step);
            }
            if (Math.abs(p.getZ(vi) - z) > 1e-3) {
              p.setZ(vi, z);
              var slot = side === "s" ? i : side === "e" ? N + i : side === "n" ? 2 * N + (N - 1 - i) : 3 * N + (N - 1 - i);
              p.setZ(sk + slot, z - t.node.userData.drop);
              changed = true;
            }
          }
        });
        if (changed) p.needsUpdate = true;
      });
    }
    var schedTimer = null;
    function schedule() {
      if (schedTimer) return;
      schedTimer = setTimeout(function () { schedTimer = null; update(); }, 120);
    }
    // Tiles not looked at for a minute are let go, finest first, once there
    // are more than a few hundred of them.
    function evict(now) {
      var all = Object.keys(tiles);
      if (all.length < 500) return;
      all.forEach(function (k) {
        var t = tiles[k];
        if (t.z <= Z_BASE + 2 || t.state !== "ready" || now - t.used < 60000 || t.children) return;
        group.remove(t.node);
        t.node.userData.mesh.geometry.dispose();
        Object.keys(t.tex).forEach(function (mk) { t.tex[mk].dispose(); });
        if (t.parent) t.parent.children = null;
        delete tiles[k];
      });
    }

    // ---- height at a point: the finest ready tile containing it
    function at(x, y) {
      var lon = data.origin.lon + x / m.lon, lat = data.origin.lat + y / m.lat;
      var n = 1 << Z_BASE, mc = mercator(lon, lat);
      var t = tiles[key(Z_BASE, Math.floor(mc[0] * n), Math.floor(mc[1] * n))];
      if (!t || t.state !== "ready") return coarseAt(lon, lat);
      while (t.children) {
        var n2 = 1 << (t.z + 1), c = tiles[key(t.z + 1, Math.floor(mc[0] * n2), Math.floor(mc[1] * n2))];
        if (!c || c.state !== "ready") break;
        t = c;
      }
      var N = TILE_N, b = t.b;
      var fx = (lon - b.lon0) / (b.lon1 - b.lon0) * (N - 1), fy = (lat - b.lat0) / (b.lat1 - b.lat0) * (N - 1);
      var ix = Math.max(0, Math.min(N - 2, Math.floor(fx))), iy = Math.max(0, Math.min(N - 2, Math.floor(fy)));
      var tx = Math.max(0, Math.min(1, fx - ix)), ty = Math.max(0, Math.min(1, fy - iy));
      var a = t.dem[iy * N + ix], bb = t.dem[iy * N + ix + 1], c2 = t.dem[(iy + 1) * N + ix], d = t.dem[(iy + 1) * N + ix + 1];
      if (isNaN(a) || isNaN(bb) || isNaN(c2) || isNaN(d)) return coarseAt(lon, lat);
      if (tx + ty <= 1) return a + (bb - a) * tx + (c2 - a) * ty;
      return d + (c2 - d) * (1 - tx) + (bb - d) * (1 - ty);
    }

    // ---- lines and marks laid on the ground follow the tiles as they come
    function scheduleDrape() {
      if (drapeTimer) return;
      drapeTimer = setTimeout(function () { drapeTimer = null; redrape(); }, 400);
    }
    function redrape() {
      [gridLines].concat(heads).forEach(function (obj) {
        if (!obj || !obj.userData.xy) return;
        var xy = obj.userData.xy, p = obj.geometry.getAttribute("position"), lift = obj.userData.lift || 0;
        for (var i = 0; i < xy.length / 2; i++) {
          var z = at(xy[i * 2], xy[i * 2 + 1]);
          if (z !== null) p.setZ(i, z + lift);
        }
        p.needsUpdate = true;
      });
      if (mark) {
        var z0 = at(mark.userData.x, mark.userData.y);
        if (z0 !== null) {
          var ring = mark.children[0].geometry.getAttribute("position"); ring.setZ(0, z0); ring.needsUpdate = true;
          var pin = mark.children[1]; pin.userData.base = z0;
          var pp = pin.geometry.getAttribute("position"); pp.setZ(0, z0); pp.needsUpdate = true;
          sizeMark();
        }
      }
    }

    function setMode() { Object.keys(tiles).forEach(function (k) { applyMode(tiles[k]); }); schedule(); }
    function setContours(on) {
      Object.keys(tiles).forEach(function (k) { var l = tiles[k].node && tiles[k].node.userData.lines; if (l) l.visible = on; });
    }

    // ---- the base level, cut from the grid on the page
    (function () {
      var n = 1 << Z_BASE;
      var a = mercator(terr.min_lon, terr.min_lat + terr.ny * terr.step_lat);
      var b = mercator(terr.min_lon + terr.nx * terr.step_lon, terr.min_lat);
      for (var ty = Math.floor(a[1] * n); ty <= Math.floor(b[1] * n); ty++)
        for (var tx = Math.floor(a[0] * n); tx <= Math.floor(b[0] * n); tx++) {
          var t = makeTile(Z_BASE, tx, ty, null);
          base.push(t);
          request(t);
        }
    })();

    return { group: group, update: schedule, at: at, redrape: redrape, setMode: setMode,
             setContours: setContours, count: function () { return Object.keys(tiles).length; } };
  }

  function readTiffF32(buf) {
    var dv = new DataView(buf), le = dv.getUint16(0, true) === 0x4949;
    var u16 = function (o) { return dv.getUint16(o, le); }, u32 = function (o) { return dv.getUint32(o, le); };
    var off = u32(4), n = u16(off), tags = {};
    for (var i = 0; i < n; i++) {
      var e = off + 2 + i * 12, tag = u16(e), typ = u16(e + 2), cnt = u32(e + 4);
      var size = typ === 3 ? 2 : 4, vals = [];
      if (cnt * size <= 4) {
        for (var k = 0; k < cnt; k++) vals.push(typ === 3 ? u16(e + 8 + k * 2) : u32(e + 8 + k * 4));
      } else {
        var ptr = u32(e + 8);
        for (var k2 = 0; k2 < cnt; k2++) vals.push(typ === 3 ? u16(ptr + k2 * 2) : u32(ptr + k2 * 4));
      }
      tags[tag] = vals;
    }
    var w = tags[256][0], h = tags[257][0], out = new Float32Array(w * h);
    if (tags[322]) {
      var tw = tags[322][0], th = tags[323][0], across = Math.ceil(w / tw);
      tags[324].forEach(function (o, ti) {
        var tx = (ti % across) * tw, ty = Math.floor(ti / across) * th;
        for (var r = 0; r < th; r++) {
          var y = ty + r; if (y >= h) break;
          for (var c = 0; c < tw; c++) {
            var x = tx + c; if (x >= w) break;
            out[y * w + x] = dv.getFloat32(o + (r * tw + c) * 4, le);
          }
        }
      });
    } else {
      var rps = (tags[278] || [h])[0];
      tags[273].forEach(function (o, si) {
        var base = si * rps * w, cnt2 = tags[279][si] / 4;
        for (var k3 = 0; k3 < cnt2 && base + k3 < out.length; k3++) out[base + k3] = dv.getFloat32(o + k3 * 4, le);
      });
    }
    return { w: w, h: h, z: out };
  }

  // What the view is centred on, at the resolution the distance deserves.
  // Asked for a little after the camera stops moving, and only when it has
  // moved far enough or come close enough to need a different window.
  var mark = null;                       // the isolated well's ring and pin

  function ringTexture() {
    if (ringTexture.tex) return ringTexture.tex;
    var c = document.createElement("canvas"), S = 64; c.width = c.height = S;
    var g = c.getContext("2d");
    g.lineWidth = 5; g.strokeStyle = "#b7532e";
    g.beginPath(); g.arc(S / 2, S / 2, 22, 0, Math.PI * 2); g.stroke();
    g.lineWidth = 2; g.strokeStyle = "#f7f4ef";
    g.beginPath(); g.arc(S / 2, S / 2, 26, 0, Math.PI * 2); g.stroke();
    g.beginPath(); g.arc(S / 2, S / 2, 18, 0, Math.PI * 2); g.stroke();
    ringTexture.tex = new THREE.CanvasTexture(c);
    return ringTexture.tex;
  }

  function markWell(wi) {
    unmark();
    if (wi < 0 || !data) return;
    var W = data.wells, x = W.x[wi], y = W.y[wi], z = W.ground[wi] === null ? 0 : W.ground[wi];
    mark = new THREE.Group();
    var rg = new THREE.BufferGeometry();
    rg.setAttribute("position", new THREE.Float32BufferAttribute([x, y, z], 3));
    var ring = new THREE.Points(rg, new THREE.PointsMaterial({
      map: ringTexture(), size: 30, sizeAttenuation: false, transparent: true,
      alphaTest: 0.04, depthTest: false, depthWrite: false }));
    ring.renderOrder = 10;
    mark.add(ring);
    var pg = new THREE.BufferGeometry();
    pg.setAttribute("position", new THREE.Float32BufferAttribute([x, y, z, x, y, z], 3));
    var pin = new THREE.LineSegments(pg, new THREE.LineBasicMaterial({
      color: 0xb7532e, transparent: true, opacity: 0.9, depthTest: false }));
    pin.renderOrder = 10;
    pin.userData = { base: z };
    mark.add(pin);
    mark.userData = { wi: wi, x: x, y: y };
    root.add(mark);
    sizeMark();
  }

  function unmark() {
    if (mark) { root.remove(mark); mark = null; }
  }

  // The pin's height follows the view: a fifth of the viewing distance, in
  // ground metres, so it reads the same from anywhere.
  function sizeMark() {
    if (!mark) return;
    var pin = mark.children[1], a = pin.geometry.getAttribute("position");
    var h = Math.max(20, dist * 0.2) / Math.max(EXAG, 1);
    a.setZ(1, pin.userData.base + h);
    a.needsUpdate = true;
  }
  function mercator(lon, lat) {
    var sn = Math.sin(lat * Math.PI / 180);
    return [(lon + 180) / 360, 0.5 - Math.log((1 + sn) / (1 - sn)) / (4 * Math.PI)];
  }


  //: what the ground can wear, applied to every tile
  function applyGround() {
    var credit = document.getElementById("credit");
    if (credit) credit.innerHTML = (BASEMAPS[groundMode] || {}).credit || "";
    if (terrain) terrain.setMode();
  }

  function buildGrid() {
    if (!plss || !terr) return;
    var m = metres(), pts = [], STEP = 600;
    function push(lon1, lat1, lon2, lat2) {
      var x1 = (lon1 - data.origin.lon) * m.lon, y1 = (lat1 - data.origin.lat) * m.lat;
      var x2 = (lon2 - data.origin.lon) * m.lon, y2 = (lat2 - data.origin.lat) * m.lat;
      var len = Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
      var n = Math.max(1, Math.ceil(len / STEP)), prev = null;
      for (var i = 0; i <= n; i++) {
        var t = i / n, x = x1 + (x2 - x1) * t, y = y1 + (y2 - y1) * t;
        var z = terrainAt(x, y);
        if (z === null) { prev = null; continue; }
        var cur = [x, y, z + 0.3];
        if (prev) pts.push(prev[0], prev[1], prev[2], cur[0], cur[1], cur[2]);
        prev = cur;
      }
    }
    (plss.features || []).forEach(function (f) {
      var geom = f.geometry;
      if (!geom) return;
      var polys = geom.type === "Polygon" ? [geom.coordinates] : geom.coordinates;
      polys.forEach(function (rings) {
        rings.forEach(function (ring) {
          for (var i = 1; i < ring.length; i++)
            push(ring[i - 1][0], ring[i - 1][1], ring[i][0], ring[i][1]);
        });
      });
    });
    if (!pts.length) return;
    var g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(pts), 3));
    var xy = new Float32Array(pts.length / 3 * 2);
    for (var q = 0; q < pts.length / 3; q++) { xy[q * 2] = pts[q * 3]; xy[q * 2 + 1] = pts[q * 3 + 1]; }
    gridLines = new THREE.LineSegments(g, new THREE.LineBasicMaterial({
      color: 0x54606b, transparent: true, opacity: 0.55 }));
    gridLines.userData = { xy: xy, lift: 0.3 };
    gridLines.renderOrder = 2;
    root.add(gridLines);
  }

  // Which township the view is centred over, from the same polygons.
  function townshipAt(x, y) {
    if (!plss) return null;
    var m = metres();
    var lon = data.origin.lon + x / m.lon, lat = data.origin.lat + y / m.lat;
    var feats = plss.features || [];
    for (var f = 0; f < feats.length; f++) {
      var geom = feats[f].geometry;
      if (!geom) continue;
      var polys = geom.type === "Polygon" ? [geom.coordinates] : geom.coordinates;
      for (var p = 0; p < polys.length; p++) {
        if (inRing(polys[p][0], lon, lat)) return feats[f].properties.label;
      }
    }
    return null;
  }

  function inRing(ring, x, y) {
    var inside = false;
    for (var i = 0, j = ring.length - 1; i < ring.length; j = i++) {
      var xi = ring[i][0], yi = ring[i][1], xj = ring[j][0], yj = ring[j][1];
      if ((yi > y) !== (yj > y) &&
          x < (xj - xi) * (y - yi) / (yj - yi) + xi) inside = !inside;
    }
    return inside;
  }

  function buildSurfaces() {
    meshes = [];
    if (!surf) return;
    var g = surf.grid;
    surf.surfaces.forEach(function (sf) {
      var z = sf.z_ft, dm = sf.nearest_control_m;
      var pos = [], col = [], base = new THREE.Color(sf.colour);
      var pale = new THREE.Color("#efe9dd");
      function at(gx, gy) { return gy * g.nx + gx; }
      for (var gy = 0; gy < g.ny - 1; gy++) {
        for (var gx = 0; gx < g.nx - 1; gx++) {
          var i00 = at(gx, gy), i10 = at(gx + 1, gy),
              i01 = at(gx, gy + 1), i11 = at(gx + 1, gy + 1);
          if (z[i00] === null || z[i10] === null ||
              z[i01] === null || z[i11] === null) continue;
          var xs = [g.x0 + gx * g.cell_m, g.x0 + (gx + 1) * g.cell_m];
          var ys = [g.y0 + gy * g.cell_m, g.y0 + (gy + 1) * g.cell_m];
          var quad = [[xs[0], ys[0], z[i00], dm[i00]], [xs[1], ys[0], z[i10], dm[i10]],
                      [xs[1], ys[1], z[i11], dm[i11]], [xs[0], ys[0], z[i00], dm[i00]],
                      [xs[1], ys[1], z[i11], dm[i11]], [xs[0], ys[1], z[i01], dm[i01]]];
          quad.forEach(function (v) {
            pos.push(v[0], v[1], v[2] * 0.3048);
            var t = Math.min(1, (v[3] || 0) / 4000);
            var c = base.clone().lerp(pale, t * 0.75);
            col.push(c.r, c.g, c.b);
          });
        }
      }
      if (!pos.length) return;
      var geo = new THREE.BufferGeometry();
      geo.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
      geo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
      var mat = new THREE.MeshBasicMaterial({
        vertexColors: true, transparent: true, opacity: 0.6,
        side: THREE.DoubleSide, depthWrite: false });
      var m = new THREE.Mesh(geo, mat);
      m.userData = { name: sf.name };
      m.renderOrder = -2; meshes.push(m);
      root.add(m);
    });
  }

  function drawLegend() {
    legend.innerHTML = "";
    var noneWells = 0;
    data.wells.prod.forEach(function (pr) { if (pr < 0) noneWells++; });

    function row(colour, name, sub, on, toggle) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.innerHTML = '<span class="sw" style="background:' + colour + '"></span>' +
                    '<span>' + name + '<i class="d">' + sub + '</i></span>';
      b.addEventListener("click", function () {
        var nowOn = toggle();
        b.setAttribute("aria-pressed", nowOn ? "true" : "false");
        syncAllButton();
        applyVisible();
      });
      legend.appendChild(b);
    }

    function subline(depth, ntops, nwells) {
      return (depth === undefined || depth === null
              ? "" : depth.toLocaleString() + " ft &middot; ") +
             ntops.toLocaleString() + " tops" +
             (nwells ? " &middot; " + nwells.toLocaleString() + " producing" : "");
    }

    if (!combine) {
      // Every name apart: BIG GEORGE LOWER is its own row, as filed.
      data.formations.forEach(function (f, i) {
        // Depth and picks were a separate diagram once. The well count is
        // what the row also governs: switching it off takes the tops at
        // that horizon and the wells completed in it together.
        row(f.colour, f.name, subline(f.median_depth_ft, f.tops, f.wells),
            !hidden[i], function () {
              hidden[i] = !hidden[i];
              return !hidden[i];
            });
      });
    } else {
      // Names combined into the unit the evidence put them in. One switch
      // governs every bench and spelling of it; the row says how many.
      var units = [], byUnit = {};
      data.formations.forEach(function (f, i) {
        var u = f.unit || f.name;
        if (!byUnit[u]) { byUnit[u] = []; units.push(u); }
        byUnit[u].push(i);
      });
      units.forEach(function (u) {
        var idx = byUnit[u], f0 = data.formations[idx[0]];
        var ntops = 0, nwells = 0;
        idx.forEach(function (i) {
          ntops += data.formations[i].tops; nwells += data.formations[i].wells || 0;
        });
        var names = idx.length > 1 ? " &middot; " + idx.length + " names" : "";
        var anyOn = idx.some(function (i) { return !hidden[i]; });
        row(f0.colour, u, subline(f0.median_depth_ft, ntops, nwells) + names,
            anyOn, function () {
              var on = !idx.some(function (i) { return !hidden[i]; });
              idx.forEach(function (i) { hidden[i] = !on; });
              return on;
            });
      });
    }

    if (noneWells) {
      row("#8a9098", "No producing formation filed",
          noneWells.toLocaleString() + " wells", !hiddenNone, function () {
            hiddenNone = !hiddenNone;
            return !hiddenNone;
          });
    }
    buildLabels();
  }

  // ------------------------------------------------------------- labels
  // A name written at the middle of each formation's own tops. Drawn in the
  // page rather than the scene, and dropped when it would land on a name
  // already written, so the view thins out its own labels as it zooms out.
  function buildLabels() {
    var box = document.getElementById("flabels");
    if (!box) return;
    box.innerHTML = "";
    labels = [];
    tops.forEach(function (p) {
      var f = data.formations[p.userData.formation];
      if (!f || !p.userData.anchor) return;
      var el = document.createElement("div");
      el.className = "flabel";
      el.textContent = f.name;
      box.appendChild(el);
      labels.push({ el: el, f: p.userData.formation, a: p.userData.anchor,
                    n: f.tops || 0 });
    });
    // Placed most-picked first, so when two names would collide it is the
    // obscure one that gives way. With 240 names in the region, first-come
    // put Tomcat A on the screen and Big George off it.
    labels.sort(function (a, b) { return b.n - a.n; });
  }

  function placeLabels() {
    if (!labels.length || !camera) return;
    var w = host.clientWidth, h = host.clientHeight, taken = [];
    var v = new THREE.Vector3();
    labels.forEach(function (L) {
      if (!showLabels || hidden[L.f]) { L.el.style.display = "none"; return; }
      v.set(L.a[0], L.a[1], L.a[2] * EXAG).project(camera);
      if (v.z > 1) { L.el.style.display = "none"; return; }
      var x = (v.x * 0.5 + 0.5) * w, y = (-v.y * 0.5 + 0.5) * h;
      if (x < 30 || y < 10 || x > w - 30 || y > h - 10) {
        L.el.style.display = "none"; return;
      }
      for (var i = 0; i < taken.length; i++) {
        if (Math.abs(taken[i][0] - x) < 80 && Math.abs(taken[i][1] - y) < 15) {
          L.el.style.display = "none"; return;
        }
      }
      taken.push([x, y]);
      L.el.style.display = "block";
      L.el.style.left = x + "px";
      L.el.style.top = y + "px";
    });
  }

  function syncAllButton() {
    var btn = document.getElementById("allstrata");
    if (!btn) return;
    var anyShown = data.formations.some(function (f, i) { return !hidden[i]; });
    btn.textContent = anyShown ? "Hide all" : "Show all";
  }

  function applyScale() { root.scale.set(1, 1, EXAG); }
  var exagBefore = 15;
  function setExag(v) {
    // The point the camera looks at is stored in stretched units, so when
    // the stretch changes the point has to move with the ground it is on,
    // or a wellhead in the centre of the screen slides off it.
    if (EXAG) target.z *= v / EXAG;
    EXAG = v;
    var ex = document.getElementById("ex"), exv = document.getElementById("exv");
    if (ex) ex.value = v;
    if (exv) exv.innerHTML = v + "&times;";
    applyScale();
    if (camera) place();
  }

  function applyVisible() {
    heads.forEach(function (h) { h.visible = true; });
    if (terrain) { terrain.setContours(showContours); terrain.update(); }
    if (gridLines) gridLines.visible = showGrid;
    tops.forEach(function (p) { p.visible = !hidden[p.userData.formation]; });
    lines.forEach(function (l) {
      var k = l.userData.prod;
      l.visible = showPaths && !(k === "none" ? hiddenNone : hidden[k]);
    });
    meshes.forEach(function (m) {
      var i = data.formations.findIndex(function (f) { return f.name === m.userData.name; });
      m.visible = showSurfaces && !hidden[i];
    });
  }

  // ---- camera: drag to rotate, wheel to zoom, shift or right button to pan
  var NORTH_UP = -Math.PI / 2, OVERHEAD = 0.15;
  var target = new THREE.Vector3(), dist = 60000, yaw = NORTH_UP, pitch = OVERHEAD;
  function place() {
    dist = Math.max(25, Math.min(2e6, dist));
    var r = dist;
    // Clipping planes follow the distance, so a pad at thirty metres and a
    // basin at six hundred kilometres are both inside them.
    camera.near = Math.max(0.5, r / 1500);
    camera.far = Math.max(50000, r * 25);
    camera.updateProjectionMatrix();
    camera.position.set(
      target.x + r * Math.sin(pitch) * Math.cos(yaw),
      target.y + r * Math.sin(pitch) * Math.sin(yaw),
      target.z + r * Math.cos(pitch));
    camera.up.set(0, 0, 1);
    camera.lookAt(target);
    orient();
    sizeHeads();
    sizeMark();
    if (terrain) terrain.update();
  }

  // Which way the camera is facing, in the terms a survey reader uses: a rose
  // that turns with the view, the bearing of the line of sight as a quadrant
  // bearing and an azimuth, and how far above horizontal the eye sits.
  function orient() {
    var rose = document.getElementById("rose"),
        out = document.getElementById("orient");
    if (!rose && !out) return;
    camera.updateMatrixWorld();
    var right = new THREE.Vector3(), up = new THREE.Vector3(), fwd = new THREE.Vector3();
    camera.matrixWorld.extractBasis(right, up, fwd);
    var north = new THREE.Vector3(0, 1, 0);
    if (rose) {
      // Screen angle of true north, measured clockwise from the top of the
      // screen, which is exactly what the rose has to be turned by.
      var a = Math.atan2(right.dot(north), up.dot(north)) * 180 / Math.PI;
      rose.setAttribute("transform", "rotate(" + a.toFixed(1) + ")");
    }
    if (!out) return;
    var look = new THREE.Vector3().subVectors(target, camera.position);
    var az = (Math.atan2(look.x, look.y) * 180 / Math.PI + 360) % 360;
    var ns = (az <= 90 || az >= 270) ? "N" : "S";
    var ew = (az < 180) ? "E" : "W";
    var q = (az <= 90) ? az : (az < 180) ? 180 - az : (az < 270) ? az - 180 : 360 - az;
    var above = 90 - pitch * 180 / Math.PI;
    var km = (dist / 1000);
    out.innerHTML =
      "Looking <b>" + ns + " " + q.toFixed(0) + "&deg; " + ew + "</b> " +
      "(azimuth " + az.toFixed(0) + "&deg;)<br>" +
      "Eye <b>" + (above >= 0 ? above.toFixed(0) + "&deg; above" : (-above).toFixed(0) + "&deg; below") +
      "</b> horizontal, " + (km < 10 ? km.toFixed(1) : km.toFixed(0)) + " km out<br>" +
      "<span id=\"where\"></span>";
    where();
  }

  // Where the view is centred, in ground terms rather than scene metres.
  function where() {
    var el = document.getElementById("where");
    if (!el || !data || !data.origin) return;
    var mlat = 111132.0, mlon = 111320.0 * Math.cos(data.origin.lat * Math.PI / 180);
    var lat = data.origin.lat + target.y / mlat,
        lon = data.origin.lon + target.x / mlon;
    var twp = townshipAt(target.x, target.y);
    el.innerHTML = "Centre " + (twp ? "<b>" + twp + "</b> &middot; " : "") +
      lat.toFixed(4) + "&deg;N " + Math.abs(lon).toFixed(4) + "&deg;W";
  }
  function home() {
    if (window.gossansDebug) console.debug("home()", new Error().stack.split(String.fromCharCode(10)).slice(2, 5).join(" <- "));
    // While a well is isolated, home is the well, not the basin.
    if (isolated >= 0 && data) {
      var W = data.wells;
      target.set(W.x[isolated], W.y[isolated], (W.ground[isolated] || 0) * EXAG);
      dist = 2500; yaw = NORTH_UP; pitch = 1.0; place();
      return;
    }
    var box = new THREE.Box3().setFromObject(root);
    if (box.isEmpty()) return;
    box.getCenter(target);
    dist = box.getSize(new THREE.Vector3()).length() * 0.9;
    // Fit the view distance to whatever the data turns out to be. A fixed far
    // plane hid the whole scene once, when filed elevations put a formation
    // top 241,000 km above sea level and the camera sat outside its own
    // clipping range with no error anywhere.
    yaw = NORTH_UP; pitch = OVERHEAD; place();
  }
  function bindCamera() {
    var down = null;
    host.addEventListener("contextmenu", function (e) { e.preventDefault(); });
    host.addEventListener("pointerdown", function (e) {
      down = { x: e.clientX, y: e.clientY, pan: e.shiftKey || e.button === 2,
               x0: e.clientX, y0: e.clientY, moved: false };
      host.setPointerCapture(e.pointerId);
    });
    // A press that did not drag is a click, and a click on a wellhead or a
    // top isolates that well.
    host.addEventListener("pointerup", function (e) {
      if (!down || down.moved || e.button !== 0) return;
      var r = host.getBoundingClientRect();
      mouse.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
      var hit = pickHit();
      if (hit) isolate(hit.wi);
    });
    host.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - down.x, dy = e.clientY - down.y;
      down.x = e.clientX; down.y = e.clientY;
      if (Math.abs(e.clientX - down.x0) + Math.abs(e.clientY - down.y0) > 4) down.moved = true;
      if (down.pan) {
        // Pan along the camera's own right and up axes. The previous version
        // derived them from yaw by hand and had both horizontal terms
        // inverted, so the scene moved opposite to the drag. Taking the basis
        // from the camera matrix is right at any orientation, including when
        // looking from below, where the hand-rolled version also failed.
        var k = dist / 900;
        camera.updateMatrixWorld();
        var right = new THREE.Vector3(), up = new THREE.Vector3(), fwd = new THREE.Vector3();
        camera.matrixWorld.extractBasis(right, up, fwd);
        target.addScaledVector(right, -dx * k);
        target.addScaledVector(up, dy * k);
      } else {
        yaw -= dx * 0.006;
        pitch = Math.max(0.05, Math.min(Math.PI - 0.05, pitch - dy * 0.006));
      }
      place();
    });
    host.addEventListener("pointermove", function (e) { if (!down) hover(e); });
    host.addEventListener("pointerleave", function () {
      var tip = document.getElementById("tip");
      if (tip) tip.style.display = "none";
    });
    addEventListener("pointerup", function () { down = null; });
    host.addEventListener("wheel", function (e) {
      e.preventDefault();
      dist *= e.deltaY > 0 ? 1.12 : 0.89;
      place();
    }, { passive: false });
  }

  // ---------------------------------------------------------- hover
  // What is under the cursor, said in the page rather than drawn in the
  // scene. Wellheads and tops are the only things worth naming; a ray is cast
  // once per frame at most, and not while the view is being dragged.
  var raycaster = new THREE.Raycaster(), mouse = new THREE.Vector2(), hoverQueued = false;
  function hover(e) {
    var r = host.getBoundingClientRect();
    var px = e.clientX - r.left, py = e.clientY - r.top;
    mouse.set((px / r.width) * 2 - 1, -(py / r.height) * 2 + 1);
    if (hoverQueued) return;
    hoverQueued = true;
    requestAnimationFrame(function () { hoverQueued = false; pick(px, py); });
  }

  function formationsOf(wi) {
    var W = data.wells, names = [];
    if (W.prod[wi] >= 0) names.push(data.formations[W.prod[wi]].name);
    (data.multi[String(wi)] || []).forEach(function (fi) {
      var n = data.formations[fi].name;
      if (names.indexOf(n) < 0) names.push(n);
    });
    return names;
  }

  function wellHtml(wi) {
    var W = data.wells, ops = data.operators || [];
    var forms = formationsOf(wi);
    return "<b>" + (W.name[wi] || "unnamed") + "</b><br>" +
      "<span class=\"m\">API " + W.api[wi] + (ops[W.op[wi]] ? " &middot; " + ops[W.op[wi]] : "") + "</span><br>" +
      (forms.length ? "Completed in " + forms.join(", ") : "No producing formation filed") +
      (forms.length > 1 ? " <span class=\"m\">(" + forms.length + " formations)</span>" : "") + "<br>" +
      "<span class=\"m\">" + (topsPerWell && topsPerWell[wi]
        ? topsPerWell[wi] + " tops drawn" : "no top with a usable elevation") + " &middot; " +
      (hasPathArr && hasPathArr[wi] ? "directional survey on file" : "no survey; drawn vertical") + "<br>" +
      "Ground " + Math.round(W.ground[wi]).toLocaleString() + " m, " +
      (W.datum[wi] === 1 ? "from 3DEP" : "as filed") + "</span>";
  }

  function pickHit() {
    if (!data || !camera) return null;
    raycaster.setFromCamera(mouse, camera);
    raycaster.params.Points.threshold = Math.max(40, dist * 0.005);
    var targets = tops.filter(function (p) { return p.visible; });
    heads.forEach(function (h) { if (h.visible) targets.push(h); });
    var hits = raycaster.intersectObjects(targets, false);
    if (!hits.length) return null;
    var h = hits[0], ud = h.object.userData;
    return { h: h, ud: ud, wi: ud.wi[h.index] };
  }

  function pick(px, py) {
    var tip = document.getElementById("tip");
    if (!tip || !data) return;
    var got = pickHit();
    if (!got) { tip.style.display = "none"; return; }
    var h = got.h, ud = got.ud, html;
    if (ud.heads) {
      html = wellHtml(ud.wi[h.index]);
    } else {
      var f = data.formations[ud.formation], T = data.tops[ud.formation], ti = ud.ti[h.index];
      html = "<b>" + f.name + "</b> <span class=\"m\">top</span><br>" +
        T.d[ti].toLocaleString() + " ft filed depth &middot; " +
        (T.z[ti] >= 0 ? "+" : "\u2212") + Math.abs(T.z[ti]).toLocaleString() + " m to sea level<br>" +
        "<span class=\"m\">" + (data.wells.name[ud.wi[h.index]] || data.wells.api[ud.wi[h.index]]) + "</span>";
    }
    tip.innerHTML = html;
    tip.style.display = "block";
    var r = host.getBoundingClientRect();
    tip.style.left = Math.min(px + 14, r.width - 260) + "px";
    tip.style.top = Math.min(py + 14, r.height - 90) + "px";
  }

  function resize() {
    var w = host.clientWidth, h = host.clientHeight;
    renderer.setSize(w, h, false);
    camera.aspect = w / Math.max(h, 1);
    camera.updateProjectionMatrix();
    hud.innerHTML = "Measured tops and wellbores only. Nothing is drawn between wells.";
  }
}

// three.min.js is loaded with defer, so it is not present while this inline
// script is being parsed. Deferred scripts finish before DOMContentLoaded,
// which is the earliest moment THREE is reliably defined.
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", gossansStrata);
} else {
  gossansStrata();
}
"""


ASSETS = "".join(["<style>", STYLE, "</style>",
                  "<script>", SCRIPT, "</script>"])
EMBED = SECTIONS + ASSETS
BODY = HERO + EMBED
