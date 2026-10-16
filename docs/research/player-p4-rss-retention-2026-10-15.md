# P3-F9: harvest RSS growth, read-only investigation (2026-10-15)

Scope: why the mpv seek-preview harvest grows process RSS by ~3 MB per capture on the Apple TV. Code read in the clone `~/Claude/Projects/NuvioMobile-player-p4` at `975a70109` (paths under `iosApp/NuvioTV/Screens/`). No code changed, nothing built. The mpv, libplacebo and MoltenVK sources are not in the tree (MPVKit ships binaries only: `Libmpv`, `Libplacebo`, `MoltenVK` xcframeworks under DerivedData `SourcePackages/artifacts/mpvkit`), so the native half is argued from the binaries' strings, the simulator crash stack from P2, and mpv's documented screenshot code path.

## The numbers

- Harvest Only, Dune 2560×1070 HEVC 10-bit SDR on mpv: RSS 796 MB at 2 captures → 923 MB at 43 captures (10:58–11:19), so +127 MB over 41 captures = **3.1 MB per capture**. Captures were 82–225 ms, so the scheduler backed off to 30 s after the first (`[Harvest] slow … interval now 30s`), which matches 41 captures in 21 min.
- Off, same file, fresh process: 721 → peak 823 (+69 s) → steady 673–746 → 704 MB at +1280 s.
- The Harvest Only start reading (796 MB) was taken inside the same startup hump the Off run shows (823 at +69 s). Against Off's steady state (~700 MB) the harvest run ends ~220 MB higher, which is **~5 MB per capture**. So the true slope is 3–5 MB per capture.
- Raw frame per capture: 2560×1070×4 = 10.96 MB of `bgr0`. The NV12 surface of that frame is 4.1 MB and the P010 surface 8.2 MB. The JPEG store ended at 0.2 MB.
- No log has per-capture RSS (the `[Harvest] stored` line lost `rss=` after P2), so the slope is two endpoints, not a curve.

## §1 Mechanism (best reading): native retention inside mpv's VO screenshot path, not the Swift half

**What differs between Off and Harvest Only on mpv.** `viewDidLoad` (lines 495–530): Off sets `harvest = HarvestScheduler(intervalSec: 0)` (line 527) and `ThumbScheduler(enabled: false)` (line 530). Harvest Only keeps the 10 s scheduler and the same `ThumbScheduler(enabled: false)`. `allowsDecode` gates every thumbnailer path (lines 1722, 2065, 2111, `KeyframeThumbnailer(` only at 2136 behind 2111), so the decoder is never opened in either mode. The `[Mem]` tick and `rebuildPreviewSummary` run in both modes. **The only code that runs in Harvest Only and not in Off is `startHarvest` → `captureHarvestFrame` → `screenshot-raw` → `harvestCaptured`.**

**The Swift half cannot hold 3 MB per capture** (detail in §2): every per-capture object is either a local that dies with its closure (the 11 MB `Data`, the full-size `CGImage`, the `CGContext`) or is under 25 KB and capped (the JPEG entry, one `lastDecoded` image, one `previewFrame`). Nothing appends per capture except the store, which ended at 0.2 MB.

**The mpv half does real GPU work per capture that normal playback never does.** `screenshotRaw` sends `screenshot-raw video bgr0` (line 3699). In mpv 0.41, `screenshot_get` asks the VO first (`VOCTRL_SCREENSHOT`, unscaled, no subs/OSD) and only falls back to `vo_get_current_frame` + `mp_image_hw_download` when the VO declines or `screenshot-sw` is set. The bundled libmpv has both the `screenshot-sw` option and the `"Falling back to software screenshot."` string, so that structure is present. P2's simulator crash stack shows which path this build takes: `gl_video_screenshot` → libplacebo `pl_tex_download` → MoltenVK `MVKDeviceMemory::ensureMTLBuffer` → a host-pointer `MTLBuffer` (plan doc, Agent B, `NuvioTV-2026-10-07-092338.ips`). So each capture, on mpv's VO thread:

1. re-maps the current VideoToolbox frame (an IOSurface-backed `CVPixelBuffer`) into Vulkan through MoltenVK,
2. resizes the renderer's intermediate FBOs from the display size (3840×2160 on this TV) down to the source size, renders into a newly created 2560×1070 render target, then resizes them back,
3. downloads that render target into a freshly `mp_image_alloc`'d host buffer, which libplacebo imports as a no-copy `MTLBuffer` (`VK_EXT_external_memory_host`),
4. frees the render target and the imported buffer. libplacebo defers those frees until its command completes.

Normal playback runs steps 1 and 2 at one fixed size and never runs 3 or 4. A small per-capture leftover in any of these steps grows linearly with captures and stays flat in Off. That matches the measurement. The likely leftovers, all native and all on mpv's VO thread (a plain pthread with no autorelease pool our code can drain):

- **(a) a retained decoder surface.** The screenshot takes its own reference to the current frame (`vo_get_current_vo_frame` / a new `frame_priv` + hwdec mapper on `gpu-next`). If the mapping made for the screenshot is never released, through a `CVMetalTextureCache` that is not flushed or a mapper that is never destroyed, VideoToolbox's pool allocates a replacement surface each time. One 2560×1070 NV12 surface is 4.1 MB; a P010 one is 8.2 MB before Apple's surface compression. **This is the closest size match to 3–5 MB.**
- **(b) Metal objects autoreleased on the VO thread.** MoltenVK wraps queue submission and present in `@autoreleasepool`, which is why per-frame rendering is flat. The screenshot-only calls (`vkCreateImage`/`vkAllocateMemory` with a host-pointer import/`vkFreeMemory`) may autorelease objects that are only freed when the thread exits. If one of those objects retains a texture or an imported range, it lives until the player closes.
- **(c) allocator pools that grow on alternating sizes** (libplacebo `vk_malloc` slabs, MoltenVK/IOGPU heaps): resizing between 3840×2160 and 2560×1070 twice per capture can fragment them. This should plateau, not grow linearly. It is the weakest candidate.

Which of (a), (b) or (c) it is cannot be settled without sources or Instruments. All three live in the VO screenshot path, and all three disappear if the VO path is not used. The fix is built on that (§3).

The renderer setting is unknown for the 10:58 run. The `vo` option is `gpu` unless Settings › Playback › Enhanced Video Renderer is on, then `gpu-next` (lines 803–814), and no log line records it. The two VOs implement the screenshot differently (`gl_video_screenshot` vs vo_gpu_next's `video_screenshot`), so record the setting on the next run (§3, step 0).

## §2 Ruled out

1. **The 11 MB `MPVRawFrame.bytes` kept alive by the thumbnail.** `makeThumbnail` (SeekPreviewStore.swift 370–386): `provider` and `source` are locals. The returned image comes from `CGContext(data: nil…)` + `makeImage()`, and that context owns its own 320×134 buffer, so the result holds no reference to `source` or the provider. After `makeImage()` the context is released and the image's backing becomes a private 171 KB copy. The utility block (`harvestCaptured`, lines 1984–1996) captures `frame`, `sec`, `store` and `publish`. It is released after it runs, and the inner `Task` captures only `thumb`, `store` and `publish`. Even if one full frame were kept by mistake, it would be 11 MB held once, not 3 MB per capture. Size rules out a per-capture retention of the whole frame unless memory compression shrinks it, and no list exists that could hold one per capture.
2. **Pile-up through `Task`/`publish`.** `publish` captures `[weak self]`. Nothing stores the `Task` or the result. `applyStoreSnapshot` (2002–2008) copies a `SeekPreviewSnapshot` (numbers and a version) into `storeMirror` and sets an `Int`. No collection grows.
3. **Image mirrors on main.** `TransportBarModel` holds one `previewFrame: CGImage?` (line 47) and `previewFrames: Int` (line 51). The store keeps a single `lastDecoded` (line 128). There is no `[Double: CGImage]` cache anywhere in `Player/` or the controller. A 320×134 image is 171 KB, so even an unbounded mirror would need ~18 images per capture to reach 3 MB. Ruled out by size and by reading the code.
4. **The store.** JPEG entries of 9–12 KB, caps 200 entries / 6 MB in Harvest Only (lines 98–99, `caps(for:)`), evicted by `evictOverCaps`. Measured 0.2 MB.
5. **The crash sentinel.** `HarvestCrashSentinel` writes one fixed key (`player.harvestInFlightOwner`) twice per capture and syncs to disk once per file (lines 1932–1936). The value is a single UUID string, so nothing grows.
6. **mpv's result node.** `withCommandResult` (3685–3694) frees the node with `mpv_free_node_contents` in a `defer`. `cmd_screenshot_raw` steals the image into the node's byte array, so the free covers the `mp_image`. The `strdup`'d args are freed. If this leaked, it would be 11 MB per capture, not 3.
7. **Allocator caching of the 11 MB transients** (the `mp_image`, the Swift `Data` copy). Darwin's large allocator returns these to the VM or keeps a small bounded cache. That gives a plateau, not linear growth.
8. **Keyframe thumbnailer.** Not opened in Harvest Only (§1). Step 5's Harvest + Decode run grew less (+70 MB) with fewer captures on a 4K title, which fits a per-capture cost, not a decoder cost.
9. **Logs and the Info row rebuild.** Small; they run in Off too.

## §3 Fix, smallest first, and the device proof

**Step 0, instrumentation (DEBUG, a few lines, same commit as the A/B):**
- Add `rss=\(ProcessMemory.footprintMB())` back to the `[Harvest] stored` line (`harvestCaptured`'s `publish`, line 1981) so every capture logs a point on the curve.
- Log the VO once per file (`getString("current-vo")` in the existing `[MPVStats] +0s` block) so a run shows `gpu` vs `gpu-next`.

**Step 1, the fix candidate (one option, behind a DEBUG A/B first): `screenshot-sw=yes`.** It is a runtime-settable mpv option. Set it as a property right before the capture in `captureHarvestFrame` (or once in the option list at lines 813+): `setMpvString("screenshot-sw", "yes")`. mpv then skips `VOCTRL_SCREENSHOT` and takes `vo_get_current_frame` → `mp_image_hw_download` (a `CVPixelBuffer` lock + copy) → swscale to `bgr0`. That path creates no Vulkan texture, imports no host pointer, makes no MoltenVK allocation and does no FBO resize, so it bypasses all three candidates in §1. Shape: a DEBUG default `debug.harvestScreenshotSW` (default YES in the A/B build), read in `viewDidLoad` beside `debug.harvestSynthetic`, stored on the controller, applied on `eventQueue` before `screenshotRaw`.
- **Cost to check:** the copy and swscale run on mpv's core thread inside the command. Watch `took=`, which already logs per capture, and `dropped=`/`underruns` in `[MPVStats]`. At 2560×1070, swscale NV12/P010 → `bgr0` is likely 20–60 ms. The VO path measured 82–225 ms, so this may also be faster.
- **Colour caveat:** the software path does not tone map. swscale converts PQ/HLG/DV values as if they were SDR, so HDR10 thumbnails come out washed out and DV profile 5 comes out green or purple. For SDR (the measured file), output matches the VO path. Two ways out: (i) use `screenshot-sw=yes` only when `video-params/gamma` is not `pq`/`hlg` and no DV is signalled, keeping the VO path (and its leak) for HDR; or (ii) request `rgba64` in the sw path and run the existing `HDRThumbnailToneMap` (already used by the decoder) in `makeThumbnail`. That needs a new `bitmapInfo` arm; today `rgba64` returns nil by design. (i) is small and fixes the measured case; (ii) drops the VO path entirely.
- **Possible bonus (unproven):** the simulator trap is inside the VO readback, so with `screenshot-sw=yes` the real harvest may run on the simulator.

**Step 2, Swift hygiene (independent of the leak, small):** scale inside `withCommandResult`'s `read` closure, straight from the node's `ba.data` pointer (`CGDataProvider(dataInfo:data:size:releaseData:)` with no release, or `withUnsafeBytes`), before `mpv_free_node_contents`. Then hand only the 171 KB `CGImage` to the utility queue. That removes the 11 MB `Data` copy and one 11 MB transient per capture, and adds ~5–10 ms on `eventQueue`. Also wrap the capture and the scale in `autoreleasepool { }`. These calls run on our GCD threads, so this cannot help with VO-thread objects, but it costs nothing. **Neither change fixes the native slope; don't present them as the fix.**

**Step 3, only if step 1's A/B still shows a slope:** the leak is in the hardware-download or swscale path itself (hypothesis 5, mpv `mp_image_pool`/`mp_sws` reinit). The next lever is to stop calling mpv for frames: serve Harvest Only from the `KeyframeThumbnailer` at played positions. That is a larger change, and it already tone maps.

**Device proof (rig, Test 2 profile, same Dune 2560×1070 SDR file, native OFF):**
1. Baseline A: Harvest Only, current code, `-debug.harvestIntervalSec 10`. The backoff will move it to 30 s because captures exceed 60 ms. Play 12 min = 20+ captures and read `rss=` per `[Harvest] stored` line. Expect ~60–100 MB over 20 captures.
2. Run B: same, with `debug.harvestScreenshotSW YES`. **Oracle: RSS slope across 20 captures < 10 MB** (taken from capture 3 on, after the startup hump), with `took=` and `underruns=0` recorded.
3. Close test (one run each): after A, close the player, wait 30 s and read RSS from the next player open's first `[Mem] +5s` line. If RSS falls back near the pre-play figure, the retention is tied to the mpv instance (VO thread pool or GPU resources freed at `mpv_terminate_destroy`), which supports (a)/(b) over a process-wide allocator.
4. Record `current-vo`. If A was on `gpu-next`, repeat A once on `gpu` (Enhanced Video Renderer off). A slope on only one VO tells upstream which screenshot implementation leaks.
5. If B is flat, check one HDR10 title with B to see the colour caveat before deciding between (i) and (ii).

## §4 Simulator

The real harvest is off on the simulator (lines 516–526), and the VO screenshot path crashes there, so **the leak's native half has only one oracle: the device.** The simulator can clear the Swift half:
- `-debug.harvestSynthetic YES` feeds `harvestCaptured` exactly as the real path does (lines 1926, 1959–1965), but at 640×360. If the Swift half leaked in proportion to frame size, 640×360 would show ~0.25 MB per capture, ~10 MB over 40 captures, which sits inside `[Mem]` noise. **Add a DEBUG size knob** (`debug.harvestSyntheticSize 2560x1070`, two lines in `syntheticHarvestFrame`) and run 40 captures at `-debug.harvestIntervalSec 5` (synthetic captures take ~2 ms, so no backoff). Oracle: `rss=` on `[Harvest] stored` grows < 10 MB from capture 3 to 40. Flat means the Swift half is clean and §1 stands.
- The same synthetic size knob on the device (DEBUG `captureHarvestFrame` honours `harvestSynthetic` on hardware too) is the cleanest split: synthetic flat while real `screenshot-raw` grows proves the cause is mpv-side on the TV itself.
- One `screenshot-sw=yes` run on the simulator is worth a try (§3).

## §5 Confidence

- **High** that the growth is caused by the capture and is not the store, the Swift image path or any mirror. The mode diff isolates the capture path, and every Swift-side holder is bounded and tens to hundreds of KB.
- **Medium** that it sits in mpv's VO screenshot path (`VOCTRL_SCREENSHOT` → libplacebo/MoltenVK/VideoToolbox mapping) rather than in the generic hardware-download + swscale path, and therefore that `screenshot-sw=yes` removes it.
- **Low** on which sub-mechanism (retained VT surface, VO-thread autorelease, pool growth). The 3–5 MB per capture fits one retained 2560×1070 decoder surface best, but that rests on size alone.

What would change my mind:
- The 2560×1070 synthetic run grows (sim or device). Then the Swift half leaks after all; look first at the `Data` → `CFData` bridge and the `CGImage` drawn from it.
- `screenshot-sw=yes` still grows at the same slope. Then the culprit is common to both paths: the `mp_image` alloc/hw download or swscale context reuse, or the result node. Go to §3 step 3.
- RSS does not drop at player close. Then it is a process-level cache (IOGPU/IOSurface or the malloc zone), not per instance. Instruments' VM Tracker / Allocations on the device would be the next tool.
- The slope differs sharply between `gpu` and `gpu-next`. Then it is one VO's screenshot implementation, which makes it an upstream-report candidate for mpv or MPVKit.
