#!/usr/bin/env python3
"""Every number on "The tracking plan as code" (analyst 1). The plan and validator below are the
code the page prints, run against one real GH Archive hour.

Internal build script. Not linked from any audience-facing page.

Usage:  python3 materials/tracking-plan-numbers.py <path to 2024-03-04-15.json.gz>
"""
import gzip
import json
import sys
from collections import Counter

# The tracking plan: Object Action names, the source event, and the properties each must carry.
PLAN = {
    "Repository Created": {"when": ("CreateEvent", "ref_type", "repository"),
                           "props": {"repo_id": int, "owner_id": int, "is_org": bool}},
    "Code Pushed":        {"when": ("PushEvent", None, None),
                           "props": {"repo_id": int, "actor_id": int, "commits": int}},
    "Issue Opened":       {"when": ("IssuesEvent", "action", "opened"),
                           "props": {"repo_id": int, "actor_id": int, "issue_number": int}},
    "Pull Request Opened": {"when": ("PullRequestEvent", "action", "opened"),
                            "props": {"repo_id": int, "actor_id": int, "base_branch": str}},
    "Repository Starred": {"when": ("WatchEvent", "action", "started"),
                           "props": {"repo_id": int, "actor_id": int}},
}


def to_plan(e):
    """Map one raw event to (plan name, properties) or None if the plan does not track it."""
    p = e.get("payload") or {}
    for name, spec in PLAN.items():
        t, key, val = spec["when"]
        if e["type"] == t and (key is None or p.get(key) == val):
            props = {"repo_id": e["repo"]["id"], "actor_id": e["actor"]["id"], "owner_id": e["actor"]["id"],
                     "is_org": "org" in e,
                     "commits": p.get("size"),
                     "issue_number": (p.get("issue") or {}).get("number"),
                     "base_branch": ((p.get("pull_request") or {}).get("base") or {}).get("ref")}
            return name, {k: props[k] for k in spec["props"]}
    return None


def violations(name, props):
    return [k for k, typ in PLAN[name]["props"].items() if not isinstance(props.get(k), typ)]


tracked, untracked, bad = Counter(), Counter(), Counter()
zero_commit_pushes = 0
logins_per_id, ids_per_login = {}, {}
n = 0
for line in gzip.open(sys.argv[1], "rt"):
    e = json.loads(line)
    n += 1
    logins_per_id.setdefault(e["actor"]["id"], set()).add(e["actor"]["login"])
    ids_per_login.setdefault(e["actor"]["login"], set()).add(e["actor"]["id"])
    m = to_plan(e)
    if m is None:
        untracked[e["type"]] += 1
        continue
    tracked[m[0]] += 1
    if m[0] == "Code Pushed" and m[1]["commits"] == 0:
        zero_commit_pushes += 1
    for k in violations(*m):
        bad[(m[0], k)] += 1

print("raw events", n)
print("tracked by the plan", sum(tracked.values()), "= %.1f%%" % (100 * sum(tracked.values()) / n))
for k, v in tracked.most_common():
    print("  %-20s %7d" % (k, v))
print("not in the plan (top 5):", untracked.most_common(5))
print("property violations:", dict(bad) if bad else "none")
print("Code Pushed with commits == 0 (type-valid, meaning-wrong):", zero_commit_pushes)
print("actor ids with more than one login this hour:", sum(1 for s in logins_per_id.values() if len(s) > 1))
print("logins with more than one id this hour:", sum(1 for s in ids_per_login.values() if len(s) > 1))
