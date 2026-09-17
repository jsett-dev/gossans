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

TITLE = "The strata, in three dimensions, with nothing drawn between the wells"

DESCRIPTION = (
    "Formation tops and wellbore paths in the Powder River Basin, in 3D, built "
    "from Wyoming's filings. Every point is a measurement. No surface is drawn "
    "between wells, because nothing was measured there."
)

HEAD_EXTRA = """
<script defer
        src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>"""

BODY = r"""
  <section class="thesis article">
    <div class="crumb">Model &middot; Strata in three dimensions</div>
    <h1>The layers are real. The surfaces between them would not be.</h1>
    <p class="standfirst">
      Drag to rotate, scroll to zoom, hold shift to pan. Each mark is a
      formation top at the depth an operator filed for it. Each line is a
      wellbore. Where a well has a directional survey on file the path is the
      one it describes; where it has none the line is vertical, because that is
      all the record supports.
    </p>
  </section>

  <div class="block">
    <div class="rail"><b>View</b><span>Measured tops</span><span>and wellbores</span></div>
    <div class="col">
      <div class="ctlgrp" id="ctl"></div>
      <div class="scenewrap">
        <canvas id="scene"></canvas>
        <div id="hud" class="hud">loading&hellip;</div>
        <div id="legend" class="legend3d"></div>
      </div>
      <p class="detail" id="note"></p>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Honesty</b><span>What is not here</span></div>
    <div class="col prose">
      <p>
        There is no layer cake. A surface joining one well's Niobrara top to
        the next well's is a guess about everything in between, and at this
        well spacing that is mostly guess. Drawn in three dimensions and
        shaded, it would look like knowledge.
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
        Vertical exaggeration is on by default because the basin is about a
        hundred kilometres across and a couple of kilometres deep, and at true
        scale the layers collapse into a line. Exaggeration distorts dip and
        thickness. The figure is shown above and can be set to 1.
      </p>
    </div>
  </div>
"""

STYLE = r"""
.scenewrap { position: relative; border: 1px solid var(--rule); background: var(--paper-2);
  height: min(70vh, 620px); overflow: hidden; }
.scenewrap canvas { display: block; width: 100%; height: 100%; touch-action: none; cursor: grab; }
.scenewrap canvas:active { cursor: grabbing; }
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
.legend3d .n { margin-left: auto; color: var(--ink-3); }
"""

SCRIPT = r"""
function gossansStrata() {
  var host = document.getElementById("scene");
  if (!host) return;
  var hud = document.getElementById("hud"), legend = document.getElementById("legend"),
      ctl = document.getElementById("ctl"), note = document.getElementById("note");

  function fail(msg) { hud.textContent = msg; }
  if (!window.THREE) { fail("The 3D library did not load, so this view cannot draw."); return; }

  var EXAG = 15, showPaths = true, onlySurveyed = false, data = null, hidden = {};
  var renderer, scene, camera, root, tops = [], lines = [];

  fetch("/data/strata.json").then(function (r) {
    if (!r.ok) throw new Error(r.status);
    return r.json();
  }).then(function (d) { data = d; build(); }).catch(function () {
    fail("Could not load the strata data.");
  });

  function controls() {
    ctl.innerHTML =
      '<label class="ctl">Vertical exaggeration <input id="ex" type="range" min="1" max="40" step="1" value="' + EXAG + '"> <b id="exv">' + EXAG + '&times;</b></label>' +
      '<label class="ctl"><input id="cp" type="checkbox" checked> Wellbores</label>' +
      '<label class="ctl"><input id="cs" type="checkbox"> Only wells with a survey</label>' +
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

    drawLegend();
    applyScale();
    applyVisible();
  }

  function drawLegend() {
    legend.innerHTML = "";
    data.formations.forEach(function (f, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("aria-pressed", hidden[i] ? "false" : "true");
      b.innerHTML = '<span class="sw" style="background:' + f.colour + '"></span>' +
                    '<span>' + f.name + '</span><span class="n">' + f.tops + '</span>';
      b.addEventListener("click", function () {
        hidden[i] = !hidden[i];
        b.setAttribute("aria-pressed", hidden[i] ? "false" : "true");
        applyVisible();
      });
      legend.appendChild(b);
    });
  }

  function applyScale() { root.scale.set(1, 1, EXAG); }

  function applyVisible() {
    tops.forEach(function (p) { p.visible = !hidden[p.userData.formation]; });
    lines.forEach(function (l) { l.visible = showPaths; });
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
        var k = dist / 900;
        target.x -= (dx * Math.sin(yaw) + dy * Math.cos(yaw) * 0.3) * k;
        target.y += (dx * Math.cos(yaw) - dy * Math.sin(yaw) * 0.3) * k;
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


BODY = "".join([BODY, "<style>", STYLE, "</style>",
                "<script>", SCRIPT, "</script>"])
