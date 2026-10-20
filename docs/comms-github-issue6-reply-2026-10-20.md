# GitHub issue #6 reply (drafted 2026-10-20): BUG-172, native-player micro-stutter. NOT POSTED

First reply on youngchris29-art/NuvioTV #6 "Streaming jittering-stuttering" (megustalamangusta666-pixel, 2026-10-16: "Every 5-10 second there's a micro stutter with a freeze frame when using native player"; no build, device, title or stream type given). Unreproduced here. The ask is the five facts the tracker row lists, plus one lead worth checking: the Apple TV player is fed by the on-device remux in 6–16 s segments, so a hitch on that cadence could be a segment-boundary stall. Post only after Christian's go.

Lint: body 5/5 (`python3 scripts/deslop/deslop.py`); cleanse skipped (Codex quota out until 10-29).

```
Thanks for the report. I have not been able to make this happen on my Apple TV, so I need a few details to find it:

1. Which build? Settings → About shows it. The current beta is 0.3.0-beta.19-rc10.
2. Which Apple TV (4K 2nd or 3rd gen, or HD) and which tvOS version?
3. What were you playing: a 4K HDR or Dolby Vision file, or 1080p? From a debrid service (Real-Debrid, TorBox) or a direct link from an add-on?
4. Does the same file stutter in the mpv player? Settings → Player → Default Player switches it.
5. Are Match Content → Match Frame Rate and Match Dynamic Range on in the tvOS Settings?

One thing to try: when the picture freezes, note roughly how many seconds apart the freezes are. The Apple TV player receives the film in pieces of 6 to 16 seconds. If the freezes land on that rhythm I know where to look.
```
