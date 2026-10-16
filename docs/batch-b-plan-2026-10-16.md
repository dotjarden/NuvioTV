# Batch B: the mechanical half (B1–B10), 2026-10-16

**Status: IN PROGRESS.** Master plan `docs/master-plan-2026-10-14.md` §4.4 (re-sequenced 2026-10-16 from
Steven's rc4 verdict, `docs/steven-beta19-rc4-verdict-2026-10-16.md`), decisions D11–D15 accepted as written.
Clone `~/Claude/Projects/NuvioMobile-batch-b`, branch `claude/batch-b` off `tvos-shared-extraction`
`8e8090806` (Batch D + P4 merged, uncut). Not merged, not cut: rc5 (build 137) is cut on Christian's go
after the merge; its notes must say the heading details are OFF by default and that rc4's hero-ON folder
line is the toggle's ON state.

## Scope (his order)

| # | Item | Tracker | Agent |
|---|---|---|---|
| B1 | "Show Catalog Details in Headings" toggle, default OFF: Stage/Discover heading add-on suffix + the folder line on both Homes | BUG-145, BUG-159 revert, FEAT-67 | α |
| B2 | Exit from the mpv player suspends the app (repro on the device first, then fix) | BUG-165 P1 | main |
| B3 | Far-left card clipped with No Zoom on Focus ON | BUG-164 P2 | β |
| B4 | Per-row landscape cards: size from Poster Size, row height, trailer reveal | BUG-162, BUG-163 P2 | γ |
| B5 | Folder ← Detail restore on the Stage; Home ← folder re-grab regardless of age | BUG-156 P2 | δ |
| B6 | Stage heading→shelf second trim | BUG-146 P3 | β |
| B7 | Layout picker out of the folder page's band into Settings › Home Screen › Collections Layout | FEAT-71 | β |
| B8 | Best Result card: title, year, type only | FEAT-72 | α |
| B9 | Stage folder page seeds from the first item once row 0 lands, folder logo docked | FEAT-70 | β |
| B10 | DV profile 5 on mpv forces gpu-next + the routing note | BUG-166 quick half | α |

## Method

Wave 1: α (B1, B8, B10) ∥ β (B3, B6, B7, B9), main session on B2's probes, shield and simulator leg →
build + commit → Wave 2: γ (B4) ∥ δ (B5), B2 device repro + fix → gates (NuvioTVTests, Debug + Release
simulator, the relevant UI legs with `-collect-test-diagnostics never`) → two Opus read-only review
rounds (Codex on its limit until 10-29) → device pass in the Test 2 profile with the rig
(`docs/device-rig-2026-10-15.md`, `scripts/device/`, `preflight.sh` before every walk, rig lock
`~/.config/nuviotv-device/rig.lock`) → OUTCOME.

## OUTCOME

### B2 · BUG-165 exit eject (device repro 2026-10-16 18:00–18:45 ET, Test 2, Living Room ATV, rig)

**What reproduces and what does not.** Baseline build `8e809080` and the Wave 1 build `029c6f847` (with
the hardening below) were walked from the Continue Watching hold menu → Play Manually → a source, with
Home underneath and native forced off through `-player.nativeDolbyVision NO` so the route is mpv:

| Exit press | Baseline | Fixed build |
|---|---|---|
| 100 ms Menu (1080p MKV) | clean, picker in ~1 s | clean (`menu began action=exit` → `shield armed` → `menu cancelled sinceExit=23ms` → `viewWillDisappear sinceExit=25ms` → `shield disarmed held=557ms swallowed=0` → `terminate_destroy took=76ms`) |
| 0 ms Menu (the 10-15 rig eject) | clean | clean (`took=111ms`) |
| Menu, then Menu 0.25 s later | — | clean, picker still up; the second press reached neither the controller nor the shield |
| 100 ms Menu from a 4K DV · HDR10+ MKV on gpu-next, second Menu 2.5 s later | — | clean; the second Menu dismissed the picker to Home, as it should |
| **Menu held 0.8 s** | **tvOS home screen, app suspended** | **tvOS home screen, app suspended, with NO `menu began` line**: mpv kept decoding in the background. The baseline run shows no third Vulkan teardown either. |

So the only eject either build produced is tvOS's own press-and-hold-Back-to-Home gesture, which the
system handles before the app sees the press. The native engine exited cleanly on the same walk. The
teardown that the 10-16 triage suspected (`mpv_terminate_destroy` on the main thread) takes 76–132 ms
once moved off it; the "6 s of black" in Steven's video is not the player's teardown on this box. In
Test 2 no display-mode re-sync happened (screenshots worked during the 4K play), so the TV-side
re-sync his Match Content setting adds could not be timed here.

**Working theory for his box.** His TV goes black for seconds after the exit (the HDMI re-sync back from
the title's mode: his Chihiro exit was black for ~4–6 s too, and that one landed on the picker), he
presses Back again and holds it, tvOS goes Home with the picker still up: exactly the "source list on
reopen" his video shows. His answer on the exact press (asked in the 21:06Z DM) decides. The app cannot
intercept the system hold.

**What was built anyway (hardening, all verified harmless on hardware):** `MenuExitShield` (a window
recogniser enabled only between the exit decision and the cover's end; it never claimed a press in
seven exits); `MenuPrecedence.swallowsRelease(.exit)` is now true (the exit press's release no longer
runs up the responder chain; tvOS cancels it anyway ~20 ms after the dismissal starts); the cover's
Menu recogniser is not re-enabled on the way out; `mpv_terminate_destroy` runs on `eventQueue` (the
Metal layer kept alive by the block) with `[MPV] terminate_destroy took=`; `[MenuProbe]` phase lines on
every Menu press; `-debug.menuExitShieldOff YES` A/B knob. Simulator legs
`testMenuExitOverRootKeepsTheAppForeground` (passes) and the opt-in control
`testMenuExitOverRootControlWithShieldOff` (`PLAYER_EXIT_CONTROL=1`): the control passes too, so the
simulator cannot show what the shield changes; the leg guards the exit-then-double-Menu path, not the
shield. Evidence: `docs/research/batch-b-device-2026-10-16/` (r3–r10, console-repro-b/c.log,
console-fix-a/b.log; redact `/stremio/<token>/` before committing logs).

**For the DM / release notes:** ask Steven whether he held Back; tell him a held Back is tvOS's Home
gesture and that the picker stays where it was on reopen; the mpv exit itself is now instant on the app
side. If his answer is a single short press, the next lever is his `[MenuProbe]` lines (every Menu press
now logs its phase), which need his console or a Developer pane readout (not built).
