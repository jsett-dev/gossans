/* Arps decline fitting, in the browser.
 *
 * A direct port of tools/decline.py. The Python is the reference and this is
 * checked against it: same inputs, same parameters to six figures. If you
 * change one, change both and re-run the comparison in tools/compare_ports.py.
 *
 * Everything here runs on the visitor's machine. Nothing is uploaded, and
 * there is no server to upload it to.
 */
(function (global) {
  "use strict";

  // Below this the hyperbolic is numerically indistinguishable from exponential.
  var B_EXPONENTIAL = 1e-6;

  function rate(t, qi, Di, b) {
    if (b < B_EXPONENTIAL) return qi * Math.exp(-Di * t);
    return qi * Math.pow(1.0 + b * Di * t, -1.0 / b);
  }

  function cumulative(qi, Di, b, q) {
    if (Di <= 0) return Infinity;
    if (b < B_EXPONENTIAL) return (qi - q) / Di;
    if (Math.abs(b - 1.0) < B_EXPONENTIAL) return (qi / Di) * Math.log(qi / q);
    return (qi / ((1.0 - b) * Di)) * (1.0 - Math.pow(q / qi, 1.0 - b));
  }

  function secantFromNominal(Di, b) { return 1.0 - rate(1.0, 1.0, Di, b); }
  function tangentFromNominal(Di) { return 1.0 - Math.exp(-Di); }

  // Sum of squared error in log rate, with the initial rate solved
  // analytically at each node. Fitting on the log matters: production spans
  // two orders of magnitude, and a fit on raw rate ignores the tail where the
  // reserve lives.
  function sseLog(t, q, Di, b) {
    var resid = [], i, shape;
    for (i = 0; i < t.length; i++) {
      shape = rate(t[i], 1.0, Di, b);
      if (shape <= 0.0) return {sse: Infinity, qi: 0.0};
      resid.push(Math.log(q[i]) - Math.log(shape));
    }
    var mean = 0;
    for (i = 0; i < resid.length; i++) mean += resid[i];
    mean /= resid.length;
    var sse = 0;
    for (i = 0; i < resid.length; i++) sse += (resid[i] - mean) * (resid[i] - mean);
    return {sse: sse, qi: Math.exp(mean)};
  }

  // Coarse-to-fine grid search over the two nonlinear parameters. Easier to
  // audit than a solver whose failure modes you cannot see, and the failure
  // mode that matters is reported rather than hidden: an exponent that lands
  // on its bound means the search hit a wall.
  function fit(t, q, opts) {
    opts = opts || {};
    var bLo0 = opts.bMin === undefined ? 0.0 : opts.bMin;
    var bHi0 = opts.bMax === undefined ? 2.0 : opts.bMax;
    var dLo0 = opts.diMin === undefined ? 0.05 : opts.diMin;
    var dHi0 = opts.diMax === undefined ? 5.0 : opts.diMax;
    var rounds = opts.rounds === undefined ? 6 : opts.rounds;
    var nodes = opts.nodes === undefined ? 40 : opts.nodes;

    var tt = [], qq = [], i;
    for (i = 0; i < t.length; i++) {
      if (q[i] !== null && q[i] !== undefined && q[i] > 0) { tt.push(t[i]); qq.push(q[i]); }
    }
    if (tt.length < 4) throw new Error("need at least four positive rate points to fit");

    var bLo = bLo0, bHi = bHi0, dLo = dLo0, dHi = dHi0;
    var best = null, r, j, b, Di, out;

    for (r = 0; r < rounds; r++) {
      for (i = 0; i <= nodes; i++) {
        b = bLo + (bHi - bLo) * i / nodes;
        for (j = 0; j <= nodes; j++) {
          Di = dLo + (dHi - dLo) * j / nodes;
          if (Di <= 0) continue;
          out = sseLog(tt, qq, Di, b);
          if (best === null || out.sse < best.sse) {
            best = {sse: out.sse, qi: out.qi, Di: Di, b: b};
          }
        }
      }
      var bSpan = (bHi - bLo) / nodes * 2;
      var dSpan = (dHi - dLo) / nodes * 2;
      bLo = Math.max(bLo0, best.b - bSpan); bHi = Math.min(bHi0, best.b + bSpan);
      dLo = Math.max(dLo0, best.Di - dSpan); dHi = Math.min(dHi0, best.Di + dSpan);
    }

    var logs = qq.map(Math.log), m = 0;
    for (i = 0; i < logs.length; i++) m += logs[i];
    m /= logs.length;
    var sst = 0;
    for (i = 0; i < logs.length; i++) sst += (logs[i] - m) * (logs[i] - m);
    var r2 = sst > 0 ? 1.0 - best.sse / sst : NaN;

    var tol = (bHi0 - bLo0) / 1000.0;
    var pinned = best.b <= bLo0 + tol || best.b >= bHi0 - tol;

    return {
      qi: best.qi, Di_nominal: best.Di, b: best.b,
      De_secant: secantFromNominal(best.Di, best.b),
      De_tangent: tangentFromNominal(best.Di),
      r2_log: r2, n: qq.length, b_pinned_to_bound: pinned
    };
  }

  // When a hyperbolic decline flattens to the terminal rate, in years.
  function switchTime(Di, b, terminalEffective) {
    if (b < B_EXPONENTIAL) return null;
    var Dt = -Math.log(1.0 - terminalEffective);
    if (Dt <= 0 || Dt >= Di) return null;
    return (Di / Dt - 1.0) / (b * Di);
  }

  // A hyperbolic with an exponent near or above one barely converges when
  // integrated forever, and exponents that high are ordinary early in life.
  // Without the switch the forecast books a reserve the well never delivers.
  function eur(params, qLimit, cumToDate, terminalEffective) {
    cumToDate = cumToDate || 0.0;
    if (terminalEffective === undefined) terminalEffective = 0.06;
    var qi = params.qi, Di = params.Di_nominal, b = params.b;
    var plain = cumulative(qi, Di, b, qLimit);
    if (terminalEffective === null) return cumToDate + plain * 365.25;

    var ts = switchTime(Di, b, terminalEffective);
    if (ts === null) return cumToDate + plain * 365.25;

    var qSwitch = rate(ts, qi, Di, b);
    if (qSwitch <= qLimit) return cumToDate + plain * 365.25;

    var Dt = -Math.log(1.0 - terminalEffective);
    return cumToDate + (cumulative(qi, Di, b, qSwitch)
                        + (qSwitch - qLimit) / Dt) * 365.25;
  }

  global.Decline = {
    rate: rate, cumulative: cumulative, fit: fit, eur: eur,
    switchTime: switchTime,
    secantFromNominal: secantFromNominal,
    tangentFromNominal: tangentFromNominal,
    B_EXPONENTIAL: B_EXPONENTIAL
  };
})(this);
