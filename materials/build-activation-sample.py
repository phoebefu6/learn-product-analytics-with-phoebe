#!/usr/bin/env python3
"""Stage 2 of the activation bench: cohort events -> assets/pa-sample.js

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 materials/build-activation-sample.py <cache-dir>

Reads <cache-dir>/cohort.json and <cache-dir>/cohort-events.jsonl written by
fetch-gharchive-cohort.py, and writes assets/pa-sample.js with json.dumps.

Decisions, stated once (the course map explains each; the bench page teaches them):
  unit        a public repository whose CreateEvent (ref_type "repository") falls in the hour
              2024-03-04 15:00-15:59 UTC. GH Archive cannot see sign-ups, so "first time we saw
              an account" is not "a new user"; the birth of a repository IS visible, so the
              repository is the unit, like a new workspace in a SaaS product.
  cohort      the FIRST new repository of each account in that hour, accounts whose login ends
              in "[bot]" excluded. One account making 115 repositories in an hour is automation,
              not 115 customers.
  bots        events by any login ending in "[bot]" are dropped everywhere (behaviour and return).
  windows     w0 = the birth hour itself, w1 = first day (hours 0-23 after the birth hour's start),
              w7 = first 7 days. Hours are sampled one in two (offsets 0, 2, 4 ...)
              so every count is "seen in the sampled hours".
  return      at least one event on the repository by a non-bot account in the sampled hours of
              days 28 to 41 (offsets 672 ... 1006, every second hour). That is weeks 5 and 6.
  behaviours  ev   = all events (the anti-lever family)
              push = PushEvent count
              days = distinct days (0-6) with any event
              work = IssuesEvent or PullRequestEvent with action "opened"
              ppl  = distinct non-bot accounts active on the repository
              star = WatchEvent count (a star, per the GitHub event types docs)
  every count is capped at 99 to keep the file small; no threshold on the bench goes above 50.
"""
import json
import os
import sys
from collections import defaultdict

WINDOWS = {"w0": 1, "w1": 24, "w7": 168}
RET_FROM, RET_TO = 672, 1008
CAP = 99
FEATURES = ["ev", "push", "days", "work", "ppl", "star"]


def is_bot(login):
    return login.endswith("[bot]")


def build(cache):
    cohort_all = {int(k): v for k, v in json.load(open(os.path.join(cache, "cohort.json"))).items()}
    ev = defaultdict(list)
    birth_order = {}
    for i, line in enumerate(open(os.path.join(cache, "cohort-events.jsonl"))):
        o, t, rid, aid, login, det = json.loads(line)
        ev[rid].append((o, t, aid, login, det))
        if o == 0 and t == "CreateEvent" and det == "repository" and rid not in birth_order:
            birth_order[rid] = i

    # first repository per human account, by position of its CreateEvent in the birth hour file
    first = {}
    for rid, (aid, login, name) in cohort_all.items():
        if is_bot(login):
            continue
        k = birth_order.get(rid, 10 ** 12)
        if aid not in first or k < first[aid][0]:
            first[aid] = (k, rid)
    repos = sorted(rid for _, rid in first.values())

    out = {f + "_" + w: [] for w in WINDOWS for f in FEATURES if f != "days" or w == "w7"}
    ret = []
    for rid in repos:
        rows = [r for r in ev[rid] if not is_bot(r[3])]
        for w, lim in WINDOWS.items():
            win = [r for r in rows if r[0] < lim]
            vals = {
                "ev": len(win),
                "push": sum(1 for r in win if r[1] == "PushEvent"),
                "days": len({r[0] // 24 for r in win}),
                "work": sum(1 for r in win if r[1] in ("IssuesEvent", "PullRequestEvent") and r[4] == "opened"),
                "ppl": len({r[2] for r in win}),
                "star": sum(1 for r in win if r[1] == "WatchEvent"),
            }
            for f in FEATURES:
                if f == "days" and w != "w7":
                    continue  # one day or less: days is 1 whenever ev > 0, the reader derives it
                out[f + "_" + w].append(min(CAP, vals[f]))
        ret.append(1 if any(RET_FROM <= r[0] < RET_TO for r in rows) else 0)

    meta = {
        "cohortHour": "2024-03-04T15:00Z",
        "reposBornInHour": len(cohort_all),
        "botCreated": sum(1 for v in cohort_all.values() if is_bot(v[1])),
        "accounts": len(first),
        "n": len(repos),
        "sampledHours": {"activation": 84, "return": 168},
        "returnWindow": "days 28 to 41, every second hour",
    }
    return meta, out, ret


def write(meta, out, ret, path):
    body = {"meta": meta, "ret": ret}
    body.update(out)
    js = ("/* pa-sample.js - the activation bench cohort for learn-product-analytics-with-phoebe.\n"
          " * Real public GitHub events from GH Archive (https://www.gharchive.org/). One entry per\n"
          " * repository born in the hour 2024-03-04 15:00 UTC (first new repository of each non-bot\n"
          " * account). <feature>_<window> arrays hold counts seen in the sampled hours; ret = 1 if the\n"
          " * repository had any non-bot event in the sampled hours of days 28 to 41.\n"
          " * Generated by materials/build-activation-sample.py with json.dumps. Do not edit by hand. */\n"
          "window.PA_SAMPLE = " + json.dumps(body, separators=(",", ":")) + ";\n")
    with open(path, "w") as f:
        f.write(js)
    return len(js)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    meta, out, ret = build(sys.argv[1])
    here = os.path.dirname(os.path.abspath(__file__))
    n = write(meta, out, ret, os.path.join(here, "..", "assets", "pa-sample.js"))
    print(json.dumps(meta))
    print("returned", sum(ret), "of", len(ret), "; wrote assets/pa-sample.js", n, "bytes")
