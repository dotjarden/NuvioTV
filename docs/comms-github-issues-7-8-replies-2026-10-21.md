# GitHub #7 (BUG-197) and #8 (BUG-198) replies — drafted 2026-10-21 — POSTED

**Status: POSTED 2026-10-21 04:20:52Z / 04:20:53Z** on Christian's go: #7 https://github.com/youngchris29-art/NuvioTV/issues/7#issuecomment-6307958234, #8 https://github.com/youngchris29-art/NuvioTV/issues/8#issuecomment-6307958484 (`gh issue comment --body-file`), both verified byte-identical through `gh issue view`. Was: NOT POSTED.

Both issues are erdist's, filed 2026-10-20 on youngchris29-art/NuvioTV. Triage is in `docs/beta-feedback-tracker.md` (BUG-197, BUG-198). Post only on Christian's go, with `gh issue comment <n> --repo youngchris29-art/NuvioTV --body-file <file>`, then verify through `gh issue view`.

What the drafts promise: both fixes "in the next build" (Batch P Wave 2 → rc11). Soften before posting if rc11 is cut before Wave 2 lands.

Lint: both bodies 5/5 (`python3 scripts/deslop/deslop.py`); cleanse skipped (Codex quota out until 10-29).

## #7 — Plugins settings, one row per provider (patch attached)

Facts in the draft: the diagnosis is right (the pane is a native tvOS List and the whole repository block is one List row); the patch applies cleanly to the current tip; it lands in the next build with credit; two small changes on our side (a lone repository starts expanded; the header row feeds the description pane); the collapse and A–Z order come with it.

```
Thanks, this is a good one, and the diagnosis is right. On tvOS the Sources pane is a native List, and the whole repository block (name, count, trash button, every provider switch) was one List row, so one row got the focus and Select flipped all of it.

Your patch applies cleanly to the current tip and I'm taking it as is, with credit, for the next build. Two small changes on my side:

- A repository starts expanded when it's the only one installed, so the common case stays one press away.
- The header row feeds the description pane on the right, like the other rows do.

The collapse and the A to Z order come with it. Thanks for doing the work.
```

## #8 — Background trailer keeps playing after Play

Facts in the draft: confirmed in code; it is the series path (a film's Play stops the trailer, a series' Play does not, because the series Play cover was never on the list of covers that stop it); the fix is one line and goes in the next build; with Trailer Sound on, that is the audio the reporter heard under the player.

```
Confirmed, and it's a series-only bug. Pressing Play on a film stops the background trailer, but a series goes through a different cover (the one that holds its source picker and the player), and that cover was never on the list of things that stop the trailer. So the trailer kept running underneath, and with Trailer Sound on you heard it under the episode.

The fix is one line and goes in the next build. Thanks for the clear steps.
```
