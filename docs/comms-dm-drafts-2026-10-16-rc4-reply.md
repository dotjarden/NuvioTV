# DM draft — reply to Steven's beta.19-rc4 verdict (2026-10-16)

Status: DRAFT, NOT SENT. Lint: see the bottom. Send only on Christian's go, through the chat recipe in memory
`reddit-chat-smash-fetch` (one process, CSS locators, log to `~/Library/Logs/`). One bubble.

Context: his DM 2026-10-16 20:09Z + two videos (`docs/steven-beta19-rc4-verdict-2026-10-16.md`). What this
says: thanks; owns the BUG-159 misread; the player answer with settings for his setup (native player ON,
tvOS Match Content Dynamic Range ON, Enhanced Video Renderer OFF, Seek Preview Frames default); what is in
the next build and what comes later; asks for the engine + press on the eject, his rail mode's name, and a
photo of the landscape row once the size changes.

---

Hi Steven,

Thanks for the walk and the two videos, they settled most of this in one pass.

First, the "Genre · 8 sources" line on the old Home: my mistake. Your photos showed it on one hero mode and not the other, and I read that as a missing line instead of a line you wanted gone. Next build: one switch in Appearance, off by default, that hides the add-on name and the source count on both Homes. The old Home goes back to how it was.

The return position: both cases are real. Coming back from a film inside a collection was never wired on the new Home, so that one is a plain fix. Coming back to Home from a collection has a fix in rc4 that misses on your box, so I will widen it. If it still jumps after the next build I will ask for a screenshot of the Row Settle pane.

Wide posters from your add-on: the cards use a fixed size that ignores your poster size, and the row keeps the height of a portrait row, which is why the heading floats. Next build sizes the card from your poster setting and the row from the card. The trailer playing with sound and no picture sits in the same code path, so I expect it to go with those two, but I want to see it on a test row first before I call it fixed.

The far-left poster being cut: thanks for the edit, that was the key. With "No Zoom on Focus" on, the row leaves less room at its left edge than the playing trailer card needs, so the card and its outline get clipped. Fix in the next build.

Headings on the new Home: I will bring them down one more step. Tell me if the next build still reads high.

Collections: the layout switch leaves the page and goes into Settings. Opening a collection on the first film instead of the collection card is a change I want to make too.

Best Result: the card keeps the title and the year plus film or series. The "found in" line and the rating move to the row below.

Discover: agreed on the direction. A grid with a type and genre picker over one general catalog is where I want to take it; you will see a first version once the Home work above is in, and the per-genre rows would become a secondary view.

The player, with your setup:

- Keep "Native player (Dolby Vision & HDR)" on. Files that say "DV · HDR10" in the source list are Dolby Vision profile 8 and play through the native path with real DV output.
- A source that says only "DV" (your Animals file) is profile 5. Those go to the mpv player today, and mpv needs "Enhanced Video Renderer" (Player › Video) to colour them right. Yours is off, so turn it on; it applies to the next video. The green and magenta picture in your video is exactly that case. I will make the app pick the renderer by itself for those files.
- Keep "Match Content Frame Rate" on in the app and in tvOS Settings, as you have it.
- Thumbnails while scrubbing follow the picture, so on that file they were green too. If you see any stutter, Settings › Developer › Seek Preview Frames › Off.
- The start time is slow because the app probes the file for the native path first and then starts mpv from cold. That is a known gap and on the list.

The exit that leaves the app: I saw it in your video at 6:20, the app went to the Apple TV home screen and came back on the source list. Two questions so I can reproduce it: was that the mpv player (the one with the round buttons at the bottom right) or the native one, and what did you press to leave, a single Menu tap, a hold, or something after the pause card? Both of your plays started from the Continue Watching hold menu, which is one difference I am looking at.

Two small asks: which sidebar mode are you on now (Hidden, from your message), and once the wide row changes size, a photo of that row at rest.

Next build: the heading switch, the return from a film inside a collection, the wide row size, the left-edge clip, the heading step, the layout switch move, Best Result, and the renderer pick for profile 5 files. Being worked on with no date yet: the return to Home from a collection on your box, the wide-row trailer, the exit that leaves the app, the Discover grid, the collection opening on its first film, the start time, and the thumbnail cadence.

Chris

---

## Lint

`python3 scripts/deslop/deslop.py <body>` → **5/5 CLEAN** (re-linted after the 10-16 softening pass: Discover, the wide-row trailer and the closing list downgraded from promises to intent; was 744 words; a first pass scored 3/5 on "landscape" ×3 and one rule-of-three list, both rewritten). **Codex cleanse SKIPPED:** `codex exec` fails with "refresh token has expired, log out and sign in again" (`codex login` needed; the review quota reset is 10-29 anyway). Re-lint after any edit.
