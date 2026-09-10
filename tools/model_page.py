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
    <div class="rail"><b>Map</b><span>Every well we hold</span></div>
    <div class="col">
      <div class="ctl"><div class="ctlgrp" id="mapviews"></div></div>
      <div id="leaflet" class="leafwrap"></div>
      <div class="legend" id="maplegend"></div>
      <p class="prose" style="color:var(--ink-2); margin-top:14px; font-size:14px;">
        Hollow circles are wells we hold production for but will not put a
        recovery number on, because the fit was refused. They are drawn rather
        than dropped: a map that shows only the wells that behaved is a map
        that has quietly chosen its own evidence.
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
.ctl { display:flex; flex-wrap:wrap; gap:10px 26px; margin-bottom:18px; }
.ctlgrp { display:flex; flex-wrap:wrap; gap:6px; }
.ctlgrp button { font-family:var(--f-data); font-size:11px; letter-spacing:.1em;
  text-transform:uppercase; padding:6px 11px; background:transparent;
  border:1px solid var(--rule); color:var(--ink-2); cursor:pointer; }
.ctlgrp button:hover { border-color:var(--rust); color:var(--ink); }
.ctlgrp button[aria-pressed="true"] { background:var(--rust); border-color:var(--rust);
  color:#fff; }
.leafwrap { height:520px; border:1px solid var(--rule); background:var(--paper-2); }
.leafwrap .leaflet-container { background:var(--paper-2); font-family:var(--f-data); }
.leafwrap .leaflet-popup-content { font-family:var(--f-data); font-size:12px;
  line-height:1.7; }
.leafwrap .leaflet-control-attribution { font-size:9px; }
.mapwrap { overflow-x:auto; border:1px solid var(--rule); background:var(--paper-2); }
.mapwrap svg { display:block; width:100%; min-width:620px; height:auto; }
.legend { display:flex; flex-wrap:wrap; align-items:center; gap:8px 18px;
  margin:12px 0 0; font-family:var(--f-data); font-size:11px; color:var(--ink-2); }
.legend .sw { display:inline-block; width:22px; height:11px; margin-right:6px;
  vertical-align:-1px; border:1px solid var(--rule); }
.detail { margin-top:16px; padding:14px 16px; border-left:2px solid var(--rust);
  font-family:var(--f-data); font-size:13px; line-height:1.75; color:var(--ink-2); }
.detail b { color:var(--ink); }
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
    lmap = L.map("leaflet", {scrollWheelZoom:false});
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
      if (mapView.k === "none" || !p.sound || !v) {
        // A well we hold but will not value. Drawn hollow, never dropped.
        style = {radius:3, color:"#8a8f8c", weight:1, fill:false, opacity:0.75};
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
      parts.push('<span><i class="sw" style="border-radius:50%;width:12px;'+
        'background:transparent;border-color:#8a8f8c"></i>fit refused, not valued</span>');
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
