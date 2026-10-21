# R0: the Wave 3c rig session (no code) — checklist, 2026-10-21

Runs once `scripts/device/ready.sh` passes (one attempt per session; REFUSED = stop). Test 2 only. Nothing 4K until the last item. Every log under this folder is rig output: redact add-on hosts before any commit (`rig-log-staging-rule`), stage files by name.

## 0. Leftovers from Phase 1a (Wave 3 device pass, session 3)

| # | Build on the box | Check | Record |
|---|---|---|---|
| 0.1 | `claude/up-skip-rebased` `0c05b6ab2` Debug is installed (session 2) | `console.sh start console-upskip.log -- -debug.homeScrollProbe YES`; Home row 3 "Test Collection" → Select on "Test Folder" → Menu (pop) → Up, ×5 on Stage; Appearance → Home look Classic → same ×5. Expect focus on row 2 (Trending Movies), never the hero or row 1; `[HomeReturn]` lines. | `../wave3-device-pass-2026-10-21/README.md` session 3 |
| 0.2 | install `claude/wave3` `823450355` Debug (`~/Claude/Projects/NuvioMobile-wave3/iosApp/build/DerivedDataDevice/Build/Products/Debug-appletvos/NuvioTV.app`) | Search: type an uncached query (e.g. `zygmunt`), `[SearchPerf] catalog … retry=` lines; if Cinemeta 504s, the failure + Retry row shows above People. | same |
| 0.3 | same | BUG-199b live seek, Animals Comet NF DV MP4 (`-player.nativeDolbyVision YES`): resume at the saved position, two transport seeks; expect `seeking to segment N (dts …)` and no `landed … aborting`. **Last item of the session** (4K debrid). | same |

## 1. W3-12: install Steven's config in Test 2 (from his rc11 video + rc10 table)

Appearance: accent White; Accent Focus Ring ON; ring takes poster colour ON; depth takes poster colour ON; No Zoom OFF; row edge fade OFF; catalog details in headings ON; OLED deep black ON; Settings style Default; Navigation Rail, Hidden at rest, Position Corner, Labels Shown; Discover off; Font **System**; Size Medium+; Corners **Rounded**; Hide Titles ON; landscape rows OFF; Card Depth ON (Subtle, Soft, Full); Home look **Classic**; Detail look **Cinematic**. Screenshot the Appearance pane top to bottom (`01-config-*.png`). Then every Detail item twice: Rounded and Square.

## 2. W3-12 captures (Debug for probes, Release for walks)

| # | Item | Steps | Expect / record |
|---|---|---|---|
| 2.1 | FEAT-82 icon sizes | Detail of a film and a series (Animals; a series with Shuffle): screenshot the action row at rest and with each button focused; Rounded then Square. Measure **glyph** boxes and button frames in the full-size PNGs. | glyph vs frame table; `checkmark.circle` ring vs `plus` |
| 2.2 | BUG-194 two moves | `-debug.detailFocusProbe YES`: cast card → biography → Back, ×5; `[DetailPop]` + `moves=`; `rec.sh for 20` on one run. | lands on the card in one move or not, with the lines |
| 2.3 | BUG-206 Cinematic choppier | Release build; `walk-detail.sh` with xctrace Animation Hitches: Cinematic Detail then Classic Detail (Appearance → Detail look); `compare.py`. Then the same walk on a build of tag `tvos-v0.3.0-beta.19-rc7` (build it once in the wave3 clone: `git checkout tvos-v0.3.0-beta.19-rc7`, device Release build, re-checkout). `-debug.detailScrollProbe YES` on one Debug run for W3-15's press-1 window. | hitch counts: rc12-candidate Cinematic vs Classic vs rc7 Cinematic |

## 3. Baselines and repros for Phase 1c

| # | Item | Steps | Expect / record |
|---|---|---|---|
| 3.1 | W3-13 Card Depth baselines | Release, his config: `walk-home.sh` on Classic ×2 with depth ON, ×2 OFF; switch Home look to Stage: ×2 ON, ×2 OFF. `compare.py 14 50`. | the four baselines (Classic has none yet) |
| 3.2 | BUG-209 held slide | Debug, Classic, Hide Titles, `-debug.homeScrollProbe YES`: 8 Downs at 0.6 s; `rec.sh for 10` at 30 fps on three presses. | `slide apply … via=settle` lines today; single vs double landing on the frames |
| 3.3 | BUG-210 repro | Classic: focus the Prime Video / Netflix tile in Streaming Services ×5 with `rec.sh` at the highest fps; grep `[HomeHero] present item=nuvio.folder … waited=` and `debug_heroText … maxLive=`. | `waited` ≤ 0.3 s and `maxLive=1` → camera artefact (close); else owner fix |
| 3.4 | W3-15 Home press 1 | Release, `-debug.homeScrollProbe YES`, Animation Hitches: Classic 3 presses from the top ×3 (Menu to top between); Stage the same. Time Profiler once per look (`timeprofile.py`): `HomeView.body` / `StripPager.body` in the press-1 window. | press-1 vs 2–3 hitch window |
| 3.5 | W3-16 picker baseline | `python3 scripts/device/fixtures/picker-rows-addon.py 8769` on the Mac; install `http://192.168.1.127:8769/manifest.json` in Test 2 (Add-ons › Install from manifest URL); open any film's Sources; Animation Hitches over 30 Down + 30 Up at 0.35 s. Remove the add-on at the end of the session. | baseline hitches; `HomeBodyCounter.tick("StreamRow")` |
| 3.6 | W3-17 A/B | Debug, accent White: a watched film's Detail, Right from Watched ×3 with `rec.sh` burst; the same with `-debug.detailScrollAB 4`; the same on an unwatched film and on Library saved vs not. | which buttons lag; whether leg 4 lags |
| 3.7 | W3-18 cold start | Release: kill the app, cold launch, rail → Search with `rec.sh`; today's placeholder for the before. | the +1.1 s frame |

## 4. Tear-down

Remove the picker-rows add-on and any dummy key; leave Test 2 in Steven's config (the device pass in §5 of the plan uses it); `console.sh stop`; redact and copy the logs here by name.
