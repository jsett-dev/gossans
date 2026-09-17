#!/usr/bin/env python3
"""The interactive basin model page.

Drawn from public records only, and drawn so that the gaps in those records
are as visible as the data. A cell with no well control is left empty rather
than filled from its neighbours, because contouring across an empty township
invents structure and the invention disappears the moment it is coloured in.
"""

TITLE = "The Powder River Basin, as far as the public record actually knows it"

DESCRIPTION = (
    "An interactive model of Campbell and Converse counties built from Wyoming's "
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
      This one is built from Wyoming's own filings and nothing else. Where there
      are no wells there is no colour, because a smooth surface drawn across an
      empty township is an invention that becomes invisible the moment it is
      shaded in. Every cell carries the number of wells behind it.
    </p>
    <div class="costline" id="hdr">Loading the basin&hellip;</div>
  </section>

  <div class="block">
    <div class="rail"><b>Views</b><span>Map and 3D</span></div>
    <div class="col">
      <div class="viewswitch">
        <a class="vs on" href="#mapview">Map</a>
        <a class="vs" href="#strata">Three dimensions</a>
      </div>
      <div class="ctl"><div class="ctlgrp" id="mapviews"></div></div>
      <div id="mapview" class="maprow">
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
          <p class="zoomhint" id="zoomhint"></p>
          <h3>Wells</h3>
          <div class="legend" id="maplegend"></div>
            </div>
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
  </div>

  <div class="block">
    <div class="rail"><b>Model</b><span>Township and range</span></div>
    <div class="col">
      <div class="ctl">
        <div class="ctlgrp" id="views"></div>
        <div class="ctlgrp" id="fms"></div>
      </div>
      <div class="mapwrap">
        <svg id="map" viewBox="0 0 760 560" role="img"
             aria-label="Township and range map of the Powder River Basin"></svg>
      </div>
      <div class="legend" id="legend"></div>
      <div class="detail" id="detail">
        <b>Click a cell.</b> Each square is one survey township, six miles by
        six. Hatched squares have wells but not enough of what the current view
        needs. Empty squares have no wells at all. Neither is filled in from
        its neighbours.
      </div>
    </div>
  </div>

  <div class="block">
    <div class="rail"><b>Section</b><span>Stratigraphy</span></div>
    <div class="col">
      <h2>What is stacked underneath, and how well each layer is known.</h2>
      <p class="prose" style="color:var(--ink-2); margin-bottom:20px;">
        Median subsea depth of each formation top across the mapped area, with
        the number of picks behind it. A layer with few picks is a layer this
        model barely knows.
      </p>
      <div class="mapwrap">
        <svg id="strat" viewBox="0 0 760 420" role="img"
             aria-label="Stratigraphic column"></svg>
      </div>
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
.panel .sw.sma { border:0; background:linear-gradient(90deg,#cfe0c5,#f0e2b8,#e6d3d3); height:11px; }
.panel .zoomhint { color:var(--ink-3); margin:8px 0 0; font-size:11px; }
.viewswitch { display:flex; gap:0; margin-bottom:14px; }
.viewswitch .vs { font-family:var(--f-data); font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; padding:8px 16px; border:1px solid var(--rule);
  text-decoration:none; color:var(--ink-2); }
.viewswitch .vs + .vs { border-left:0; }
.viewswitch .vs:hover { color:var(--ink); }
.viewswitch .vs.on { background:var(--paper-3); color:var(--ink); }
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

  function draw(){
    var svg=$("map"); svg.innerHTML="";
    var defs=el("defs");
    var pat=el("pattern",{id:"thin",width:"6",height:"6",patternUnits:"userSpaceOnUse",
      patternTransform:"rotate(45)"});
    pat.appendChild(el("rect",{width:"6",height:"6",fill:"var(--paper-2)"}));
    pat.appendChild(el("line",{x1:"0",y1:"0",x2:"0",y2:"6",stroke:"var(--rule)","stroke-width":"2"}));
    defs.appendChild(pat); svg.appendChild(defs);

    var cells=data.cells.filter(function(c){return c.twp&&c.rge;});
    var twps=cells.map(function(c){return +c.twp;});
    var rges=cells.map(function(c){return +c.rge;});
    var tMin=Math.min.apply(null,twps), tMax=Math.max.apply(null,twps);
    var rMin=Math.min.apply(null,rges), rMax=Math.max.apply(null,rges);

    var pad=44, W=760-pad*2, H=560-pad*2;
    var cw=W/(rMax-rMin+1), ch=H/(tMax-tMin+1);

    var vals=cells.map(valueOf).filter(function(v){return v!==null&&v!==undefined;});
    var lo=Math.min.apply(null,vals), hi=Math.max.apply(null,vals);
    // Structure is depth below sea level: deeper should read as deeper.
    var invert = (view.k==="struct");

    cells.forEach(function(c){
      // Range increases westward, so higher range sits further left.
      var x=pad+(rMax-(+c.rge))*cw, y=pad+(tMax-(+c.twp))*ch;
      var v=valueOf(c), fill;
      if(v===null||v===undefined){
        fill = c.wells ? "url(#thin)" : "none";
      } else {
        var f=(hi===lo)?0.5:(v-lo)/(hi-lo);
        fill=shade(invert?1-f:f);
      }
      var g=el("g",{"class":"cell"});
      g.appendChild(el("rect",{x:x+1,y:y+1,width:cw-2,height:ch-2,fill:fill,
        stroke:"var(--rule)","stroke-width":"1"}));
      g.addEventListener("click",function(){ sel=c; detail(); });
      svg.appendChild(g);
    });

    for(var r=rMin;r<=rMax;r++){
      if((rMax-r)%2) continue;
      svg.appendChild(text(pad+(rMax-r)*cw+cw/2, pad-12, "R"+r+"W", "middle"));
    }
    for(var t=tMin;t<=tMax;t++){
      if((tMax-t)%2) continue;
      svg.appendChild(text(pad-10, pad+(tMax-t)*ch+ch/2+4, "T"+t+"N", "end"));
    }
    legend(lo,hi,invert);
  }

  function text(x,y,s,anchor){
    var e=el("text",{x:x,y:y,"text-anchor":anchor||"start",
      "font-family":"var(--f-data)","font-size":"10",fill:"var(--ink-3)"});
    e.textContent=s; return e;
  }

  function legend(lo,hi,invert){
    var L=$("legend"); L.innerHTML="";
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
    parts.push('<span><i class="sw" style="background:var(--paper-2);'+
      'background-image:repeating-linear-gradient(45deg,var(--rule) 0 2px,transparent 2px 6px)"></i>'+
      hatchLabel+'</span>');
    parts.push('<span><i class="sw" style="background:transparent"></i>no wells at all</span>');
    L.innerHTML=parts.join("")+'<span style="color:var(--ink-3)">'+view.unit+'</span>';
  }

  function detail(){
    var d=$("detail");
    if(!sel){ return; }
    var s=[];
    s.push("<b>T"+sel.twp+"N R"+sel.rge+"W</b>"+(sel.county?" &middot; "+sel.county+" County":""));
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

  // ---------------------------------------------------------------- cadastral
  // Townships come as one file. Sections and quarter-quarters are per
  // township, fetched as the map moves, because all of them at once is 42 MB
  // of grid nobody can read until they have zoomed in.
  function cadastral(map){
    var loaded = {}, groups = {
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

    fetch("/data/plss_townships.geojson").then(function(r){return r.json();})
      .then(function(g){
        L.geoJSON(g, {style: style.twp, onEachFeature: function(f, l){
          l.bindTooltip(f.properties.label,
            {permanent:true, direction:"center", className:"plsslab twp"});
        }}).addTo(groups.twp);
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
    [groups.twp, groups.sec, groups.qq].forEach(function(g){ map.addLayer(g); });
    refresh();
  }

  function strat(){
    var svg=$("strat"); svg.innerHTML="";
    var rows=data.stratigraphy; if(!rows.length) return;
    var deep=Math.min.apply(null,rows.map(function(r){return r.median;}));
    var shal=Math.max.apply(null,rows.map(function(r){return r.median;}));
    var pad=30, H=420-pad*2, maxPicks=Math.max.apply(null,rows.map(function(r){return r.picks;}));
    rows.forEach(function(r){
      var y=pad+(shal-r.median)/(shal-deep||1)*H;
      var w=40+(r.picks/maxPicks)*300;
      svg.appendChild(el("rect",{x:180,y:y-7,width:w,height:14,
        fill:shade(0.25+0.5*(r.picks/maxPicks)),stroke:"var(--rule)"}));
      var a=text(172,y+4,r.formation,"end"); svg.appendChild(a);
      var b=text(190+w,y+4,r.median.toLocaleString()+" ft  ("+r.picks+" picks)");
      svg.appendChild(b);
    });
    svg.appendChild(text(180,18,"bar length is how many picks stand behind the depth"));
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
      b.onclick=function(){ view=o; controls(); draw(); };
      v.appendChild(b);
    });
    var f=$("fms"); f.innerHTML="";
    if(view.k!=="struct") return;
    var names={};
    data.cells.forEach(function(c){ for(var k in (c.structure||{})) names[k]=1; });
    Object.keys(names).sort().slice(0,8).forEach(function(n){
      var b=document.createElement("button");
      b.textContent=n; b.setAttribute("aria-pressed", n===formation);
      b.onclick=function(){ formation=n; controls(); draw(); };
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
    lmap = L.map("leaflet", {scrollWheelZoom:true});
    cadastral(lmap);
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
      // Three states, and they are not the same thing. A refused fit is a well
      // we decline to value. A missing measure is a well we cannot normalise
      // because its perforated interval was never filed. Calling the second
      // one "refused" would be the same lie the grid used to tell.
      if (mapView.k === "none") {
        style = {radius:3.5, color:"#6f7472", weight:1, fill:false, opacity:0.8};
      } else if (!p.sound) {
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
          : "<i>Fit refused. No recovery number is claimed for this well.</i><br>") +
        "<span style='color:#777'>API " + p.api + "</span>");
      layer.addLayer(m);
    });
    layer.addTo(lmap);

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
        return !f.properties.sound; }).length;
      var nomeasure = wellData.features.filter(function(f){
        return f.properties.sound && !f.properties[mapView.k]; }).length;
      parts.push('<span><i class="sw" style="border-radius:50%;width:12px;'+
        'background:transparent;border:1px dashed #b0574a"></i>fit refused ('+
        refused.toLocaleString()+')</span>');
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
      j.counties.join(" and ")+" counties";
    var names={};
    j.cells.forEach(function(c){ for(var k in (c.structure||{})) names[k]=1; });
    formation=Object.keys(names).sort()[0]||null;
    $("unknown").innerHTML=(j.unknown||[]).map(function(u){
      return "<li>"+u+"</li>";}).join("");
    controls(); draw(); strat(); bars(); startMap();
  }).catch(function(e){
    $("hdr").textContent="Could not load the basin data: "+e;
  });
})();
</script>
"""
