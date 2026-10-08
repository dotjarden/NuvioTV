# Player P3 spec: keyframe thumbnailer, scheduler, store merge, I-frame hardening (2026-10-08)

Scope: plan `docs/player-revamp-plan-2026-10-06.md` § "Batch P3" as amended by the spike verdict in § "P3 started" (10-08). The native I-frame rendition stays for FF/RW scan only; AVKit's paused-scrub preview never requests I-frames on tvOS 27, so native scrub thumbnails are out of scope. P3's main work is the mpv `KeyframeThumbnailer` (A2) feeding the P2 `SeekPreviewStore` for the unwatched part of the timeline, plus a Developer mode switch that gates both engines. Read-only basis: clone `~/Claude/Projects/NuvioMobile-player`, branch `claude/player-p3`, tip `25fd73ea1`. Paths are under `iosApp/NuvioTV/` unless stated. Line numbers below are from that tip; agents grep the MARKs and symbols instead.

## 0. Decisions this spec makes (for the critique)

1. **HDR path: option (d), tone-map in Swift after the downscale.** `sws_scale` converts the decoded 10-bit frame to 320 px `RGB48` with the frame's BT.2020 matrix, then a pure Swift function (`HDRThumbnailToneMap`) applies the PQ or HLG EOTF, an extended-Reinhard shoulder, the BT.2020 → BT.709 matrix and the sRGB curve on 57,600 pixels. Rejected: (a) `zscale` needs libzimg, which the MPVKit 0.41 / FFmpeg 8.1 build does not list among its dependencies (UNVERIFIED, agent A checks `avfilter_get_by_name("zscale")` once and logs it), and a filter graph per file is more native state to tear down; (b) VideoToolbox decode adds a hardware session that lives beside mpv's own VT session, has its own teardown order under BUG-141, and does not run on the simulator; (c) flat frames would make every HDR thumbnail grey, and most 4K debrid sources are HDR. Option (d) is pure, unit-testable, runs on the simulator, costs well under 2 ms.
2. **Software decode only in P3.** `thread_count = 2`, `FF_THREAD_SLICE`, `AV_CODEC_FLAG2_FAST`, `skip_loop_filter = AVDISCARD_ALL`, never `skip_frame`. VideoToolbox is the follow-up if the device pass measures a 4K median `took=` above 250 ms.
3. **Dolby Vision:** profile 7 and 8 decode their base layer (libavcodec ignores the enhancement layer NAL units; a separate EL track is never opened because the thumbnailer takes the first non-attached-picture video stream). **Profile 5 (and any DV config with `bl_signal_compatibility_id == 0`) is skipped**: its base layer is IPTPQc2 and decodes to wrong colours. The harvest still covers played ground there.
4. **Byte budget for the pre-warm: `min(2 % of the file, 150 MB)`, 40 MB when the size is unknown.** Scrub jobs may go past it up to a hard ceiling of budget + 50 MB. Bytes counted are what avio consumed (`AVIOContext.bytes_read`, open included); TCP read-ahead beyond that is not counted (§5).
5. **Lazy open.** The thumbnailer opens on the first scrub miss or after 20 s of healthy playback, whichever is first, never at `FILE_LOADED`, so it never competes with startup buffering.
6. **Pre-warm order: coarse to fine, forward-biased.** Levels at 60 s, then 30 s, then the target spacing (10 s for films up to two hours, `duration / 720` beyond). Within a level, slots sort by weighted distance from the playhead (ahead × 1, behind × 2). A budget cut leaves even coarse coverage rather than a dense patch near the playhead.
7. **Rate:** at most 8 pre-warm frames per 10 s tick, back to back, then idle until the next tick. A 20-minute session can therefore ask for up to 960 frames; the store's decode share and the byte budget are the binding caps, and the plan's 1500-frame cap stays as a constant that rarely binds.
8. **Store caps grow in decode mode:** 800 entries / 16 MB total (harvest-only keeps 200 / 6 MB). Harvest frames are never evicted by decode frames; a full store rejects pre-warm inserts and ends the pre-warm for the file.
9. **Merge rules:** a played frame (harvest) beats a decoded frame within 1 s; a decoded frame never replaces anything; nothing is ever bulk-assigned. A cancelled pass keeps every frame it inserted.
10. **Scrub refine:** a scrub lookup that returns a frame more than 5 s from the target still shows it, and also asks the decoder for the exact keyframe. A lookup miss asks too. Requests debounce 50 ms, last target wins.
11. **One heavy thing at a time:** no decode starts while a harvest capture is in flight and no harvest starts while a decode is in flight. A pre-warm frame already in flight is not aborted by a scrub request; the scrub job runs next with a QoS boost.
12. **Yield signal:** pre-warm runs only when not `paused-for-cache`, no seek in flight, no seek landed in the last 3 s, `demuxer-cache-duration ≥ 15 s` (or the cache reaches the end of the file), and the cache did not fall by more than 2 s over the last 10 s. Pre-warm also runs while paused (the viewer deciding where to scrub is the best time).
13. **Default mode for this rc: Harvest Only.** Key `debug.seekPreviewMode`, string values `off`, `harvest`, `decode`; unset reads `harvest`.
14. **Mode Off also turns the native I-frame rendition off and drops `#EXT-X-INDEPENDENT-SEGMENTS`**, so Off is exactly the pre-P3 master and a full rollback lever on both engines.
15. **I-frame serving mode defaults to trim in every build.** The tip ships "whole" outside DEBUG (see §8, finding 1). DEBUG `-debug.iframeMode` keeps `trim|cut`; "whole" is deleted.
16. **Lifetime:** the thumbnailer may outlive its controller by at most one in-flight read (about 100 ms after the interrupt fires), holding no reference to the controller, the mpv handle or any UI state. Blocking `deinit` on a semaphore was rejected (main-thread stall on every exit).
17. **Simulator:** the harvest stays off there (P2), the decoder is pure CPU and runs, so the decode legs are simulator legs and the P3 gate depends on them.
18. **Sources the decoder takes:** `http`, `https` and `file` URLs whose demuxer is `matroska` or `mov`, with a video keyframe index of at least two entries after open. HLS, MPEG-TS and index-less files are skipped (an index-less MKV seek scans the file linearly, which is the debrid-cost failure to avoid).

## 1. Data contract

`SeekPreviewSource` (`Screens/Player/TransportBarModel.swift:8`) gains one method; the store conforms:

```swift
enum PreviewFrameOrigin: String, Sendable { case harvest, decode }
struct SeekPreviewMatch: @unchecked Sendable { let image: CGImage; let sec: Double; let origin: PreviewFrameOrigin }

protocol SeekPreviewSource: AnyObject, Sendable {
    func thumbnail(near sec: Double) async -> CGImage?          // unchanged (P2 callers)
    func match(near sec: Double) async -> SeekPreviewMatch?      // P3: frame + its stamp + origin
}
```

`TransportBarModel` gains `@Published var decodedFrames: Int = 0`; the bar probe appends ` decoded=\(model.decodedFrames)` after `aw=` (end of the line, P2 order untouched). `MPVPlaybackState.previewStoreSummary` keeps its role (§6).

New `Screens/Player/SeekPreviewMode.swift` (agent A creates it, agent B consumes it):

```swift
nonisolated enum SeekPreviewMode: String, CaseIterable, Sendable {
    case off, harvest, decode
    static let defaultsKey = "debug.seekPreviewMode"
    static let defaultMode: SeekPreviewMode = .harvest
    static func parse(_ raw: String?) -> SeekPreviewMode { raw.flatMap(Self.init(rawValue:)) ?? defaultMode }
    static func current(_ d: UserDefaults = .standard) -> SeekPreviewMode { parse(d.string(forKey: defaultsKey)) }
    var harvests: Bool { self != .off }
    var decodes: Bool { self == .decode }
    var nativeIFrames: Bool { self != .off }
}
```

Read once per controller in `viewDidLoad` and once per `LocalHLSServer` at creation ("applies to the next playback").

## 2. `Screens/Player/KeyframeThumbnailer.swift` (new, mpv engine)

### 2.1 Shape

```swift
import Libavformat; import Libavcodec; import Libavutil; import Libswscale

struct ThumbFileFacts: Sendable {         // filled by open
    let container: String; let durationSec: Double; let sizeBytes: Int64?
    let keyframeIndex: [Double]           // seconds on mpv's timeline, sorted
    let hdr: HDRFormat; let dvSkip: Bool
}
enum ThumbOpenResult: Sendable { case ready(ThumbFileFacts), refused(ThumbStopReason) }
enum ThumbFrameResult: @unchecked Sendable {
    case frame(CGImage, keyframeSec: Double, tookMs: Double, decodeMs: Double, bytes: Int64)
    case failed(ThumbStopReason?)        // nil = transient (this slot only); non-nil = stop the file
    case aborted
}

final class KeyframeThumbnailer: @unchecked Sendable {
    init(url: URL, headers: [String: String])
    func open() async -> ThumbOpenResult                  // once; later calls return the first result
    func frame(at sec: Double, urgent: Bool) async -> ThumbFrameResult
    func releaseDecoder()                                 // frees the codec context (pools), keeps the demuxer
    func close()                                          // idempotent, any thread, returns at once
    var bytesRead: Int64 { get }                          // lock-protected, any thread
}
```

All native state (`AVFormatContext*`, `AVCodecContext*`, `SwsContext*`, the reusable `AVPacket`/`AVFrame`) lives only on `queue = DispatchQueue(label: "player.thumbs", qos: .utility)`. Never `eventQueue`, never main. `frame(at:urgent:)` wraps `queue.async(qos: urgent ? .userInitiated : .utility)` in a `withCheckedContinuation`; the queue block captures `self` (the thumbnailer) strongly, nothing else.

### 2.2 Open

Same pattern as `MediaProbe.probe` (`Screens/MediaProbe.swift:79`) and `RemuxSession.runRemux` (`:296-328`):

- `MediaProbeNetwork.ensureInit()` (make it `internal`, it is `private` today; or call `avformat_network_init()` through a shared once).
- `avformat_alloc_context()`; `interrupt_callback = AVIOInterruptCB(callback: thumbShouldInterrupt, opaque: Unmanaged.passUnretained(gate).toOpaque())`, where `gate` is a `ThumbInterruptGate` (lock-protected `aborted: Bool` and `deadline: TimeInterval`) owned by the thumbnailer. The thumbnailer outlives the format context (the context is closed on `queue` before the thumbnailer can deinit), so unretained is safe.
- Options: `headers` = `MediaProbe.ffmpegHeaderBlock(headers)` when non-empty (the SAME addon headers mpv sends, credentials included: this is the media host); `rw_timeout` 5,000,000; `timeout` 5,000,000; `reconnect` 0; `probesize` 2,000,000; `analyzeduration` 0; `fflags` `+nobuffer`.
- `avformat_open_input` with a 10 s gate deadline. Skip `avformat_find_stream_info` when the chosen video stream's `codecpar` already has `width > 0` and `extradata_size > 0` (MKV and MP4 headers normally do); otherwise call it under the same deadline.
- Container check: `iformat.name` contains `matroska` or `mov`, else `.refused(.container)`.
- Video stream: first `AVMEDIA_TYPE_VIDEO` without `AV_DISPOSITION_ATTACHED_PIC` (copy `MediaProbe`'s rule).
- Index: `avformat_index_get_entries_count` / `avformat_index_get_entry` on that stream, keep `AVINDEX_KEYFRAME` entries, convert to seconds on mpv's timeline (§2.4). For MKV, if the count is below 2, force one `av_seek_frame(…, 0, AVSEEK_FLAG_BACKWARD)` (the demuxer loads Cues on its first seek) and read the count again; still below 2 → `.refused(.noIndex)`.
- HDR: `color_trc` → `HDRFormat` via `MediaProbe`'s mapping (make `hdrFormat` internal). DV: read `AV_PKT_DATA_DOVI_CONF` from `codecpar` coded side data the way `MediaProbe.dolbyVision` does; `dvSkip = config present && compatId == 0`. `dvSkip` → `.refused(.dvProfile5)`.
- HTTP refusals: `AVERROR_HTTP_FORBIDDEN`, `AVERROR_HTTP_TOO_MANY_REQUESTS`, `AVERROR_HTTP_OTHER_4XX`, `AVERROR_HTTP_SERVER_ERROR` → `.refused(.httpRefused)`; anything else → `.refused(.openFailed)`. Never retried for this file.
- Logs (never the URL; debrid paths carry tokens): `[Thumbs] open took=%.0fms container=%@ index=%d size=%.0fMB budget=%.0fMB hdr=%@` and `[Thumbs] off reason=%@`.

### 2.3 Frame

```text
frame(at: sec):
  gate.deadline = now + (urgent ? 3 : 6)            // per frame
  if gate.aborted → .aborted
  ts = seconds → stream time_base, + stream.start_time (or format start_time)
  av_seek_frame(fmt, vIndex, ts, AVSEEK_FLAG_BACKWARD)   (< 0 → .failed(nil))
  loop av_read_frame:
    skip packets of other streams (av_packet_unref)
    first video packet with AV_PKT_FLAG_KEY → keep; non-key video packets before it → unref, continue
    read budget: stop after 64 packets or 8 MB without a key packet → .failed(nil)
  ensure decoder open (lazy: avcodec_find_decoder, parameters_to_context, flags2 |= AV_CODEC_FLAG2_FAST,
                       skip_loop_filter = AVDISCARD_ALL, thread_count = 2, thread_type = FF_THREAD_SLICE)
  avcodec_send_packet(key); avcodec_send_packet(nil)      // drain: one packet in, one frame out
  avcodec_receive_frame until a frame or EOF; avcodec_flush_buffers (decoder reusable after a drain)
  keyframeSec = best_effort_timestamp (fallback pkt.pts) on mpv's timeline
  scale (§2.5) → CGImage 320 wide
  .frame(image, keyframeSec, tookMs (whole call), decodeMs (send→receive), bytes (bytes_read delta))
```

`AVERROR_EXIT` from any call with `gate.aborted` set → `.aborted`. A deadline expiry → `.failed(nil)` (the slot is marked tried, the file continues). Three consecutive deadline expiries → `.failed(.stalled)` (stop for the file).

`skip_frame` is never set. Orivio's handoff §7.9: with `AVDISCARD_NONKEY` on MKV the decoder swallows every packet. Agent A puts that sentence in a comment above the decoder setup.

### 2.4 Timeline alignment

mpv's `time-pos` is relative to the file's start time; P2 found chapter times at −0.023 on the fixture for the same reason. Stamp = `(pts − startPts) × time_base`, where `startPts` = the video stream's `start_time` when set, else `fmt.start_time` rescaled, else 0. The sim leg checks a decode requested at 120 s on the fixture (2 s GOP) stamps within [118, 120.05].

### 2.5 Scale and HDR

- SDR: `sws_getCachedContext(src: w × h, frame.format → dst: 320 × targetHeight, AV_PIX_FMT_BGR0, SWS_BILINEAR)`, `sws_setColorspaceDetails` from `frame.colorspace` / `color_range` (BT.709 default), output into a `CGContext`-compatible buffer, `CGImage` with `noneSkipFirst | byteOrder32Little` (the `PreviewFrameScaler` format). `targetHeight` via `PreviewFrameScaler.targetHeight` and `SeekPreviewStore.targetWidth`. If the bundled headers expose FFmpeg 8's `sws_scale_frame` with colour-aware conversion, agent A may use it; the output contract is the same.
- HDR (`hdr10`, `hlg`, DV 7/8): scale to 320 px `AV_PIX_FMT_RGB48LE` with the BT.2020 matrix, then `HDRThumbnailToneMap.apply(rgb48:width:height:transfer:) -> CGImage` (new pure file `Screens/Player/HDRThumbnailToneMap.swift`):
  - PQ: SMPTE ST 2084 EOTF to nits; HLG: inverse OETF then the BT.2100 OOTF at 1000 nits (system gamma 1.2).
  - `L = nits / 203` (reference white = 1.0); shoulder `L' = L × (1 + L / Lw²) / (1 + L)` with `Lw = 1000 / 203` (use the mastering display max from side data when present, clamped 400–4000 nits).
  - BT.2020 → BT.709 linear matrix, clamp 0…1, sRGB OETF, 8 bits.
- DV P7/P8 base layers are HDR10 or HLG by compatibility id and take the same path.

### 2.6 Lifetime and teardown (BUG-141 class)

- The controller holds `private var thumbnailer: KeyframeThumbnailer?` strongly, created lazily (decision 5) on main.
- `close()`: sets `gate.aborted = true` synchronously (the interrupt callback returns 1 on its next poll; avformat polls during blocking reads, so a stalled read returns within roughly 100 ms), then `queue.async { self.teardownNative() }`. `teardownNative` frees the decoder, the sws context, packet and frame, then `avformat_close_input`. Idempotent through a `closed` flag checked on `queue`. Every native entry point checks `closed` first.
- In `destroyPlayer` (MARK "Teardown"), BEFORE `mpv_terminate_destroy` and with no weak reference formed: `thumbnailer?.close(); thumbnailer = nil` (plain property write). Ordering against mpv is irrelevant (the thumbnailer never touches mpv), but closing first starts the abort while mpv shuts down.
- The thumbnailer never captures the controller, `state`, the mpv handle or `eventQueue`. Results reach the controller through the `async` call made from a `Task { @MainActor [weak self] in … }` created on main; after `await`, `guard let self` and, before touching anything, `guard self.thumbnailer === captured` (a stale result from a closed thumbnailer is dropped). The store insert goes through a `@Sendable` closure that captures only the store and a `[weak state]` publisher, the P2 `harvestCaptured` shape.
- There is no `eventQueue` block in the decode path, so the P2 "strong main hop at the end of an `eventQueue` block" rule applies only to the new cache-health read (§3.3), which follows `refreshBufferedAsync` exactly: `[weak self]` in, `guard let self, self.mpv != nil`, strong `DispatchQueue.main.async { self.… }` at the end.
- `releaseDecoder()` (queue-async) frees only the codec context and sws context: called when a pre-warm pass ends and 2 s after the last scrub job, so a 4K decoder's frame pools (one 4K 10-bit frame is about 25 MB) do not sit in memory between passes.

## 3. Scheduler: `Screens/Player/ThumbScheduler.swift` (new, pure)

### 3.1 API

```swift
nonisolated enum ThumbStopReason: String, Sendable {
    case frameCap, storeFull, byteBudget, httpRefused, openFailed, noIndex, container, dvProfile5, stalled, modeOff
}
nonisolated struct ThumbScheduler {
    struct Config {
        var tickSec = 10.0, framesPerTick = 8, frameCap = 1500
        var scrubDebounceSec = 0.05, scrubRefineSec = 5.0
        var openAfterHealthySec = 20.0, healthyCacheSec = 15.0, cacheFallLimitSec = 2.0
        var quietAfterSeekSec = 3.0, quietAfterScrubSec = 2.0
    }
    enum Job: Equatable { case scrub(Double), prewarm(Double) }
    struct Inputs {
        var now: TimeInterval, positionSec: Double, durationSec: Double
        var cacheWait: Bool, cacheSec: Double, cacheTrendSec: Double, cacheReachesEnd: Bool
        var seekInFlight: Bool, scrubbing: Bool, recentInput: Bool, harvestInFlight: Bool
        var storeStamps: [Double]            // sorted, all origins
        var storeAcceptsDecode: Bool
        var bytesRead: Int64, byteBudget: Int64, scrubCeiling: Int64
        var opened: Bool                     // thumbnailer ready
    }
    init(config: Config = .init(), enabled: Bool)
    private(set) var inFlight: Job?
    private(set) var decoded = 0
    private(set) var stopped: ThumbStopReason?
    mutating func setKeyframeIndex(_ secs: [Double])
    mutating func noteScrubMiss(target: Double, now: TimeInterval)
    mutating func noteScrubEnded(now: TimeInterval)
    mutating func noteSeekLanded(now: TimeInterval)
    mutating func shouldOpen(_ i: Inputs) -> Bool
    mutating func next(_ i: Inputs) -> Job?
    mutating func noteStarted(_ job: Job, now: TimeInterval)
    mutating func noteFinished(_ job: Job, result: Outcome, now: TimeInterval)
    mutating func stop(_ reason: ThumbStopReason)
    enum Outcome: Equatable { case stored(keyframeSec: Double), duplicate(keyframeSec: Double), rejectedFull, failed, aborted }
    static func prewarmOrder(position: Double, duration: Double, spacing: Double,
                             index: [Double], covered: [Double], tried: [Double]) -> [Double]
    static func targetSpacing(duration: Double) -> Double   // 10 up to 7200 s, else duration / 720
}
```

### 3.2 Rules, exactly

- **Disabled** (`enabled == false`, mode not `decode`): `next` and `shouldOpen` always return nil/false.
- **One in flight:** `next` returns nil while `inFlight != nil` or `stopped != nil` (a stopped scheduler still serves nothing; the store keeps what it has).
- **Global gates for any job:** `!cacheWait && !seekInFlight && !harvestInFlight && opened`.
- **Scrub jobs:** `noteScrubMiss` stores `pendingScrub = (target, dueAt: now + 0.05)`; a newer miss replaces it (last wins). `next` returns `.scrub(snapped)` when `now ≥ dueAt`, `bytesRead < scrubCeiling`, and the snapped keyframe is not tried and not in `storeStamps` within 1 s. `snapped` = the greatest index entry ≤ target (the target itself when the index is sparse, i.e. its median gap exceeds 3 × the target spacing). A scrub that would duplicate is dropped silently. Scrub jobs ignore the cache-health and recent-input gates (the viewer is asking now) but not the global gates.
- **Pre-warm jobs** need, in addition: `!scrubbing`, `!recentInput`, `now ≥ lastScrubEnd + 2`, `now ≥ lastSeekLanded + 3`, cache healthy (`cacheReachesEnd || (cacheSec ≥ 15 && cacheTrendSec ≥ −2)`), `storeAcceptsDecode`, `bytesRead < byteBudget`, `decoded < frameCap`, and a tick slot: a pass starts at most once per `tickSec` and issues at most `framesPerTick` jobs; any failed gate ends the pass (the next tick starts a new one). Hitting the byte budget, the frame cap or a full store calls `stop` with that reason for pre-warm only (`stopped` covers pre-warm; scrub jobs check their own ceiling), so record pre-warm stops in a separate `prewarmStopped`.
- **Order:** `prewarmOrder` builds the levels 60, 30, `targetSpacing`; each level's slots are `k × level` for `k ≥ 0` inside `[0, duration − 2]`, snapped to the keyframe index as above, deduplicated, minus any slot within `level / 2` of a `covered` stamp or within 1 s of a `tried` stamp; sorted by `(slot ≥ position ? slot − position : 2 × (position − slot))`, ties earlier first. The scheduler recomputes the order at each pass start from the store's current stamps (merge, never assign: a pass never assumes the store matches its own bookkeeping).
- **Tried set:** every finished job adds its requested slot and, when known, its `keyframeSec`. `.duplicate` also adds both. `.aborted` adds nothing (that slot can come back). `.failed` adds the requested slot.
- **Cancel keeps what it decoded:** a pass that ends early leaves the store and `tried` as they are; `decoded` counts only `.stored`.
- **Open:** `shouldOpen` returns true once, on the first pending scrub miss, or when `healthyPlaySec ≥ 20` (accumulated over ticks where the cache-healthy rule holds and `!cacheWait`).

### 3.3 How the harvest and the decoder divide the timeline

The harvest (P2) covers played ground for free at about one frame per 10 s of playback. The decoder fills what is not covered: unwatched ground ahead first, then holes behind the playhead (a forward seek skipped them, or the harvest was off: simulator, crash guard, 4K backoff to 30 s). Division is by coverage, not by a watched/unwatched line: any slot with a stored stamp within half the level spacing is skipped, whatever its origin. A decode frame that later lands within 1 s of a harvest frame is dropped by the store (§4); a harvest frame that lands on a decoded one replaces it, so played ground converges on the exact frames the viewer saw.

Cache health input: `demuxer-cache-duration` is read on `eventQueue` every 2 s while the mode is `decode` (new `refreshCacheHealthAsync()` beside `refreshBufferedAsync` in MARK "Buffered ranges (P1)", same block shape), and `cacheTrendSec` is the change over the last 10 s from a small ring buffer on main. `cacheReachesEnd = position + cacheSec ≥ duration − 1`. Not a new observed property: a continuous observer would flood the event loop.

### 3.4 Controller wiring (`MPVPlayerView.swift`, new MARK "Seek preview decode (P3)" right after "Seek preview harvest (P2)")

- `viewDidLoad` (the "Seek preview store (P2-B)" block): read `SeekPreviewMode.current()`. `off` → `harvest = HarvestScheduler(intervalSec: 0)` and no thumb scheduler; `harvest` → P2 as today; `decode` → P2 harvest plus `thumbs = ThumbScheduler(enabled: true)` and a store built with the decode caps (§4).
- `refreshState`, at the harvest call site: start the harvest only if `harvest.tick(...) && thumbs.inFlight == nil` (the tick stays true until it runs, so nothing is lost). Then `driveThumbs(snap)`: build `Inputs` (`harvestInFlight: harvest.inFlight`), `if thumbs.shouldOpen(i) { openThumbnailer() }`, `if let job = thumbs.next(i) { startThumbJob(job) }`.
- `startThumbJob`: `thumbs.noteStarted`, then `Task { @MainActor [weak self] in let r = await thumbnailer.frame(at:urgent:); guard let self, self.thumbnailer === t else { return }; … }`. On `.frame`: hand the image to a utility-queue insert (P2 `harvestCaptured` shape) that returns the store outcome, then `thumbs.noteFinished` on main and, if the outcome is stored, `state.transport.decodedFrames = thumbs.decoded`, update the summary (§6), log `[Thumbs] decode at=%.1f kf=%.1f took=%.0fms dec=%.0fms bytes=%dKB job=scrub|prewarm`, and immediately call `driveThumbs` again so a pass runs back to back. For a scrub job, if `transport.mode` is still `.scrubbing(target)` and `|target − kf| ≤ store tolerance`, call `requestPreviewFrame()` so the card picks the new frame up.
- Scrub hook (MARK "Swipe scrub (P2)", `handlePreviewFrameDecision`, `.start` case): switch the lookup to `source.match(near: target)`; after the token guard, set `previewFrame = match?.image` and, when the mode is `decode` and (`match == nil` or `|match.sec − target| > 5`), call `thumbs.noteScrubMiss(target:now:)` and arm a 50 ms `DispatchWorkItem` that calls `driveThumbs`. Scrub end (the existing reset paths) calls `thumbs.noteScrubEnded`.
- Landing hook (Event loop, `MPV_EVENT_PLAYBACK_RESTART`, beside `harvest.noteSeekLanded`): `thumbs.noteSeekLanded(now:)`.
- Pass end (a `next` returning nil after a pre-warm job) and 2 s after the last scrub job: `thumbnailer?.releaseDecoder()`.
- Teardown: §2.6.

## 4. Store merge rules (`SeekPreviewStore.swift`)

Additions, keeping the P2 behaviour for harvest-only callers:

```swift
enum InsertOutcome: Equatable { case stored, replaced, keptExisting, rejectedFull, invalid }
init(streamKey:, codec:, maxEntries:, maxBytes:)                       // unchanged signature
static let decodeMaxEntries = 800, decodeMaxBytes = 16 * 1024 * 1024
@discardableResult func insert(_ image: CGImage, at sec: Double, origin: PreviewFrameOrigin = .harvest) -> InsertOutcome
func match(near sec: Double) -> SeekPreviewMatch?
func setKeyframeSpacing(_ sec: Double?)                                  // median index gap from the thumbnailer
func stamps() -> [Double]
var counts: (harvest: Int, decode: Int) { get }
var acceptsDecode: Bool { get }                                          // a decode insert would not need eviction
```

- `Entry` gains `origin`.
- **Near-duplicate (within 1.0 s of the nearest entry):** incoming harvest → replaces (any origin) → `.replaced`; incoming decode → no change → `.keptExisting`.
- **Eviction after a harvest insert:** while over a cap, remove the smallest-`seq` decode entry; when none is left, the smallest-`seq` harvest entry (P2 rule).
- **A decode insert that would push the store over a cap** is rejected (`.rejectedFull`, nothing evicted). Scrub-origin decodes use the same rule: the scheduler only pays for a scrub decode the viewer asked for, and a full store means the coverage is already dense.
- **Tolerance:** `tol = min(max(sampleSpacing(), keyframeSpacing ?? 0, 5), 30)`. Decode frames are stamped at the keyframe, which sits up to one GOP before the requested time; folding the GOP into the floor is the plan's "±GOP" lookup.
- `match` uses the same nearest-entry search and decode cache as `thumbnail(near:)`; `thumbnail(near:)` becomes `match(near:)?.image`.
- `coverage()` and `sampleSpacing()` unchanged (all origins).

Tests (`SeekPreviewStoreTests`, extended; the existing cases must still pass untouched):
1. Harvest within 1 s of a decode entry replaces it (origin flips to harvest, count unchanged).
2. Decode within 1 s of a harvest entry is `.keptExisting`, bytes unchanged.
3. Decode within 1 s of a decode entry is `.keptExisting`.
4. Harvest insert over the entry cap evicts the oldest decode entry, not the oldest harvest entry.
5. Harvest insert over the cap with no decode entries evicts the oldest harvest (P2 behaviour).
6. Decode insert at the cap is `.rejectedFull` and evicts nothing; `acceptsDecode` false.
7. Byte cap behaves like the entry cap for both origins.
8. `match` returns the stamp and origin; `thumbnail(near:)` equals `match?.image`.
9. `setKeyframeSpacing(8)` with harvest spacing 10 keeps tol 10; with spacing 12 and two sparse entries, tol becomes 12; never above 30.
10. `counts` and `stamps()` track inserts, replaces and evictions.

## 5. Network discipline

- **Same URL and headers mpv uses.** `context.url` and `context.requestHeaders` (already sanitized by `sanitizePlaybackHeaders`), serialized with `MediaProbe.ffmpegHeaderBlock`, exactly as `RemuxSession` (`:307-308`) and `MediaProbe` (`:96-97`) do. The plan's pointer to "the credential-free URL path the addon subtitle download uses" is the opposite case: that path strips the stream's credentials because the subtitle host is a third party (§8, finding 2). The thumbnailer talks to the media host itself, so it must send them.
- **A second HTTP connection.** One persistent connection opened lazily; each keyframe read is a seek, which avformat's http protocol serves as a new `Range: bytes=N-` request on the same or a reopened connection. Range requests are open-ended, so the kernel can receive up to one TCP window beyond what avio consumes before the next seek closes the stream. The Info row counts avio bytes (`pb.pointee.bytes_read` delta per call, plus the open), so it understates the wire by up to that window per frame. A custom AVIOContext issuing bounded `URLSession` ranges is the fix if the device pass shows the debrid cache suffering; not in P3.
- **Never while buffering:** §3.2 global gates (`cacheWait`), plus the pre-warm cache-health rule.
- **Budget:** decision 4. `sizeBytes` from `avio_size`. `[Thumbs] off reason=byteBudget read=%.1fMB` when the pre-warm stops on it.
- **Debrid links** are the case to protect: Real-Debrid style hosts may cap connections per link or per account. Any HTTP 4xx/5xx from the thumbnailer stops it for the file with `httpRefused`, and the main stream is never touched. The device pass (§10 item 2) watches the main stream's cache seconds while the pre-warm runs.
- **No logs of the URL or headers**, in any build.

## 6. Developer toggle and Info row

- `DeveloperSettingsPane.swift`: `@AppStorage(SeekPreviewMode.defaultsKey) private var seekPreviewMode = SeekPreviewMode.defaultMode.rawValue`; a `SettingsPickerRow` placed right after "Thumbnail Harvest (A/B)": title "Seek Preview Frames (A/B)", options `["harvest", "decode", "off"]`, labels "Harvest Only", "Harvest + Decode", "Off", `descriptionID: .devSeekPreviewMode`. The harvest crash guard stays on its own row; "Off After a Crash" still wins for the harvest half.
- `SettingsDescriptions.swift`: `case devSeekPreviewMode = "dev.seekPreviewMode"`, description (deslop 5/5, linted 10-08):
  "An A/B switch for where the player's seek preview gets its pictures. Harvest Only saves them from the video as it plays. Harvest + Decode also reads pictures from parts you have not watched yet, which downloads a little extra from the stream. Off shows times only and turns off the picture track the Apple TV player uses to fast forward and rewind."
  Add the case to the "Applies to the next playback." footnote list beside `.devHarvestInterval`. New strings into `Localizable.xcstrings` (agents add keys; translations follow the usual pass).
- Info tab "Seek Previews" row (`MPVPlayerPanelAdapter.rebuildInfo`, fed by `state.previewStoreSummary`): in decode mode the summary becomes `"\(n) · \(mb) MB · last decode \(ms) ms · \(read) MB read"`; DEBUG appends ` · RSS \(rss) MB · h \(harvest) / d \(decode)`. When the decoder stopped: `"… · decode off: \(reason)"` with plain words ("no seek index", "the server refused", "budget used", "store full", "Dolby Vision profile 5", "not supported for this file").
- Probe: ` decoded=` (§1).

## 7. Native half (agent B)

- `SegmentMap.masterPlaylist(…, iFrames:)`: when `iFrames` is true, insert `#EXT-X-INDEPENDENT-SEGMENTS` after `#EXT-X-VERSION:7` and keep the `EXT-X-I-FRAME-STREAM-INF` line; when false, neither line (byte-identical to the pre-spike master). `iFramePlaylist()` gains `#EXT-X-INDEPENDENT-SEGMENTS` after the version line. Every segment starts on its boundary keyframe (`RemuxSession` cuts there), so the tag is true for the media playlist too.
- `LocalHLSServer.init` gains `iFrames: Bool` (stored, immutable); `renderedPlaylist` passes it to `masterPlaylist`; with it false, `iframe.m3u8` and `iframe-NNNNN.m4s` answer 404.
- `NativePlaybackCoordinator` (the `LocalHLSServer(` call, `:567`): `iFrames: SeekPreviewMode.current().nativeIFrames`.
- `serveIFrame`: default `mode = "trim"` in every build; DEBUG `-debug.iframeMode` accepts `trim` and `cut` only; delete the `whole` branch and its comment, and log one line in DEBUG when an unknown value is ignored.
- Tests (`IFrameFragmentTests` or a new `IFramePlaylistGatingTests`): master with `iFrames: false` has no `I-FRAME-STREAM-INF` and no `INDEPENDENT-SEGMENTS`; with `true` has both, INDEPENDENT-SEGMENTS second line; `iFramePlaylist()` carries INDEPENDENT-SEGMENTS and `I-FRAMES-ONLY`; `SeekPreviewMode.parse` (nil → harvest, garbage → harvest, each value round-trips, `nativeIFrames` false only for off). If `LocalHLSServer` can be built in a unit test from a synthetic `SegmentMap` without a remux, add: `renderedPlaylist(named: "iframe.m3u8")` is nil with `iFrames: false`.
- Sim check (scripted, not XCUITest): DEBUG log `[HLS] master iframes=%d independent=%d` once per server. Run the native smoke (`-debug.remuxSmokeURL http://127.0.0.1:8000/test-long.mkv`) twice, once with `-debug.seekPreviewMode off` and once with nothing, through `simctl launch --console`, and grep the line (`iframes=0 independent=0`, then `iframes=1 independent=1`); both runs must still reach `readyToPlay`. Record the two log lines in the report.
- Not in P3: the remuxer recording every keyframe for a denser grid (the map is built up front and segments are produced just in time, so it needs a different design), and any native scrub overlay.

## 8. Findings where the code contradicts the plan's target design

1. **"whole" ships today.** `LocalHLSServer.serveIFrame` sets `var mode = "whole"` and only DEBUG can override it, so a Release build of the spike tip serves whole 10–28 MB segments as I-frames, the mode the spike saw break a remux. Agent B fixes it (§7); until then the tip must not be cut.
2. **The plan's network pointer is backwards.** `MPVPlayerView.swift:549-557` in the plan is now the `subAdd` credential guard (`:1436-1470`), which deliberately drops the stream's credential headers for third-party subtitle hosts. The thumbnailer must send them (§5), following `RemuxSession`/`MediaProbe`.
3. **The 1500-frame cap cannot bind against the P2 store.** The store holds 200 entries / 6 MB with insertion-order eviction, so a pre-warm would evict played frames and could never pass 200. §4 adds origin-aware eviction and decode caps of 800 / 16 MB; the effective cap is the store's.
4. **Store replace rule.** P2's insert replaces the nearest entry within 1 s whatever arrives, so a decoded keyframe would overwrite the exact played frame. §4 makes harvest win.
5. **Plan wording "JPEG → store" in the thumbnailer.** The store already encodes; the thumbnailer hands a `CGImage` (P2 contract).
6. **"Stream Info gains a row".** The P2 row lives in the Info tab ("Seek Previews"); P3 extends that row rather than adding one.
7. **`isBuffering`.** The plan says pause while `isBuffering`; that published flag is `cacheWait || (coreIdle && !paused)`, and `coreIdle` is true briefly after every seek. The scheduler uses `cacheWait` plus the explicit seek-quiet window and cache health.
8. **Native "remuxer records every keyframe"** is out of P3 (spike finding: the map is fixed up front).
9. **Libswscale and Libavfilter have no importer in the app yet.** MPVKit's `Package.swift` lists both products (`:34`), so `import Libswscale` should resolve; agent A proves it with a build before writing anything else.
10. **`MediaProbeNetwork.ensureInit` and `MediaProbe.hdrFormat`/`dolbyVision` are private.** Agent A widens them to internal rather than copying them.

## 9. Tests and gates

Unit (NuvioTVTests):

- `ThumbSchedulerTests` (pure, at least 16): disabled returns nil; scrub miss debounces 50 ms (nil at +0.04, job at +0.05); a newer miss replaces the pending one (last wins); one in flight (no job while a pre-warm runs; the scrub job is next when it finishes); scrub pre-empts the queued pre-warm and the pre-warm waits 2 s after scrub end; global gates (`cacheWait`, `seekInFlight`, `harvestInFlight`, not opened) block both kinds; `recentInput` blocks pre-warm only; cache falling more than 2 s over 10 s blocks pre-warm, `cacheReachesEnd` overrides; seek landing quiets pre-warm 3 s; at most 8 per tick, next pass only after 10 s; byte budget stops pre-warm while scrub continues to the ceiling, then stops scrub too; `storeAcceptsDecode == false` stops pre-warm with `storeFull`; `frameCap` stops it; `.duplicate` marks the slot and the keyframe as tried; `.aborted` leaves the slot retryable; a cancelled pass keeps `decoded` and `tried`; `prewarmOrder` is coarse to fine, forward-biased, skips covered slots, snaps to the index and dedupes; `targetSpacing` (7200 → 10, 10800 → 15); `shouldOpen` fires once, on a miss or after 20 s healthy.
- `SeekPreviewStoreTests` additions: §4 list.
- `HDRThumbnailToneMapTests`: PQ code value for 203 nits maps to about 255 grey (± 3); PQ 0 → 0; PQ 10000 nits stays ≤ 255 with no wrap; HLG 0.75 signal lands near reference white; a pure BT.2020 green clips inside 0…255; SDR never enters the function.
- `KeyframeThumbnailerTests` (integration, skip unless `http://127.0.0.1:8000/test-long.mkv` answers a HEAD): `frame(at: 120)` returns a 320-wide image with `keyframeSec` in [118, 120.05]; a second call at 121 returns the same keyframe (duplicate path); `close()` before `open()` and twice is safe; abort latency: point a thumbnailer at a local `NWListener` that accepts and never answers, call `close()` 100 ms into `open()`, and assert the open returns `.refused`/aborted within 400 ms.
- Native gating tests (§7), `SeekPreviewMode` parse tests.

Sim legs (`PlayerTransportUITests`, smoke rig, `-player.bufferMB 8` as today):

- `testDecodePrewarmGrows`: `launch(extra: ["-debug.seekPreviewMode", "decode"])`; within 60 s of playback, `decoded ≥ 10` and `thumbs ≥ 10`. On the simulator the harvest is off, so every frame here came from the decoder. The fixture is 122 MB, so 2 % is 2.4 MB; agent A measures bytes per 720p keyframe on the first run and, if the budget binds before 10, adds a DEBUG `-debug.thumbBudgetMB` and passes it in the leg (recorded as a deviation).
- `testDecodeScrubIntoUnwatched`: decode mode, play 25 s, then scrub-inject forward to around 400 s (no harvest or pre-warm frame near it yet: pre-warm is still on its 60 s level); assert `mode=scrubbing` and `frame=1` within 1.5 s (the "about 1 s" target plus probe polling), and the card frame is near the target (add `ftgt=` to the probe only if needed to prove distance; otherwise the log line `[Thumbs] decode … job=scrub` with `kf` within 5 s of the target is the evidence).
- `testDecodeOffByMode`: `-debug.seekPreviewMode off`: after 30 s, `thumbs=0 decoded=0`.
- P2 and P1 legs unchanged and re-run: `testHarvestPlumbingSynthetic` (harvest mode, the default), the scrub legs, chapters, aspect, the six P1 legs.

Gates: whole NuvioTVTests scheme green, the legs above PASS on FA87, Debug + Release builds, device Debug build.

## 10. Device pass (Test profile, Living Room ATV, console attached)

Set Developer › Seek Preview Frames to Harvest + Decode unless the item says otherwise.

1. 4K HEVC HDR10 debrid title, unwatched: scrub into the second half; a frame within 300 ms, the card never blocks the playhead, colours look right (not grey, not neon). Read `[Thumbs] decode … took= dec=` for 1080p and 4K files; record medians.
2. Same debrid link: while the pre-warm runs, Stream Info's cache seconds never fall toward zero and playback never stalls; note `N MB read` and the stop reason after 10 minutes.
3. RSS (DEBUG summary) delta ≤ 60 MB after 20 minutes of a 4K file in decode mode.
4. DV profile 7 file: thumbnails from the base layer, no crash. A profile 5 file, if one is at hand: the row reads "decode off: Dolby Vision profile 5", harvest still fills played ground.
5. Native engine (DV title): FF/RW scan still steps pictures with the rendition on (mode Harvest Only); with mode Off, scan works without pictures and playback is otherwise unchanged.
6. Exit mid-decode (Menu during a scrub into unwatched 4K ground, and once right after opening a title in decode mode): no crash, `[Thumbs]` shows the abort, the next title plays.
7. Paused-scrub re-check on the native engine with `#EXT-X-INDEPENDENT-SEGMENTS`: pause, swipe; do previews appear and does AVKit request any `iframe-` file (console)? Record yes or no; either answer closes the lever.
8. Harvest Only (default): behaves exactly like P2 (no `[Thumbs]` lines).
9. A link whose host refuses a second connection, if one shows up: the decoder stops with "the server refused" and the stream plays on.

## 11. Agent briefs (Wave 1, sequential in the one clone)

Common: clone `~/Claude/Projects/NuvioMobile-player`, branch `claude/player-p3` (exists; do not create another, `git checkout -b` refuses over the MPVKit symlink). MPVKit is a symlink over the gitlink: stage by explicit paths, never `git add -A`; ignore `git status` errors on MPVKit. One build at a time. Commands from `~/Claude/Projects/NuvioMobile-player/iosApp`; Bash sandbox OFF for `xcodebuild test`. Simulator `FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E`.

- Build: `xcodebuild -project iosApp.xcodeproj -scheme NuvioTV -configuration Debug -destination 'platform=tvOS Simulator,id=FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E' -derivedDataPath build/DerivedData build` (Release: `-configuration Release`).
- Unit: `xcodebuild test -project iosApp.xcodeproj -scheme NuvioTVTests -destination '<same>' -derivedDataPath build/DerivedData -collect-test-diagnostics never -only-testing:NuvioTVTests/<Class>`.
- Smoke server: `cd build/smoke && python3 range_server.py 8000 .` (background).
- UI: `TEST_RUNNER_PLAYER_BAR_PROBE=1 TEST_RUNNER_PLAYER_SMOKE_URL=http://127.0.0.1:8000/test-long.mkv TEST_RUNNER_PLAYER_SMOKE_CHAPTERS_URL=http://127.0.0.1:8000/test-long-chapters.mkv xcodebuild test -project iosApp.xcodeproj -scheme NuvioTVUITests -destination '<same>' -derivedDataPath build/DerivedDataUITests -collect-test-diagnostics never -only-testing:NuvioTVUITests/PlayerTransportUITests/<test>`. The simulator wedges after about six UI runs: `xcrun simctl shutdown` then `boot` the UDID.
- Report: commits (hash + one line), gates with counts, every leg's final probe line, measured `took=`/`dec=`/bytes per keyframe on the fixture, deviations from this spec with the reason, open questions.

**Agent A (decoder side, commit prefix `player P3 A:`).** Owns: new `Screens/Player/SeekPreviewMode.swift`, `KeyframeThumbnailer.swift`, `ThumbScheduler.swift`, `HDRThumbnailToneMap.swift`; `SeekPreviewStore.swift`; `TransportBarModel.swift` (protocol, `decodedFrames`); `PlayerTransportBar.swift` (probe field only); `MPVPlayerPanelAdapter.swift` (summary only if the row needs it); `Screens/MediaProbe.swift` (visibility only); `DeveloperSettingsPane.swift`, `SettingsDescriptions.swift`, `Localizable.xcstrings`; `MPVPlayerView.swift` regions: the P2-B field block (grep "Seek preview harvest (P2-B)"), the store block in `viewDidLoad` (grep "Seek preview store (P2-B)"), the harvest call site in `refreshState` (grep "playback time only, never while the transport moves"), MARK "Buffered ranges (P1)" (add `refreshCacheHealthAsync`), the new MARK "Seek preview decode (P3)", MARK "Swipe scrub (P2)" (`handlePreviewFrameDecision` and the scrub reset paths), the `PLAYBACK_RESTART` landing hook (grep `harvest.noteSeekLanded`), MARK "Teardown" (`destroyPlayer`); tests listed in §9 except the native ones; the three UI legs. Order: (0) prove `import Libswscale` builds; (1) `SeekPreviewMode` + store merge rules + tests; (2) `ThumbScheduler` + tests; (3) `HDRThumbnailToneMap` + tests; (4) `KeyframeThumbnailer` + integration tests (measure bytes per keyframe); (5) controller wiring, Developer row, Info row, probe; (6) UI legs; (7) whole-scheme unit run, P1/P2 regression legs, Release build. One commit per step.

**Agent B (native hardening, commit prefix `player P3 B:`), after A has landed.** Owns: `Screens/SegmentMap.swift`, `Screens/LocalHLSServer.swift`, `Screens/NativePlaybackCoordinator.swift` (the server construction only), `NuvioTVTests/IFrameFragmentTests.swift` or a new `IFramePlaylistGatingTests.swift`. Reads `SeekPreviewMode` (do not edit it). Order: (1) master/I-frame playlist gating + INDEPENDENT-SEGMENTS + tests; (2) server flag, 404 when off, trim default, `whole` removed, DEBUG log line; (3) coordinator wiring; (4) the scripted native smoke check in both modes with the log lines; (5) unit scheme, Debug + Release builds, re-run `IFrameFragmentTests`. Does not touch `MPVPlayerView.swift`.
