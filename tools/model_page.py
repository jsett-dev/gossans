#!/usr/bin/env python3
"""The interactive basin model page.

Drawn from public records only, and drawn so that the gaps in those records
are as visible as the data. A cell with no well control is left empty rather
than filled from its neighbours, because contouring across an empty township
invents structure and the invention disappears the moment it is coloured in.
"""

TITLE = "The Powder River Basin, as far as the public record actually knows it"

DESCRIPTION = (
    "An interactive model of the Powder River Basin, Wyoming and Montana, built from the states' "
    "own filings: structure, recovery and completion intensity by township and "
    "range, with every gap in the record left visible."
)

HEAD_EXTRA = """
<link rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css">
<script defer
        src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>"""

BODY = r"""
  <section class="thesis article">
    <div class="crumb">Model &middot; Powder River Basin</div>
    <h1>Most basin maps are confident where the data is not.</h1>
    <p class="standfirst">
      This one is built from Wyoming's and Montana's own filings and nothing else. Where there
      are no wells there is no colour, because a smooth surface drawn across an
      empty township is an invention that becomes invisible the moment it is
      shaded in. Every cell carries the number of wells behind it.
    </p>
    <div class="costline" id="hdr">Loading the basin&hellip;</div>
  </section>

  <div class="block">
    <div class="rail"><b>Views</b><span>Map and 3D</span></div>
    <div class="col">
      <div class="viewswitch" role="tablist" aria-label="Basin view">
        <a class="vs on" role="tab" aria-selected="true" data-view="map"
           href="#mapview">Map</a>
        <a class="vs" role="tab" aria-selected="false" data-view="strata"
           href="#strata">Three dimensions</a>
        <a class="vs" role="tab" aria-selected="false" data-view="surface"
           href="#surface">Surface</a>
      </div>
      <div id="mapview" class="pane">
      <div class="ctl"><div class="ctlgrp" id="mapviews"></div></div>
      <div class="maprow">
        <div id="leaflet" class="leafwrap"></div>
        <div class="panel" id="layers">
          <h3>Layers</h3>
          <label><input id="lay-twp" type="checkbox" checked>
            <i class="sw" style="border-color:#54606b"></i> Township and range</label>
          <label><input id="lay-sec" type="checkbox" checked>
            <i class="sw" style="border-color:#8a9098"></i> Sections</label>
          <label><input id="lay-qq" type="checkbox" checked>
            <i class="sw" style="border-color:#b7532e"></i> Quarter-quarters</label>
          <label><input id="lay-sma" type="checkbox">
            <i class="sw sma"></i> Surface ownership</label>
          <label><input id="lay-model" type="checkbox" checked>
            <i class="sw model"></i> Township model</label>
          <label><input id="lay-contour" type="checkbox">
            <i class="sw" style="border-color:#6b6b6b"></i> Contours (50 m)</label>
          <p class="zoomhint" id="zoomhint"></p>
          <h3>Township model</h3>
          <div class="ctlgrp" id="views"></div>
          <div class="ctlgrp" id="fms"></div>
          <div class="legend" id="modellegend"></div>
          <h3>Wells</h3>
          <div class="legend" id="maplegend"></div>
            </div>
      </div>
      <div class="detail" id="detail">
        <b>Click a township.</b> Each six-mile square is filled by the measure
        chosen above. Faint grey squares have wells but too few sound fits to
        report a median, and are left blank rather than borrowed from their
        neighbours. Unfilled squares have no wells at all.
      </div>
      <p class="detail" id="cadnote">
        Survey grid and surface ownership from the Bureau of Land Management,
        provided as is. In BLM's words, these data are neither legal documents
        nor land surveys and must not be used as such: the grid is drawn for
        reference, not to determine anybody's corner. Sections and
        quarter-quarters load for the townships on screen, so zoom in to see
        them. Surface ownership shows which agency administers the surface, and
        says nothing about who owns the minerals underneath.
      </p>
      <p class="prose" style="color:var(--ink-2); margin-top:14px; font-size:14px;">
        Filled circles carry a number. Dashed circles are wells whose decline
        fit was refused, so we will not claim a recovery for them. Plain hollow
        circles are wells with a sound fit that simply cannot be normalised,
        because the perforated interval was never filed. All three are drawn:
        a map showing only the wells that behaved is a map that has quietly
        chosen its own evidence.
      </p>
      </div>
<!--PANE3D-->
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Result</b><span>By producing formation</span></div>
    <div class="col">
      <h2>Recovery per thousand feet, which is the ranking that survives normalising.</h2>
      <div class="mapwrap">
        <svg id="bars" viewBox="0 0 760 300" role="img"
             aria-label="Recovery per thousand feet by formation"></svg>
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Limits</b><span>What is not known</span></div>
    <div class="col prose">
      <p>
        This is a structural and performance model. It is not a reservoir model,
        and the difference is most of the list below.
      </p>
      <ul class="unknown" id="unknown"></ul>
      <p style="margin-top:24px;">
        Everything above comes from the Wyoming Oil and Gas Conservation
        Commission and can be checked against the same filings.
        <a href="/powder-river-basin/">The written study</a> sets out the method.
      </p>
    </div>
  </div>

<style>
.leafwrap { height:560px; border:1px solid var(--rule); background:var(--paper-2); }
.maprow { display:grid; grid-template-columns: minmax(0,1fr) 230px; gap:14px; align-items:stretch; }
@media (max-width: 860px) { .maprow { grid-template-columns: minmax(0,1fr); } }
.panel { border:1px solid var(--rule); padding:12px 13px; font-family:var(--f-data);
  font-size:11.5px; line-height:1.6; overflow-y:auto; max-height:560px; }
.panel h3 { font-family:var(--f-data); font-size:10px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--ink-3); margin:0 0 7px; }
.panel h3 + h3, .panel .legend + h3 { margin-top:16px; }
.panel label { display:flex; align-items:center; gap:7px; padding:2px 0; cursor:pointer; }
.panel .sw { width:13px; height:9px; border:1.5px solid var(--ink-3); flex:none; }
.panel .sw.model { border:0; background:linear-gradient(90deg,#eeeeea,#b7532e); height:11px; }
.panel .legend { display:block; margin-top:8px; }
.panel .legend span { display:flex; align-items:center; gap:7px; padding:1px 0; }
.panel .ctlgrp { margin-top:6px; }
.panel .sw.sma { border:0; background:linear-gradient(90deg,#cfe0c5,#f0e2b8,#e6d3d3); height:11px; }
.panel .zoomhint { color:var(--ink-3); margin:8px 0 0; font-size:11px; }
.viewswitch { display:flex; gap:0; margin-bottom:14px; }
.viewswitch .vs { font-family:var(--f-data); font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; padding:8px 16px; border:1px solid var(--rule);
  text-decoration:none; color:var(--ink-2); }
.viewswitch .vs + .vs { border-left:0; }
.viewswitch .vs:hover { color:var(--ink); }
.viewswitch .vs.on { background:var(--paper-3); color:var(--ink); }
.viewswitch .vs { cursor:pointer; }
.paneoff { display:none !important; }
/* Grid labels: drawn always, revealed by zoom. Hiding them with CSS avoids
   rebinding thousands of tooltips every time the map moves. */
.plsslab { background:none; border:0; box-shadow:none; color:var(--ink-3);
  font-family:var(--f-data); font-size:10px; padding:0; }
.plsslab.twp { color:var(--ink-2); font-size:11px; }
.plsslab.qq { font-size:9px; color:var(--redline); }
.lz-twp .plsslab.twp, .lz-sec .plsslab.sec, .lz-qq .plsslab.qq { display:block; }
.plsslab.twp, .plsslab.sec, .plsslab.qq { display:none; }
.leafwrap .leaflet-container { background:var(--paper-2); font-family:var(--f-data); }
.leafwrap .leaflet-popup-content { font-family:var(--f-data); font-size:12px;
  line-height:1.7; }
.leafwrap .leaflet-control-attribution { font-size:9px; }
.cell { cursor:pointer; }
.cell:hover { stroke:var(--rust); stroke-width:2; }
ul.unknown { list-style:none; padding:0; margin:18px 0 0; }
ul.unknown li { padding:12px 0 12px 22px; border-top:1px solid var(--rule-2);
  position:relative; color:var(--ink-2); }
ul.unknown li::before { content:"\2014"; position:absolute; left:0;
  color:var(--rust); }
</style>

<script>
(function () {
  var VIEWS = [
    {k:"per_ft", label:"Recovery",  unit:"bbl per 1,000 ft", fmt:function(v){return v.toLocaleString();}},
    {k:"lb_ft",  label:"Intensity", unit:"lb proppant per ft", fmt:function(v){return v.toLocaleString();}},
    {k:"struct", label:"Structure", unit:"ft subsea", fmt:function(v){return v.toLocaleString();}},
    {k:"wells",  label:"Control",   unit:"wells with a sound fit", fmt:function(v){return v;}}
  ];
  var view = VIEWS[0], formation = null, data = null, sel = null;

  function $(id){ return document.getElementById(id); }
  function el(n,a){ var e=document.createElementNS("http://www.w3.org/2000/svg",n);
    for(var k in a) e.setAttribute(k,a[k]); return e; }

  function valueOf(c){
    if(view.k==="struct"){
      return (formation && c.structure[formation]) ? c.structure[formation].subsea : null;
    }
    if(view.k==="wells") return c.fitted || null;
    if(c.thin) return null;
    return c[view.k];
  }

  // Neutral to rust. Deliberately one hue: two-ended scales imply a midpoint
  // that means something, and here none does.
  function shade(f){
    var stops=[[238,238,234],[224,206,186],[206,166,132],[178,116,80],[140,62,42]];
    var x=Math.max(0,Math.min(0.999,f))*(stops.length-1);
    var i=Math.floor(x), t=x-i, a=stops[i], b=stops[i+1]||stops[i];
    return "rgb("+Math.round(a[0]+(b[0]-a[0])*t)+","+
                  Math.round(a[1]+(b[1]-a[1])*t)+","+
                  Math.round(a[2]+(b[2]-a[2])*t)+")";
  }

  // The township model. This was an SVG grid of squares next to a map that
  // draws the same townships from the survey polygons; now it is a layer on
  // that map, so a reader is not asked to hold two pictures of one thing.
  var modelLayer = null, cellBy = {}, band = {lo:0, hi:1, invert:false};

  function modelStyle(f){
    var c = cellBy[f.properties.label], v = c ? valueOf(c) : null;
    if (v === null || v === undefined)
      return {stroke:false, fillOpacity: (c && c.wells) ? 0.22 : 0, fillColor:"#8a9098"};
    var t = (band.hi === band.lo) ? 0.5 : (v - band.lo) / (band.hi - band.lo);
    return {stroke:false, fillOpacity:0.55, fillColor: shade(band.invert ? 1 - t : t)};
  }

  function paintModel(){
    if (!data) return;
    var vals = data.cells.map(valueOf).filter(function(v){
      return v !== null && v !== undefined; });
    if (!vals.length) return;
    band.lo = Math.min.apply(null, vals);
    band.hi = Math.max.apply(null, vals);
    // Structure is depth below sea level, so deeper has to read as deeper.
    band.invert = (view.k === "struct");
    if (modelLayer) { modelLayer.setStyle(modelStyle); modelLayer.bringToBack(); }
    legend(band.lo, band.hi, band.invert);
  }

  function text(x,y,s,anchor){
    var e=el("text",{x:x,y:y,"text-anchor":anchor||"start",
      "font-family":"var(--f-data)","font-size":"10",fill:"var(--ink-3)"});
    e.textContent=s; return e;
  }

  function legend(lo,hi,invert){
    var L=$("modellegend"); if(!L) return; L.innerHTML="";
    var parts=[];
    for(var i=0;i<5;i++){
      var f=i/4, v=lo+(hi-lo)*f;
      parts.push('<span><i class="sw" style="background:'+shade(invert?1-f:f)+
        '"></i>'+view.fmt(Math.round(v))+'</span>');
    }
    // Why a cell is blank depends on what is being shown, and saying the
    // wrong reason is the exact failure this page exists to avoid.
    var hatchLabel = (view.k==="struct")
      ? "wells, but no picks for this formation"
      : "wells, but too few sound fits";
    parts.push('<span><i class="sw" style="background:#8a9098;opacity:.35"></i>'+
      hatchLabel+'</span>');
    parts.push('<span><i class="sw" style="background:transparent;'+
      'border:1px solid var(--rule)"></i>no wells at all</span>');
    L.innerHTML=parts.join("")+'<span style="color:var(--ink-3)">'+view.unit+'</span>';
  }

  function detail(){
    var d=$("detail");
    if(!sel){ return; }
    var s=[];
    var tt = String(sel.twp), rr = String(sel.rge);
    if (!/[NS]$/.test(tt)) tt += "N";
    if (!/[EW]$/.test(rr)) rr += "W";
    s.push("<b>T"+tt+" R"+rr+"</b>"+(sel.county?" &middot; "+sel.county+" County":""));
    s.push(sel.wells+" wells, "+sel.fitted+" with a sound fit"+
      (sel.refused?", "+sel.refused+" refused":""));
    if(sel.thin) s.push("<b>Too few sound fits to report a median.</b> "+
      "Recovery and intensity are left blank for this township rather than "+
      "borrowed from its neighbours.");
    else {
      if(sel.per_ft) s.push("Recovery "+sel.per_ft.toLocaleString()+" bbl per 1,000 ft");
      if(sel.eur) s.push("Median well recovery "+sel.eur.toLocaleString()+" bbl");
      if(sel.lb_ft) s.push("Completion "+sel.lb_ft.toLocaleString()+" lb proppant per ft");
    }
    var keys=Object.keys(sel.structure||{});
    if(keys.length){
      var bits=keys.map(function(k){
        return k+" "+sel.structure[k].subsea.toLocaleString()+" ft ("+
          sel.structure[k].picks+" picks)";});
      s.push("Tops: "+bits.join(" &middot; "));
    } else s.push("No formation tops with enough picks in this township.");
    d.innerHTML=s.join("<br>");
  }

  // ------------------------------------------------------------------ views
  // Map and 3D occupy the same place on the page and swap, rather than the
  // button scrolling to a second view further down. Both libraries size
  // themselves from a visible container, so each is told to re-measure the
  // moment its pane is shown.
  function viewswitch(){
    var tabs = document.querySelectorAll(".viewswitch .vs");
    if (!tabs.length) return;
    var mapPane = document.getElementById("mapview");
    var strataPane = document.getElementById("strata");
    if (!mapPane || !strataPane) return;

    function show(which){
      var wantMap = which === "map";
      mapPane.classList.toggle("paneoff", !wantMap);
      strataPane.classList.toggle("paneoff", wantMap);
      tabs.forEach(function(t){
        var on = t.dataset.view === which;
        t.classList.toggle("on", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      var v = window.gossansViews || {};
      if (wantMap && v.map) { v.map.invalidateSize(); }
      if (!wantMap && v.resize3d) { v.resize3d(); }
      // The scene defines its preset hook only once its data has loaded;
      // until then the wish is left for it to find.
      if (!wantMap) {
        if (v.preset3d) v.preset3d(which);
        else { window.gossansViews = v; v.pendingPreset = which; }
      }
    }
    function fromHash(){
      if (/^#well=/.test(location.hash)) return "surface";
      return location.hash === "#strata" ? "strata"
           : location.hash === "#surface" ? "surface" : "map";
    }
    tabs.forEach(function(t){
      t.addEventListener("click", function(e){
        e.preventDefault();
        show(t.dataset.view);
        // The view goes in the address bar so a reload, a bookmark or a
        // link somebody sends on opens the view they were looking at.
        if (history.replaceState)
          history.replaceState(null, "", "#" + t.dataset.view);
      });
    });
    // /strata/ redirects here with #strata, and anything linking to the
    // scene does the same, so arrive on the view that was asked for.
    show(fromHash());
    addEventListener("hashchange", function(){
      show(fromHash());
    });
  }

  // ---------------------------------------------------------------- cadastral
  // Townships come as one file. Sections and quarter-quarters are per
  // township, fetched as the map moves, because all of them at once is 42 MB
  // of grid nobody can read until they have zoomed in.
  // The township polygons are a megabyte and both views on this page want
  // them. One fetch, shared, rather than one each.
  function townshipsGeoJSON(){
    var g = window.gossansData = window.gossansData || {};
    if (!g.townships)
      g.townships = fetch("/data/plss_townships.geojson")
        .then(function(r){ return r.ok ? r.json() : null; });
    return g.townships;
  }

  function cadastral(map){
    var loaded = {}, groups = {
      model: L.layerGroup(),
      twp: L.layerGroup(), sec: L.layerGroup(), qq: L.layerGroup()
    };
    var sma = L.tileLayer(
      "https://gis.blm.gov/arcgis/rest/services/lands/BLM_Natl_SMA_Cached_with_PriUnk/MapServer/tile/{z}/{y}/{x}",
      { opacity: 0.45, maxZoom: 16,
        attribution: "Surface management agency: BLM" });

    var style = {
      twp: {color:"#54606b", weight:1.4, fill:false},
      sec: {color:"#8a9098", weight:0.7, fill:false},
      qq:  {color:"#b7532e", weight:0.4, fill:false, opacity:0.75}
    };

    // Cells carry the direction the state filed - 42N 75W, 4S 60E - and
    // older exports carried none, meaning north and west. One key for both.
    function tkey(t, r){
      t = String(t); r = String(r);
      if (!/[NS]$/.test(t)) t += "N";
      if (!/[EW]$/.test(r)) r += "W";
      return t + " " + r;
    }
    (data.cells || []).forEach(function(c){ cellBy[tkey(c.twp, c.rge)] = c; });

    townshipsGeoJSON().then(function(g){
        if (!g) return;
        L.geoJSON(g, {style: style.twp, onEachFeature: function(f, l){
          l.bindTooltip(f.properties.label,
            {permanent:true, direction:"center", className:"plsslab twp"});
        }}).addTo(groups.twp);
        modelLayer = L.geoJSON(g, {style: modelStyle, onEachFeature: function(f, l){
          var c = cellBy[f.properties.label];
          if (!c) return;
          l.on("click", function(){ sel = c; detail(); });
        }}).addTo(groups.model);
        paintModel();
      }).catch(function(){});

    // Which townships are on screen, from the township file we already have.
    var twpIndex = [];
    fetch("/data/plss/index.json").then(function(r){return r.json();})
      .then(function(ix){ twpIndex = Object.keys(ix); refresh(); }).catch(function(){});

    function wantedIds(){
      var out = [], b = map.getBounds();
      groups.twp.eachLayer(function(gl){
        gl.eachLayer && gl.eachLayer(function(l){
          if (l.getBounds && b.intersects(l.getBounds()) && l.feature)
            out.push(l.feature.properties.plssid);
        });
      });
      return out;
    }

    function fetchInto(kind, id){
      var key = kind + id;
      if (loaded[key]) return;
      loaded[key] = true;
      var url = kind === "sec" ? "/data/plss/sec_" + id + ".geojson"
                               : "/data/plss/" + id + ".geojson";
      fetch(url).then(function(r){ return r.ok ? r.json() : null; })
        .then(function(g){
          if (!g) return;
          L.geoJSON(g, {style: style[kind], onEachFeature: function(f, l){
            var t = kind === "sec" ? f.properties.sec : f.properties.q;
            l.bindTooltip(String(t), {permanent:true, direction:"center",
                                      className:"plsslab " + kind});
          }}).addTo(groups[kind]);
        }).catch(function(){});
    }

    // One place decides both what is fetched and what is legible. Labels are
    // in the DOM from the moment a layer loads and are revealed by these
    // classes, which is far cheaper than rebinding tooltips on every move.
    var SHOW = { twp: 9, sec: 11, qq: 14 };
    function refresh(){
      var z = map.getZoom(), c = map.getContainer();
      if (map.hasLayer(groups.sec) && z >= SHOW.sec)
        wantedIds().forEach(function(id){ fetchInto("sec", id); });
      if (map.hasLayer(groups.qq) && z >= 13)
        wantedIds().forEach(function(id){ fetchInto("qq", id); });
      ["twp","sec","qq"].forEach(function(k){
        c.classList.toggle("lz-" + k, z >= SHOW[k] && map.hasLayer(groups[k]));
      });
      var hint = document.getElementById("zoomhint");
      if (!hint) return;
      if (map.hasLayer(groups.qq) && z < SHOW.qq)
        hint.textContent = "Zoom in for quarter-quarter labels.";
      else if (map.hasLayer(groups.sec) && z < SHOW.sec)
        hint.textContent = "Zoom in for section numbers.";
      else
        hint.textContent = "";
    }
    map.on("moveend zoomend", refresh);

    function bind(id, layer){
      var el = document.getElementById(id);
      if (!el) return;
      el.addEventListener("change", function(){
        if (el.checked) map.addLayer(layer); else map.removeLayer(layer);
        refresh();
      });
    }
    bind("lay-twp", groups.twp);
    bind("lay-sec", groups.sec);
    bind("lay-qq", groups.qq);
    bind("lay-sma", sma);
    bind("lay-model", groups.model);
    // Contours are a megabyte or two and are fetched the first time asked for.
    groups.contour = L.layerGroup();
    var contoursLoaded = false;
    bind("lay-contour", groups.contour);
    document.getElementById("lay-contour").addEventListener("change", function(e){
      if (!e.target.checked || contoursLoaded) return;
      contoursLoaded = true;
      fetch("/data/contours.json").then(function(r){ return r.ok ? r.json() : null; })
        .then(function(g){
          if (!g) return;
          L.geoJSON(g, {style: function(f){
            return {color:"#6b6b6b", weight: f.properties.index ? 1.1 : 0.5,
                    opacity: f.properties.index ? 0.7 : 0.45};
          }, onEachFeature: function(f, l){
            if (f.properties.index) l.bindTooltip(f.properties.z + " m", {sticky:true});
          }}).addTo(groups.contour);
        }).catch(function(){});
    });
    // The fill goes on first so the survey lines and the wells sit above it.
    [groups.model, groups.twp, groups.sec, groups.qq]
      .forEach(function(g){ map.addLayer(g); });
    refresh();
  }

  function bars(){
    var svg=$("bars"); svg.innerHTML="";
    var rows=(data.formations||[]).filter(function(r){return r.per_ft;}).slice(0,8);
    if(!rows.length) return;
    var max=Math.max.apply(null,rows.map(function(r){return r.per_ft;}));
    rows.forEach(function(r,i){
      var y=26+i*32, w=(r.per_ft/max)*440;
      svg.appendChild(el("rect",{x:170,y:y-11,width:w,height:18,
        fill:shade(0.35+0.5*(r.per_ft/max)),stroke:"var(--rule)"}));
      svg.appendChild(text(162,y+3,r.formation,"end"));
      svg.appendChild(text(178+w,y+3,r.per_ft.toLocaleString()+"  ("+r.wells+" wells)"));
    });
    svg.appendChild(text(170,14,"bbl per 1,000 ft of perforated interval"));
  }

  function controls(){
    var v=$("views"); v.innerHTML="";
    VIEWS.forEach(function(o){
      var b=document.createElement("button");
      b.textContent=o.label; b.setAttribute("aria-pressed", o===view);
      b.onclick=function(){ view=o; controls(); paintModel(); };
      v.appendChild(b);
    });
    var f=$("fms"); f.innerHTML="";
    if(view.k!=="struct") return;
    var names={};
    data.cells.forEach(function(c){ for(var k in (c.structure||{})) names[k]=1; });
    Object.keys(names).sort().slice(0,8).forEach(function(n){
      var b=document.createElement("button");
      b.textContent=n; b.setAttribute("aria-pressed", n===formation);
      b.onclick=function(){ formation=n; controls(); paintModel(); };
      f.appendChild(b);
    });
  }

  // ------------------------------------------------------------ the map
  var MAPVIEWS = [
    {k:"perft", label:"Recovery per 1,000 ft", unit:"bbl"},
    {k:"eur",   label:"Recovery per well",     unit:"bbl"},
    {k:"none",  label:"Just the wells",        unit:""}
  ];
  var mapView = MAPVIEWS[0], lmap = null, layer = null, wellData = null;

  function startMap(){
    if (typeof L === "undefined") { return setTimeout(startMap, 200); }
    // Wheel zoom on, to match the 3D view on the same page. Leaflet
    // already pans by dragging.
    // Canvas rather than SVG for the markers: fifty thousand wells as SVG
    // circles is fifty thousand DOM nodes, and the map stops answering.
    lmap = L.map("leaflet", {scrollWheelZoom:true, preferCanvas:true});
    window.gossansViews = window.gossansViews || {};
    window.gossansViews.map = lmap;
    cadastral(lmap);
    viewswitch();
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 15, minZoom: 6,
      attribution: 'Basemap &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors. ' +
                   'Wells: Wyoming Oil and Gas Conservation Commission.'
    }).addTo(lmap);
    fetch("/data/wells.geojson").then(function(r){ return r.json(); })
      .then(function(gj){ wellData = gj; mapControls(); paintMap(); })
      .catch(function(e){
        document.getElementById("maplegend").textContent =
          "Could not load the well locations: " + e;
      });
  }

  function paintMap(){
    if (!wellData || !lmap) return;
    if (layer) lmap.removeLayer(layer);

    var vals = wellData.features
      .map(function(f){ return f.properties[mapView.k]; })
      .filter(function(v){ return v; })
      .sort(function(a,b){ return a-b; });
    // Clip at the tenth and ninetieth so a couple of outliers do not flatten
    // the whole scale into one colour.
    var lo = vals.length ? vals[Math.floor(vals.length*0.1)] : 0;
    var hi = vals.length ? vals[Math.floor(vals.length*0.9)] : 1;

    layer = L.layerGroup();
    wellData.features.forEach(function(f){
      var p = f.properties, c = f.geometry.coordinates;
      var v = p[mapView.k];
      var style;
      // Four states, and they are not the same thing. A well never fitted
      // has no oil history to fit: most of the basin's gas and coalbed wells.
      // A refused fit is a well we decline to value. A missing measure is a
      // well we cannot normalise because its perforated interval was never
      // filed. Calling any of these "refused" would be the same lie the grid
      // used to tell.
      var fit = p.fit || (p.sound ? "sound" : "refused");
      if (mapView.k === "none") {
        style = {radius:3.5, color:"#6f7472", weight:1, fill:false, opacity:0.8};
      } else if (fit === "none") {
        style = {radius:2, color:"#9aa0a6", weight:0.8, fill:false, opacity:0.5};
      } else if (fit === "refused") {
        style = {radius:3, color:"#b0574a", weight:1.1, fill:false,
                 opacity:0.75, dashArray:"2,2"};
      } else if (!v) {
        style = {radius:3, color:"#8a8f8c", weight:1, fill:false, opacity:0.6};
      } else {
        var t = Math.max(0, Math.min(1, (v-lo)/((hi-lo)||1)));
        style = {radius:4.5, color:"#00000022", weight:1,
                 fillColor:shade(t), fill:true, fillOpacity:0.92};
      }
      var m = L.circleMarker([c[1], c[0]], style);
      m.bindPopup(
        "<b>" + (p.name || p.api) + "</b><br>" +
        (p.op || "operator not filed") + "<br>" +
        (p.trs ? p.trs + " &middot; " : "") + (p.co ? p.co + " County" : "") + "<br>" +
        (p.fm ? "Producing from " + p.fm + "<br>" : "") +
        (p.sound
          ? ((p.eur ? "Recovery " + p.eur.toLocaleString() + " bbl<br>" : "") +
             (p.perft ? p.perft.toLocaleString() + " bbl per 1,000 ft<br>" : ""))
          : (fit === "none"
             ? "<i>No oil history to fit.</i><br>"
             : "<i>Fit refused. No recovery number is claimed for this well.</i><br>")) +
        "<span style='color:#777'>API " + p.api + "</span>");
      layer.addLayer(m);
    });
    layer.addTo(lmap); sinkModel();

    var pts = wellData.features.map(function(f){
      return [f.geometry.coordinates[1], f.geometry.coordinates[0]]; });
    if (pts.length) lmap.fitBounds(pts, {padding:[20,20]});

    var L2 = document.getElementById("maplegend");
    if (mapView.k === "none") {
      L2.innerHTML = '<span>' + wellData.features.length.toLocaleString() +
        ' wells, all drawn the same</span>';
    } else {
      var parts = [];
      for (var i=0;i<5;i++){
        var t=i/4, v=lo+(hi-lo)*t;
        parts.push('<span><i class="sw" style="border-radius:50%;width:12px;'+
          'background:'+shade(t)+'"></i>'+Math.round(v).toLocaleString()+'</span>');
      }
      var refused = wellData.features.filter(function(f){
        return (f.properties.fit || (f.properties.sound ? "sound" : "refused")) === "refused"; }).length;
      var unfitted = wellData.features.filter(function(f){
        return f.properties.fit === "none"; }).length;
      var nomeasure = wellData.features.filter(function(f){
        return f.properties.sound && !f.properties[mapView.k]; }).length;
      parts.push('<span><i class="sw" style="border-radius:50%;width:12px;'+
        'background:transparent;border:1px dashed #b0574a"></i>fit refused ('+
        refused.toLocaleString()+')</span>');
      if (unfitted) {
        parts.push('<span><i class="sw" style="border-radius:50%;width:12px;'+
          'background:transparent;border-color:#9aa0a6"></i>no oil history to fit ('+
          unfitted.toLocaleString()+')</span>');
      }
      if (nomeasure) {
        var why = (mapView.k === "perft")
          ? "no perforated interval filed" : "no recovery figure";
        parts.push('<span><i class="sw" style="border-radius:50%;width:12px;'+
          'background:transparent;border-color:#8a8f8c"></i>'+why+' ('+
          nomeasure.toLocaleString()+')</span>');
      }
      parts.push('<span style="color:var(--ink-3)">'+mapView.unit+'</span>');
      L2.innerHTML = parts.join("");
    }
  }

  function sinkModel(){ if (modelLayer) modelLayer.bringToBack(); }

  function mapControls(){
    var v = document.getElementById("mapviews"); v.innerHTML = "";
    MAPVIEWS.forEach(function(o){
      var b = document.createElement("button");
      b.textContent = o.label;
      b.setAttribute("aria-pressed", o === mapView);
      b.onclick = function(){ mapView = o; mapControls(); paintMap(); };
      v.appendChild(b);
    });
  }

  fetch("/data/basin.json").then(function(r){ return r.json(); }).then(function(j){
    data=j;
    $("hdr").innerHTML = j.wells_total.toLocaleString()+" wells &middot; "+
      j.months.toLocaleString()+" production months &middot; "+
      j.wells_sound.toLocaleString()+" sound fits &middot; "+
      (j.counties.length <= 3 ? j.counties.join(" and ")+" counties"
                               : j.counties.length+" counties across Wyoming and Montana");
    var names={};
    j.cells.forEach(function(c){ for(var k in (c.structure||{})) names[k]=1; });
    formation=Object.keys(names).sort()[0]||null;
    $("unknown").innerHTML=(j.unknown||[]).map(function(u){
      return "<li>"+u+"</li>";}).join("");
    controls(); bars(); startMap();
  }).catch(function(e){
    $("hdr").textContent="Could not load the basin data: "+e;
  });
})();
</script>
"""
