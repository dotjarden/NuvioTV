# P3 spec critique and reconciliation (2026-10-08)

Opus critique of `player-p3-spec-thumbnailer.md` against the plan's P3 section, the spike OUTCOME (four device runs), the P2 critique and review rounds, and the clone `~/Claude/Projects/NuvioMobile-player` at `claude/player-p3` tip `7d0f25a8f`. Read-only on code, no builds.

**Verdict: GO for Wave 1 once C1 and C2 are applied to the spec.** The spec is close to the code: the MARKs, `MediaProbe` helpers, `RemuxSession` patterns, the `subAdd` guard, the probe line, the Developer row and the description list are where it says. Spec §8 finding 1 is already DONE (`7d0f25a8f` flipped `serveIFrame` to `trim` in every build); agent B still deletes the `whole` branch (C17). The two blockers: the scheduler reads an actor's state synchronously, and the cache-health rule never passes on the high-bitrate 4K files P3 exists for.

Counts: **2 P1 / 10 P2 / 15 P3.**

## 1. Correctness against the code

**C1 (P1) The scheduler cannot read the store; the probe cannot see decoded frames.** `SeekPreviewStore` is an `actor` (`SeekPreviewStore.swift:37`); P2 inserts through `Task { await store.insert(...) }`. `ThumbScheduler.Inputs` needs `storeStamps` and `storeAcceptsDecode` synchronously in `refreshState` on main, every 0.5 s. Separately, `thumbs=` is `TransportBarModel.previewFrames`, written only by the harvest's `publish` closure, and the harvest is off on the simulator, so `testDecodePrewarmGrows` (`thumbs ≥ 10`) cannot pass as written. **Resolution:** `insert` returns `InsertResult { outcome, count, bytes, harvest, decode, stamps, acceptsDecode }` (one snapshot taken inside the actor after the insert). One main-actor `applyStoreSnapshot(_:)` on the controller handles both origins: it stores `storeMirror` (what `Inputs` reads), sets `previewFrames = count`, and rebuilds the summary (C21). The harvest path moves to the same call. `acceptsDecode` checks the entry cap before the JPEG encode, so a rejected decode never pays the encode.

**C2 (P1) The cache-health rule never passes on 4K remuxes.** With Streaming Buffer at 0 (the default) mpv keeps `demuxer-max-bytes` at 150 MiB (`MPVPlayerView.swift:834-838` sets it only when the user picks a size). A 60 Mbps remux tops out near 21 s of forward cache, 80 Mbps near 16 s, 100 Mbps near 12 s, and at steady state the cache sits at that cap. `cacheSec ≥ 15` then fails or hovers on the boundary, so the pre-warm (and the 20 s lazy open, which uses the same rule) never runs on the files where the harvest backs off to 30 s. **Resolution:** healthy = `cacheReachesEnd || cacheSec ≥ 15 || fwBytes ≥ 0.6 × maxBytes`, with `cacheTrendSec ≥ −2` kept. The 2 s read on `eventQueue` takes `demuxer-cache-state` (`fw-bytes`, `eof`) plus `demuxer-cache-duration`; `maxBytes` is the value `setupMpv` applied (150 MiB when unset). `Inputs` gains `cacheFill: Double`. Add scheduler tests: a 12 s cache at 0.9 fill is healthy; a 12 s cache at 0.3 fill is not.

**C3 (P2) Index priming uses the threshold `RemuxSession` already proved wrong.** Spec §2.2 primes the MKV index only when it has fewer than 2 entries. `RemuxSession.buildSegmentMap` (`:1118-1131`) records device truth: `find_stream_info` deposits 3 to 6 keyframe entries on high-bitrate remuxes, which defeats a `< 2` check, and tail-loaded Cues (mkvmerge default, and ffmpeg's muxer, which wrote the fixture) load only on a seek. **Resolution:** copy its rule: prime when `count < max(2, Int(duration / 30) + 1)`, by `av_seek_frame(fmt, -1, fmt.duration, AVSEEK_FLAG_BACKWARD)`, then reread. Still under the threshold → `.refused(.noIndex)`. Agent A copies the rule (does not edit `RemuxSession.swift`) and cites the source line in a comment.

**C4 (P2) HDR routing reads `codecpar`, which may be empty without `find_stream_info`.** Spec §2.2 skips `find_stream_info` when width and extradata are present, then takes `color_trc` from `codecpar`. In MKV that field comes from the Colour element only; remuxes without one report `unspecified` until the decoder parses the SPS VUI. The fixture itself reports `color_transfer=unknown`. A PQ file would take the SDR path and come out grey, the failure decision 1 exists to avoid. **Resolution:** route per frame on the decoded `AVFrame.color_trc` (and `color_primaries`, `color_range`, with mastering metadata from `AV_FRAME_DATA_MASTERING_DISPLAY_METADATA`), falling back to `codecpar` only when the frame says unspecified. The DV profile 5 skip stays on `codecpar` coded side data (`AV_PKT_DATA_DOVI_CONF` comes from the MKV header and the `dvcC`/`dvvC` box, as in `MediaProbe.dolbyVision`). For HDR the spec must say explicitly: `sws_setColorspaceDetails(ctx, sws_getCoefficients(SWS_CS_BT2020), srcRange, …, dstRange: 1, 0, 1 << 16, 1 << 16)` after every `sws_getCachedContext`, with limited range assumed when the frame says unspecified. `sws_getCachedContext` defaults to BT.601.

**C5 (P2) The tone-map test contradicts the tone-map formula.** With `L = 203 / 203 = 1` and `Lw = 1000 / 203`, the extended Reinhard gives `L' = (1 + 1 / 24.27) / 2 = 0.52` linear, which the sRGB curve makes about 191, not 255 ± 3. The agent would have to fail the test or bend the curve. **Resolution:** keep the curve (it maps `Lw` to exactly 1, which is its point), add a named `exposure` constant (start at 1.0, tune on the device pass), and write the test as "203 nits lands at the formula's value ± 3" computed in the test from the same constants. HLG 0.75 → about 203 nits is correct (BT.2408) and so lands at the same value.

**C6 (P2) HTTP: there is no persistent connection, and the bundled FFmpeg can bound the ranges.** avformat's http protocol reopens on every seek (new TCP and TLS per keyframe), so "one persistent connection" in §5 is wrong, and the open-ended `Range: bytes=N-` lets the socket pull up to a TCP window past what avio counts. `strings` on the bundled `Libavformat` shows `request_size`, `initial_request_size` and `multiple_requests`. **Resolution:** set `request_size` to 2 MB (4K keyframes run 0.5 to 3 MB) and leave `multiple_requests` at 0, so each frame is a bounded range on a connection that closes with the response. Wire bytes then match `bytes_read`, and between frames the thumbnailer holds no connection at all, which matters on hosts that cap connections per link (mpv reconnecting after a long pause must never be refused because of us). Correct §5's text. Budget the scrub latency as connect + TLS + one range, about 150 to 300 ms on a debrid CDN before decode; device item 1 records it.

**C7 (P3) Frame-path HTTP errors.** §2.3 maps only deadlines and abort. An `AVERROR_HTTP_*` from `av_seek_frame` or `av_read_frame` mid-file must return `.failed(.httpRefused)` (stop the file), same as at open.

**C8 (P3) Read loop.** Set `discard = AVDISCARD_ALL` on every stream except the chosen video stream after open. The demuxer then drops audio and subtitle blocks without returning them, and the "64 packets" budget counts only video (a TrueHD track can return dozens of packets before the video key when Cues lack `CueRelativePosition`). Keep the 8 MB byte cap.

**C9 (P3) Sparse Cues and open-GOP.** After a backward seek, matroskadec returns the key packet at the cue at or before the target (`skip_to_keyframe` from that cue's timestamp), so the frame is reliably at or before the target. With sparse Cues it can be a whole cue gap early; the `.duplicate` and tried rules stop that from looping, which is enough for P3. For H.264 set `flags2 |= AV_CODEC_FLAG2_SHOW_ALL`: an open-GOP I-frame without a recovery-point SEI is otherwise held back and the drain returns nothing. HEVC CRA decodes standalone (no RASL is sent).

**C10 (P3) Timeline origin.** mpv rebases `time-pos` on the demuxer's start time, which is `fmt.start_time` (min over streams), not the video stream's. Swap the precedence in §2.4: `fmt.start_time` rescaled first, then the video stream's, then 0. The fixture starts both at 0, so the [118, 120.05] check holds either way.

**C11 (P3) The FFmpeg surface, recorded.** Spec §8.9 says `Package.swift` lists `Libswscale` and `Libavfilter` as products (`:34`); they are binary targets the `_FFmpeg` target depends on (products are only `MPVKit` and `MPVKit-GPL`). Import still works: `AudioTranscoder.swift` already does `import Libswresample`, a target of the same kind, and `Libswscale.framework` ships a module map. The app links the non-GPL `MPVKit`; its `Libavfilter` has `scale`, `colorspace`, `tonemap` and `libplacebo` but no `zscale` and no zimg, so option (a) is out, as the spec guessed. swscale is major 9 and exposes `sws_scale_frame` with an `intent` field (lcms2 is bundled), which can colour-convert on its own. **Resolution:** forbid `sws_scale_frame` in P3 (it could tone-map a second time); agent A logs `sws_test_transfer(AVCOL_TRC_SMPTE2084, 0)` once at step 0, for a follow-up. Also set `user_agent` to mpv's (`libmpv`) when the addon headers carry none, so a UA-gated CDN treats both connections the same. §8.2 is confirmed: `applyRequestHeaders` sends `context.requestHeaders` to the media host, and `subAdd` (`:1437`) strips credentials only for third-party subtitle hosts.

**C12 (P3) Tone-map cost.** About nine `pow` calls per pixel over 57,600 pixels is 10 to 20 ms optimized and several times that in Debug, not "well under 2 ms". Use a 4096-entry PQ (or HLG) EOTF table indexed by `rgb48 >> 4` and a 4096-entry sRGB table over clamped linear. Log `tm=` beside `dec=`.

## 2. Lifetime and threading

**C13 (P2) Decision 16 is compatible with the BUG-141 standard, with three fixes.** The thumbnailer never touches mpv, the controller or `state`; its FFmpeg handles live and die on its own serial queue, and `closed` stops every later entry point. That meets "nothing touches a handle after teardown". Fixes: (a) the outlive window is not about 100 ms. `getaddrinfo` is not interrupt-polled, and a 4K software decode plus scale cannot be interrupted, so state it as "until the current DNS lookup or decode returns", during which the decoder's 4K pools (about 25 to 40 MB) are still alive. (b) Define `deinit` as `teardownNative()` when `closed` is false. No queue block can be pending at deinit (every block retains `self`), so this is safe, and it covers a thumbnailer dropped without `close()`. As written, the format context and socket leak. (c) Every queue block resumes its continuation exactly once on every path, including `closed` (`open` → `.refused(.modeOff)`, `frame` → `.aborted`).

**C14 (P2) Wiring gaps in §3.4.** (a) `openThumbnailer` must call `driveThumbs` when the open finishes, or a pending scrub waits up to the next 0.5 s tick, which eats the 1.5 s leg budget. (b) `noteFinished` runs on main for every result, `.failed` and `.aborted` included; only the stale-thumbnailer guard skips it. (c) `destroyPlayer` cancels the 50 ms scrub work item and the 2 s `releaseDecoder` item beside `previewFrameWork`. (d) After `setKeyframeIndex`, the controller calls `store.setKeyframeSpacing`.

**C15 (P3) The new cache read.** Give it a `cacheHealthReadPending` flag like `bufferedReadPending`, so a read stalled behind the core lock does not queue a new one every 2 s. End both paths with a strong main hop, including `mpv == nil` (the `startHarvest` shape, review r1 #5), rather than copying `refreshBufferedAsync`'s bare guard return.

**C16 (P3) Mutual exclusion is right as written** (`tick` stays on the left so played time accrues). A scrub can wait behind a first 4K capture (725 ms on the device); accepted.

## 3. Scheduler and store

Coarse-to-fine order, 8 frames per tick, the 2 % / 150 MB / 40 MB budget with a 50 MB scrub overrun, 800 entries / 16 MB, harvest-wins merge, the 5 s refine rule and the lazy open all check out against the device numbers (12 KB per 320 px frame, so 800 frames is about 10 MB). Pre-warm while paused stays: the Apple TV has no battery, the cache rule (C2) protects mpv's reads, and C6 means no idle connection is held.

**C17 (P3) Eviction.** "Oldest decode entry" evicts the 60 s level first, which is the coarse coverage decision 6 protects. Evict the decode entry with the smallest gap to its neighbours instead (oldest on ties). Adjust store test 4 accordingly.

**C18 (P3) Store test 9 is ambiguous.** "With spacing 12 and two sparse entries" fixes neither the entry stamps nor `sampleSpacing`. Write it as concrete stamps: entries at 0 and 10 (spacing 10) with `setKeyframeSpacing(12)` → tol 12; `setKeyframeSpacing(40)` → 30.

## 4. Native half

**C19 (P2) `#EXT-X-INDEPENDENT-SEGMENTS` is not true for every segment.** The tag is legal in an I-frame playlist and in the multivariant playlist, where it applies to every media playlist. But `RemuxSession` cuts on `AV_PKT_FLAG_KEY` (`:967`), which is set on HEVC CRA frames, and x265 encodes open-GOP by default, so many segments start with leading pictures that reference the previous segment. Asserting independence on the master is a false claim on the main media playlist, which matters after a seek. **Resolution:** put the tag in `iframe.m3u8` only (each fragment there is one intra sample, so it is true). The master-level tag goes behind DEBUG `-debug.iframeIndependentMaster`, default off, for device item 7 only. Off stays byte-identical to the pre-spike master. Fix the test wording too: after `#EXT-X-VERSION:7` is the third line, not the second.

**C20 (P2) The trim fallback serves whole segments.** `serveIFrame` falls back to `?? data` in both `trim` and `cut` (`LocalHLSServer.swift:576-579`), so a fragment the trimmer cannot parse goes out as the whole 10 to 28 MB segment, the mode that broke a remux. **Resolution:** a nil trim answers 404 and logs one DEBUG line; `cut` keeps the same rule. Delete the `whole` branch (§8.1's default flip is already in `7d0f25a8f`). A unit test feeds a malformed fragment through the decision helper.

**C21 (P3) The native smoke oracle is sound** (`RemuxSmokeTest` drives a real coordinator and prints `readyToPlay`), and a `LocalHLSServer` builds in a unit test from a synthetic `SegmentMap`, so the `iframe.m3u8 == nil` test is in reach. Log `independent=` per playlist.

## 5. Tests and legs

**C22 (P2) `testDecodeOffByMode` proves nothing on the simulator.** The harvest is already off there and decode is off by default, so `thumbs=0 decoded=0` holds before any P3 code exists. **Resolution:** launch with `-debug.harvestSynthetic YES -debug.seekPreviewMode off` and assert `thumbs=0` after 30 s. That needs mode Off to beat the synthetic flag in `viewDidLoad`: the Off branch runs after the sentinel and simulator blocks and forces `HarvestScheduler(intervalSec: 0)`. Pair it with `testHarvestPlumbingSynthetic` unchanged (harvest mode) as the positive control.

**C23 (P2) `testDecodeScrubIntoUnwatched` has the wrong premise and an unreadable oracle.** By 25 s the open has fired and the first pass has decoded 60, 120 … 480 ahead of the playhead, so 420 is stored and the scrub to 400 shows it at once (the leg passes on the pre-warm, not the scrub path). An XCUITest cannot read the app's `[Thumbs]` console line either. **Resolution:** scrub at about 8 s of playback, before the 20 s open, so the miss drives the open and the decode; add ` fsec=<%.1f|nil>` (the card frame's stamp, from `SeekPreviewMatch.sec`) after `decoded=` and assert `|fsec − scrub| ≤ 5` within 1.5 s. The forward distance from the scrub inject depends on the Auto curve; the agent calibrates the script from the probe's `scrub=` field.

**C24 (P3) `testDecodePrewarmGrows` fits.** Fixture (`ffprobe`): 600 s, 720p HEVC, keyframes every 2 s at about 24 KB, colour unspecified (SDR path), 122 MB, so the budget is 2.4 MB. Ten frames take about 1 MB through avio's 32 KB buffer, `-player.bufferMB 8` holds about 40 s (cache rule passes), and passes at about 20, 30, 40, 50 s give up to 32 frames in 60 s. `-debug.thumbBudgetMB` stays a fallback. No sim leg exercises HDR; unit tests plus device item 1 cover it.

**C25 (P3) P2 order untouched:** `decoded=` then `fsec=` after `aw=`. The integration test reaches `127.0.0.1:8000` from the unit-test host; `range_server.py` is threaded and answers HEAD and bounded ranges.

## 6. Prose and keys

**C26 (P3) Keys and copy.** No collisions: `debug.seekPreviewMode`, `debug.thumbBudgetMB` and `debug.iframeIndependentMaster` appear nowhere in the clone; `debug.iframeMode` exists, DEBUG only. The description passes as written; "downloads a little extra" is fair against a remux but put the number in: "…which downloads up to 150 MB more per title." Re-lint after the edit. Info words are plain. One summary builder (C1) keeps the harvest publish from overwriting the decode fields every 10 s, and keeps "Off after a crash in an earlier playback" until the decoder adds its own part.

**C27 (P3) Agent shape.** Agent A as written owns four new files, the store, the controller wiring, four test classes and three UI legs in one run. Split it.

## Reconciled contract

| Item | Owner | Contract |
|---|---|---|
| `SeekPreviewMode` | B (creates) | `Screens/Player/SeekPreviewMode.swift` per §1; key `debug.seekPreviewMode` = `off` / `harvest` / `decode`, unset = `harvest` |
| `SeekPreviewSource` | A1 | adds `match(near:) async -> SeekPreviewMatch?`; `PreviewFrameOrigin`, `SeekPreviewMatch` per §1 |
| Store | A1 | `insert(_:at:origin:) -> InsertResult` (C1); harvest-wins merge; densest-decode eviction (C17); `decodeMaxEntries 800`, `decodeMaxBytes 16 MB`; `setKeyframeSpacing` |
| Store mirror | A2 | `applyStoreSnapshot` on main: `storeMirror`, `previewFrames`, summary (C1, C26) |
| `ThumbScheduler` | A1 | §3 plus `cacheFill` (C2) |
| `HDRThumbnailToneMap` | A1 | LUTs (C12), `exposure` constant, formula-derived test (C5) |
| `KeyframeThumbnailer` | A2 | §2 plus C3, C4, C6, C7, C8, C9, C10, C11, C13 |
| Native | B | tag in `iframe.m3u8` only, master behind DEBUG (C19); `iFrames:` on the server; nil trim → 404, `whole` deleted (C20) |
| Debug keys | | `debug.seekPreviewMode`; `debug.thumbBudgetMB` (fallback only); `debug.iframeMode` `trim`/`cut`; `debug.iframeIndependentMaster` Bool |
| Bar probe (after `aw=`) | A2 | ` decoded=<n> fsec=<%.1f|nil>` |
| Logs | | `[Thumbs] open … / decode at= kf= took= dec= tm= bytes= job= / off reason=`; `[HLS] master iframes= independent=`; never a URL or header |
| Developer rows | A2 | …, Swipe Scrub Speed, Thumbnail Harvest (A/B), **Seek Preview Frames (A/B)**, then the Trailer Letterbox toggle; `devSeekPreviewMode` after `devHarvestInterval`, in the "Applies to the next playback." arm |
| HTTP options | A2 | `headers` from `requestHeaders`, `user_agent` = `libmpv` when unset, `request_size` 2 MB, `multiple_requests` 0, `rw_timeout` and `timeout` 5 s, `reconnect` 0 |

**Run order: sequential, one agent at a time, same clone and branch `claude/player-p3`.**

1. **Agent B** (native, small, lands the Release-safety fixes first): creates `SeekPreviewMode.swift` and its parse tests, then §7 with C19, C20, C21. Does not touch `MPVPlayerView.swift`. Gates: `IFrameFragmentTests` plus the new gating tests, the scripted native smoke in both modes, Debug + Release.
2. **Agent A1** (pure code): step 0 import proof (`import Libswscale`, log `sws_test_transfer`), the store merge rules and `InsertResult`, `ThumbScheduler`, `HDRThumbnailToneMap`, `TransportBarModel` protocol additions, and their tests. No controller edits. Gates: the three unit classes, the whole NuvioTVTests scheme.
3. **Agent A2** (native decoder and wiring): `KeyframeThumbnailer` and its integration tests, `MediaProbe` visibility, the controller regions listed in §11, the Developer and Info rows, the probe fields, legs `testDecodePrewarmGrows`, `testDecodeScrubIntoUnwatched` (C23), `testDecodeOffByMode` (C22), then the P1 and P2 regression legs and the Release build. Report per-keyframe bytes, `took=`, `dec=` and `tm=` on the fixture.

Then Opus review rounds over `7d0f25a8f..tip` (Codex is out until 10-29), then the device pass in the Test profile, with item 1 recording connect plus range latency (C6) and item 2 reading `fill=` alongside cache seconds (C2).
