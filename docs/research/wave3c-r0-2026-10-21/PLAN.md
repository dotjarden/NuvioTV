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

## Findings (session 2026-10-21 23:05Z–)

- **Rig:** the day's "drops" are the box losing its **IPv4** path while IPv6 stays up (no A record from Bonjour, `ping` dead, `ping6` 10 ms; devicectl rides IPv6). `atvctl.py` now accepts an IPv6 address; the session ran the Companion over `fe80::…%en0` via `NUVIOTV_DEVICE_CONF=/tmp/nuviotv-device-v6` (a copy of `atv.env` with the link-local address). To fold into `atv.sh`: resolve the v6 from `dns-sd -G v4v6 Living-Room.local` when v4 is unreachable.
- **Profile:** under the Christian tvOS user the app's remembered profile is **Chris (profile 2)**; every launch now carries `-debug.rememberLastProfile NO` and the picker is walked by screenshot (Right → Test 2, `selecting profile 3`).
- **Steven's config installed in Test 2** (shots `04-*`, `07`, `09`, `12`): device-local keys by launch argument (`-sidebar_style rail -rail_visibility hidden -rail_position corner -rail_labels shown -home_layout classic -ui_font system -accent_focus_ring YES -focus_ring_poster_color YES -depth_rail_poster_color YES -no_zoom_on_focus NO -row_edge_fade off -show_catalog_details_in_headings YES -settings_style default -detail_action_icons_only NO -detail_trailer_autoplay NO -detail_trailer_background NO`), synced ones in the pane: accent **White** (was Ocean), Card Depth on Subtle / Soft / **Full** (was Top), Medium+, Rounded, Hide Titles on, Landscape off, OLED on. Discover left at Own Tab.
- **FEAT-82 (icon sizes) REPRODUCED in his config** (`21-detail-rest`, `22-detail-btn1..3`, `crops/`): the three round buttons are the same size (platter 300 px focused), the **glyphs are not**: trailer 28 × 22 pt, watched (`checkmark.circle`) 25 × 25 pt, add (`plus`) 20 × 20 pt. His "icons are still not all the same size" is the optical glyph size; the rig's earlier pass measured button frames only. Fix = equalise the glyph boxes (a fixed symbol frame + per-symbol scale), not the frames.
- **BUG-194 (two moves back from an actor) REPRODUCED in his config:** cast → biography → Back ×5 → `[DetailPop] end row=cast key=1 moves=3 held=0 landed≈560–620 focused=cast idx=1` every time (rungs at t=17 forced, 368 forced, 835 free). **Same with Accent Focus Ring OFF** (`console-r0-ringoff.log`, moves=3, landed≈600): the ring is not the difference. Still to A/B: Card Depth (on the cast circles), Medium+, Classic Home, White accent. The Wave 1 pass that saw one move ran Stage + system font + Labels Shown + Square.
- **Search (BUG-208 fix, build `823450355`):** three uncached queries, 27 catalog calls, `retry=none` on all (no 504 tonight); the `[SearchPerf] catalog … retry=` line is in place (`console-search.log` in `../wave3-device-pass-2026-10-21/`).
- **BUG-210 (old text under a collection logo) NOT REPRODUCED:** focusing the Test Folder tile ×5 on Classic (`console-r0-home.log`) logs `[HomeHero] present item=nuvio.folder:… backdrop=cached logo=text waited=0` every time; the only `waited>0` presents are first-seen titles (4–16 ms). With cached art there is no wait and no mixed frame. The remaining path is a cold folder backdrop (`folderDeadline` ≤ 1.5 s), during which the previous hero stays whole (one identity for logo and text), so his frame reads as the phone blending two TV frames. Close as not reproduced; re-open only if he sees it on rc12 with a cold folder.
- **BUG-209 (heading lands high, drops a notch) before-state** on the rc11-class build: eight Downs at 0.6 s on Classic with Hide Titles logged one `slide apply … via=quiet` (the quiet-settle release) and no `via=immediate`; the after-check on the wave3c build looks for `via=immediate anim=track exempt=1` per Down.
- **Not run this session:** W3-17's A/B burst (the rig's screenshot burst is ~1.3 s per frame, too coarse for a sub-second colour lag); W3-18's cold-start recording (same); the picker stub add-on (the box cannot reach the Mac's IPv4 while its own IPv4 is down; retry when `ping 192.168.1.86` answers).
- **Picker stub add-on installed in Test 2** (`37-addon-installed`: "Installed Picker Rows fixture."; the fixture runs on the Mac at port 8769 and serves 48 rows for every title). Test 2 also has Comet (debrid) and Torrentio installed, so the picker has real rows too. Remove the fixture at tear-down.

## Release walks (build `823450355` Release, Steven's settings, Test 2) — partial, 2026-10-22 00:00Z–01:33Z

| Run | Hitches | App ms | Max ms | Note |
|---|---|---|---|---|
| detail-cinematic (Severance, 10 down / 10 up) | 65 | 1552 | 166.8 | two 167 ms stalls at 7.9 s and 8.6 s (GPU work), one 100 ms at 5.3 s |
| home-classic-depth (run 2) | 96 | 1818 | 66.7 | Classic, Card Depth on |
| home-classic-nodepth (run 1) | 72 | 1318 | 50.0 | Classic, `-debug.homeNoCardDepth YES` |

Only three of thirteen recordings held a complete walk: Instruments times out "waiting for device to boot" on roughly two runs in three right after a previous session (a 45 s gap and three attempts are now the runner's defaults), and the Companion over IPv4 failed mid-walk (`_hidC failed`) on the Stage runs while the box's IPv4 flapped. The other nine (Classic Detail, rc7 Cinematic Detail, the second Classic pair, the four Stage runs, the picker) are rerunning over IPv6 (`NUVIOTV_DEVICE_CONF=/tmp/nuviotv-device-v6`). `summary-attempt1.txt`, `summary-attempt2.txt` hold the first two passes.
