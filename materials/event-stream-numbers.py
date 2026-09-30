#!/usr/bin/env python3
"""Every number quoted on "Meet the event stream" (analyst 2). Runs the page's own pandas code.

Internal build script. Not linked from any audience-facing page.

Usage
-----
  python3 materials/event-stream-numbers.py <path to 2024-03-04-15.json.gz>

The file is one GH Archive hour, https://data.gharchive.org/2024-03-04-15.json.gz (about 150 MB).
"""
import sys

import pandas as pd

path = sys.argv[1]
raw = pd.read_json(path, lines=True, compression="gzip")
df = pd.DataFrame({
    "ts": pd.to_datetime(raw["created_at"], utc=True),
    "type": raw["type"],
    "actor": raw["actor"].str["login"],
    "actor_id": raw["actor"].str["id"],
    "repo": raw["repo"].str["name"],
})
print("events", len(df), "columns in the raw file", list(raw.columns))
print("span", df.ts.min(), "to", df.ts.max())
print((df["type"].value_counts(normalize=True) * 100).round(1).head(6).to_string())
df["is_bot"] = df["actor"].str.endswith("[bot]")
print("actors", df.actor_id.nunique(), "bot actors", df[df.is_bot].actor_id.nunique(),
      "bot share of events %.1f%%" % (100 * df.is_bot.mean()))
per = df.groupby("actor_id").size()
print("events per actor: median %d, mean %.2f, max %d; actors with 1 event %.1f%%" % (
    per.median(), per.mean(), per.max(), 100 * (per == 1).mean()))
top = df.groupby("actor").size().sort_values(ascending=False).head(5)
print("top actors:", top.to_dict())
top1 = per.sort_values(ascending=False)
k = max(1, len(top1) // 100)
print("top 1%% of actors (%d) produce %.1f%% of events" % (k, 100 * top1.head(k).sum() / len(df)))

hum = df[~df.is_bot].sort_values(["actor_id", "ts"])
gap = hum.groupby("actor_id")["ts"].diff()
hum = hum.assign(new=(gap.isna() | (gap > pd.Timedelta(minutes=30))))
hum["session"] = hum.groupby("actor_id")["new"].cumsum()
sess = hum.groupby(["actor_id", "session"]).agg(n=("type", "size"), start=("ts", "min"), end=("ts", "max"))
print("human actors", hum.actor_id.nunique(), "sessions", len(sess),
      "median events/session %d, mean %.2f" % (sess.n.median(), sess.n.mean()))
print("actors with 2+ sessions inside the hour", int((hum.groupby("actor_id")["session"].max() >= 2).sum()))
same = (df.groupby("ts").size() > 1).mean()
print("share of distinct timestamps shared by 2+ events %.1f%%" % (100 * same))
