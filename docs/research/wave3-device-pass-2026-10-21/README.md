# Wave 3 device pass, 2026-10-21 (Test 2, Living Room, tvOS 27.2)

Build: `claude/wave3` `b79ea5606` Debug (`-player.nativeDolbyVision YES`, Rail Corner, Labels Shown, trailers off). Logs `console-199.log`; shots 960 px.

| Item | Result | Evidence |
|---|---|---|
| **BUG-199, run 1** | **Probe timed out** (`probe took 4036ms cap=4000ms result=nil` → `mpv — probe unavailable`): the same Comet NF DV MP4 probed in 2.0–2.2 s yesterday. On a debrid link the 4 s cap is a coin flip, and a timeout sends the film to mpv silently. **This is Steven's "every HDR movie launches in mpv with HDR10"** (BUG-166 on rc11): not a routing bug, a probe timeout on his network. Filed as a finding on BUG-166. | `console-199.log` :89-90 |
| BUG-199, run 2 (wrong row: the XEBEC NF WEB-DL DV MKV, `DV P8.1`, tb 1/1000) | **PASS as an MKV regression check:** native, 195 segments in 80 s, `grid probe … {656:1000} unit=656 clamps=0 nets=0`, every `seg N done ptsNets=0`, no write error, no handover. The picker's remembered expansion moved the row count. | `console-199.log` :479-569 |
| **BUG-199, run 3 (the right file: `…DV.HDR[Ben The Men].mp4`, tb 1/16000, 4330 keyframes)** | **Segment-7 failure GONE** (`seg 1 done ptsNets=0`, no `write error -22`, no `Packet duration` lines), **but a second defect behind it:** AVPlayer resumed at its saved position (segment 33), and the reposition aborted four times — `reposition landed at pts=3072000 wanted 3070672` (two frames late) — then `remux failed mid-play: reposition failed repeatedly` → mpv. The segment boundaries come from the stream's index entries, which the mov demuxer fills with DTS; the scan compares the landing keyframe's PTS, and on B-frame content a keyframe's pts is its dts plus the reorder offset. Every seek on this file class fails the same way; rc11 never got that far. **Fix dispatched (BUG-199b)**; re-check owed: resume at ~3.8 min and a forward seek on that file. Also noted: `[mov,mp4] Packet corrupt (stream 0, dts = 238672)` from the source at segment 3 (the stream itself). | `console-199.log` after :478 |
| **S6: destructive row on the platter** | PASS: Remove Repository focused = dark title, grey subtitle, red glyph on the white platter; at rest red title and glyph. (Remove API Key in Sources: same component, not re-shot.) | `21-remove-row-focused` |
| **S6: focus after Remove** | PASS: Remove → alert (Cancel focused) → Right → Remove: the repository leaves the list, **focus lands on the manifest field**, the "Installed Device-pass fixture repo." status line is gone, "No plugin repositories installed yet." shows. Fixture repository (4 providers) expanded, Remove row at the bottom of the pane: the lazy-row case passed with no delay. | `22-alert`, `23-after-remove` |
| S6: knobs deleted | Not a device item (Release walk unchanged by it). | |
| **W3-3 up-skip** | pending: Debug build of `claude/up-skip-rebased` → folder pop → Up on Stage and Classic. | |

## Rig notes
- A Companion `seq` that lands on the rail's profile row and Selects opens the profile picker with **Chris** focused: always screenshot before a Select in the rail; recovered with Right → Test 2.
- The Comet NF DV MP4 is one row ABOVE the K83 PL MKV when Comet is the expanded group; the picker remembers expansion across visits, so "5 Downs" is not stable. Screenshot, then count.
- The plugin fixture must be restarted per session (`python3 scripts/device/fixtures/plugin-repo-fixture.py 8768`).
