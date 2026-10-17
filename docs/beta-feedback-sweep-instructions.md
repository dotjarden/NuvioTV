# Beta feedback sweep — canonical procedure

This file is the single source of truth for the daily beta-feedback sweeps. Both runs follow it:

- **Morning sweep** — cloud Routine ("NuvioTV morning feedback sweep — 8am ET", fires 12:00 UTC;
  created 2026-08-21, replacing the old local scheduled task on Christian's machine).
- **Evening sweep** — cloud Routine ("NuvioTV Reddit feedback sweep — 7pm ET", fires 23:00 UTC).

The morning sweep is deliberately an hour after the Daily GitHub Issue Check Routine (11:00 UTC)
so the two never race each other on the same GitHub state.

Where a sweep's own prompt and this file differ, **this file wins** — which is why behaviour
changes land here rather than in the two Routines' prompt boxes. (Both prompts open by telling the
run to read this file first, so a change here reaches both sweeps on their next firing with no UI
edit.) **New 2026-08-24: every sweep now merges its branch into `main` as it lands — see §6.** As of 2026-08-21 the sweep
covers **two sources**: the Reddit beta thread *and* the GitHub repo (issues + pull requests).
GitHub was added after issue #1 sat 27 days without a reply while the Reddit thread got all the
attention (see `docs/issue-triage-plan-2026-08-21.md` §6.3). **As of 2026-10-08 there is a third
source, Christian's Reddit DMs (chat rooms + the legacy inbox) — see §1b.** It is the one source
the cloud sweeps cannot read themselves: it needs the logged-in ego lite session on Christian's
Mac, so a local scheduled task does the fetch and the cloud sweeps report its freshness.

## 1. Reddit thread check

1. Fetch the thread's public Atom feed:
   `https://www.reddit.com/r/NuvioForks/comments/1wtmutc/tvos_nuviotv_a_native_apple_tv_app_built_on/.rss`
   (r/NuvioForks, post `1wtmutc`, live since 2026-09-29. The old r/Nuvio thread `1v26ebw` was removed by
   that sub's moderators on 2026-09-27 and is archived; do not fetch it.)
   using a unique descriptive User-Agent such as `nuviotv-beta-feedback-tracker/1.0` (a generic
   Mozilla UA gets 403'd).
2. If reddit.com is unreachable from the environment (network policy), **do not guess or
   fabricate feed content**. Note the blocked fetch in the digest and continue with the GitHub
   check below — a blocked Reddit fetch no longer aborts the whole sweep, but it must never be
   silently papered over.
3. Compare against the watermark (newest comment id + timestamp) recorded in
   `docs/beta-feedback-tracker.md`'s header. Comments at or before the watermark are already
   processed.

## 1b. Reddit DM check (chat rooms + legacy inbox)

Testers write to Christian directly as often as they post in the thread — Steven's whole
beta.17/18/19 cycle ran over Reddit chat, and u/marcomez18 and u/napes22 both asked for things
in DMs that never reached the thread. Those messages are feedback like any other and belong on
the tracker, so the sweep reads them. Two facts shape how:

- **Reddit chat has no public feed and no API the fork can register for.** The chat is a
  Matrix backend (`matrix.redditspace.com`); the only credential is the short-lived chat token
  the logged-in web app keeps in `localStorage`, and the only logged-in Reddit session is the
  ego lite browser on Christian's Mac. **The cloud sweeps therefore never fetch DMs.** They
  read the tracker's DM line (below) and report its age. Do not try the Matrix API, the chat
  page, or any credential from a cloud run; do not ask Christian to paste a token.
- **The fetch is a script, local only:** `scripts/reddit/fetch-dms.sh` (wrapper) runs
  `scripts/reddit/fetch-dms.mjs` inside the ego-browser runtime. It lists every joined chat
  room via the Matrix API (so a *new* tester's first DM is seen without anyone knowing the room
  id), reads the messages newer than the watermark with the sender's display name and the
  exact timestamp, flags image/video attachments as `[image mxc://…]`, and reads the legacy
  inbox (`/message/inbox.json`: private messages, comment replies, username mentions) with the
  session cookies. The token stays inside that process; nothing secret is written to disk.
  Known rules are in the wrapper's header and in memory `reddit-dm-sweep` — the short version:
  ego lite must be running and signed in to reddit.com, calls need stdin on `/dev/null`, ego
  prints its output on stderr, and the task space is resolved by numeric id (by-name creation
  hangs now and then).

### 1b.1 Who runs it

- **Local scheduled task `nuviotv-reddit-dm-check`** (desktop app, `~/.claude/scheduled-tasks/`,
  fires 8:40 AM and 7:40 PM local, i.e. ~40 min after each cloud sweep so their `main` merge
  has landed). It pulls `main`, runs the fetch against the DM watermark, applies §1b.2–1b.3,
  commits on `main`, pushes. It only runs while the desktop app is open; a missed firing runs
  at the next launch.
- **An interactive session** that is already reading DMs for other reasons (a Steven verdict,
  a tester repro) applies the same steps and moves the watermark, so the scheduled task finds
  nothing new.
- **Cloud sweeps (morning / evening):** read the DM line, compute its age, and put a mandatory
  `DMs:` line in the digest (§1b.4). Nothing else.

### 1b.2 Running the fetch

```
scripts/reddit/fetch-dms.sh --since <DM_WATERMARK> --summary
```

`<DM_WATERMARK>` is the ISO timestamp on the tracker header's **`Reddit DMs (chat + inbox)`**
line. The digest prints, per room with new messages, every message newer than the watermark
(`sender (me)` marks Christian's own), then the new inbox items, then
`Newest event overall (next watermark): <ISO>` — that value becomes the new watermark. Drop
`--summary` for JSON. Exit codes: `3` = no or expired chat token (tell Christian to open
`reddit.com/chat` in ego lite and sign in; leave the watermark alone), `4` = ego-browser not
reachable or wedged (same: leave the watermark, log the miss). **Never move the watermark on a
failed fetch, and never fabricate DM content** — a blocked DM check is reported, not papered
over, exactly like a blocked thread fetch.

### 1b.3 Classifying DMs

Same rules as thread comments (§3 and the tracker's own header: 8-field rows, `\|` inside
cells, ` — *Prior:* ` between dated notes), with these DM specifics:

- **Row link:** a chat message has no permalink. Write `DM (Reddit chat, u/<name>, <ISO ts>)`
  in the link position; an inbox item uses its `context` permalink when it has one.
- **Christian's own messages** (`(me)`) are context, never items — except when they state that a
  fix shipped or a question was answered, which updates the matching row's status, the same
  exception the thread check makes for `isSubmitter`.
- **Inbox comment replies on the beta thread duplicate §1.** Dedupe by comment id against the
  thread watermark; only inbox items from *other* subs, mentions, and private messages (`pm`)
  are new information.
- **Steven's room (u/mrStevenx3) is usually already handled** by the interactive session that
  read his verdict the same day — CLAUDE.md's open-items list names the verdict record
  (`docs/steven-*-verdict-*.md`) and the tracker rows it created. Check there first; if the
  message is already recorded, note "already triaged in <doc>" in the digest and do not add a
  row. If it is *not* recorded, it is an unread verdict: add the rows, and list the message as
  a **comms-owed item** (his DMs always get a reply).
- **Attachments** (`[image …]`, `[video …]`, Smash links) cannot be read by the script. Note
  them in the row as "N photos attached, unread" so the next interactive session pulls them
  (recipe in memory `reddit-chat-smash-fetch`). Never record what a photo "probably shows".
- **A DM awaiting Christian's reply is a comms-owed item** and stays in the digest until a reply
  is sent. The sweep **never sends a DM**: replies go through the copy rule (CLAUDE.md,
  SlopMonster loop) and Christian's go, in an interactive session.
- **Privacy:** rows carry the reporter's Reddit handle and a one-line paraphrase of the ask,
  the same as thread comments. Do not paste whole private conversations into the tracker or
  the dashboard; link the room id only in the update log if a later session needs it.

### 1b.4 What the tracker and the digest carry

- Tracker header line (keep it one line, directly under **Newest comment seen (watermark)**):
  `**Reddit DMs (chat + inbox):** last checked <YYYY-MM-DD HH:MMZ> (<local task|interactive|by hand>) — watermark <ISO ts> (<who/what that newest event was>); <n> rooms, <k> new messages, <m> inbox items; <one-line outcome>`
  The watermark is the newest chat or inbox event the run *processed*, usually Christian's own
  last reply.
- Update-log line per DM run, like any sweep: `**YYYY-MM-DD (DM check, local task)** — …`.
  A run with nothing new logs `DMs: quiet` and still refreshes the header line's "last checked".
- **The digest's `DMs:` line is mandatory for every sweep, cloud or local.** A cloud sweep
  writes `DMs: last checked <when> by <whom>, <age>h ago — <outcome>` and, when the age passes
  **36 h**, prefixes it with ⚠️ and names the cause it can see (desktop app closed, ego lite
  signed out per the last update-log entry, …). A local run writes the fetch outcome. As with
  GitHub, omission is indistinguishable from not looking.
- A DM-only change (new row, status change, comms-owed) makes the run a **normal run** for §3
  and §4 — dashboard ITEMS, digest and lanes updated, artifact republished. DM-sourced rows
  live in the same tables and the same ITEMS array; `DM` in the link cell is what marks them.

## 2. GitHub check (issues + pull requests)

Repo: `youngchris29-art/NuvioTV`. Use whatever GitHub access the session has, in this order of
preference: GitHub MCP tools → `gh` CLI → unauthenticated public API via WebFetch
(`https://api.github.com/repos/youngchris29-art/NuvioTV/issues?state=open` — this endpoint
returns PRs too; a `pull_request` key marks them).

1. **Open issues:** for each, check for comments newer than the sweep's last run.
   - A new issue → a tracker row like any other feedback source (priority, bucket, status),
     with the issue URL noted in the row and the reporter's GitHub handle as the who.
   - A new comment on an existing issue → update its row exactly as a Reddit reply would.
   - An issue awaiting *our* reply (retest ask, close-or-confirm, requested info) is a
     **comms-owed item** and must appear in the digest until posted.
2. **Open pull requests:** note number, title, branch, mergeability/CI state, and what is
   blocking. Surface them in the digest. **The sweep never merges, closes, or pushes to a PR**
   — it only reports.
3. If GitHub is unreachable, say so in the digest — never skip the check silently.
4. The digest's **GitHub line is mandatory** even on a quiet day: `GitHub: quiet (2 open
   issues unchanged, 0 PRs)` beats omission, because omission is indistinguishable from
   the pre-2026-08-21 behavior of not looking.

## 3. Tracker + dashboard update

New items or changes from **either source** →

- `docs/beta-feedback-tracker.md`: append/update item rows, header bullets, update log.
  Never remove manual edits — the daily run only appends/updates.
- `docs/beta-feedback-dashboard.html`: the ITEMS array in its bottom `<script>` (one 7-field
  entry per tracker row: id, priority, arrow up/down on priority change, bucket
  [open|waiting|unreleased|shipped|closed|declined], short stable title, "State · qualifier"
  status label, one-sentence note), the ~5 header pills, the "Latest sweep" digest (push the
  previous digest into the Archive as a new details entry), and the Now/Next/Waiting lanes.
  Tiles and counts derive from ITEMS at runtime — **never hand-edit numbers in markup**.
- `docs/beta-feedback-items.json` (**new 2026-10-17**): the machine-readable mirror that the
  **NuvioTV Tester Feedback** dashboard (https://claude.ai/artifact/UcBu7mTfKqyiW9dnywnYXX) reads
  live on every open, from
  `https://raw.githubusercontent.com/youngchris29-art/NuvioTV/main/docs/beta-feedback-items.json`.
  It needs **no republish** — the file on `main` is the dashboard. One object per tracker row under
  `rows`, nine string fields: `id`; `kind` (`Bug` | `Feature request` | `UX feedback`, from the ID
  prefix); `priority` (`P0`…`P4`, the current one, no arrows); `stage`; `tester`; `build` (the beta
  or rc the fix shipped in, e.g. `beta.19-rc5`; empty unless stage is Released); `reporter`
  (`u/name`, `GitHub (handle)`, or `In-house` for items Christian or a review found); `first_seen`
  (`YYYY-MM-DD`); `summary` (one plain sentence, no markdown, ≤ 170 characters). `stage` is one of
  `Open` | `Released` | `Closed, no fix` — a fix counts as **Released** once it is in a build a
  tester holds (a beta *or* an rc), not when it is merged. `tester` depends on stage — Open:
  `Not started` | `Waiting on reporter` | `Reopened after fix` | `Researched, not built`; Released:
  `Confirmed by tester` | `Partly confirmed` | `Awaiting tester` | `In-house only` (nobody outside
  will report back) | `Closed unconfirmed` (closed under the no-re-report rule); Closed, no fix:
  `Not a bug / declined / superseded` | `Duplicate of <ID>`. Every row the run adds, and every row
  whose tracker Status it changes, gets its JSON row added or updated **in the same commit**: a
  tester verdict that confirms a fix flips `tester` to `Confirmed by tester`; one that says it is
  still broken moves the row to `Open` / `Reopened after fix`; a cut moves `Awaiting next build`
  items to `Released` with the build. Bump the top-level `generated` timestamp, keep the `_about`
  key, and validate before committing —
  `python3 -c "import json; json.load(open('docs/beta-feedback-items.json'))"` — because a syntax
  error blanks the live dashboard for every reader until the next push.
- GitHub-sourced rows live in the same ITEMS array and the same tracker tables as Reddit rows;
  they are distinguished by the issue link in the row, not by a separate silo.

## 4. Republish the dashboard

Republish with the Artifact tool: file `docs/beta-feedback-dashboard.html` **with** url
`https://claude.ai/code/artifact/0d62393a-48c8-4bf9-ba1e-43a996052abf` (WebFetch that url first
if the tool asks; keep the 📺 favicon). **Never publish without the url.**

The **Tester Feedback** dashboard (`docs/beta-feedback-items.json`) is never republished: it reads
the JSON from `main` when opened, so pushing `main` (§6) is what updates it.

## 5. Quiet run

A run is quiet only when **every** source it reads held still: Reddit watermark unchanged **and** no new
GitHub issue/PR activity (a cloud sweep does not read DMs, so a stale-but-unchanged DM line
does not make it a normal run — it makes it a ⚠️ line in the digest; a local DM run is quiet
when the DM watermark holds). Then: update only the last-checked lines in both files, commit
`sweep: quiet run YYYY-MM-DD`, skip the republish. Activity on either source makes it a normal
run for both files. **A quiet run still merges to `main` per §6** — the republish is what a quiet
run skips, never the merge.

## 6. Commit, then merge to `main` — every sweep, as it lands

Commit tracker + dashboard (+ anything else the run touched) together and push to the session's
designated branch.

**Then merge that branch into `main` and push `main`. This is not optional, and it applies to
quiet runs too.** Christian authorised this standing on 2026-08-24; it is the explicit permission
the session's default "never push to a branch other than your designated one" rule asks for, and
it is scoped to exactly this: merging a sweep's own commits into `main`. It does not authorise
pushing anything else to `main`, force-pushing, or rewriting history.

### Why this step exists

Each scheduled sweep is handed a *fresh* `claude/*` designated branch and clones `main`. Before
this rule, sweeps committed there, pushed, and nothing ever merged back — so `main` froze while
sibling branches accumulated the real history, and each new session started blind to the previous
one. On 2026-08-24 the morning sweep found `main` frozen at `50cb163` since 08-22 with **four**
unmerged sweep branches, and found concrete damage: the 08-23 *evening* run had re-derived the
tracker header from the 08-22 state because its checkout could not see that morning's run. A day
of history was one stale clone away from being lost. Merging on landing is what stops that.

### The merge

```
git push -u origin <designated-branch>
git fetch origin main
git checkout main && git merge --no-ff <designated-branch> && git push origin main
git checkout <designated-branch>
```

**Classifier fix (2026-08-28):** every one of these commands is now explicitly
allowlisted in the checked-in `.claude/settings.json` (Christian approved and
created it by hand after five classifier-blocked merges, 08-24 → 08-28). Cloud
clones inherit it, so the merge should no longer be blocked. If a merge is
*still* refused despite the allowlist, that is a new finding — name it in the
digest, and fall back to the documented hand-fold route (file-level three-way
fold committed as a normal commit + a row in the do-not-re-merge table below)
rather than leaving the branch stranded.

Use `--no-ff` so each sweep stays one identifiable commit range in `main`'s history.

**The cloud checkout arrives shallow (2026-09-13).** In a shallow clone
`git rev-list --count origin/main..<branch>` over-reports unmerged commits and
`git diff origin/main...<branch>` fails with `no merge base`, which makes
already-merged branches look stranded. Run `git fetch --deepen=500 origin` before
trusting those counts in the orphaned-sweep-branch audit below. A fresh clone may
also sit behind `origin/main`, so catch it up before merging.

**On conflict** (only possible if `main` moved while the sweep ran) the two files conflict
predictably, and the resolution is mechanical:

- **Header lines** (`Last checked`, `Newest comment seen`, the dashboard's `Last checked` pill) —
  take the *newer* run's text, and make sure the older run's text survives in that line's
  `— *Prior:*` chain.
- **Update log entries / dashboard digest** — keep **both** sides. These are append-only; losing
  one is the exact failure this rule exists to prevent.
- **Item rows / the ITEMS array** — keep both sides' edits unless they touch the same field of the
  same id, in which case the newer run wins.

If a conflict is *not* mechanically resolvable that way, **stop, leave `main` untouched, and say
so in the digest** — never force-push, and never drop a side to make the merge go through.

### Absorb orphaned sweep branches

While on `main`, also pick up any sweep work stranded on earlier branches. A remote branch counts
as an **orphaned sweep branch** only if *every* commit it carries that is not already in `main`:

1. has a message beginning `sweep:`, **and**
2. touches nothing outside `docs/beta-feedback-tracker.md`, `docs/beta-feedback-dashboard.html` and `docs/beta-feedback-items.json`.

That test deliberately excludes release and feature branches — never merge one of those on the
sweep's initiative. Merge qualifying branches **oldest first**, before merging the current run,
resolving conflicts by the rules above, and list what you absorbed in the digest. If nothing
qualifies, say so and move on.

**Passing the two-part test is necessary, not sufficient — audit the branch's content before
merging it.** A branch can qualify and still be *superseded*, in which case merging it drags
`main` backwards. Check whether its changes are already present in `main` (or in the current
run's branch) by some other route — a reconciliation commit, a cherry-pick, a hand-fold — and if
they are, **skip it and say so**, rather than merging it for the sake of a tidy graph.

**Delete absorbed branches from the remote as part of absorbing them** (`git push origin
--delete <branch>`). A deleted branch cannot be resurrected by a later sweep, which retires
the risk the old "do NOT re-merge" table existed to guard. That table (six branches absorbed
between 08-22 and 08-28, four of them via hand-fold or supersession rather than a plain merge)
was retired on 2026-08-28 when Christian had all fourteen accumulated `claude/*` sweep branches
deleted from the remote — every one verified either fully merged (0 unmerged commits) or
documented-absorbed first. A sweep's own designated branch is the one exception: leave it —
the platform owns its lifecycle.

### Report it

The digest and the commit message both state the merge outcome — `merged to main (<sha>)`, or
`merge blocked: <reason>` when it could not complete. A sweep that could not merge is a finding
worth a notification, not a silent skip: a frozen `main` is invisible until someone goes looking,
which is how it went unnoticed for two days.
