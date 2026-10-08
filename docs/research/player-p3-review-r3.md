# Player P3 review, round 3

Reviewer: read-only Opus, standing in for Codex (over quota until 2026-10-29).
Clone `~/Claude/Projects/NuvioMobile-player`, branch `claude/player-p3`, full range `11944d02e..dce3b2700`, focus on the r2 fix round `65c97d385..dce3b2700` (`9b1593e9e`, `cbcb1a1d3`, `9751063c3`, `d85bf9ad6`, `1796ecea6`, `dce3b2700`). Line numbers are at `dce3b2700`.

**Verdict: CLEAN (0 P1 / 0 P2 / 4 P3).** Every r2 finding is fixed or answered. No threading, teardown or continuation rule regressed. The P3s are cost-accounting precision and one 4K behaviour worth a follow-up.

## Checked and found clean

- **r2 #1 (P2), fixed.** `idleCloseWanted` (`ThumbScheduler.swift:236`) keeps the base conditions and adds the three branches. Stamps: scrub miss (`:193`, after the `enabled`/`stopped` guard), scrub end (`:206`), scrub job start (`:286`) and finish (`:291`); `noteIdleClosed` resets to nil (`:248`). `noteScrubEnded` has one caller, the scrubbing true to false edge (`MPVPlayerView.swift:2668`), so no non-scrub event refreshes the minute. Store-hit-only sessions are covered by the end stamp. `driveThumbs` runs on the periodic tick (`:1717`) whenever decode is allowed, paused included, so the 60 s close fires. Both clocks are `systemUptime`. When `leftOpen` is false at 1080p the host has already closed (Connection: close), so the minute only holds memory and a half-closed socket.
- **r2 #2, fixed.** `byteBudget` (`:107`): unknown or non-positive size returns 40 MB before any arithmetic; no division by a variable; `size / 10` caps the 16 MB floor below 160 MB (the fixture's 11.6 MB, the test pins it). The pre-warm UI leg runs without the knob.
- **r2 #3, fixed.** Catalog parses as JSON (1,430 keys), `"%@ MB read"` is gone everywhere, `"%@ MB used"` is the only reference and matches the code. It is `{}` like every other P3 key (English fallback), consistent with the rest of the Developer strings. The Settings description's "about 200 MB" still matches 150 + 50.
- **r2 #4, answered with evidence.** 18 of 18 `iframe-*.m4s` served 200 with `mode=trim` under the `data_offset` gate on the native smoke.
- **r2 #5, fixed.** `testFrameDecodesAfterThePrimingCapFired` asserts `primingCapHit`, which is set under the same `gate.byteLimitHit` condition that runs the `error`/`eof_reached` reset, so the reset provably ran; it then decodes 300 s and 120 s on the same context.
- **r2 #6, fixed.** `openRequests` (`KeyframeThumbnailer.swift:142`) uses the measured counts; the MP4 check matches `"mov,mp4,m4a,3gp,3g2,mj2"`; negative consumed is clamped. See P3 #2 for the crossed term.
- **r2 #7, fixed.** No `%d` left in added lines across the range.
- **`httpOffset` (`:709`).** `av_opt_get_int(pb, "offset", AV_OPT_SEARCH_CHILDREN)` walks AVIOContext, URLContext, HTTPContext; neither avio nor URLContext defines an `offset` option, so it reads `HTTPContext.off` (bytes received, continuous across range-end reconnects), for https too. Called only from `frameOnQueue` (seek and its `defer`), so on the thumbnailer queue. On `file://` the option does not exist: nil, and the resize is also refused, so the range stays 512 KB and `requestLeftOpen` returns true. That default is the safe side (close), and a local reopen is cheap.
- **Threading and lifetime.** The new `_leftOpen` / `_primingCapHit` sit under `bytesLock`; main reads them through locked getters. The container name is read inside `openOnQueue` while `fmt` is still owned by the queue. `closeThumbnailer` and the idle close are unchanged in shape; `inFlight == nil` and `thumbReleaseWork == nil` still gate the close. DEBUG logs stay under `#if DEBUG`.
- **Last pass.** `MediaProbe` visibility changes, the `iFrames` plumbing in `NativePlaybackCoordinator`, `SegmentMap.iFramePlaylist` and its name parser read clean.

## P1

None.

## P2

None.

## P3

**1. On 4K, every scrub session after the pre-warm stop still reopens** (`KeyframeThumbnailer.swift:157`, `:512`; `ThumbScheduler.swift:236`). A 4K frame range is 1 MB and a decode stops at the keyframe's end, so `read % 1 MB != 0` almost always and `leftOpen` is true. The idle close then fires as soon as the session ends, and the next session pays connect, header and a first frame charged as three 1 MB requests, about 4 to 5 MB and a visible first-picture wait. That is the r2 P2 behaviour, now limited to 4K by design. Recommendation: acceptable for this batch, since the scrub frames themselves (about 2 MB each at 4K) dominate the 50 MB headroom and the alternative is a stalled request held at the host. Follow-up: at scrub end, read the open range to its boundary on the queue (at most 1 MB; the host then closes) and keep the thumbnailer under the 60 s rule. That costs less than a reopen and removes the wait.

**2. The crossed-range term double counts** (`:142`, with `charge` at `:174`). Each crossed range is added as a whole request while its bytes are already in `consumed`, and `consumed / 512 KB` also counts bytes spread over the measured seeks as crossings (exactly 512 KB read in one range counts one crossing that never happened). The Cue-less open is charged 35.4 MB for 16.4 MB read, but that file ends in `.noIndex` anyway, so no budget decision changes. The real effect is a high-bitrate first open where `find_stream_info` reads several MB: the charge roughly doubles (about 12 MB for a 5 MB probe), which takes pre-warm frames, not scrub. The budget is not a hard stop for scrubbing (the ceiling adds 50 MB), so nothing refuses decode for the whole file. Fix: charge `consumed + seeks × range` and drop the crossed term, or charge crossings only past the last measured seek.

**3. `httpAtSeek` is not always a request start** (`:523`). If `av_seek_frame` lands inside the avio buffer or within the short-seek window (HTTP reports the TCP window), avio reads through and no new request begins at that offset, so the modulo runs from the wrong origin. The result errs toward true (an extra close) and is false only on an exact multiple, so the harm is small. A comment saying it is a heuristic would do. A firmer signal would compare `off` against the request's end if a future FFmpeg exposes it.

**4. A small file still pays an open just to stop** (`ThumbScheduler.swift:107`, `shouldOpen` at `:261`). Under about 30 MB the budget (a tenth) is below one first-open charge, so the pre-warm opens, stops on budget, and the idle close follows. r2's minimum suggestion (skip the pre-warm open when the budget is below one open plus 8 frames) was not taken. Rare for this app's sources. Fix if convenient: gate the pre-warm branch of `shouldOpen` on `budget >= 3 MB + 8 × 288 KB`.

## Device-pass additions from this round

- The 256 KB "host finishes" threshold was measured on loopback, whose buffers are large. On a real host at 1080p, check that a scrub-play-scrub inside a minute shows no reopen and no stall.
- 4K title: after the pre-warm `stop`, run scrub, play 10 s, scrub eight times; record `idle close … leftOpen=1`, each `reopen=1` open time, first-frame latency, and whether decode switches off.
