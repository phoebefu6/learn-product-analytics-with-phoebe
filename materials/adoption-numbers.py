#!/usr/bin/env python3
"""Every feature-adoption number quoted on the adoption pages (leader 4, analyst 6).

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 materials/adoption-numbers.py <cache-dir>

Same cohort and rules as build-activation-sample.py (first new repository of each non-bot
account born 2024-03-04 15:00 UTC; bot events dropped; every second hour sampled). A "feature"
is a GitHub capability a repository can use, read from the event type:
  push = PushEvent · branch = CreateEvent ref_type branch · issue = IssuesEvent opened
  pr = PullRequestEvent opened · release = ReleaseEvent · wiki = GollumEvent
For each feature, over the first 7 days (offsets 0 to 166):
  breadth  = share of the cohort that used it at least once
  depth    = among users, median and mean uses
  time     = among users, median hours from the birth hour to the first sampled use
  valued?  = came-back rate (days 28-41) of users vs non-users
"""
import importlib.util
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bas", os.path.join(HERE, "build-activation-sample.py"))
bas = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bas)

FEATS = {
    "push": lambda t, d: t == "PushEvent",
    "branch": lambda t, d: t == "CreateEvent" and d == "branch",
    "issue": lambda t, d: t == "IssuesEvent" and d == "opened",
    "pr": lambda t, d: t == "PullRequestEvent" and d == "opened",
    "release": lambda t, d: t == "ReleaseEvent",
    "wiki": lambda t, d: t == "GollumEvent",
}


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    import json
    from collections import defaultdict
    cache = sys.argv[1]
    cohort_all = {int(k): v for k, v in json.load(open(os.path.join(cache, "cohort.json"))).items()}
    ev = defaultdict(list)
    birth = {}
    for i, line in enumerate(open(os.path.join(cache, "cohort-events.jsonl"))):
        o, t, rid, aid, login, det = json.loads(line)
        ev[rid].append((o, t, aid, login, det))
        if o == 0 and t == "CreateEvent" and det == "repository" and rid not in birth:
            birth[rid] = i
    first = {}
    for rid, (aid, login, _) in cohort_all.items():
        if bas.is_bot(login):
            continue
        k = birth.get(rid, 10 ** 12)
        if aid not in first or k < first[aid][0]:
            first[aid] = (k, rid)
    repos = sorted(rid for _, rid in first.values())
    n = len(repos)
    rows = {r: [e for e in ev[r] if not bas.is_bot(e[3])] for r in repos}
    back = {r: any(672 <= e[0] < 1008 for e in rows[r]) for r in repos}
    print("cohort", n, "came back", sum(back.values()))
    for name, test in FEATS.items():
        uses = {r: [e[0] for e in rows[r] if e[0] < 168 and test(e[1], e[4])] for r in repos}
        users = [r for r in repos if uses[r]]
        if not users:
            print(name, "no users")
            continue
        depth = [len(uses[r]) for r in users]
        ttime = [min(uses[r]) for r in users]
        bu = sum(back[r] for r in users) / len(users)
        non = [r for r in repos if not uses[r]]
        bn = sum(back[r] for r in non) / len(non)
        later = sum(1 for x in ttime if x >= 24)
        print("%-8s breadth %5d = %5.1f%%  depth median %d mean %.1f  first use: median %dh, %d of %d after day one"
              "  back: users %.1f%% vs rest %.1f%%" % (
                  name, len(users), 100 * len(users) / n, statistics.median(depth), statistics.mean(depth),
                  statistics.median(ttime), later, len(users), 100 * bu, 100 * bn))
    breadth = [sum(1 for f, test in FEATS.items() if any(e[0] < 168 and test(e[1], e[4]) for e in rows[r])) for r in repos]
    for k in range(0, 5):
        grp = [r for r, b in zip(repos, breadth) if (b == k if k < 4 else b >= 4)]
        if grp:
            print("used %s%d features: %5d repos (%5.1f%%), came back %.1f%%" % (
                "" if k < 4 else ">=", k, len(grp), 100 * len(grp) / n, 100 * sum(back[r] for r in grp) / len(grp)))


if __name__ == "__main__":
    main()
