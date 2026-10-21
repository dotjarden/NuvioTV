# GitHub issue #5 reply (refreshed 2026-10-21) — FEAT-56, SenPlayer built — NOT POSTED

Supersedes `docs/comms-github-issue5-reply-2026-10-15.md` (drafted 10-16, never posted). Second reply on youngchris29-art/NuvioTV [#5](https://github.com/youngchris29-art/NuvioTV/issues/5) (`4rtz1z`), after our 2026-10-06 comment that promised SenPlayer "in a coming build" and asked for his SenPlayer version (no answer since). 

What changed since the 10-16 draft: SenPlayer rode the rc track from rc5 (Batch D, merged 10-16) and is in rc11 (build 143), but no public build has carried it; the next public build is beta.19 (plan in memory: rc12 + soak + walkthrough → Wave 4 → public IPA, no date). Steven's rc5 verdict (10-17): he has Infuse Pro only, no SenPlayer, and the Living Room box has none either, so the hand-off is still untested on hardware. The draft now names beta.19 as the carrier and says there is no date.

Optional: Christian may prefer to hold this until beta.19 ships and post a "it's in" note instead. Post only on his go: `gh issue comment 5 --repo youngchris29-art/NuvioTV --body-file <file>`, verify through `gh issue view`.

Lint: body 5/5 (`python3 scripts/deslop/deslop.py`); cleanse skipped (Codex quota out until 10-29).

```
SenPlayer is built and will be in beta.19, the next public build. No date on it yet, I'm working through a round of tester fixes first. Once SenPlayer is installed on the Apple TV it shows up under Settings → Player as a default player, and in the hold menu on any source row, the same as Infuse and VidHub. The handoff sends the link, the title, the resume position and the add-on subtitle, and NuvioTV listens for the position SenPlayer reports when you come back.

I built it against the parameter names Outplayer and VidHub use, since SenPlayer doesn't publish its scheme, and I don't have SenPlayer on my own Apple TV to check it end to end. When the build lands, tell me three things: did it start at your resume point, did the subtitle show, and did your position carry back to NuvioTV when you exited. If any of those misses I'll adjust the handoff.
```
