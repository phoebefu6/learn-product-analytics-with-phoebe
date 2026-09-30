#!/usr/bin/env python3
"""Actor-day sample for the engagement pages (power-user curve, defining "active").

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 materials/fetch-gharchive-actors.py <cache-dir> [--workers 8]

Streams two fixed hours a day, 03:00 and 15:00 UTC, for the 28 days 2024-03-04 to 2024-03-31
(56 hourly GH Archive files), and keeps every event whose actor id is divisible by 20: a
deterministic 5 percent sample of accounts, so the same accounts are followed through every hour.
Logins ending in "[bot]" are kept in the file and dropped by the reader, so the drop is visible.

Writes <cache-dir>/actors/<YYYY-MM-DD-H>.json : {actor_id: [login, n_events, n_push, n_pr_or_issue_opened]}
and <cache-dir>/actor-days.json combining them.

Source: GH Archive, https://www.gharchive.org/ . A day here means "seen in at least one of the two
sampled hours that UTC day", which is a sample of the day, not the whole day.
"""
import datetime as dt
import gzip
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

DAY0 = dt.date(2024, 3, 4)
HOURS = [(DAY0 + dt.timedelta(days=d), h) for d in range(28) for h in (3, 15)]
ACTOR_ID = re.compile(rb'"actor":\{"id":(\d+),')
MOD = 20
OUT = None


def name(day, h):
    return "%s-%d" % (day.isoformat(), h)


def _init(out):
    global OUT
    OUT = out


def one(item):
    day, h = item
    path = os.path.join(OUT, name(day, h) + ".json")
    if os.path.exists(path):
        return name(day, h), "cached"
    url = "https://data.gharchive.org/%s.json.gz" % name(day, h)
    proc = subprocess.Popen(["curl", "-sfL", "--retry", "3", url], stdout=subprocess.PIPE)
    acc, n = {}, 0
    with gzip.GzipFile(fileobj=proc.stdout) as gz:
        for line in gz:
            n += 1
            m = ACTOR_ID.search(line)
            if m is None or int(m.group(1)) % MOD:
                continue
            e = json.loads(line)
            a = acc.setdefault(e["actor"]["id"], [e["actor"]["login"], 0, 0, 0])
            a[1] += 1
            if e["type"] == "PushEvent":
                a[2] += 1
            elif e["type"] in ("PullRequestEvent", "IssuesEvent") and (e.get("payload") or {}).get("action") == "opened":
                a[3] += 1
    if proc.wait() != 0:
        raise RuntimeError("download failed: " + url)
    with open(path + ".tmp", "w") as f:
        json.dump({"events": n, "actors": acc}, f)
    os.rename(path + ".tmp", path)
    return name(day, h), "events %d sampled actors %d" % (n, len(acc))


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    base = sys.argv[1]
    workers = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
    out = os.path.join(base, "actors")
    os.makedirs(out, exist_ok=True)
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(out,)) as ex:
        for nm, msg in ex.map(one, HOURS):
            print(nm, msg, flush=True)
    combined = {}
    for day, h in HOURS:
        combined[name(day, h)] = json.load(open(os.path.join(out, name(day, h) + ".json")))
    with open(os.path.join(base, "actor-days.json"), "w") as f:
        json.dump(combined, f)
    print("hours:", len(HOURS))


if __name__ == "__main__":
    main()
