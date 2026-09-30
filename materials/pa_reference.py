#!/usr/bin/env python3
"""Independent Python reference for the activation bench. Must agree with assets/pa-bench.js
on every count before any page quotes a number.

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 materials/pa_reference.py            # prints the ladder, real and shuffled
  python3 materials/pa_reference.py --check    # also runs the node engine and diffs every count

Reads assets/pa-sample.js (the JSON inside it). The shuffle is mulberry32 + Fisher-Yates with
seed 20240304, ported bit for bit from pa-bench.js.
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "..", "assets", "pa-sample.js")
SEED = 20240304
M32 = 0xFFFFFFFF

PRESETS = [
    ("push1", "push", "w1", 1), ("push7", "push", "w7", 1), ("days2", "days", "w7", 2),
    ("ppl2", "ppl", "w7", 2), ("work1", "work", "w7", 1), ("star1", "star", "w7", 1),
    ("vol3", "ev", "w7", 3), ("burst10", "ev", "w0", 10),
]


def load():
    s = open(SAMPLE).read()
    start = s.index("{", s.index("window.PA_SAMPLE"))
    return json.loads(s[start:s.rstrip().rindex(";")])


def imul(a, b):
    return (a * b) & M32


def mulberry32(a):
    state = [a & M32]

    def rnd():
        a = (state[0] + 0x6D2B79F5) & M32
        state[0] = a
        t = imul(a ^ (a >> 15), 1 | a)
        t = ((t + imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296
    return rnd


def shuffled(arr, seed):
    out, rnd = list(arr), mulberry32(seed)
    for i in range(len(out) - 1, 0, -1):
        j = math.floor(rnd() * (i + 1))
        out[i], out[j] = out[j], out[i]
    return out


def column(s, f, w):
    if f == "days" and w != "w7":
        return [1 if x > 0 else 0 for x in s["ev_" + w]]
    return s[f + "_" + w]


def evaluate(s, f, w, k, broken=False):
    flag = [1 if x >= k else 0 for x in column(s, f, w)]
    if broken:
        flag = shuffled(flag, SEED)
    ret = s["ret"]
    n, a = len(flag), sum(flag)
    ra = sum(r for r, g in zip(ret, flag) if g)
    r_all = sum(ret)
    return {"n": n, "activated": a, "returnedActivated": ra, "notActivated": n - a,
            "returnedNot": r_all - ra, "returnedAll": r_all}


def half_up(x, places):
    m = 10 ** places
    return math.floor(x * m + 0.5) / m


def describe(c):
    rate_a = c["returnedActivated"] / c["activated"] if c["activated"] else None
    rate_n = c["returnedNot"] / c["notActivated"] if c["notActivated"] else None
    lift = rate_a / rate_n if rate_a is not None and rate_n else None
    return ("act %5d (%5.1f%%)  back %3d = %5.1f%%  rest %3d/%d = %4.1f%%  lift %s  diff %s pts  caught %5.1f%%" % (
        c["activated"], half_up(100 * c["activated"] / c["n"], 1), c["returnedActivated"],
        half_up(100 * rate_a, 1) if rate_a is not None else float("nan"),
        c["returnedNot"], c["notActivated"], half_up(100 * rate_n, 1) if rate_n is not None else float("nan"),
        ("%.2fx" % half_up(lift, 2)) if lift is not None else "n/a",
        ("%+.1f" % half_up(100 * (rate_a - rate_n), 1)) if lift is not None else "n/a",
        half_up(100 * c["returnedActivated"] / c["returnedAll"], 1)))


def main():
    s = load()
    print("meta", json.dumps(s["meta"]))
    print("cohort", len(s["ret"]), "came back", sum(s["ret"]),
          "= %.1f%%" % half_up(100 * sum(s["ret"]) / len(s["ret"]), 1))
    py = {}
    for pid, f, w, k in PRESETS:
        real, brk = evaluate(s, f, w, k), evaluate(s, f, w, k, True)
        py[pid] = {"real": real, "broken": brk}
        print("%-8s real   %s" % (pid, describe(real)))
        print("%-8s broken %s" % (pid, describe(brk)))
    if "--check" in sys.argv:
        js = ("global.window={};require('./pa-sample.js');const B=require('./pa-bench.js');"
              "const L=B.ladder(window.PA_SAMPLE);const o={};"
              "for(const k in L){o[k]={};for(const m of ['real','broken']){const r=L[k][m];"
              "o[k][m]={n:r.n,activated:r.activated,returnedActivated:r.returnedActivated,"
              "notActivated:r.notActivated,returnedNot:r.returnedNot,returnedAll:r.returnedAll};}}"
              "console.log(JSON.stringify(o));")
        out = subprocess.check_output(["node", "-e", js], cwd=os.path.join(HERE, "..", "assets"))
        node = json.loads(out)
        bad = [(k, m) for k in py for m in ("real", "broken") if py[k][m] != node[k][m]]
        print("node vs python:", "AGREE on every count (%d presets x 2)" % len(py) if not bad else "DISAGREE %s" % bad)
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
