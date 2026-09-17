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
    "from Wyoming's filings. Measurements by default. Interpolated surfaces can "
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
        <div id="legend" class="legend3d"></div>
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
        <h3>Display</h3>
        <div class="ctlgrp" id="ctl"></div>
        <p class="orient" id="orient"></p>
        <p class="zoomhint">
          Drag to rotate, scroll to zoom, hold shift to pan. Each mark is a
          formation top at the depth an operator filed for it; each line is a
          wellbore, following its filed survey where one exists and vertical
          where none does. The ground is the USGS bare-earth elevation model
          on a 400&nbsp;m grid, with the township lines laid on it.
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
        The ground surface is the one surface here that is not an inference.
        It is the U.S. Geological Survey's bare-earth elevation model, built
        largely from airborne lidar and served at one metre, resampled onto a
        400&nbsp;m grid because what it is wanted for is a datum under a
        column of formation tops rather than a terrain analysis. Bare earth
        means the ground, not the trees or the buildings on it, and anything
        needing the real resolution should go to
        <a href="https://www.usgs.gov/3d-elevation-program">3DEP</a> rather
        than to this page. Compared against the elevations operators filed
        with their own formation tops, on 400 wells, the filed figure sits a
        median 14&nbsp;m above this grid, which is about what a kelly bushing
        height plus a 400&nbsp;m average of the ground should look like.
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
.legend3d { position: absolute; right: 12px; top: 12px; bottom: 12px; overflow-y: auto;
  font-family: var(--f-data); font-size: 11px; background: var(--paper);
  border: 1px solid var(--rule); padding: 8px 10px; min-width: 20ch; }
.legend3d button { display: flex; align-items: center; gap: 7px; width: 100%;
  background: none; border: 0; padding: 2px 0; font: inherit; color: var(--ink-2);
  cursor: pointer; text-align: left; }
.legend3d button[aria-pressed="false"] { opacity: .35; }
.legend3d .sw { width: 11px; height: 11px; flex: none; }
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
  var showGround = true, showGrid = true;
  var data = null, surf = null, terr = null, plss = null, hidden = {};
  var renderer, scene, camera, root, tops = [], lines = [], meshes = [];
  var ground = null, gridLines = null;

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
    ctl.innerHTML =
      '<label class="ctl">Vertical exaggeration <input id="ex" type="range" min="1" max="40" step="1" value="' + EXAG + '"> <b id="exv">' + EXAG + '&times;</b></label>' +
      '<label class="ctl"><input id="cp" type="checkbox" checked> Wellbores</label>' +
      '<label class="ctl"><input id="cs" type="checkbox"> Only wells with a survey</label>' +
      '<label class="ctl"><input id="cf" type="checkbox"> Interpolated surfaces</label>' +
      '<label class="ctl"><input id="cg" type="checkbox" checked> Ground surface</label>' +
      '<label class="ctl"><input id="ck" type="checkbox" checked> Township grid</label>' +
      '<button class="ctl" id="allstrata" type="button">Hide all strata</button>' +
      '<button class="ctl" id="reset" type="button">Reset view</button>';
    document.getElementById("ex").addEventListener("input", function (e) {
      EXAG = +e.target.value;
      document.getElementById("exv").innerHTML = EXAG + "&times;";
      applyScale();
    });
    document.getElementById("cp").addEventListener("change", function (e) {
      showPaths = e.target.checked; applyVisible();
    });
    document.getElementById("cs").addEventListener("change", function (e) {
      onlySurveyed = e.target.checked; rebuild();
    });
    document.getElementById("cf").addEventListener("change", function (e) {
      showSurfaces = e.target.checked;
      applyVisible();
      hud.innerHTML = showSurfaces
        ? "Surfaces are <b>interpolated</b>: a weighted average of nearby filed "
          + "tops, not measurements. They stop where well control does."
        : "Measured tops and wellbores only. Nothing is drawn between wells.";
    });
    document.getElementById("cg").addEventListener("change", function (e) {
      showGround = e.target.checked; applyVisible();
    });
    document.getElementById("ck").addEventListener("change", function (e) {
      showGrid = e.target.checked; applyVisible();
    });
    document.getElementById("allstrata").addEventListener("click", function () {
      // Hiding every formation leaves the wellbores, which is the useful
      // state: the holes on their own, with nothing draped on them.
      var anyShown = data.formations.some(function (f, i) { return !hidden[i]; });
      data.formations.forEach(function (f, i) { hidden[i] = anyShown; });
      this.textContent = anyShown ? "Show all strata" : "Hide all strata";
      drawLegend();
      applyVisible();
    });
    document.getElementById("reset").addEventListener("click", home);
  }

  function build() {
    controls();
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
    bindCamera();
    renderer.setAnimationLoop(function () { renderer.render(scene, camera); });

    var c = data.counts;
    document.getElementById("nsurv").textContent = c.not_surveyed.toLocaleString();
    note.textContent = "Generated " + data.generated + " from " +
      c.tops.toLocaleString() + " filed formation tops across " +
      c.wells.toLocaleString() + " wells. " + c.surveyed.toLocaleString() +
      " have a directional survey; " + c.not_surveyed.toLocaleString() + " do not. " +
      "Paths are thinned to " + c.path_points_kept_per_well + " stations each, dropping " +
      c.survey_stations_dropped_by_thinning.toLocaleString() + " stations. " +
      c.tops_dropped_rare_formation.toLocaleString() +
      " tops in formations with fewer than 25 records are not shown.";
  }

  function rebuild() {
    while (root.children.length) root.remove(root.children[0]);
    tops = []; lines = [];
    var wells = data.wells.filter(function (w) { return !onlySurveyed || w.surveyed; });

    // Tops, one point cloud per formation so the legend can toggle them.
    data.formations.forEach(function (f, fi) {
      var pts = [];
      wells.forEach(function (w) {
        w.tops.forEach(function (t) {
          if (t[0] === fi && t[2] !== null) pts.push(w.x, w.y, t[2] * 0.3048);
        });
      });
      if (!pts.length) return;
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
      // Sized in screen pixels, not world units. At 90 m across and a
      // camera 100 km away, every top rendered sub-pixel and the scene
      // came up blank.
      var m = new THREE.PointsMaterial({ color: f.colour, size: 3.5,
                                         sizeAttenuation: false });
      var p = new THREE.Points(g, m);
      p.userData = { formation: fi };
      tops.push(p); root.add(p);
    });

    // Wellbores: the filed survey where there is one, otherwise vertical.
    var surveyed = [], vertical = [];
    wells.forEach(function (w) {
      if (w.surveyed && w.path) {
        for (var i = 1; i < w.path.length; i++) {
          surveyed.push(w.path[i - 1][0], w.path[i - 1][1], w.path[i - 1][2]);
          surveyed.push(w.path[i][0], w.path[i][1], w.path[i][2]);
        }
      } else if (w.tops.length) {
        var zs = w.tops.map(function (t) { return t[2]; }).filter(function (z) { return z !== null; });
        if (zs.length < 1) return;
        var top = Math.max.apply(null, zs) * 0.3048, bot = Math.min.apply(null, zs) * 0.3048;
        vertical.push(w.x, w.y, top, w.x, w.y, bot);
      }
    });
    [[surveyed, "#54606b", 1], [vertical, "#8a9098", 1]].forEach(function (pair) {
      if (!pair[0].length) return;
      var g = new THREE.BufferGeometry();
      g.setAttribute("position", new THREE.Float32BufferAttribute(pair[0], 3));
      var l = new THREE.LineSegments(g, new THREE.LineBasicMaterial({
        color: pair[1], transparent: true, opacity: 0.7 }));
      lines.push(l); root.add(l);
    });

    buildSurfaces();
    // The ground and the grid cost real time to build and do not depend on
    // any of the switches that cause a rebuild, so they are built once and
    // put back afterwards.
    if (ground) root.add(ground); else buildGround();
    if (gridLines) root.add(gridLines); else buildGrid();
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

  function terrainAt(x, y) {
    if (!terr) return null;
    var m = metres();
    var lon = data.origin.lon + x / m.lon, lat = data.origin.lat + y / m.lat;
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

  function buildGround() {
    if (!terr) return;
    var nx = terr.nx, ny = terr.ny, m = metres();
    var pos = new Float32Array(nx * ny * 3), col = new Float32Array(nx * ny * 3);
    var lo = Infinity, hi = -Infinity, i, j, k;
    for (i = 0; i < terr.z.length; i++) {
      var v = terr.z[i];
      if (v === null) continue;
      if (v < lo) lo = v;
      if (v > hi) hi = v;
    }
    for (j = 0; j < ny; j++) {
      for (i = 0; i < nx; i++) {
        k = j * nx + i;
        var lon = terr.min_lon + (i + 0.5) * terr.step_lon;
        var lat = terr.min_lat + (j + 0.5) * terr.step_lat;
        var z = terr.z[k];
        pos[k * 3] = (lon - data.origin.lon) * m.lon;
        pos[k * 3 + 1] = (lat - data.origin.lat) * m.lat;
        pos[k * 3 + 2] = (z === null ? lo : z);
      }
    }
    // No lights in this scene, so the relief is shaded here: a slope term from
    // the neighbouring cells, lit from the north-west the way a map is.
    for (j = 0; j < ny; j++) {
      for (i = 0; i < nx; i++) {
        k = j * nx + i;
        var xw = pos[(j * nx + Math.max(0, i - 1)) * 3 + 2];
        var xe = pos[(j * nx + Math.min(nx - 1, i + 1)) * 3 + 2];
        var ys = pos[(Math.max(0, j - 1) * nx + i) * 3 + 2];
        var yn = pos[(Math.min(ny - 1, j + 1) * nx + i) * 3 + 2];
        var d = terr.step_m * 2;
        var nxv = -(xe - xw) / d, nyv = -(yn - ys) / d, nz = 1;
        var len = Math.sqrt(nxv * nxv + nyv * nyv + nz * nz);
        var lit = (nxv * -0.55 + nyv * 0.55 + nz * 0.63) / len;
        var shade = 0.55 + 0.45 * Math.max(0, lit);
        var t = (hi === lo) ? 0.5 : (pos[k * 3 + 2] - lo) / (hi - lo);
        // Sandstone in the low ground, slate on the high, both muted so the
        // measurements stay the brightest thing on the screen.
        col[k * 3]     = (0.85 - 0.30 * t) * shade;
        col[k * 3 + 1] = (0.77 - 0.24 * t) * shade;
        col[k * 3 + 2] = (0.63 - 0.06 * t) * shade;
      }
    }
    var idx = new Uint32Array((nx - 1) * (ny - 1) * 6), p = 0;
    for (j = 0; j < ny - 1; j++) {
      for (i = 0; i < nx - 1; i++) {
        var a = j * nx + i, b = a + 1, c = a + nx, d2 = c + 1;
        idx[p++] = a; idx[p++] = c; idx[p++] = b;
        idx[p++] = b; idx[p++] = c; idx[p++] = d2;
      }
    }
    var g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    g.setAttribute("color", new THREE.BufferAttribute(col, 3));
    g.setIndex(new THREE.BufferAttribute(idx, 1));
    ground = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
      vertexColors: true, side: THREE.DoubleSide,
      transparent: true, opacity: 0.72, depthWrite: false }));
    ground.renderOrder = -1;
    root.add(ground);
  }

  // The survey grid, laid on the ground rather than floating over it. Each
  // township edge is walked in steps so it follows the terrain it crosses.
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
        var cur = [x, y, z + 25];
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
    gridLines = new THREE.LineSegments(g, new THREE.LineBasicMaterial({
      color: 0x54606b, transparent: true, opacity: 0.55 }));
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
      meshes.push(m);
      root.add(m);
    });
  }

  function drawLegend() {
    legend.innerHTML = "<h4>Median depth &middot; picks</h4>";
    data.formations.forEach(function (f, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-pressed", hidden[i] ? "false" : "true");
      // The median depth and the number of picks behind it were a separate
      // diagram on this page. They belong on the thing that draws the tops.
      var d = (f.median_depth_ft === undefined || f.median_depth_ft === null)
        ? "" : f.median_depth_ft.toLocaleString() + " ft";
      b.innerHTML = '<span class="sw" style="background:' + f.colour + '"></span>' +
                    '<span>' + f.name + '<i class="d">' + d + '</i></span>' +
                    '<span class="n">' + f.tops + '</span>';
      b.addEventListener("click", function () {
        hidden[i] = !hidden[i];
        b.setAttribute("aria-pressed", hidden[i] ? "false" : "true");
        syncAllButton();
        applyVisible();
      });
      legend.appendChild(b);
    });
  }

  function syncAllButton() {
    var btn = document.getElementById("allstrata");
    if (!btn) return;
    var anyShown = data.formations.some(function (f, i) { return !hidden[i]; });
    btn.textContent = anyShown ? "Hide all strata" : "Show all strata";
  }

  function applyScale() { root.scale.set(1, 1, EXAG); }

  function applyVisible() {
    if (ground) ground.visible = showGround;
    if (gridLines) gridLines.visible = showGrid;
    tops.forEach(function (p) { p.visible = !hidden[p.userData.formation]; });
    lines.forEach(function (l) { l.visible = showPaths; });
    meshes.forEach(function (m) {
      var i = data.formations.findIndex(function (f) { return f.name === m.userData.name; });
      m.visible = showSurfaces && !hidden[i];
    });
  }

  // ---- camera: drag to rotate, wheel to zoom, shift or right button to pan
  var target = new THREE.Vector3(), dist = 60000, yaw = 0.6, pitch = 0.9;
  function place() {
    var r = Math.max(2000, dist);
    camera.position.set(
      target.x + r * Math.sin(pitch) * Math.cos(yaw),
      target.y + r * Math.sin(pitch) * Math.sin(yaw),
      target.z + r * Math.cos(pitch));
    camera.up.set(0, 0, 1);
    camera.lookAt(target);
    orient();
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
    var box = new THREE.Box3().setFromObject(root);
    if (box.isEmpty()) return;
    box.getCenter(target);
    dist = box.getSize(new THREE.Vector3()).length() * 0.9;
    // Fit the view distance to whatever the data turns out to be. A fixed far
    // plane hid the whole scene once, when filed elevations put a formation
    // top 241,000 km above sea level and the camera sat outside its own
    // clipping range with no error anywhere.
    camera.far = Math.max(40000, dist * 20);
    camera.near = Math.max(1, dist / 5000);
    camera.updateProjectionMatrix();
    yaw = 0.6; pitch = 0.9; place();
  }
  function bindCamera() {
    var down = null;
    host.addEventListener("contextmenu", function (e) { e.preventDefault(); });
    host.addEventListener("pointerdown", function (e) {
      down = { x: e.clientX, y: e.clientY, pan: e.shiftKey || e.button === 2 };
      host.setPointerCapture(e.pointerId);
    });
    host.addEventListener("pointermove", function (e) {
      if (!down) return;
      var dx = e.clientX - down.x, dy = e.clientY - down.y;
      down.x = e.clientX; down.y = e.clientY;
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
    addEventListener("pointerup", function () { down = null; });
    host.addEventListener("wheel", function (e) {
      e.preventDefault();
      dist *= e.deltaY > 0 ? 1.12 : 0.89;
      place();
    }, { passive: false });
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
