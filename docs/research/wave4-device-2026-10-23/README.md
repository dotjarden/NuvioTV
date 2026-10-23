# Wave 4 device check — 2026-10-23, Debug build `e3867a35` on the Living Room box, Test 2

Launch args per leg (numeric Bools), the Test 2 profile every time, the app killed at the end; nothing in the profile changed (one Sources picker opened and closed, no library add).

| Item | Check | Result | Shot |
|---|---|---|---|
| BUG-223 | Classic, `-debug.homeHeroOff YES -debug.homeHeroProbe YES`: launch, read the probe | **PASS**: `rows … n=1` (the collection) at +1.0 s, `seedSettle reason=backstop` at +4.0 s (both catalog sources still loading), ONE `present` (the Continue Watching title) and ONE `paint`; no second present within 12 s. The pre-fix shape was CW at once, then the first catalog title ~650 ms later. | `bug223-classic-hero-off-12s` |
| D-7 | Classic, Show Catalog Details on, Test Collection › Test Folder focused | **PASS**: title "Test Folder", line "2 sources" (was "Test Folder · 2 sources") | `d7-folder-line` |
| D-8 | Settings › Appearance, White selected, focus on White | **PASS**: the focused swatch is lifted and ringed; distinct from the rest even when it is the selected one | `d8-white-focused-selected` |
| D-5 | `-detail_layout classic`, Sheriff Country Detail, Details block | **PASS**: "Ratings  IMDb 6.9 · Rotten Tomatoes 75% · Metacritic 67 · Trakt 80% · TMDB 74%" (brand labels, Cinematic order) | `d5-classic-details-ratings` |
| BUG-215 | hardware root list, Default style | the lift was never clipped on hardware (the report is simulator-only); the side-open clip is checked by eye on the simulator in the next legs run | — |
| BUG-222 | Debug `78b83c26`, `-debug.trailerProbe 1`: Animals by deep link (1 visit), Sheriff Country via Upcoming (2 visits with the trailer settings on, 3 with both off) | **NOT REPRODUCED**: every visit logged `hero resolve candidate=` → `[TrailerExtract] selection` → `[TrailerRepack] serving` and showed the Watch Trailer button. The resolver has no cache, so the D9 sighting (probe off, no lines) is most likely YouTube refusing every candidate once (`LOGIN_REQUIRED` on `android_vr` was seen on the first Animals attempt before `visionos` answered). | `bug222-visit3-settings-off` |

Rig notes: the DEBUG collections seed and the deep link work on the box; Select on a Continue Watching card opens the Sources picker (Menu closes it); the hero-off launch needs `-home_layout classic` or the Stage's own seed rules apply.

## Later the same day (Debug `28806f7d`, Test 2)

| Item | Check | Result | Shot |
|---|---|---|---|
| FEAT-85 | Home after Test 2 enters: Up Next cards; hold menu on one; Go to Details; Remove | **PASS** (first build `096a000a` and the round-2 build): three cards ("Up Next · S04E20" …), the stage shows the episode's title and synopsis; hold menu = Play Manually / Go to Details / Mark Episode Watched / Remove (no Start Over); Go to Details opens the series with Play reading "Next Up · S4E20"; Remove clears the card at once and the dismissal held across a relaunch; the cards are on screen within 3 s of entering the profile, one present / one paint | `feat85-upnext-focused`, `feat85-hold-menu`, `feat85-round2-home-3s` |
| D-4 | Sheriff Country Detail with both trailer settings on: let the cover auto-play, Menu, shots at +2.3 s and +7.6 s | **NOT REPRODUCED**: the still is up at both marks, no black; the background trailer did not resume after the cover (`bridge phase=idle` at 06.06, no hero `attach` after it), so there was no resume gap to see. The D9 sighting (look B, 2–6 s black) stays the only evidence; D-4 stays open at P3 with its diagnosis in the plan | `d4-after-cover-2s` |

The `atv.sh press menu` single press did not register during a full-screen trailer; `atv.sh seq menu` did.
