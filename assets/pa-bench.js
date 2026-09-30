/* pa-bench.js - the activation bench for learn-product-analytics-with-phoebe
 *
 * 8,348 real public GitHub repositories, each born in the hour 2024-03-04 15:00 UTC, followed
 * through GH Archive (see pa-sample.js and materials/build-activation-sample.py). The learner
 * picks a candidate activation definition ("did X at least k times in the first N"), and the
 * bench counts, from those rows:
 *   - how many repositories that definition calls activated,
 *   - the later-return rate (any non-bot event in the sampled hours of days 28 to 41) for the
 *     activated and for the rest,
 *   - the lift (ratio) and the difference in points,
 *   - the share of all later returners the definition caught.
 * Nothing is modelled. The break button shuffles the behaviour across the cohort with a fixed
 * seed, so the definition keeps its size but loses its link to the repository: the lift should
 * fall to about 1. materials/pa_reference.py reproduces every count exactly.
 */
(function (root) {
  "use strict";

  var FEATURES = {
    ev:   { label: "events of any kind", unit: "events", one: "event" },
    push: { label: "pushes of code", unit: "pushes", one: "push" },
    days: { label: "separate days seen", unit: "days", one: "day" },
    work: { label: "issues or pull requests opened", unit: "issues or pull requests opened", one: "issue or pull request opened" },
    ppl:  { label: "different people active", unit: "different people active", one: "person active" },
    star: { label: "stars received", unit: "stars received", one: "star received" }
  };
  var WINDOWS = { w0: "the birth hour", w1: "the first day", w7: "the first 7 days" };
  var SEED = 20240304;

  var PRESETS = [
    { id: "push1", f: "push", w: "w1", k: 1, label: "Pushed code on day one",
      note: "At least one push in the first day. The definition most teams write first." },
    { id: "push7", f: "push", w: "w7", k: 1, label: "Pushed code in week one",
      note: "Same behaviour, a week to do it in." },
    { id: "days2", f: "days", w: "w7", k: 2, label: "Came back on a second day",
      note: "Seen on at least two different days in week one." },
    { id: "ppl2", f: "ppl", w: "w7", k: 2, label: "A second person showed up",
      note: "At least two different accounts active on the repository in week one." },
    { id: "work1", f: "work", w: "w7", k: 1, label: "Opened an issue or pull request",
      note: "Someone used the repository as a place to plan or review work in week one." },
    { id: "star1", f: "star", w: "w7", k: 1, label: "Got a star",
      note: "Somebody else starred it in week one. Not something the owner does." },
    { id: "vol3", f: "ev", w: "w7", k: 3, label: "Volume: 3 or more events in week one",
      note: "Count everything, set a bar, call it activation.", anti: true },
    { id: "burst10", f: "ev", w: "w0", k: 10, label: "Busy birth hour: 10 or more events",
      note: "A flurry of setup activity in the first hour.", anti: true }
  ];

  /* ---------- the same PRNG and shuffle the Python reference uses ---------- */
  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function shuffled(arr, seed) {
    var out = arr.slice(), rnd = mulberry32(seed);
    for (var i = out.length - 1; i > 0; i--) {
      var j = Math.floor(rnd() * (i + 1));
      var t = out[i]; out[i] = out[j]; out[j] = t;
    }
    return out;
  }

  function column(s, f, w) {
    if (f === "days" && w !== "w7") return s["ev_" + w].map(function (x) { return x > 0 ? 1 : 0; });
    return s[f + "_" + w];
  }

  /* Every figure the page quotes comes from here. Counts are exact integers. */
  function evaluate(s, def, broken) {
    var col = column(s, def.f, def.w);
    var flag = col.map(function (x) { return x >= def.k ? 1 : 0; });
    if (broken) flag = shuffled(flag, SEED);
    var n = flag.length, a = 0, ra = 0, rAll = 0;
    for (var i = 0; i < n; i++) {
      rAll += s.ret[i];
      if (flag[i]) { a++; ra += s.ret[i]; }
    }
    var na = n - a, rn = rAll - ra;
    var rateA = a ? ra / a : null, rateN = na ? rn / na : null;
    return {
      n: n, activated: a, returnedActivated: ra, notActivated: na, returnedNot: rn, returnedAll: rAll,
      share: a / n, rateA: rateA, rateN: rateN, rateAll: rAll / n,
      lift: (rateA !== null && rateN) ? rateA / rateN : null,
      diffPts: (rateA !== null && rateN !== null) ? (rateA - rateN) * 100 : null,
      caught: rAll ? ra / rAll : 0,
      degenerate: a === 0 || na === 0
    };
  }

  /* display rounding shared with the Python reference: round half up */
  function r1(x) { return (Math.round(x * 10) / 10).toFixed(1); }
  function pct(x) { return r1(x * 100) + "%"; }
  function fmtN(x) { return x.toLocaleString("en-US"); }
  function x2(x) { return (Math.round(x * 100) / 100).toFixed(2); }

  function ladder(s) {
    var out = {};
    PRESETS.forEach(function (p) {
      out[p.id] = { real: evaluate(s, p, false), broken: evaluate(s, p, true) };
    });
    return out;
  }

  /* ---------- UI ---------- */
  function esc(t) {
    return String(t).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  function metric(label, value, unit, kind) {
    return '<div class="mb-metric"><span class="mb-mlabel">' + esc(label) + "</span>" +
      '<span class="mb-mvalue">' + esc(value) + "</span>" +
      '<span class="mb-munit">' + esc(unit) + "</span>" +
      '<span class="mb-mkind is-' + kind + '">' + kind + "</span></div>";
  }

  function verdict(r, def, broken) {
    if (r.degenerate) {
      return ["bad", r.activated === 0
        ? "Nobody meets this definition, so there is nothing to compare. Lower the bar or widen the window"
        : "Every repository meets this definition, so it separates nobody. A definition everyone passes is not a moment"];
    }
    if (broken) {
      return ["ok", "Shuffled: the same " + r.activated + " activated slots, dealt to random repositories. Lift " +
        x2(r.lift) + "x. Near 1 is what no link looks like, and it is the floor every real definition is judged against"];
    }
    if (r.lift < 1) {
      return ["bad", "Activated repositories came back LESS often than the rest (" + r.returnedActivated + " of " +
        r.activated + " against " + pct(r.rateN) + "). With counts this small, read it as no signal, not as harm"];
    }
    if (def.anti || r.share > 0.4) {
      return ["bad", "This calls " + pct(r.share) + " of the cohort activated for a lift of " + x2(r.lift) +
        "x. Volume makes the activated group big; it does not make it predictive"];
    }
    if (r.lift >= 4) {
      return ["good", "Activated repositories came back " + x2(r.lift) + " times as often, and the definition caught " +
        pct(r.caught) + " of everyone who came back. A strong correlation. Not yet a cause"];
    }
    return ["ok", "Lift " + x2(r.lift) + "x on " + pct(r.share) + " of the cohort. A signal, but a weak one"];
  }

  var rootEl, readout, bars, custom, breakBtn, s, current = null, broken = false, radios = {};

  function currentDef() {
    if (current !== "custom") {
      for (var i = 0; i < PRESETS.length; i++) if (PRESETS[i].id === current) return PRESETS[i];
    }
    var f = custom.querySelector("[data-k=f]").value, w = custom.querySelector("[data-k=w]").value;
    var k = parseInt(custom.querySelector("[data-k=k]").value, 10);
    if (!(k >= 1)) k = 1;
    if (k > 50) k = 50;
    return { id: "custom", f: f, w: w, k: k, label: "Your definition" };
  }

  function render() {
    var def = currentDef();
    var r = evaluate(s, def, broken);
    var g = verdict(r, def, broken);
    var defLine = "Activated = at least " + def.k + " " + (def.k === 1 ? FEATURES[def.f].one : FEATURES[def.f].unit) + " in " + WINDOWS[def.w] + (broken ? ", behaviour shuffled" : "");
    readout.innerHTML =
      '<p class="mb-hint"><strong>' + esc(defLine) + "</strong></p>" +
      '<div class="mb-verdict is-' + g[0] + '">' + esc(g[1]) + ' <span class="mb-mkind is-measured">measured</span></div>' +
      '<div class="mb-metrics">' +
        metric("Activated", r.activated.toLocaleString("en-US"), pct(r.share) + " of " + r.n.toLocaleString("en-US") + " repositories", "measured") +
        metric("Came back, activated", r.rateA === null ? "n/a" : pct(r.rateA), fmtN(r.returnedActivated) + " of " + fmtN(r.activated), "measured") +
        metric("Came back, the rest", r.rateN === null ? "n/a" : pct(r.rateN), fmtN(r.returnedNot) + " of " + fmtN(r.notActivated), "measured") +
        metric("Lift", r.lift === null ? "n/a" : x2(r.lift) + "x", r.diffPts === null ? "" : (r.diffPts >= 0 ? "+" : "") + r1(r.diffPts) + " points", "measured") +
        metric("Returners caught", pct(r.caught), r.returnedActivated + " of all " + r.returnedAll + " who came back", "measured") +
      "</div>";
    var wA = r.rateA === null ? 0 : Math.min(100, r.rateA * 250), wN = r.rateN === null ? 0 : Math.min(100, r.rateN * 250);
    bars.innerHTML =
      '<div class="pa-bar"><span class="pa-blab">Activated</span><span class="pa-btrack"><span class="pa-bfill is-a" style="width:' + wA.toFixed(1) + '%"></span></span><b>' + (r.rateA === null ? "n/a" : pct(r.rateA)) + "</b></div>" +
      '<div class="pa-bar"><span class="pa-blab">The rest</span><span class="pa-btrack"><span class="pa-bfill" style="width:' + wN.toFixed(1) + '%"></span></span><b>' + (r.rateN === null ? "n/a" : pct(r.rateN)) + "</b></div>" +
      '<p class="mb-hint">Bars: share that came back in weeks 5 and 6. The whole cohort came back at ' + pct(r.rateAll) + ".</p>";
    breakBtn.textContent = broken ? "Unshuffle: back to the real behaviour" : "Break it: shuffle the behaviour";
    breakBtn.classList.toggle("is-on", broken);
  }

  function setPreset(id) {
    current = id;
    Object.keys(radios).forEach(function (k) {
      radios[k].classList.toggle("is-on", k === id);
      var i = radios[k].querySelector("input");
      if (i) i.checked = (k === id);
    });
    if (id !== "custom") {
      var p = currentDef();
      custom.querySelector("[data-k=f]").value = p.f;
      custom.querySelector("[data-k=w]").value = p.w;
      custom.querySelector("[data-k=k]").value = p.k;
    }
    render();
  }

  function buildUI() {
    var panel = document.createElement("div");
    panel.className = "mb-presets";
    PRESETS.concat([{ id: "custom", label: "Your own definition", note: "Pick the behaviour, the window and the bar below." }]).forEach(function (p) {
      var lab = document.createElement("label");
      lab.className = "mb-preset" + (p.anti ? " is-anti" : "");
      lab.innerHTML = '<input type="radio" name="pa-p" value="' + p.id + '">' +
        '<span class="mb-pname">' + esc(p.label) + (p.anti ? ' <em class="mb-anti">the volume trap</em>' : "") + "</span>" +
        '<span class="mb-pnote">' + esc(p.note) + "</span>";
      panel.appendChild(lab);
      radios[p.id] = lab;
      lab.querySelector("input").addEventListener("change", function () { setPreset(p.id); });
    });

    custom = document.createElement("div");
    custom.className = "pa-custom";
    var fo = Object.keys(FEATURES).map(function (k) { return '<option value="' + k + '">' + esc(FEATURES[k].label) + "</option>"; }).join("");
    var wo = Object.keys(WINDOWS).map(function (k) { return '<option value="' + k + '">' + esc(WINDOWS[k]) + "</option>"; }).join("");
    custom.innerHTML = '<label>At least <input data-k="k" type="number" min="1" max="50" value="1"></label>' +
      '<label><select data-k="f">' + fo + "</select></label>" +
      '<label>in <select data-k="w">' + wo + "</select></label>";
    custom.addEventListener("input", function () { setPreset("custom"); });
    custom.addEventListener("change", function () { setPreset("custom"); });

    var ctl = document.createElement("div");
    ctl.className = "pa-ctl";
    breakBtn = document.createElement("button");
    breakBtn.type = "button";
    breakBtn.className = "btn pa-break";
    breakBtn.addEventListener("click", function () { broken = !broken; render(); });
    ctl.appendChild(breakBtn);

    var hint = document.createElement("p");
    hint.className = "mb-hint";
    hint.textContent = s.meta.n.toLocaleString("en-US") + " real public repositories from GH Archive, each the first new repository an account created in the hour " +
      "2024-03-04 15:00 UTC (bot accounts excluded). Behaviour is counted in every second hour of the first week; " +
      "came back = any non-bot event in every second hour of days 28 to 41. GH Archive cannot see sign-ups, so the unit is a new repository, not a new person. " +
      "Nothing here is modelled: every number is a count.";

    readout = document.createElement("div"); readout.className = "mb-readout";
    bars = document.createElement("div"); bars.className = "pa-bars";
    rootEl.appendChild(panel); rootEl.appendChild(custom); rootEl.appendChild(ctl);
    rootEl.appendChild(hint); rootEl.appendChild(readout); rootEl.appendChild(bars);
    setPreset("push1");
  }

  function init() {
    rootEl = document.getElementById("pa-activation-bench");
    if (!rootEl || !root.PA_SAMPLE) return;
    s = root.PA_SAMPLE;
    buildUI();
    root.PA_BENCH = {
      presets: PRESETS.map(function (p) { return p.id; }),
      show: setPreset,
      setBroken: function (b) { broken = !!b; render(); },
      ladder: function () { return ladder(s); },
      evaluate: function (def, b) { return evaluate(s, def, b); }
    };
  }

  var api = { PRESETS: PRESETS, FEATURES: FEATURES, WINDOWS: WINDOWS, SEED: SEED,
              evaluate: evaluate, ladder: ladder, shuffled: shuffled, mulberry32: mulberry32,
              fmt: { r1: r1, pct: pct, x2: x2 } };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document !== "undefined") {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
    else init();
  }
})(typeof window !== "undefined" ? window : this);
