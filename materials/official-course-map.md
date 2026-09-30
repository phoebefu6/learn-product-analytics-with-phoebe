# Official course map - learn-product-analytics-with-phoebe

"Product Analytics: Events to Decisions". Bucket `data`, diff 2 (Core), audience both, two tracks:
Leader 6 (a1-a6, no code) + Analyst 8 (b1-b8, Python + in-browser). 45 minutes a session. Built
2026-09-29. Internal document: never linked from an audience page.

Evidence tiers used below:
- **read** = read at the primary source during this build (quote or number checked on the page itself)
- **reported** = only available through a secondary source (a transcript on another site, a blog
  summary); pages must say "reported" and never state it as law
- **measured** = computed in this build from real GH Archive rows by a script in `materials/`
- **constructed** = generated from a fixed seed; pages and widgets must say "constructed"

## Seams (link out in one line, never teach)

| Topic | Owner course |
|---|---|
| Retention curves, cohorts, survival, CLV | https://phoebefu6.github.io/learn-customer-retention-with-phoebe/ |
| North-star metric, driver trees | https://phoebefu6.github.io/learn-metric-decomposition-with-phoebe/ |
| E-commerce funnels, paths, PDP | https://phoebefu6.github.io/learn-user-journey-analytics-with-phoebe/ |
| A/B tests, causal proof of an activation lever | https://phoebefu6.github.io/learn-experimentation-with-phoebe/ |
| Building dashboards | https://phoebefu6.github.io/learn-business-intelligence-with-phoebe/ |
| Consuming metrics as an exec | https://phoebefu6.github.io/learn-data-literacy-with-phoebe/ |

This course owns: event instrumentation and the tracking plan, identity, defining "active",
activation and aha moments, engagement / stickiness / the power-user curve, feature adoption,
AI feature analytics, and the product review. Adoption funnels here are feature funnels
(saw -> tried -> used again), not purchase funnels.

## The data, and the decisions behind it

### GH Archive (read + measured)
- GH Archive records "the public GitHub timeline" and serves hourly files at
  `https://data.gharchive.org/YYYY-MM-DD-H.json.gz`, UTC, no login; since 2015-01-01 the files use
  the Events API format (read, gharchive.org).
- Event objects carry id, type, actor, repo, payload, public, created_at (read, GitHub REST docs
  "GitHub event types"). CreateEvent ref_type is branch, tag or repository; WatchEvent means "a
  user stars a repository"; IssuesEvent / PullRequestEvent actions include opened (read). The
  current docs no longer list PushEvent `size`; the 2024 files still carry it (measured: present).
- One hour, 2024-03-04 15:00 UTC (`2024-03-04-15.json.gz`, 150,807,371 bytes): 279,130 events;
  raw columns id, type, actor, repo, payload, public, created_at, org; PushEvent 56.2 percent,
  CreateEvent 14.2, PullRequestEvent 7.1, DeleteEvent 5.4, IssueCommentEvent 4.8, WatchEvent 3.4;
  74,491 actors, 409 of them `[bot]` logins producing 15.5 percent of events; events per actor
  median 1, mean 3.75, max 25,458 (a login without the [bot] suffix, `censameesss`); 52.1 percent
  of actors have one event; top 1 percent of actors (744) produce 38.7 percent of events; top five
  logins censameesss 25,458, github-actions[bot] 19,528, dependabot[bot] 8,962, renovate[bot]
  6,769, SolukGece 3,033. Human actors 74,082 in 76,584 sessions (30-minute gap), median 1 event
  per session, mean 3.08; 2,502 actors have 2+ sessions inside the hour; every one of the hour's
  distinct timestamps is shared by 2+ events, so created_at alone cannot order the stream
  (script: `event-stream-numbers.py`, log reproduced 2026-09-29).
- Tracking plan run on the same hour (`tracking-plan-numbers.py`): 5 plan events track 189,640
  events = 67.9 percent (Code Pushed 156,983, Repository Created 10,384, Pull Request Opened
  10,030, Repository Starred 9,447, Issue Opened 2,796); not in the plan, top: CreateEvent
  (branch/tag) 29,113, DeleteEvent 15,033, IssueCommentEvent 13,398, PullRequestEvent (other
  actions) 9,662, PullRequestReviewEvent 8,515; zero type violations; 234 Code Pushed events have
  commits == 0 (type-valid, meaning-wrong); CreateEvent 39,497 = branch 27,168 (68.8%) + repository
  10,384 + tag 1,945; the page's example event is id 36226160836, a PushEvent at
  2024-03-04T15:00:00Z, size 1, refs/heads/main; 7 actor ids appear with more than one login inside
  one hour (renames), 0 logins with more than one id. Lesson: key identity on the id.

### The activation cohort (the bench) - decision and reasoning
- **GH Archive cannot see sign-ups.** The first time an account appears in a window is not the
  day it was created: most accounts in any hour are years old. A "first seen" cohort would be a
  cohort of people who happened to be quiet before the window. That heuristic is rejected.
- **What GH Archive can see is a birth**: a CreateEvent with ref_type "repository" happens once,
  at the moment a public repository is created. So the unit is a **new repository**, the way a
  SaaS product counts a new workspace or project. It is honest about what it is: projects, not
  people, and only public ones.
- Cohort hour 2024-03-04 15:00-15:59 UTC: 10,384 repositories born (measured), 127 created by
  `[bot]` logins. Some accounts create many (mkarmark 115, direwolf-github 105 in the hour).
  **Cohort = the first new repository of each non-bot account in the hour: 8,348 repositories.**
  One account creating 115 repositories is automation, not 115 customers.
- Events by `[bot]` logins are dropped everywhere. Bots without the suffix cannot be detected
  from names reliably and stay in; the pages say so.
- Sampling: every second hour. Activation grid offsets 0, 2 ... 166 from the cohort hour
  (84 hours, days 0-6); return grid offsets 672, 674 ... 1006 (168 hours, days 28-41 = weeks 5-6).
  Every count is "seen in the sampled hours". 252 hourly files, about 37 GB streamed, nothing
  stored but the cohort's events (44,573 kept). Scripts: `fetch-gharchive-cohort.py` then
  `build-activation-sample.py`; the shipped file `assets/pa-sample.js` is 285,995 bytes.
- **Came back** = at least one non-bot event on the repository in the return grid.
  325 of 8,348 came back = 3.9 percent. Most new repositories are never touched again; that is
  itself the first finding.
- Behaviours per window (birth hour w0, first day w1, first 7 days w7; capped at 99): all events,
  pushes, separate days seen (w7 only; 1 by construction in w0/w1), issues or PRs opened,
  distinct non-bot people, stars received.

### Bench canon (python `pa_reference.py --check` and node `pa-bench.js` AGREE on every count, 8 presets x 2)

| Preset | Definition | Activated | Came back, activated | Came back, rest | Lift | Diff | Returners caught |
|---|---|---|---|---|---|---|---|
| push1 | 1+ push, first day | 2,779 (33.3%) | 151 = 5.4% | 174 / 5,569 = 3.1% | 1.74x | +2.3 pts | 46.5% |
| push7 | 1+ push, first 7 days | 3,268 (39.1%) | 210 = 6.4% | 115 / 5,080 = 2.3% | 2.84x | +4.2 | 64.6% |
| days2 | seen on 2+ days, first 7 | 1,186 (14.2%) | 154 = 13.0% | 171 / 7,162 = 2.4% | 5.44x | +10.6 | 47.4% |
| ppl2 | 2+ people, first 7 | 288 (3.4%) | 53 = 18.4% | 272 / 8,060 = 3.4% | 5.45x | +15.0 | 16.3% |
| work1 | 1+ issue or PR opened, first 7 | 214 (2.6%) | 31 = 14.5% | 294 / 8,134 = 3.6% | 4.01x | +10.9 | 9.5% |
| star1 | 1+ star, first 7 | 194 (2.3%) | 24 = 12.4% | 301 / 8,154 = 3.7% | 3.35x | +8.7 | 7.4% |
| vol3 (anti) | 3+ events of any kind, first 7 | 3,839 (46.0%) | 232 = 6.0% | 93 / 4,509 = 2.1% | 2.93x | +4.0 | 71.4% |
| burst10 (anti) | 10+ events in the birth hour | 117 (1.4%) | 4 = 3.4% | 321 / 8,231 = 3.9% | 0.88x | -0.5 | 1.2% |

Break button (seeded shuffle, mulberry32 + Fisher-Yates, seed 20240304) lifts: push1 1.04,
push7 0.97, days2 0.85, ppl2 1.07, work1 1.33, star1 1.33, vol3 0.97, burst10 1.32. Differences
-0.6 to +1.3 points. The shuffle keeps the group size and removes the link, so these are what "no
signal" looks like at each group size; small groups (117 to 288) wander furthest from 1.

What the bench shows, stated honestly (these are the only claims pages may make from it):
1. Volume is not worthless but it is broad: "3+ events in week one" calls 46.0 percent activated
   and catches 71.4 percent of returners, at a lift of 2.93x; "seen on 2+ days" calls 14.2
   percent activated at 5.44x. Same data, the repeat-day rule separates far better per head.
2. The volume trap in its sharpest form: a busy birth hour (10+ events) has lift 0.88x, 4 of 117
   came back. The count is noise-sized, so the claim is "no signal", never "harm"; its shuffled
   version reads 1.32x, which shows how far 117 rows wander by chance. Setup activity is not
   engagement.
3. The strongest predictors are early versions of the outcome (coming back on a second day) or
   things the owner does not control (a star). A predictor is not a lever: proving that pushing
   people toward the behaviour changes return needs an experiment (seam: experimentation).
4. Where the brief expected "total events" to reverse at every window, the data does not show
   that: it reverses only in the birth hour. Pages teach what the data shows.

Other birth-hour volume thresholds (measured with the same rules, exploration log 2026-09-29):
2+ events in the birth hour 69.5 percent activated, lift 1.49x; 5+ 10.8 percent, 1.58x.

### Adoption (measured, `adoption-numbers.py`, same cohort, first 7 days)

| Feature | Breadth | Depth median / mean | First use median | Came back: users vs rest |
|---|---|---|---|---|
| push | 3,268 = 39.1% | 2 / 3.6 | 0 h (489 of 3,268 after day one) | 6.4% vs 2.3% |
| branch created | 5,744 = 68.8% | 1 / 1.4 | 0 h (87 after day one) | 4.3% vs 3.0% |
| issue opened | 44 = 0.5% | 1 / 2.5 | 15 h (17 after day one) | 29.5% vs 3.8% |
| PR opened | 183 = 2.2% | 1 / 3.3 | 6 h (64 after day one) | 12.0% vs 3.7% |
| release | 36 = 0.4% | 1 / 2.2 | 3 h (9 after day one) | 11.1% vs 3.9% |
| wiki edit | 11 = 0.1% | 1 / 3.9 | 2 h (3 after day one) | 9.1% vs 3.9% |

Breadth of use: 0 features 2,171 (26.0%) came back 2.0%; 1: 3,289 (39.4%) 3.0%; 2: 2,685 (32.2%)
5.7%; 3: 187 (2.2%) 11.8%; 4+: 16 (0.2%) 37.5%. "Branch created" is the widest-adopted feature
and the weakest signal: most of it is the default branch being created by the first push, a
setup artefact. Small groups (11 wiki, 16 four-feature repos) are flagged as small on the page.

### Engagement (measured, `fetch-gharchive-actors.py` + `engagement-numbers.py`)
- Sample: every account whose id is divisible by 20 (deterministic 5 percent), two sampled hours a
  day (03:00 and 15:00 UTC), 28 days 2024-03-04 to 2024-03-31, 56 files. A "day active" means
  seen in either sampled hour that day. 79,555 accounts seen; 98 `[bot]` accounts dropped.
- Top 1 percent of accounts by events hold 30.1 percent of sampled events.
- Three definitions of active, same accounts:
  - any event: MAU 79,555; average DAU 5,110.6; DAU/MAU 6.4%; average WAU 27,490.0; DAU/WAU 18.6%
  - pushed code: MAU 48,946; DAU 3,217.9; DAU/MAU 6.6%; WAU 17,094.2; DAU/WAU 18.8%
  - opened an issue or PR: MAU 8,993; DAU 452.4; DAU/MAU 5.0%; WAU 2,761.2; DAU/WAU 16.4%
- L28 (any event): 1 day 66.7%, 2-3 days 24.0%, 4-7 7.5%, 8-14 1.6%, 15-21 0.2%, 22-28 0.1%;
  62 accounts on all 28 days (0.08%); median 1 day; top 10% of accounts hold 33.5% of account-days;
  105 accounts on 22+ days, 17 of them with bot-like names but no [bot] suffix (crude name check:
  bot, -ci, ci-, sync, deploy, commenter, assistant). Pushed: 1 day 64.2%, 2-3 26.0%, 4-7 8.0%,
  8-14 1.5%, 15-21 0.1%, 22-28 0.2%; 57 on all 28; 92 on 22+ (11 bot-like). Opened: 1 day 77.5%,
  2-3 18.3%, 4-7 3.7%, 8-14 0.4%; 1 on all 28; 4 on 22+ (1 bot-like).
- The curve is left-leaning, not a smile. Part of that is real (most public GitHub accounts are
  occasional) and part is sampling: two hours a day cannot see a daily user who works at other
  hours. Pages teach both and never claim the curve describes GitHub's real stickiness.
- `assets/pa-engagement.js` holds the three L28 histograms (json.dumps).

### Constructed code-assistant stream (constructed, `copilot-constructed.py`, seed 2022)
Two versions, 200 developers each, a week: "short" (line) and "long" (block). All rates are
assumptions stated in the script. Output: 119,905 suggestion_shown events.

| Arm | Shown | Acceptance | Kept 30s of accepted | Kept 600s | Deleted by 600s | Chars accepted per shown | Chars kept 600s per shown |
|---|---|---|---|---|---|---|---|
| long | 60,023 | 0.309 | 0.693 | 0.408 | 0.190 | 49.455 | 20.183 |
| short | 59,882 | 0.262 | 0.800 | 0.618 | 0.078 | 10.487 | 6.486 |

Per-developer acceptance 10th-90th percentile: long 0.177-0.467, short 0.127-0.390.
Lesson: acceptance and characters kept favour "long"; persistence rate favours "short". The
metric has to be chosen for the decision, and every page says the stream is constructed.

## Verified facts from primary sources

| Claim | Tier | Source |
|---|---|---|
| Ziegler et al. define acceptance rate as "the fraction of completions shown to the developer that are subsequently accepted for inclusion in the source file" | read | Ziegler et al. 2022, section 2 |
| Survey: 17,420 users emailed; 2,047 responses matched to usage data (10 Feb - 6 Mar 2022) | read | section 3.2 |
| Abstract: "the rate with which shown suggestions are accepted, rather than more specific metrics regarding the persistence of completions in the code over time, drives developers' perception of productivity" | read | abstract |
| Acceptance rate correlates best with aggregate perceived productivity, rho = 0.24, P < 0.0001; "there is still notable unexplained variance"; all persistence measures less well correlated | read | section 4 |
| Copilot acceptance rate 27% in the study, mean DCPU above 31; IntelliCode Compose CTR 10% | read | section 2 |
| Acceptance by time: weekend 23.5%, weekday non-working 23%, working hours 21.2% | read | section 5 |
| Productivity measured with SPACE dimensions S, P, C, E; persistence at 30, 120, 300, 600 s | read | sections 3.1-3.2 |
| GitHub docs: acceptance rate "measures how often developers accept Copilot's suggestions"; "Look for patterns across these signals rather than focusing on any single number" | read | docs.github.com Copilot metrics concepts page |
| Power User Curve: "a histogram of users' engagement by the total number of days they were active in a month"; "also commonly called the activity histogram or the 'L30' (coined by the Facebook growth team)"; DAU/MAU "is a single number and so blurs this variance" | read | Li Jin and Andrew Chen, a16z, 6 Aug 2018 (the brief said Andrew Chen alone; the byline is both) |
| "Facebook would have a very right-leaning smile, with 60%+ of its MAUs coming back daily" | read (their claim, not verified) | same |
| Facebook "7 friends in 10 days": "The single biggest thing we realized was to get any individual to 7 friends in 10 days" | reported | transcript quoted by Startup Archive of Chamath Palihapitiya's talk "How we put Facebook on the path to 1 billion users" (Oct 2012); video not watched; Benn Stancil (Mode, 30 Jan 2015) calls it a memorable rally cry, not a threshold |
| Mixpanel's "Magic numbers are an illusion" cites Andrew Chen that 7 in 10 could as easily have been 10 in 12 or 5 in 1 | reported | Mixpanel blog (page date shown as updated, not original) |
| Slack: "we decided that any team that has exchanged 2,000 messages in its history has tried Slack - really tried it"; "after 2,000 messages, 93% of those customers are still using Slack today" | read | Stewart Butterfield interview, First Round Review, 27 Feb 2015 ("Based on experience of which companies stuck with us and which didn't") |
| Object-Action naming: "choose your objects ... Then define actions ... your event reads Product Viewed"; "We like Proper Case for events and snake_case for properties"; "The only thing that really matters is that you keep it consistent!" | read | Twilio Segment, "Naming conventions for clean data" (moved from segment.com/academy) |
| PostHog identify: merges the anonymous person into the identified person; call identify at app load and after login; call reset() on logout; refuses re-identifying with a different distinct ID; blocks generic ids like null, anonymous, guest | read | posthog.com/docs/product-analytics/identify |
| Segment Identify spec | not read: segment.com/docs returned 403; not quoted |

Correcting famous claims: grep of `github_repo/learn-*/courses/` for "7 friends", "2,000 messages",
"power user curve", "Ziegler" found no sibling page that repeats the Facebook or Slack numbers as
law (hits were for generic "acceptance rate" and "stickiness"); nothing to file.

## Per-session coverage

### Leader track (no code)
- **a1 Events are the product's diary** - what an event is (actor, action, object, time,
  properties), Object-Action naming (Segment), the tracking plan as a contract, what the diary
  cannot see (GH Archive: no sign-ups, no private repos). Numbers: the one-hour stream facts.
- **a2 The moment that predicts staying** - activation vs aha; Facebook 7/10 (reported) and
  Slack 2,000 (read, with its survivorship problem); correlation is not cause; the bench headline
  (days2 5.44x vs push1 1.74x) quoted from canon; link experimentation.
- **a3 Engagement you can defend** - DAU/MAU, why one ratio blurs; L28 / power-user curve (Jin and
  Chen 2018); vanity vs signal; the GH Archive L28 with the sampling caveat; three definitions of
  active give three MAUs (79,555 / 48,946 / 8,993).
- **a4 Adopted is not valued** - breadth, depth, time-to-adopt; branch 68.8% vs issue 0.5%; the
  0-to-4-features gradient; "adopted" counted from setup artefacts.
- **a5 Measuring an AI feature** - acceptance rate, persistence, kept vs edited; Ziegler exact
  findings (rho 0.24, unexplained variance, perception not value); GitHub docs caveat; the
  constructed short/long comparison labelled constructed.
- **a6 The product review** - reading a product dashboard; the question set (definition, cohort,
  denominator, sampling, bots, cause); a worked review of this course's own numbers.

### Analyst track
- **b1 The tracking plan as code** - schema dict, Object-Action, properties with types, a
  validator, identity (id vs login, 7 renames in one hour; anonymous-to-known merge from PostHog
  docs). Numbers from `tracking-plan-numbers.py`.
- **b2 Meet the event stream** - load one real hour with pandas, flatten, bots, actors,
  sessionize with a 30-minute gap. Numbers from `event-stream-numbers.py`.
- **b3 Defining "active"** - same accounts, three definitions, three numbers; DAU/WAU/MAU from
  `engagement-numbers.py`.
- **b4 Hunting the activation moment** - load `pa-sample.js`, sweep candidate behaviours and
  thresholds, lift and returners caught; correlation is not cause; link experimentation.
- **b5 The power-user curve from real rows** - L28 histograms, concentration, where automation
  hides in the right tail.
- **b6 Adoption funnels and time-to-adopt** - feature funnel per repository, breadth/depth/time
  table, the breadth gradient.
- **b7 AI feature metrics** - constructed copilot stream, acceptance vs persistence vs characters
  kept; Ziegler definitions.
- **b8 The activation bench (BENCH)** - the widget; ladder; break button; the cohort decision.

## Not covered (honest list)
- Retention curves, cohort tables, survival, CLV (seam: customer retention).
- North-star and driver trees (seam: metric decomposition). Experiment design (seam).
- Dashboard building in a BI tool (seam). Vendor comparisons (Amplitude vs Mixpanel vs PostHog).
- Mobile SDK specifics, consent and privacy law for tracking (GDPR/ePrivacy), server-side
  tagging, warehouse-native CDPs.
- Any real AI-feature event stream: none is public; the AI pages use a constructed one.
- The Segment Identify spec text (403 during the build).
- Facebook's and Slack's internal analyses behind their numbers: never published.

## Citation appendix (use these exact forms)
- GH Archive. https://www.gharchive.org/ (hourly archives, data.gharchive.org).
- GitHub Docs. "GitHub event types." https://docs.github.com/en/rest/using-the-rest-api/github-event-types
- Ziegler, A., Kalliamvakou, E., Simister, S., Sittampalam, G., Li, A., Rice, A., Rifkin, D., and
  Aftandilian, E. (2022). "Productivity Assessment of Neural Code Completion." MAPS '22.
  arXiv:2205.06537.
- Jin, L. and Chen, A. (2018). "The Power User Curve: The best way to understand your most engaged
  users." a16z, 6 August 2018.
- Butterfield, S., interviewed in First Round Review (2015). "From 0 to $1B - Slack's Founder
  Shares Their Epic Launch Strategy."
- Palihapitiya, C. (2012). "How we put Facebook on the path to 1 billion users" (talk). Reported
  via transcript excerpts; Stancil, B. (2015). "Facebook's aha moment was simpler than you think." Mode.
- Twilio Segment. "Naming conventions for clean data."
- PostHog Docs. "Identifying users." https://posthog.com/docs/product-analytics/identify
- GitHub Docs. "Copilot metrics" concepts page.
