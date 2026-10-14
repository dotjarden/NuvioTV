# BUG-128 glitch video (u/an_angry_Moose, comment `pdgfqap`, 2026-10-02)

Source: `https://reddit.com/link/pdgfqap/video/ptm5pgnhe3th1/player` → `https://v.redd.it/ptm5pgnhe3th1/HLSPlaylist.m3u8`
(downloaded 2026-10-14 with ffmpeg; the DASH mp4 renditions answer 403 unauthenticated). File kept out of the repo:
`~/Downloads/bug128-moose-glitch-pdgfqap.mp4` (1280×720, 30 fps, 24.8 s, phone recording of the TV).

Surface: the default Detail full-screen trailer on beta.18 (build 132), *Pinocchio* (2022 live action) trailer, Apple TV 4K on Wi-Fi.

## What the frames show (contact-sheet-1fps.jpg, one frame per second)

| Seconds | Content |
|---|---|
| 0 | Pinocchio walking on cobbles |
| 1–2 | Pinocchio with Geppetto (A) |
| 3 | running across the square (B) |
| 4–5 | courtyard (C) |
| 6 | legs / cane (D) |
| 7–8 | **Geppetto (A) again** → the player jumped back ~6 s |
| 9 | square (B) again |
| 10–11 | courtyard (C) again |
| 12 | legs (D) again |
| 13 | Jiminy Cricket (new content) |
| 14–15 | seagull |
| 16 | Pinocchio face |
| 17–24 | **the same puppet-theatre frame for 8 s** → the hang he describes |

Read: ~6 s of playback, a seek back to ~1 s and an exact replay of the same six seconds, ~4 s of new content, then a freeze.
That is one replay cycle plus the hang ("jumps back a few seconds and replays, sometimes multiple times, finally hangs").
The replay is frame-accurate to the earlier pass, so it is a player seek within the same media, not a reload of the trailer.
