#!/usr/bin/env python3
"""The CONSTRUCTED code-assistant event stream for "AI feature metrics" (analyst 7) and
"Measuring an AI feature" (leader 5). No public AI-feature event stream exists, so this one is
generated from a fixed seed and says so on every page that uses it. The code below is the code
the page prints; its output is the only source of the page's numbers.

Internal build script. Not linked from any audience-facing page.

Usage:  python3 materials/copilot-constructed.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2022)

# Two versions of one assistant, 200 developers each, one working week.
# "short" suggests a line; "long" suggests a whole block. Every rate below is an assumption.
ARMS = {
    #          accept  kept 30s  kept 600s  deleted by 600s  chars
    "short": (0.26,    0.80,     0.62,      0.08,            40),
    "long":  (0.31,    0.70,     0.41,      0.19,            160),
}
rows = []
for arm, (p_acc, k30, k600, p_del, chars) in ARMS.items():
    for dev in range(200):
        p_dev = rng.beta(p_acc * 20, (1 - p_acc) * 20)          # developers differ
        shown = rng.poisson(60 * 5)                              # a week of suggestions
        acc = rng.random(shown) < p_dev
        u = rng.random(shown)
        kept30 = acc & (u < k30)
        kept600 = acc & (u < k600)                               # kept at 600s implies kept at 30s
        deleted = acc & (u > 1 - p_del)
        n_chars = rng.poisson(chars, shown)
        rows.append(pd.DataFrame({"arm": arm, "dev": f"{arm}-{dev:03d}", "accepted": acc,
                                  "kept_30s": kept30, "kept_600s": kept600,
                                  "deleted_600s": deleted, "chars": n_chars}))
ev = pd.concat(rows, ignore_index=True)
print("suggestion_shown events:", len(ev))

g = ev.groupby("arm")
out = pd.DataFrame({
    "shown": g.size(),
    "acceptance_rate": g["accepted"].mean(),
    "kept_30s_of_accepted": g.apply(lambda d: d.kept_30s.sum() / d.accepted.sum()),
    "kept_600s_of_accepted": g.apply(lambda d: d.kept_600s.sum() / d.accepted.sum()),
    "deleted_of_accepted": g.apply(lambda d: d.deleted_600s.sum() / d.accepted.sum()),
    "chars_accepted_per_shown": g.apply(lambda d: d.chars[d.accepted].sum() / len(d)),
    "chars_kept_600s_per_shown": g.apply(lambda d: d.chars[d.kept_600s].sum() / len(d)),
})
print(out.round(3).to_string())

per_dev = ev.groupby(["arm", "dev"])["accepted"].mean()
print("\nper-developer acceptance rate, 10th to 90th percentile:")
print(per_dev.groupby("arm").quantile([0.1, 0.9]).unstack().round(3).to_string())
