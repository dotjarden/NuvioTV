# NuvioTV (Android TV) upstream → tvOS check — 2026-10-19

Upstream: `NuvioMedia/NuvioTV`, HEAD `c613e9311` (2026-10-19). Previous baseline: `f7e2a78ad` (2026-10-16), from `docs/nuviotv-android-upstream-port-plan-2026-10-17.md`.
Window: 24 non-merge commits since the baseline. Fork HEAD checked: outer `697d92e`.

## Status of the 2026-10-17 plan (verified by grep in the fork today)
- DONE in Batch J (`06c63f150`): A1 subtitle aliases/HBS, A2 FilenameEpisodeMatcher, A3 Trakt progress resilience, A5 JS plugin `series` type, A7 Top Shelf custom posters.
- N/A on tvOS per the Batch J record: A4 (profile settings push), A6 (shuffle reload). A8 (add-on remove confirm) shipped in beta.15.
- STILL OPEN, all optional/parked: A9 4K Trailers toggle, A10 HLS/DASH proxyHeaders device check, A11 episode rating color (#1DA1F3 at 9.7+, only if an episode ratings grid exists). Section B decisions (Watch Party, Jellyfin/Emby, Ambient Mode, episode options redesign) are unchanged: defer.

## New since 2026-10-16: what the 24 commits contain
Almost all are i18n (watch party, French, Greek, Hebrew, Hungarian, Latin American Spanish, Italian) or Android-only. One feature is relevant.

## A. Recommended port

### N1. MEDIUM (S–M): per-stream audio delay via `behaviorHints.audioDelayMs` — upstream PR #3781 (merge `719f2b7a5`, commit "Support per-stream audio delay via behaviorHints.audioDelayMs")
What upstream did:
- `Stream` model gets an optional `audioDelayMs` read from `behaviorHints.audioDelayMs` (also plumbed through JS plugin results, the stream link cache, and the player nav args). Range is clamped to ±60000 ms (same as the player's existing limit).
- Player audio delay is split into parts: `deviceMs` (per-output-route, persisted), `streamMs` (from the stream hint), `sessionAdjustMs` (user tweak made while a stream delay is active; never persisted, dropped on stream change). Total = clamped sum. Only `deviceMs` is persisted, and only when `streamMs == 0`, so a stream hint never leaks into the saved per-device delay.
- New test: `StreamAudioDelayTest.kt` (162 lines) — copy it.
Fork state: no `audioDelayMs` in `shared/src` Stream models or behaviorHints parsing. The fork persists audio delay per videoId (`PlayerTrackPreferenceStorage.loadAudioDelayMs(videoId)`; `MPVPlayerView.swift` ~line 1344 applies it) and has `audioDelaySec` in the MPV state. AVPlayer path: check `NativePlaybackTab.swift` for whether native playback supports audio delay at all (likely mpv only; then the hint applies on mpv only).
Verify first:
1. `git -C /tmp/nuviotv-upstream show 719f2b7a5 -m --first-parent --stat` and read `PlayerRuntimeControllerPlaybackEvents.kt` diff.
2. Grep the fork's stream model (`shared/.../streams/` and `.../plugins/`) for `behaviorHints` parsing and add `audioDelayMs`.
Port:
- Shared Kotlin: add `audioDelayMs: Int?` to the stream model and behaviorHints DTO (clamp ±60000), carry it through the plugin result mapper and any stream cache/serialization.
- Swift: in `MPVPlayerView.swift` replace the single stored delay with device/stream/session parts using the same rules. Stream hint wins over the saved per-video delay as the base; the user's tweak while a hint is active is session-only.
- Tests: port `StreamAudioDelayTest` as a shared or Swift test for the parts math (total clamp, persistable rule, stream-change reset).
Gate: shared tests, SharedCore rebuild, NuvioTVTests, tvOS build; device pass with a stream whose add-on sets `audioDelayMs` (mpv path).
Priority note: add-on authors only use this hint if clients honor it; low user-visible urgency, so schedule with the next player batch.

## B. Checked, not worth porting
- `99f01b0b4` collections import URL read off main thread: Android main-thread networking; tvOS uses async Swift/Ktor. N/A (spot-check that the collections import call isn't run on the main actor if cheap).
- `7499cb0ac` Simkl: close non-2xx responses in `httpGet`: OkHttp resource leak; N/A for Ktor/URLSession.
- `747ce832b` autosync keeps embedded subtitle observer when libass swaps MKV extractor: ExoPlayer-specific.
- `1a8bdf6ba` Trakt unused episode-id cache removal: refactor only.
- `455bacf2d` RTL watch-party join code, `f35bb70ef` PlayerView layout trim, `a49e37cbe`/`53eb81065`/`6a74168d2` dedup, all translation commits: Android-only or Watch Party (deferred).

## C. How to run this with Claude Code
1. `git -C NuvioMobile checkout -b claude/nuviotv-n1-stream-audio-delay tvos-shared-extraction`.
2. `git clone --filter=blob:none https://github.com/NuvioMedia/NuvioTV.git /tmp/nuviotv-upstream`; read with `git show 719f2b7a5^2` / the files listed above.
3. Implement N1 (shared Kotlin model + plugin plumbing first, then the Swift player parts), run gates per `CLAUDE.md`.
4. After merging, record the new baseline here: `c613e9311` (2026-10-19), so the next NuvioTV check only reviews newer commits.
