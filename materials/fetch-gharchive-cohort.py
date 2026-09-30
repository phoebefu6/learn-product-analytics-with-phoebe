#!/usr/bin/env python3
"""Stage 1 of the activation bench: stream GH Archive hours and keep only the cohort's events.

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 materials/fetch-gharchive-cohort.py <cache-dir> [--workers 6]

What it does
  1. Downloads the cohort hour 2024-03-04 15:00 UTC and records every repository whose
     CreateEvent (payload.ref_type == "repository") appears in it. Those repositories are
     the cohort: each one is born inside that hour, which GH Archive can see directly.
  2. Streams a fixed grid of later hours and keeps only events on cohort repositories:
       activation grid  hours H0 + 0, 2, 4, ... 166    (84 hours, one in two, days 0 to 6)
       return grid      hours H0 + 672, 674, ... 1006  (168 hours, one in two, days 28 to 41)
     Nothing else is stored; each hourly file (about 150 MB compressed) is read as a stream.
  3. Writes <cache-dir>/hours/<offset>.jsonl per hour (an hour already on disk is skipped, so a
     killed run resumes), then concatenates them into <cache-dir>/cohort-events.jsonl,
     one compact list per kept event:
       [offset_hours, type, repo_id, actor_id, actor_login, detail]
     detail = ref_type for Create/Delete, action for Issues/PullRequest, size for Push, else "".

Source: GH Archive, https://www.gharchive.org/ (hourly files at data.gharchive.org/YYYY-MM-DD-H.json.gz,
no login). Event schema: GitHub REST API "GitHub event types" documentation.
"""
import datetime as dt
import gzip
import json
import os
import sys
import re
import subprocess
from concurrent.futures import ProcessPoolExecutor

H0 = dt.datetime(2024, 3, 4, 15)
ACT_OFFSETS = list(range(0, 168, 2))                      # every second hour, days 0 to 6
RET_OFFSETS = list(range(24 * 28, 24 * 42, 2))            # every second hour, days 28 to 41


def url_for(offset):
    t = H0 + dt.timedelta(hours=offset)
    return "https://data.gharchive.org/%s-%d.json.gz" % (t.strftime("%Y-%m-%d"), t.hour)


REPO_ID = re.compile(rb'"repo":\{"id":(\d+),')


def stream(offset, want=None):
    """Yield parsed events. With `want` (a set of repo ids) only lines whose repo id is in it are
    parsed; the rest are counted and skipped, which is what makes 250 hours affordable."""
    # curl, not urllib: the bucket answers 403 to urllib's default user agent
    proc = subprocess.Popen(["curl", "-sfL", "--retry", "3", url_for(offset)], stdout=subprocess.PIPE)
    with gzip.GzipFile(fileobj=proc.stdout) as gz:
        for line in gz:
            if want is not None:
                m = REPO_ID.search(line)
                if m is None or int(m.group(1)) not in want:
                    yield None
                    continue
            yield json.loads(line)
    if proc.wait() != 0:
        raise RuntimeError("download failed: " + url_for(offset))


def detail(e):
    t, p = e["type"], e.get("payload") or {}
    if t in ("CreateEvent", "DeleteEvent"):
        return p.get("ref_type") or ""
    if t in ("IssuesEvent", "PullRequestEvent"):
        return p.get("action") or ""
    if t == "PushEvent":
        return int(p.get("size") or 0)
    return ""


def keep(offset, cohort):
    rows, n = [], 0
    for e in stream(offset, cohort):
        n += 1
        if e is None:
            continue
        rid = e["repo"]["id"]
        if rid in cohort:
            rows.append([offset, e["type"], rid, e["actor"]["id"], e["actor"]["login"], detail(e)])
    return offset, n, rows


_COHORT, _HDIR = None, None


def _init(cohort, hdir):
    global _COHORT, _HDIR
    _COHORT, _HDIR = set(cohort), hdir


def one_hour(o):
    off, n, rows = keep(o, _COHORT)
    tmp = os.path.join(_HDIR, "%d.tmp" % off)
    with open(tmp, "w") as f:
        f.write("# events %d\n" % n)
        for r in rows:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
    os.rename(tmp, os.path.join(_HDIR, "%d.jsonl" % off))
    print("offset %4d  %s  events %7d  kept %6d" % (off, url_for(off).rsplit("/", 1)[1], n, len(rows)), flush=True)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out_dir = sys.argv[1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
    os.makedirs(out_dir, exist_ok=True)

    cohort = {}
    cpath = os.path.join(out_dir, "cohort.json")
    if os.path.exists(cpath):
        cohort = {int(k): v for k, v in json.load(open(cpath)).items()}
    for e in ([] if cohort else stream(0)):
        if e["type"] == "CreateEvent" and (e.get("payload") or {}).get("ref_type") == "repository":
            cohort.setdefault(e["repo"]["id"], (e["actor"]["id"], e["actor"]["login"], e["repo"]["name"]))
    with open(cpath, "w") as f:
        json.dump({str(k): v for k, v in cohort.items()}, f)
    print("cohort repositories born in", H0.isoformat(), ":", len(cohort), flush=True)

    offsets = sorted(set(ACT_OFFSETS + RET_OFFSETS))
    hdir = os.path.join(out_dir, "hours")
    os.makedirs(hdir, exist_ok=True)
    todo = [o for o in offsets if not os.path.exists(os.path.join(hdir, "%d.jsonl" % o))]

    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(cohort, hdir)) as ex:
        list(ex.map(one_hour, todo))
    with open(os.path.join(out_dir, "cohort-events.jsonl"), "w") as f:
        for o in offsets:
            for line in open(os.path.join(hdir, "%d.jsonl" % o)):
                if not line.startswith("#"):
                    f.write(line)
    print("hours on disk:", len(offsets), flush=True)


if __name__ == "__main__":
    main()
