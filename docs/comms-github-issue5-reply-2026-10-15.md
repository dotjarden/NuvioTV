# GitHub issue #5 reply (drafted 2026-10-16) — FEAT-56, SenPlayer built — NOT POSTED

Second reply on youngchris29-art/NuvioTV #5 (`4rtz1z`). Follows the 2026-10-06 comment that promised SenPlayer "in a coming build" and asked for his SenPlayer version (no answer yet). Batch D built it (`docs/batch-d-plan-2026-10-15.md`): a SenPlayer entry on the Infuse/Outplayer x-callback shape (`url`, `position` in seconds, `filename` + `name`, `sub`, `x-success`/`x-error`), the `senplayer` query scheme, and a return session so a position SenPlayer sends back is recorded. On the Living Room Apple TV the scheme probe answers (declared, not installed); SenPlayer itself is not installed there, so the hand-off, start position, subtitle and return position are untested on hardware. The parameter names come from the Outplayer/VidHub shape and SenPlayer's changelog, not from documentation.

Post only after Christian's go, and after his SenPlayer device test if he does it first (then replace paragraph 2 with the result). The build it ships in is the next rc (rc5), not rc4.

Lint: body 5/5 (scripts/deslop/deslop.py); cleanse skipped (Codex quota out until 10-29).

```
SenPlayer is in for the next build. Once it's installed on the Apple TV it shows up under Settings → Player as a default player, and in the hold menu on any source row, the same as Infuse and VidHub. The handoff sends the link, the title, the resume position and the add-on subtitle, and NuvioTV listens for the position SenPlayer reports when you come back.

I built it against the parameter names Outplayer and VidHub use, since SenPlayer doesn't publish its scheme, and I haven't had SenPlayer on my own Apple TV to check it end to end yet. If you try it when the build lands, tell me three things: did it start at your resume point, did the subtitle show, and did your position carry back to NuvioTV when you exited. If any of those misses I'll adjust the handoff; the fix is small once I know what SenPlayer expects.
```
