# Player P4 spec: native-engine parity (2026-10-15)

Scope: plan `docs/player-revamp-plan-2026-10-06.md` § "Batch P4: native-engine parity" (A8, A9, B16, B17, A6-native, B24) plus two riders from `docs/master-plan-2026-10-14.md` §2d: BUG-129 (Sources tab vs the up-next search) and BUG-143 (network-aware rejected-link memory, decision D6 = yes). Read-only basis: clone `~/Claude/Projects/NuvioMobile-player-p4`, branch `claude/player-p4` off `tvos-shared-extraction` `975a70109` (beta.19-rc4, P1–P3 + the P3 fix-ups included). Paths are under `iosApp/NuvioTV/` unless stated. Line numbers are from that tip; agents grep the symbols and MARKs instead of trusting the numbers.

## 0. Decisions this spec makes (for the critique)

1. **The native Playback tab lives in the app's own swipe-down panel, not in `customInfoViewControllers`.** It is passed as `PlayerTopPanel(extraTab:)`, exactly as mpv does (`MPVPlayerView.swift:3895-3901`). Rejected: `customInfoViewControllers = [Episodes, Sources]`. On tvOS 26 those render as pills under the seek bar, as the comments at `NativePlayerScreen.swift:19-22` and `:325-326` record, and they would split the native player into two panels the mpv player does not have.
2. **Shared columns, two thin tabs.** The speed row, the Episodes column and the Sources column move out of `MPVPlaybackTab` into `Screens/Player/PlayerPlaybackColumns.swift`. `MPVPlaybackTab` keeps its Timing and Diagnostics sections and composes the shared views. A new `NativePlaybackTab` composes speed, Episodes and Sources. Rejected: generalising `MPVPlaybackTab` over a protocol. Its Timing (audio delay) and Diagnostics (`showStreamInfo`) sections have no native mechanism, so a protocol would carry two optional capabilities that only one engine fills. The Episodes and Sources columns already depend only on `NextEpisodeEngine` plus `canSwitchStreams` and `onClose` (`MPVPlaybackTab.swift:99-227`), so they extract cleanly.
3. **No audio delay row on native.** AVPlayer has no audio offset API, and the loopback HLS path would need a remux-side PTS shift that the published playlist forbids (`RemuxSession.swift:586` comment). The row is left out of the native tab, not shown greyed. The Diagnostics toggle is left out too, because the native Info tab already carries the stream rows (`NativePlaybackCoordinator.streamInfoRows`).
4. **One speed list, kept in step through the player view controller.** `playerVC.speeds` is set to the same seven rates (0.5 to 2). The tab's row calls `playerVC.selectSpeed(_:)`, and its checkmark reads `playerVC.selectedSpeed?.rate`, re-read each time the panel opens. The panel is modal over the player, so the system pill cannot change while the tab is visible, and no KVO is needed. Rejected: writing `player.rate` from the tab. A bare rate write leaves the system pill showing the old speed, and the next `play()` restores `defaultRate`.
5. **`transportBarCustomMenuItems` = [Episodes, Sources], each opening the app panel on the Playback tab with that column focused.** Episodes appears only for a series with episodes; both appear only when `canSwitchStreams` is true. `NativePlayerHostController.onOpenPanel` gains a `PlayerPanelTab` argument (Down and swipe-down pass `.info`), plus a `PlaybackColumn?` focus hint.
6. **`externalMetadata` is item decoration, so it belongs to the coordinator (agent B), not to the view controller configuration (agent A).** `externalMetadata` is a property of `AVPlayerItem`, and every item the coordinator creates (first item, signaling retry, B17 rebuild) must carry it. A pure builder `NativeNowPlayingMetadata` makes the text items. The artwork is fetched once per coordinator, starting in `start()`. It is included in the first item's metadata if it has already arrived, and otherwise appended to the current item's array once when it lands. Later items reuse the cached array.
7. **Subtitle style: `AVTextStyleRule` with `CharacterBackgroundColorARGB`, not `BackgroundColorARGB`.** mpv's `sub-back-color` is the box drawn behind the glyphs (`opaque-box` border style when the outline is off, `MPVPlayerView.swift:1393-1397`). CMTextMarkup's per-character background is the matching key. `BackgroundColorARGB` paints the whole caption window instead. Outline: `CharacterEdgeStyle = Uniform` when `outlineEnabled`, else `None`. Size: `RelativeFontSize = fontSizeSp / 18 × 100`, clamped to 65…222 %, the same bounds mpv's 36…122 clamp gives around its default of 55. Outline colour, outline width and `bottomOffset` have no CMTextMarkup key, so they are not applied on native (§3.4).
8. **The style is applied once per item, from the snapshot the coordinator already reads at `start()`.** The coordinator does not observe `PlayerSettingsRepository` after `resolveLanguagePlan` (`:268-312`), so a Settings change applies to the next playback, as `stripSdh` already does (`:405-409`). Every item, the B17 rebuild included, gets the same rule.
9. **Pause card on native: paused for 1.5 s AND the transport bar is known hidden AND the panel is closed AND the setting is on.** The host becomes the `AVPlayerViewController` delegate (nothing sets `playerVC.delegate` today; grep verified) and reports `willTransitionToVisibilityOfTransportBar`. The card is a SwiftUI overlay in the screen's ZStack. It is not focusable, has no hit testing, and is hidden on any press, on bar show and on resume. [C-5] "Known hidden" means a `visible=false` callback arrived during this pause: the bar starts as unknown = visible, so a delegate that never fires on tvOS 26 can never put the card over the bar. There is no "dismissed for the rest of the pause" latch: mpv has none (`pauseCardVisible`, `MPVPlayerView.swift:3888-3890`), the card comes back when the bar hides again.
10. **`PauseInfoCard` is extracted by agent B as its first commit (a pure move), before agent A starts.** `MPVPlayerView.swift` is assigned to B only. The extracted card takes `context`, `positionSec` and `durationSec`, and mpv passes `state.positionSec` / `state.durationSec`.
11. **Late add-on subtitles: re-serve the master once per session, then rebuild the item at the current position.** The rebuild happens automatically only when (a) the viewer has not touched the subtitle selection since the item became ready, (b) nothing is showing, and (c) the language plan would make one of the late renditions DEFAULT. In every other case the late renditions are published as panel rows straight away, and the item is rebuilt lazily on the first pick of one. The trigger is the fetch's completion (`subsFetchCompleted()`, the `completedRequest` state) plus a 1 s debounce, never a per-emission update. That gives at most one `addSubtitleRenditions` call and at most one item swap per session. Rejected: rebuilding on every late emission (several add-ons trickle in, which would mean several stalls), and always rebuilding (a viewer who chose Off or an embedded track would get a stall for nothing).
12. **The start gate becomes "first segment ready + 3 s", with the 8 s absolute cap kept.** Today the coordinator waits up to 8 s measured from poll start (`:469`), so the plan's "settles or 3 s" is not what the code does. With a late path in place, holding startup longer than 3 s past remux readiness buys little. DEBUG `-debug.nativeSubsGateSec` overrides the 3 s for an A/B.
13. **Native chapters come from libavformat at open, mapped onto the native playlist timeline.** [C-4] The served timeline's zero is the first video keyframe, not the container start: `originTicks = map.boundaryTicks[0]` in the video stream's time base (`RemuxSession.swift:523-525`, `:552`), and every fragment's `tfdt` is written absolute against it (`avoid_negative_ts` disabled + `frag_discont`, `:506-511`, `:586-587`). So a native chapter is `chapterSec − originSec` with `originSec = boundaryTicks[0] × videoTB`, not `− start_time`. mpv's `chapter-list` is relative to the container start (`PlayerChapters.swift:45-47`); the two lists differ by `originSec − start_time` (tens of ms on most files, up to the audio lead on others). That difference is expected and is not "fixed". They go through `PlayerChapters.parseIndexed` (sort, dedupe, negative-slack clamp), are trimmed at `duration − 1` (`PlayerChapters.trimmed`), and empty titles show "Chapter N" (`PlayerChapters.displayTitle`). libavformat has already flattened the Matroska editions. The spec takes the list as it comes, which in practice is the first or default edition, and does not parse editions itself.
14. **Loading overlay replaces every bare startup spinner on both engines, the router's `.deciding` spinner in `PlayerScreen.swift:70-75` included.** That third spinner is what would otherwise flash before either engine mounts. A mid-play rebuffer keeps today's small spinner on mpv and the system's on native, and the poster is never drawn over a mid-play rebuffer. With `showLoadingOverlay` off, today's spinner and caption stay exactly as they are.
15. **No logo in the overlay.** `PlaybackContext` has no logo field (`PlaybackModels.swift:36-112`), and resolving one through `TitleLogoStore` needs a `MetaPreview`. The overlay shows the title in text. Adding `logo` to `PlaybackContext` is a follow-up, because every launch path would have to fill it.
16. **BUG-129: busy guard plus generation guard.** `loadSources()` returns early while an up-next search owns the shared flow, and every search emission is checked against a `searchGeneration` captured when the watcher was created.
17. **BUG-143: classify at the producers into a typed `PlaybackFailureKind`; a pure classifier maps engine evidence to it; only positive link evidence is remembered.** Remembered: HTTP 4xx/5xx, decode/container, placeholder clip, early end, never produced media with the host reachable, unknown. Never remembered: network (refused, unreachable, DNS, timeout, reset, TLS), offline, cancelled. When `NetworkPathMonitor` reports no usable path at the moment of failure, the kind is `.offline` whatever else was seen. The failover walk is unchanged: a transient failure still advances to the next link. Only the 8 h memory and the debrid resolve-cache invalidation are skipped. The resolve-stage timeouts in `FirstPlayAutoPlay` (`:287`, `:297`) stop rejecting too, and no resolve outcome is remembered while the path is unsatisfied (§8.4, [C-6]).
18. **Run order: B steps 0–1, then A ∥ B, then C.** [C-11] A needs only B's steps 0–1 (`PauseInfoCard`, `PlaybackFailure.kind`, `PlayerLoadingStage`, `durationSec`); after that A and B touch disjoint files and run in parallel, building and committing only when the orchestrator hands them the build lock (one `xcodebuild` and one `git commit` at a time: the clone has one index). B's two UI legs need A's `debug_nativeProbe` and `-debug.mpvSmokeEngine`, so B writes them in its step 5 and runs them in a step 8 after A's step 6 has landed. C runs after both: it edits A's `NativePlayerScreen.swift` and B's `MPVPlayerView.swift`.

## 1. Data contracts

### 1.1 New and changed types

```swift
// Screens/PlaybackModels.swift (agent B)
enum PlaybackFailureKind: String, Equatable, Sendable {
    case http, decode, placeholder, endedEarly, noMedia, unknown   // remembered
    case network, offline, cancelled, local                        // not remembered; .local = our own engine failed (B17 rebuild) [C-3]
    var remembersLink: Bool { switch self { case .network, .offline, .cancelled, .local: false; default: true } }
}
struct PlaybackFailure: Equatable {
    let reason: String; let positionSec: Double; let secondsPlayed: Double; let startedPlaying: Bool
    var engine: PlaybackEngine = .mpv
    var otherEngineEligible = false
    var kind: PlaybackFailureKind = .unknown          // NEW; producers set it
    var httpStatus: Int? = nil                        // NEW; log/diagnostic only
}
// PlaybackFailoverPolicy.shouldReject becomes:
static func shouldReject(_ f: PlaybackFailure) -> Bool { f.secondsPlayed < healthySeconds && f.kind.remembersLink }
```

```swift
// Screens/Player/PlaybackFailureClassifier.swift (NEW, agent B, pure)
enum PlaybackFailureClassifier {
    struct Verdict: Equatable { let kind: PlaybackFailureKind; let httpStatus: Int? }
    static func fromMpvLog(_ lines: [String], endFileError: String?, watchdogFired: Bool) -> Verdict
    static func fromAVError(_ code: Int32) -> Verdict            // AVERROR codes from FFmpeg
    enum Origin { case remote, loopback }                        // [C-7]
    static func fromNSError(_ error: Error?, origin: Origin) -> Verdict  // walks NSUnderlyingErrorKey; loopback NSURL → .noMedia
    static func applyingPath(_ v: Verdict, pathSatisfied: Bool) -> Verdict  // offline override
}
// Screens/Player/NetworkPathMonitor.swift (NEW, agent B)
final class NetworkPathMonitor: @unchecked Sendable {
    static let shared: NetworkPathMonitor          // NWPathMonitor on a utility queue, started on first access
    var isSatisfied: Bool { get }                  // lock-guarded; true until the first update
}
```

```swift
// Screens/Player/NativeSubtitleStyle.swift (NEW, agent B, pure)
enum NativeSubtitleStyle {
    struct Input: Equatable { var textARGB: Int64; var backgroundARGB: Int64; var outlineEnabled: Bool
                              var bold: Bool; var fontSizeSp: Int }
    static func input(from s: SubtitleStyleState) -> Input
    static func attributes(_ i: Input) -> [String: Any]        // CMTextMarkup keys
    static func rules(_ i: Input) -> [AVTextStyleRule]        // [] when attributes == default
    static func logLine(_ i: Input) -> String                  // "[Subs] style rule fg=… bg=… edge=… bold=… size=…%"
}
```

```swift
// Screens/Player/NativeNowPlayingMetadata.swift (NEW, agent B, pure except the artwork encode)
enum NativeNowPlayingMetadata {
    static func textItems(context: PlaybackContext) -> [AVMetadataItem]     // title, subtitle, description
    static func artworkItem(jpeg: Data) -> AVMetadataItem
}
// Screens/Player/NativeChapterMarkers.swift (NEW, agent B, pure)
enum NativeChapterMarkers {
    static func seconds(start: Int64, tbNum: Int32, tbDen: Int32, originSec: Double) -> Double   // [C-4]
    static func groups(_ chapters: [TransportChapter], durationSec: Double) -> [AVNavigationMarkersGroup]
}
// Screens/Player/LateSubtitlePlan.swift (NEW, agent B, pure)
enum LateSubtitlePlan {
    enum Action: Equatable { case none, publishOnly, autoRebuild(name: String) }
    static func merge(existing: [SubtitleRendition], late: [SubtitleFile]) -> [SubtitleRendition]  // indices + unique names
    static func decide(late: [SubtitleRendition], flags: [SubtitleRenditionFlags], selectionShowing: Bool,
                       legibleTouched: Bool, rebuildsUsed: Int) -> Action
}
// Screens/PlaybackModels.swift (agent B declares it; agent C's PlayerLoadingOverlay.swift adds the views)
enum PlayerLoadingStage: Equatable {
    case checking                 // PlayerScreen .deciding (MediaProbe)
    case connecting               // native: remux opening; mpv: loadfile → FILE_LOADED
    case preparing(dolbyVision: Bool)   // native: signaling known, waiting for map/init/first segment
    case subtitles                // native: holding for the add-on subtitle fetch
    case buffering(percent: Int?) // native: item not playing yet; mpv: FILE_LOADED → first PLAYBACK_RESTART
    case started                  // overlay fades out
}
```

### 1.2 Fields and closures added to existing types

- `NativePlaybackCoordinator` (agent B): `@Published private(set) var loadingStage: PlayerLoadingStage = .connecting`. B declares the enum in `PlaybackModels.swift` in wave 1, so the coordinator can publish it; C's overlay file only adds views and the status text (§8.1). Also `@Published private(set) var chapters: [TransportChapter] = []`, `@Published private(set) var lateSubtitleRows: [SubtitleRendition] = []` (renditions not yet in the current item), `@Published private(set) var isRebuildingItem = false`, `var durationSec: Double { lastDurationSec }`, `private(set) var failureKind: PlaybackFailureKind = .unknown`, `func seek(toChapter sec: Double)`, `func selectLateSubtitle(name: String)`, and [C-11] `@Published private(set) var lateState: String = "none"` (`none` / `published` / `rebuilt`, the probe's `late=` field).
- `RemuxSession` (agent B): `var chapters: [TransportChapter]` (lock-guarded, set with the signaling block at `:473-479`), `var lastErrorCode: Int32?` (the AVERROR behind the last `fail(_:)`).
- `LocalHLSServer` (agent B): `subtitles` / `subtitleFlags` become lock-guarded state behind a snapshot accessor; new `func setSubtitles(_ renditions: [SubtitleRendition], flags: [SubtitleRenditionFlags])`.
- `NativePlayerHostController` (agent A): `var onOpenPanel: ((PlayerPanelTab, PlaybackColumn?) -> Void)?` (was `(() -> Void)?`), `var onTransportBarVisibilityChange: ((Bool) -> Void)?`, `var onAnyPress: (() -> Void)?` (fed by a recogniser, see §2.3 [C-5]); conforms to `AVPlayerViewControllerDelegate`.
- `NextEpisodeEngine` (agent A): `private var searchGeneration = 0`, `func noteSourceListClosed()` (public twin of `sourceListClosed()` for the native host), `Hooks.clearStreams` and `Hooks.watchStreams` seams (§7).
- `MPVPlaybackState` (agent C): `@Published var startupStage: PlayerLoadingStage = .connecting` and `@Published var playbackStarted = false`.
- `MPVTVPlayerViewController` `reportPlaybackFailure(reason:startedPlaying:secondsPlayed:positionSec:)` gains `kind:` and `httpStatus:` (agent B).

## 2. A8: Playback tab, speeds, menu items, metadata (native)

### 2.1 `Screens/Player/PlayerPlaybackColumns.swift` (NEW, agent A)

Move these out of `MPVPlaybackTab.swift`, unchanged in look and accessibility ids:

- `PlayerSpeedRow(current: Double, onSelect: (Double) -> Void)`: the `HStack` at `:43-54` with `static let speeds: [Double] = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0]` as `PlayerPlaybackColumns.speeds` and the `player.panel.speed.<x>` ids.
- `PlayerEpisodesColumn(engine:onClose:)`: `:101-176` (`sortedEpisodes`, `watchedEpisodeKeys`, `episodeKey`, `isCurrentEpisode`, `episodeChipLabel`).
- `PlayerSourcesColumn(engine:onClose:)`: `:180-227`, including `.onAppear { engine.loadSources() }`.

`MPVPlaybackTab` keeps `settingsColumn` (speed row via `PlayerSpeedRow(current: state.playbackSpeed) { state.setSpeed?($0) }`, Timing, Diagnostics) and lays out the same `HStack` with the two extracted columns. The mpv tab must look identical after the move (the UI leg `testMpvPlaybackTabUnchanged` checks the ids).

### 2.2 `Screens/Player/NativePlaybackTab.swift` (NEW, agent A)

```swift
enum PlaybackColumn { case episodes, sources }
struct NativePlaybackTab: View {
    @ObservedObject var engine: NextEpisodeEngine
    @ObservedObject var speed: NativeSpeedModel        // @Published rate: Double; select: (Double) -> Void
    let canSwitchStreams: Bool
    let initialColumn: PlaybackColumn?
    let onClose: () -> Void
    // HStack: left column = caption "Playback Speed" + PlayerSpeedRow; then Episodes (if canSwitchStreams
    // && !sortedEpisodes.isEmpty, width 440) and Sources (if canSwitchStreams, width 560), each .focusSection().
    // initialColumn → .defaultFocus on the first row of that column (priority .userInitiated).
}
```

`NativeSpeedModel` is a small `@MainActor ObservableObject` in the same file. Agent A creates it in the container's `makeUIViewController`. `rate` is refreshed from `host.playerVC.selectedSpeed?.rate ?? 1` each time the panel opens, and `select(_:)` calls `host.playerVC.selectSpeed(match)` (where `match` is the `AVPlaybackSpeed` from `playerVC.speeds` with that rate), sets `rate`, and logs `[NativePlayer] speed → 1.25 (tab)`. [C-16] The header says `selectedSpeed` mirrors `player.defaultRate` (`AVPlayerViewController.h:186`, `:193`); it does not promise the live `rate`. After `selectSpeed`, if `player.timeControlStatus != .paused` and `player.rate != match.rate`, set `player.rate = match.rate` (the pill already agrees through `defaultRate`) and log `rateFixed=1`. `PlayerSpeedRow` adds `.accessibilityValue(current == speed ? "selected" : "")` to each button (no id change), which the leg reads. When the selected speed is not in the list (a future system default), the row shows no checkmark.

### 2.3 `Screens/Player/PlayerPanelHost.swift` (agent A)

- `onOpenPanel` becomes `((PlayerPanelTab, PlaybackColumn?) -> Void)?`; `handleOpenGesture` (`:62-70`) calls `onOpenPanel?(.info, nil)`.
- A public `func openPanel(tab: PlayerPanelTab, column: PlaybackColumn?)` runs the same guards (`panelHost == nil`, nothing presented on self or `playerVC`) and calls `onOpenPanel`. The menu-item actions call it.
- Conform to `AVPlayerViewControllerDelegate`; in `viewDidLoad` set `playerVC.delegate = self`. Implement `playerViewController(_:willTransitionToVisibilityOfTransportBar:with:)` → `onTransportBarVisibilityChange?(visible)`, and log `[NativePlayer] bar visible=1|0` (DEBUG only; it fires often).
- [C-5] `onAnyPress` cannot come from `pressesBegan`: presses reach the host only when the focused AVPVC view did not consume them (today that is only Menu with the bar hidden, `:72-84`), so Select, arrows and Play/Pause would never arrive. Add a third recogniser beside `downPress`: `UITapGestureRecognizer` with `allowedPressTypes` = select, playPause, up, down, left, right, menu, `cancelsTouchesInView = false`, same `delegate = self` (simultaneous). Its action calls `onAnyPress?()`. It must not consume anything and must not change the Menu handling in `pressesBegan`.

### 2.4 `Screens/NativePlayerScreen.swift` `AVPlayerContainer` (agent A)

In `makeUIViewController` (`:322-340`):

```swift
host.playerVC.speeds = PlayerPlaybackColumns.speeds.map {
    AVPlaybackSpeed(rate: Float($0), localizedName: String(format: "%g\u{00D7}", $0)) }
var menu: [UIMenuElement] = []
if canSwitchStreams, hasEpisodes { menu.append(UIAction(title: String(localized: "Episodes"),
    image: UIImage(systemName: "list.number")) { [weak host] _ in host?.openPanel(tab: .playback, column: .episodes) }) }
if canSwitchStreams { menu.append(UIAction(title: String(localized: "Sources"),
    image: UIImage(systemName: "arrow.triangle.2.circlepath")) { [weak host] _ in host?.openPanel(tab: .playback, column: .sources) }) }
host.playerVC.transportBarCustomMenuItems = menu
host.onOpenPanel = { [weak host] tab, column in
    guard let host else { return }
    speedModel.rate = Double(host.playerVC.selectedSpeed?.rate ?? 1)
    let extra = PlayerPanelExtraTab { NativePlaybackTab(engine: engine, speed: speedModel,
        canSwitchStreams: canSwitchStreams, initialColumn: column, onClose: { model.onClose?() }) }
    let panel = PlayerPanelHostController(rootView: PlayerTopPanel(model: model, extraTab: extra, initialTab: tab))
    model.onClose = { [weak panel] in panel?.close(animated: true) }
    host.present(panel: panel); openChanged(true)
}
host.onPanelClosed = { openChanged(false); engine.noteSourceListClosed() }
print("[NativePlayer] avpvc speeds=\(…) menu=\(menu titles) delegate=1")
```

Update the comment at `:325-326` to say that the Playback tab and the menu items replace the old `customInfoViewControllers` idea. The container gains `engine: NextEpisodeEngine`, `canSwitchStreams: Bool`, `hasEpisodes: Bool` (`!context.episodes.isEmpty && context.season != nil`), `onBarVisibility: (Bool) -> Void` and `onAnyPress: () -> Void`. Menu items are installed once in `make` (their meaning never changes in a session). The `allowedSubtitleLanguages` / contextual-action logic in `update` stays as it is.

`NativePlayerScreen.body` passes `engine: upNext`, `canSwitchStreams: onPlayNext != nil`. In the `.failed` branch (`:107-114`) the `PlaybackFailure` gains `kind: coordinator.failureKind` (§8).

### 2.5 `externalMetadata` (agent B, `Screens/Player/NativeNowPlayingMetadata.swift` + coordinator)

`textItems(context:)` builds `AVMutableMetadataItem`s with `extendedLanguageTag = "und"`:

- `.commonIdentifierTitle` = `context.title`.
- `.iTunesMetadataTrackSubTitle` = `NativeInfoHeader(context:).subtitle` ("S1 · E4 · Episode name", or the stream label for a movie), omitted when nil.
- `.commonIdentifierDescription` = `context.synopsis`, omitted when nil or empty.

`artworkItem(jpeg:)` uses `.commonIdentifierArtwork` with `value = jpeg as NSData` and `dataType = kCMMetadataBaseDataType_JPEG as String`.

Coordinator: `start()` launches `artworkTask` on the main actor. The URL is `context.poster ?? context.episodeStill`. Now Playing wants the 2:3 poster first, which is the opposite of the Info tab header. The task calls `ImageFallbackPlan.load(candidates: [url], request: ArtworkDecodeRequest(size: .points(width: 400, height: 600), fill: true, scale: 1))` (`DesignSystem/CachedAsyncImage.swift:1323`) and encodes `jpegData(compressionQuality: 0.8)` off the main actor. It stores `artworkMetadata` and, if `playerItem` exists, sets `playerItem.externalMetadata = textItems + [artwork]` once, logging `[NativePlayer] artwork attached (N KB)`. The task is cancelled in `stop()`. Every item goes through one new `private func decorate(_ item: AVPlayerItem)` that sets `preferredForwardBufferDuration = 24`, `externalMetadata`, `textStyleRules` (§3) and `navigationMarkerGroups` (§6). It is called at `:597` (first item), `:663` (signaling retry) and in the B17 rebuild. Agents must not set those properties anywhere else.

### 2.6 Strings and behaviour the system now shows

The system transport bar shows the `externalMetadata` title and subtitle above the scrubber (tvOS 15+). The smoke context's title is "MPV Smoke", so the sim legs read it. Device pass step 1 confirms the line on hardware and that the system Info area shows the synopsis.

## 3. A9: subtitles follow the app style (`AVTextStyleRule`)

### 3.1 Mapping (`NativeSubtitleStyle.attributes`)

| `SubtitleStyleState` | mpv (`MPVPlayerView.swift:1359-1397`) | CMTextMarkup key | Value |
|---|---|---|---|
| `textColor` (ARGB Int64) | `sub-color` | `kCMTextMarkupAttribute_ForegroundColorARGB` | `[a, r, g, b]` as `CGFloat` 0…1 |
| `backgroundColor` | `sub-back-color` (box behind glyphs) | `kCMTextMarkupAttribute_CharacterBackgroundColorARGB` | same; key omitted when alpha is 0 |
| `outlineEnabled` | border style `outline-and-shadow`, size `width × 1.5` | `kCMTextMarkupAttribute_CharacterEdgeStyle` | `kCMTextMarkupCharacterEdgeStyle_Uniform` when on, `_None` when off |
| `outlineColor`, `outlineWidth` | `sub-outline-color`, `sub-outline-size` | none | not applied (§3.4) |
| `bold` | `sub-bold` | `kCMTextMarkupAttribute_BoldStyle` | `kCFBooleanTrue`; key omitted when false |
| `fontSizeSp` | `sp × 55/18` clamped 36…122 | `kCMTextMarkupAttribute_RelativeFontSize` | `clamp(sp / 18 × 100, 65, 222)`; key omitted at exactly 100 |
| `bottomOffset` | `sub-pos` | none | not applied (§3.4) |
| `stripSdh` | `sub-filter-sdh` | n/a | already handled server-side (`LocalHLSServer(stripSdh:)`, `RemuxSession.Config.stripSdh`) |

`Int64` ARGB decode, as in `mpvColorString` (`:1379-1382`): `a = (argb >> 24) & 0xFF`, then r, g, b. The key strings are `kCMTextMarkupAttribute_*` CFStrings bridged with `as String`. Agent B checks each key against `CoreMedia/CMTextMarkup.h` in the Xcode 26.6 tvOS SDK before writing the mapping and records any key that is missing.

### 3.2 Where it is applied

In `NativePlaybackCoordinator.decorate(_:)` (§2.5): `item.textStyleRules = NativeSubtitleStyle.rules(input)`. `input` is computed once in `resolveLanguagePlan` from `settings.subtitleStyle` and stored. The coordinator prints the `logLine` once per session at `beginPlayback`. With every field at its default (white text, transparent background, outline on, regular weight, 18 sp) the rules still carry the uniform edge and the white foreground, so the system default style is replaced on purpose. That matches mpv, which applies the default style too.

### 3.3 Interaction with tvOS caption settings

tvOS Settings › Accessibility › Subtitles and Captioning › Style can lock a style against video override. When the viewer has done that, the system wins over `textStyleRules`. That is correct accessibility behaviour, and the spec does not work around it. The device pass checks the default system style only.

### 3.4 Not applied, and why

CMTextMarkup has no edge-colour or edge-width key (confirmed in the tvOS 26.6 SDK `CMTextMarkup.h`), so the outline is drawn in the system's contrasting edge colour. [C-13] A vertical-position key does exist (`kCMTextMarkupAttribute_OrthogonalLinePositionPercentageRelativeToWritingDirection`, 0 % top to 100 % bottom, cue centre), but whether AVPlayer honours a positional attribute from a nil-selector `AVTextStyleRule` over WebVTT cues is unverified. Agent B may try it behind DEBUG `-debug.nativeSubLinePos <pct>` on the headless rig (screenshot); unless it visibly moves cues, `bottomOffset` stays unapplied. A WebVTT cue setting (`line:`) could move cues because the server writes every VTT body, but embedded per-segment VTTs and add-on bodies would need a cue rewrite at serve time. That is out of P4 and is logged as a follow-up. The Settings rows stay shared: the description of Subtitle Position gains "(mpv player)".

## 4. B16: pause card on native

### 4.1 Extraction (agent B, first commit, pure move)

New `Screens/Player/PauseInfoCard.swift` containing the body of `MPVPlayerView.swift:4095-4140`, changed only in its inputs:

```swift
struct PauseInfoCard: View {
    let context: PlaybackContext
    let positionSec: Double
    let durationSec: Double
    // body unchanged; `remainingString` uses max(durationSec − positionSec, 0); accessibilityIdentifier("player.pauseCard")
}
```

The mpv site (`:3927-3932`) becomes `PauseInfoCard(context: context, positionSec: state.positionSec, durationSec: state.durationSec)`. Delete the private struct. Build. The commit message says "pure move".

### 4.2 Native rule (agent A, `NativePlayerScreen.swift`)

The pure rule goes in A's own new file `Screens/Player/NativePauseCardRule.swift` (not in `PauseInfoCard.swift`, which B owns):

```swift
enum NativePauseCardRule {
    static let delaySec: Double = 1.5
    static func visible(pausedSince: TimeInterval?, now: TimeInterval, barVisible: Bool, panelOpen: Bool,
                        enabled: Bool, dismissedThisPause: Bool, isPlayingPhase: Bool) -> Bool
}
```

Screen state: `@State pauseCardEnabled = true` (read once in `onAppear`, like mpv `:4005-4006`: `(PlayerSettingsRepository.shared.uiState.value_ as? PlayerSettingsUiState)?.pauseOverlayEnabled != false`), `@State barKnownHidden = false`, `@State pausedSince: TimeInterval?`, `@State showPauseCard = false`, and `@State pauseCardTask: Task<Void, Never>?`. [C-5] The rule's inputs change accordingly: `visible(pausedSince:now:barKnownHidden:panelOpen:enabled:isPlayingPhase:isRebuilding:)`, no `dismissedThisPause`.

- On `coordinator.isPaused` → true: set `pausedSince = now`, `barKnownHidden = false` (unknown counts as visible), schedule `pauseCardTask` to re-evaluate after 1.5 s. On false: clear them and set `showPauseCard = false`.
- `onBarVisibility(visible)` (from the host delegate): `barKnownHidden = !visible`; when it turns true (hidden) while paused, re-evaluate at once (and again when the 1.5 s task fires). Visible → hide the card (reason `bar`).
- `onAnyPress`: `showPauseCard = false` (reason `press`). The card may show again after the bar next hides, as on mpv.
- `coordinator.isRebuildingItem` (B17) → hidden: a rebuild's transient pause is not a viewer pause.
- `panelOpen` true → hidden.
- When the card shows, cancel and hide a pause-reason swipe hint (`hideSwipeHint()` when `swipeHintReason == .pause`). The two would overlap at the top centre.

Render in the ZStack above `AVPlayerContainer`, below the up-next caption:

```swift
if showPauseCard, coordinator.phase == .playing {
    PauseInfoCard(context: context, positionSec: coordinator.lastPositionSec, durationSec: coordinator.durationSec)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
        .padding(60)
        .allowsHitTesting(false).focusable(false)
        .transition(.opacity.animation(.easeInOut(duration: 0.25)))
}
```

`lastPositionSec` updates on the 3 s tick, so the "remaining" line can be up to 3 s stale. That is fine for a card that rounds to minutes. Log `[NativePlayer] pause card shown after 1.5s` and `[NativePlayer] pause card hidden reason=press|bar|resume|panel`.

Risk the device pass decides: if tvOS 26's transport bar never hides while paused, the card never shows on native. Step 3's oracle is the `bar visible=0` line while paused. If it never appears, the card is dropped for native in this batch (the screen keeps the code, gated off by a one-line `NativePauseCardRule.supported = false`), the Settings copy keeps "(mpv player)", the release notes say so, and Christian decides on a follow-up. [C-5] The follow-up candidate that would coexist with a visible bar is a card inside `playerVC.contentOverlayView`, which AVKit draws below its own chrome; it is not built in P4. The spec never draws the card over a visible bar. The `bar visible=` log is not DEBUG-only during P4 (rate-limited to transitions), so a Release device run can read it too.

### 4.3 Settings copy (agent C, §8.4)

`PlayerSettingsPane.swift:50` subtitle drops "(mpv player)". `SettingsDescriptions.swift:328` changes from "…This only works in the mpv player. On by default." to "…Works in both players. On by default." The code comment at `PlayerSettingsPane.swift:46-47` is updated.

## 5. B17: late add-on subtitles

### 5.1 What the code does today

`start()` (`:227-263`) mirrors the add-on list into `addonSubtitles` and logs "(after master, too late this session)" once a server exists (`:257`). `pollForFirstSegment` (`:463-500`) holds startup until `subsFetchCompleted()` or `pollStart + 8 s`. Renditions are fixed in `beginPlayback` (`:509-627`), and `LocalHLSServer.subtitles` is a `let` (`:63`). The "Coordinator:156-186 pattern" the plan cites no longer rebuilds an item: the B3 delay path reselects Off and then the same option (`forceSubtitleRefetch`, `:957-1005`), and the audio switch runs through renditions (info-panel W3, `syncAudioSelection`). **No mid-play item swap exists today.** The only `replaceCurrentItem` is the pre-play signaling retry (`handlePrePlaybackItemFailure`, `:632-671`). B17 builds the first mid-play swap and copies that retry's structure: cache-busted URL, new item, `replaceCurrentItem`, re-observe.

### 5.2 Gate change (`pollForFirstSegment`)

Replace `subsDeadline = pollStart + 8` with: `readyAt` = the first poll where `hasMap && hasInit && hasFirst`; wait while `!subsFetchCompleted() && now < min(readyAt + gate, pollStart + 8)` with `gate = 3` (DEBUG `-debug.nativeSubsGateSec`). Keep the lapsed log line and add `gate=3.0s` to it. While waiting on subtitles only, `loadingStage = .subtitles`.

### 5.3 Server (`LocalHLSServer.swift`)

- `private var _subtitles: [SubtitleRendition]`, `private var _subtitleFlags: [SubtitleRenditionFlags]` under `lock`. `init` assigns them. Add a private `subtitleSnapshot() -> ([SubtitleRendition], [SubtitleRenditionFlags])`, and route every read to it: `renderedPlaylist` (`:265-310`) and `serveSubtitle` (`:520-571`).
- `func setSubtitles(_ r: [SubtitleRendition], flags: [SubtitleRenditionFlags])` replaces both under the lock and logs `[HLS] subtitles now \(r.count) (+\(added))`. The master is rendered per request (`renderedPlaylist` → `map.masterPlaylist`), so the next master fetch carries the new `EXT-X-MEDIA` lines. Existing indices and names never change, so the cached `vttBase` entries stay valid. [C-14] The coordinator passes the existing renditions' flags verbatim and computes `subtitleFlags` only for the late ones (with `defaultTaken` seeded from whether any existing flag is DEFAULT), so the existing `EXT-X-MEDIA` lines stay byte-identical even if the language plan moved.
- [C-1] `func setStartOffset(_ sec: Double?)` (lock-guarded). While non-nil, `renderedPlaylist(masterName)` inserts `#EXT-X-START:TIME-OFFSET=<sec, %.3f>,PRECISE=YES` after `#EXT-X-VERSION`. Nil renders the master byte-identical to today. The coordinator sets it right before creating the rebuild item and clears it once that item is ready.
- [C-2] The audio renditions' `DEFAULT=YES` is rendered from `selectedAudio()` (falling back to the stored `isDefault` when it is nil), not frozen at `beginPlayback`. Today `audioRenditions` is a `let` with `isDefault: track.selected` from the start of the session (`NativePlaybackCoordinator.swift:548-557`), so a rebuild after an audio switch would default back to the original track. Before any rebuild the selected box always equals the default, so the first master is unchanged.

### 5.4 Coordinator

State: `servedAddonURLs: Set<String>` (filled in `beginPlayback`), `lateDebounce: Task?`, `lateRebuildsUsed = 0`, `legibleTouched = false`, `pendingLateSelection: String?`.

- `legibleTouched` becomes true in `select(subtitle:)` (every caller is a viewer action, except the DEBUG spike), and in `handleMediaSelectionChange` when the legible selection's canonical name differs from the last snapshot after the first `loadLegibleSelection`. That second case catches the system popover. The snapshot is taken in `loadLegibleSelection` once the group loads.
- The watcher (`:233-259`) keeps updating `addonSubtitles`. After it, and from the existing 3 s observe tick, call `checkLateSubtitles()`. When `server != nil && subsFetchCompleted()` and some `addonSubtitles` URL is not in `servedAddonURLs`, it (re)starts `lateDebounce` (1 s). When that fires:
  1. `merged = LateSubtitlePlan.merge(existing: currentRenditions, late: newFiles)`: indices continue from `max(index) + 1`, names are deduped against all existing names with the `" 2"` suffix rule from `:528-534`.
  2. `flags = existingFlags + subtitleFlags(forLate: late, defaultTaken: existingFlags.contains(where: \.isDefault))` ([C-14]), then `server.setSubtitles(merged, flags:)`. Update `subtitleRenditionsByName`, `servedAddonURLs` and `lateSubtitleRows` (the late ones), and log `[Subs] late renditions +N (names…)`.
  3. `LateSubtitlePlan.decide(...)`: `.autoRebuild(name)` when `!legibleTouched`, nothing is showing (`currentSubtitleOption == nil`), `lateRebuildsUsed == 0`, and a late rendition got `isDefault == true` in `flags`. Otherwise `.publishOnly`. Log `[Subs] late mode=auto|lazy`. [C-14] An auto rebuild is also deferred to lazy while the player is paused, in its last 5 minutes, or within 10 s of a seek (`onPositionTick` reported a jump): those are the moments the up-next card and skip seeks own.
- `selectLateSubtitle(name:)` (the panel picked a row that is in `lateSubtitleRows`): set `pendingLateSelection = name` and call `rebuildItem(reason: "pick")`. If a rebuild has already happened this session, the rendition is in the item and the adapter never calls this.
- `rebuildItem(reason:)`, at most once (`lateRebuildsUsed`), and never while `phase != .playing` or `isRebuildingItem`. [C-1][C-2][C-3] rewritten after the critique:
  ```
  let pos = CMTimeGetSeconds(player.currentTime()); let wasPlaying = player.timeControlStatus != .paused
  let audioName = currentAudioOption.map(Self.renditionName); let subName = currentSubtitleOption.map(canonical)
  isRebuildingItem = true; observeTask?.cancel()
  subtitleDelayApplyTask?.cancel(); subtitleRefetchRestoreTask?.cancel(); isRefetchingSubtitles = false
  // C-2: the new item must not pick its own audio/subtitles. Criteria are "once per item at setup" anyway (:318-321).
  player.setMediaSelectionCriteria(nil, forMediaCharacteristic: .audible)
  player.setMediaSelectionCriteria(nil, forMediaCharacteristic: .legible)
  server.setStartOffset(pos)                                   // C-1: start AT the playhead, never at t=0
  let item = AVPlayerItem(url: servedURL + "?late=1"); decorate(item)
  playerItem = item; legibleGroup = nil; audibleGroup = nil
  player.replaceCurrentItem(with: item); observeMediaSelection(item:player:)
  observePlayback(player:item:, rebuild: RebuildTarget(pos, wasPlaying, audioName, subName ?? pendingLateSelection, startedAt: now))
  ```
  **Why the start offset ([C-1]).** A new item with no start loads from t=0 before any seek can run. Segments behind the playhead are often missing on disk: the remux starts at segment 1 and a resume seek repositions it, so segments 2…k of a resumed session were never produced, and a track switched mid-play has no `aud-T-00001`. `serveSegmentJIT` answers a request for a missing file outside the producing window by repositioning the worker to it (`LocalHLSServer.swift:648-656`). The rebuilt item would drag production back to the start of the file, block 5 s per missing file and 503, and most likely fail into a mid-play fallback. `EXT-X-START` (allowed in a multivariant playlist) makes AVPlayer load at `pos`. Agent B proves it on the headless rig first: after a resume to 300 s, trigger a rebuild and check that the first media request logged after the swap is the segment holding `pos` and that no `[Remux] reposition` appears. If AVPlayer ignores the tag, the fallback is `item.seek(to: pos, toleranceBefore: .zero, toleranceAfter: .zero)` issued right after `replaceCurrentItem`, before ready, with the same request-log check; if neither keeps it off t=0, B17's rebuild is not shipped and late renditions publish as rows that apply from the next playback (report it).
  **Audio ([C-2]).** `syncAudioSelection` (`:862-871`) returns early while `isRebuildingItem` is true, so neither the media-selection notification nor the tick path (`:785-786`) can relay the new item's initial pick to `remux.selectAudio` before the restore. The master's audio DEFAULT already follows the selected track (§5.3), so the new item's first audio request is the track the worker is producing.
  **Readiness ([C-3]).** `observePlayback` gains `rebuild: RebuildTarget?`. On `readyToPlay`, a rebuild skips the resume logic, Trakt/tracker start and `readyUptime`, and instead: clears `server.setStartOffset(nil)`; sets `lastPositionSec = pos` before seeking, so the skip planner sees no jump; `await player.seek(to: pos, toleranceBefore: .zero, toleranceAfter: .zero)` only when `|currentTime − pos| > 0.5`; `play()` only if `wasPlaying`; `loadLegibleSelection`. Once both groups load, it selects the audible option named `audioName` first, then the legible option named `subName` (the late pick, or the auto-DEFAULT rendition; select it explicitly anyway, or `nil` for Off), then `isRebuildingItem = false`, `lateRebuildsUsed += 1`, `lateSubtitleRows = []`, and logs `[Subs] late rebuild reason=auto|pick at 123.4s took=0.84s audio=… sub=…`. Failure paths: the existing `!readied` + `.failed` branch goes to `handlePrePlaybackItemFailure` (`:721-723`, the signaling retry); with `rebuild != nil` it must instead call `fallbackMidPlay("late subtitle rebuild failed")` with `failureKind = .local`. The not-ready branch today only logs every 10 s (`:741-748`), so a rebuild stuck in `.unknown` would freeze the picture for good: with `rebuild != nil`, 12 s without `readyToPlay` → the same fallback. `.local` is never remembered (the link is fine; our swap failed).
  **Observer inventory ([C-3]).** Per item, torn down and re-created by the rebuild: `observeTask` (the 200 ms / 3 s polling loop, `:675-805`, cancel + new); `mediaSelectionObserver` (NotificationCenter on the item, `:837-845`, replaced by `observeMediaSelection`); the `legibleGroup` / `audibleGroup` caches and their load tasks (guarded by `playerItem === item`); `subtitleDelayApplyTask` and `subtitleRefetchRestoreTask` (cancelled above, they read the old item); the artwork attach (targets `playerItem` at landing time; `decorate` covers an item created before it lands). Per player, kept: `timeControlObserver` (KVO on `player.timeControlStatus`, `:610-618`; `hasStartedPlaying` stays true so a rebuild's waiting state never reads as a viewer pause); the media-selection criteria (cleared above on purpose). There is no `addPeriodicTimeObserver` and no KVO on item status in this coordinator (status is polled), so nothing else needs re-registering. The P3 I-frame rendition survives because `iFrames` is server state rendered into every master.
- The playback speed survives: `replaceCurrentItem` keeps `player.defaultRate`, and `play()` uses it. The subtitle delay survives because it is server state (`_subtitleDelayMs`); `subtitleDelaySlots` is 1 (`:172`), so late addon renditions need no slot setup.
- Old-item requests: AVPlayer cancels the old item's connections on replace; the server's `ConnLive` flag ends their JIT blocks. Nothing else is needed.

### 5.5 Panel rows (`NativePlayerPanelAdapter.swift`, agent B)

`rebuildSelections` (`:77-138`):

- Republish on `coordinator.$lateSubtitleRows` and `$isRebuildingItem` (add both to the merge at `:38-46`; use `Publishers.MergeMany`).
- While `isRebuildingItem` is true and `legibleGroup` is nil, return early from the subtitle half and keep the previous `model.subtitles`. That avoids a ~1 s empty list under a focused row.
- After the item's options, append one `.addon` row per `lateSubtitleRows` entry not already present by canonical name, with `id = name` and `isSelected = false`.
- `selectSubtitle(_:)` (`:140-150`): when no option in the group matches `option.id` and `lateSubtitleRows` has that name, call `coordinator.selectLateSubtitle(name:)`.

The system subtitle popover lists late renditions only after a rebuild. That is accepted and noted in the release notes.

## 6. A6-native: chapters

### 6.1 `RemuxSession.swift` (agent B)

Right after `avformat_find_stream_info` (`:330`), on the worker:

```swift
// [C-4] read after the segment map exists (right after `_segmentMap = map`, `:499`), because the origin is the map's.
let vtb = videoStream.time_base
let originSec = Double(map.boundaryTicks[0]) * Double(vtb.num) / Double(vtb.den)
var found: [TransportChapter] = []
for i in 0..<Int(input.pointee.nb_chapters) {
    guard let ch = input.pointee.chapters[i]?.pointee else { continue }
    let sec = NativeChapterMarkers.seconds(start: ch.start, tbNum: ch.time_base.num, tbDen: ch.time_base.den,
                                           originSec: originSec)
    found.append(TransportChapter(title: Self.metadataValue(ch.metadata, "title") ?? "", sec: sec))
}
let chapters = PlayerChapters.parseIndexed(count: found.count, title: { found[$0].title }, time: { found[$0].sec })
```

Store `_chapters = chapters` under the lock with `_segmentMap` (not in the earlier signaling block: the origin is not known there). Log `[Chapters] native n=\(count) origin=\(originSec) first="\(t)"@\(s) last=…`. `seconds` = `start × num / den − originSec`.

**Timeline check (verification, not discovery: the rule is stated in decision 13).** Run the headless rig on `test-long-chapters.mkv` (chapters 0 / 90 / 240 / 390 / 540 s), seek to chapter 3 on native and confirm `player.currentTime()` lands within 0.1 s of 240 − `origin`. Record `origin=` and the landing in the agent report.

### 6.2 Coordinator (agent B)

In `beginPlayback`: `chapters = PlayerChapters.trimmed(remux.chapters, durationSec: map.totalDurationSec)`, and `chapterGroups = NativeChapterMarkers.groups(chapters, durationSec:)`, which `decorate(_:)` assigns to `item.navigationMarkerGroups`. The builder makes one `AVTimedMetadataGroup` per chapter: an `AVMutableMetadataItem` with `identifier = .commonIdentifierTitle`, `value = PlayerChapters.displayTitle(c, index: i)`, `extendedLanguageTag = "und"`, and `timeRange` running from the chapter start to the next start (the last one to the duration). These are wrapped in `AVNavigationMarkersGroup(title: nil, timedNavigationMarkers:)`. With fewer than 1 chapter the array is empty. `navigationMarkerGroups` is a tvOS-only API, available in this target.

`func seek(toChapter sec: Double)`: `player.seek(to: PlayerChapters.clampedSeek(sec, durationSec: lastDurationSec), toleranceBefore: .zero, toleranceAfter: .zero)`. The screen's skip planner reads the next tick's jump as a user scrub (`onPositionTick`), so a chapter jump is never auto-skipped back. A seek past the remux frontier takes the existing JIT reposition path.

### 6.3 Panel (`NativePlayerPanelAdapter.swift`, agent B)

Port `MPVPlayerPanelAdapter.rebuildChapters` (`:118-125`) against `coordinator.chapters` and `coordinator.lastPositionSec`, called from `onTick()` and on `$chapters`. Set `model.onSelectChapter = { coordinator.seek(toChapter: $0.sec); model.onClose?() }`, the same close-after-select rule as mpv. Fix the model's comment at `PlayerTopPanelModel.swift:68` ("the native engine never fills it"). `PlayerTopPanel.tabs` (`:111-116`) already shows the tab when the list is non-empty.

## 7. Rider BUG-129 (`Screens/NextEpisodeAutoPlay.swift`, agent A)

### 7.1 The race

`loadSources()` (`:256-287`) calls `PlayerStreamsRepository.shared.clearEpisodeStreams()` and starts its own load on the shared `episodeStreamsState`. `beginSearch()`'s watcher (`:555-560`) has no generation check, so a Sources tab opened during an up-next search wipes the search's results, and the watcher then consumes the source list's emissions as if they were the next episode's.

### 7.2 Fix

1. **Busy guard.** At the top of `loadSources()`: `guard streamsWatcher == nil, phase != .searching else { sourcesBlockedBySearch = true; sourcesLoading = false; print("[UpNext] source list deferred: up-next search in flight"); return }`. Add `@Published private(set) var sourcesBlockedBySearch = false`. `PlayerSourcesColumn` shows "Finding the next episode's source…" in place of "No alternate sources found yet." when it is true. When the search ends (`tearDownSearch`, and the selection paths at `:721` / `:754` that cancel `streamsWatcher`), set it back to false. The column's `.onAppear` does not retry on its own; the viewer re-opens the tab.
2. **Generation guard.** Add `private var searchGeneration = 0`. `beginSearch()` increments it before creating the watcher and captures `let generation = searchGeneration`. The watcher's first line becomes `guard let self, generation == self.searchGeneration, let state = emitted as? StreamsUiState else { return }`. `tearDownSearch()` (`:366-378`) and `cancelSourceLoad()` (`:289-295`) also bump it, so a late emission after either is dropped.
3. **Native panel close.** Add `func noteSourceListClosed() { sourceListClosed() }` and call it from the native host's `onPanelClosed` (§2.4). This gives native the FEAT-49 layer-2 re-preload that mpv gets through `state.$panelOpen` (`:160-173`).
4. **Test seams.** `Hooks` gains `clearStreams: () -> Void` (live: `PlayerStreamsRepository.shared.clearEpisodeStreams()`) and `watchStreams: (@escaping (StreamsUiState) -> Void) -> FlowWatcher?` (live: `FlowWatcherKt.watch(...)`; tests return nil and keep the callback). `loadSources`, `beginSearch` and `tearDownSearch` route through them. [C-15] `loadSources` also calls `PlayerStreamsRepository.shared.loadEpisodeStreams` directly (`:281-287`); route it through the existing `hooks.loadStreams` (same signature), or test (3) touches SharedCore. With `watchStreams` returning nil in tests, "installs a watcher" is asserted on the spy's call count, not on a non-nil watcher; the busy guard therefore keys on `phase == .searching` OR a live watcher, never the watcher alone. A manual episode jump also searches with `phase == .searching`; its busy copy is "Finding the episode's source…" when `immediatePlay` is set. Add `#if DEBUG func forceSearchingForTesting()`, which sets `phase = .searching` and runs the watcher wiring of `beginSearch` without `settings`, so the generation guard is reachable from tests.

## 8. B24: loading overlay (agent C) and BUG-143 (agent B)

### 8.1 Stage enum and producers

`PlayerLoadingStage` (§1.1) is declared by agent B in `Screens/PlaybackModels.swift`, so B's coordinator can publish it in wave 1. C's file holds only views and the mpv reducer.

Native (agent B, coordinator):

| Moment (code) | `loadingStage` |
|---|---|
| `init` / `start()` | `.connecting` |
| poll sees `remux.videoSignaling != nil` (`updatePreparingLabel`, `:503`) | `.preparing(dolbyVision: NativePreparingLabel.isDolbyVision(s))` |
| poll waiting only on subtitles (`:483-486`) | `.subtitles` |
| `beginPlayback` → `phase = .playing` (`:621`) | `.buffering(percent: nil)` (AVPlayer gives no honest percentage) |
| first `timeControlStatus == .playing` (`hasStartedPlaying = true`, `:614`), or the item is ready and the viewer has paused it (status `.paused` after `play()` was issued) [C-9] | `.started` |

Log each transition once: `[Loading] engine=native stage=<stage> t=+1.23s`. The B17 rebuild never moves the stage back.

mpv (agent C, `MPVPlayerView.swift`): `state.startupStage` is `.connecting` until `MPV_EVENT_FILE_LOADED` (`:3506`), and `.buffering(percent:)` from then until the first `MPV_EVENT_PLAYBACK_RESTART` after the resume seek has been issued, or after FILE_LOADED when there is no resume seek. Agent C finds the resume-seek issue site; the first restart before it does not count. At that point `playbackStarted = true` and the stage is `.started`. The percentage comes from a new observed property `cache-buffering-state` (`MPV_FORMAT_INT64`, beside `:904-913`) routed through the existing property cache. As a backstop, the stage becomes `.started` if `positionSec` advances by more than 1 s while not paused. Mid-play rebuffers after `playbackStarted` keep today's small `ProgressView` (`:3910-3914`), gated `state.isBuffering && state.playbackStarted`.

`PlayerScreen` (agent C): the `.deciding` case (`:70-75`) shows the overlay with `.checking`. `MediaProbe` is one blocking call with no phases, so `.checking` is the only stage it has; there is no "Resolving link" stage on the player side (link resolution happens in the picker before the player exists). [C-9] DEBUG: each screen appends every stage it shows to a `debug_loadingHistory` label value (`checking>connecting>preparing>buffering>started`), the leg oracle, because single stages last too briefly for XCUITest polling.

### 8.2 `Screens/Player/PlayerLoadingOverlay.swift` (NEW, agent C)

```swift
struct PlayerLoadingOverlay: View {
    let context: PlaybackContext
    let stage: PlayerLoadingStage
    // ZStack: Color.black; backdrop (context.background) via CachedAsyncImage at opacity 0.28, blur 30, if present;
    // HStack(spacing: 48): poster 260×390 (context.poster, radius 14) if present;
    // VStack(leading): title (Theme.Font.screenTitle, 2 lines), header subtitle (NativeInfoHeader(context:).subtitle),
    // HStack: ProgressView() + status text (Theme.Font.body, textSecondary). Centred, max width 1200.
    // accessibilityIdentifier("player.loadingOverlay"), accessibilityValue(stage.debugName); not focusable.
}
extension PlayerLoadingStage { var statusText: String; var debugName: String }
```

Status copy: `.checking` "Checking the stream…", `.connecting` "Connecting…", `.preparing(false)` "Preparing playback…", `.preparing(true)` "Preparing Dolby Vision…" (the two existing `NativePreparingLabel` strings, reused), `.subtitles` "Loading subtitles…", `.buffering(nil)` "Buffering…", `.buffering(p)` "Buffering \(p) %". `.started` renders nothing. The overlay fades out over 0.25 s. It is shown when `showLoadingOverlay` is on, read once per screen from `PlayerSettingsUiState.showLoadingOverlay` (default true) in the view's `init` into the `@State` initial value, not in `onAppear`, which runs after the first frame and would flash the overlay when the setting is off [C-17]. With it off, each site draws exactly what it draws today.

**No-flash rule.** The overlay is the first thing drawn in each startup phase:

- `PlayerScreen.deciding` draws it from the first frame.
- `NativePlayerScreen` draws it in `.preparing` and keeps it over `AVPlayerContainer` in `.playing` until `loadingStage == .started`. The container mounts underneath, so AVKit's own spinner is covered.
- `MPVPlayerScreen` draws it above the representable until `playbackStarted`.
- A native → mpv fallback before start goes from the native overlay to the mpv overlay with the same poster, already in `ArtworkStore` memory. There is no bare-spinner frame between them.

The old `ProgressView` in `NativePlayerScreen` (`:76-81`) stays only for the setting-off branch. `NativePreparingLabelTests` keep passing because the label type is unchanged.

### 8.3 Settings row (agent C)

`showLoadingOverlay` exists in shared (`PlayerSettingsRepository.kt:36`, setter `setShowLoadingOverlay` `:389`, stored and synced as `show_loading_overlay` in `PlayerSettingsStorage.apple.kt:20`), but tvOS has no row. Add:

- `SettingsViewModel`: `@Published private(set) var showLoadingOverlay = true` (filled where `pauseOverlayEnabled` is, `:181`) and `func setShowLoadingOverlay(_:)` → `PlayerSettingsRepository.shared.setShowLoadingOverlay(enabled:)`.
- `PlayerSettingsPane` (Playback, right after Pause Info Card): `SettingsToggleRow(title: "Loading Screen", subtitle: "Show the poster and what is happening while a video starts", descriptionID: .playerLoadingScreen)`.
- `SettingsDescriptionID.playerLoadingScreen = "player.loadingScreen"` with the description "Shows the poster, the title and what the player is doing (connecting, preparing, buffering) while a video starts, in both players. Off shows a plain spinner. On by default."

Release notes: "Loading Screen (Settings › Playback), on by default; synced with the phone app's Loading overlay setting".

### 8.4 BUG-143 producers and policy (agent B)

**`NetworkPathMonitor`** (§1.1). It starts on first access; the first read happens at the first failure, which is too late for an accurate value. So `NuvioTVApp.init` touches `NetworkPathMonitor.shared` once. That is agent B's only edit outside its files and is listed in its brief.

**mpv (`MPVPlayerView.swift`).** A ring of the last 16 `warn`/`error` log lines, confined to `eventQueue` (plain array, no lock: `drainEvents` is serial), filled in the `MPV_EVENT_LOG_MESSAGE` branch (`:3584`). Store `"\(prefix): \(text)"`, using `msg.pointee.prefix`. On `END_FILE` with `MPV_END_FILE_REASON_ERROR` (`:3573-3582`), copy the ring on `eventQueue` and pass it in the existing main hop to `reportEndFileError(message, logs)`, which calls `PlaybackFailureClassifier.fromMpvLog(logs, endFileError: message, watchdogFired: false)`. [C-8] No per-line main mirror: mpv requests `warn` logs (`:799`), and a bad stream can log a warning per packet, which would put a main-queue hop per line on the BUG-2/3 path. The watchdog (`tickStartWatchdog`, `:3370-3380`, main) instead does `eventQueue.async { let logs = self.logRing; DispatchQueue.main.async { self.reportWatchdog(logs) } }` (strong hops, the C13 shape; never `sync`), stopping its timer first so it fires once; `reportPlaybackFailure`'s existing `failoverReported` guard covers a racing END_FILE. Placeholder clip (`:3404`) → `.placeholder`. Early end (`:3321`) → classify the ring first and use `.endedEarly` only when it shows no network line (a dropped connection also ends a stream early). All of them pass through `applyingPath(_, pathSatisfied: NetworkPathMonitor.shared.isSatisfied)`, and `reportPlaybackFailure` gains `kind:` and `httpStatus:` and prints them: `[Failover] mpv failure: … kind=network http=-`.

**Native (coordinator).** `failureKind` is set wherever `phase = .failed(...)` is set:

- `failIfPreplayback(stage)` (`:1286-1301`): from `remux.lastErrorCode` → `fromAVError`. With no code, `"no segments produced"` and `"no segment map"` → `.noMedia`, and anything else → `.unknown`.
- `handlePrePlaybackItemFailure` giving up (`:647-650`): `fromNSError(item.error, origin: .loopback)` [C-7]. AVPlayer errors here are about the loopback origin, so a CoreMedia decode/format code (`CoreMediaErrorDomain`, `AVFoundationErrorDomain` decode failures, -12927 and similar) → `.decode`, and an `NSURLErrorDomain` code → `.noMedia` (our own server failed to deliver, and the remote host was reachable because the remux opened it).
- `fallbackMidPlay` "stalled ~30s with no remux progress" → `.network`; "item failed mid-play" → `fromNSError(item.error, origin: .loopback)`; "remux failed mid-play: …" → `fromAVError(remux.lastErrorCode)`; "late subtitle rebuild failed" → `.local` [C-3].

These only reach `PlaybackFailure` when there is no mpv fallback (forced native), but they must be right for that path.

**`RemuxSession.fail(_:)`** gains a code. `avformat_open_input` (`:326`), `avformat_find_stream_info` (`:330`) and the `av_read_frame` error exit in the copy loop store the returned AVERROR in `_lastErrorCode` before `fail`. `lastErrorCode` is read under `lock`.

**Classifier rules (pure, all unit-tested):**

| Evidence | Kind |
|---|---|
| mpv log `HTTP error (\d{3})` or `Server returned (\d{3})`, or FFmpeg's `Server returned 4XX Client Error` / `5XX Server Error` / `400 Bad Request` / `401 Unauthorized` / `403 Forbidden` / `404 Not Found` | `.http` (status parsed, or 400/500 for the XX forms) |
| AVERROR `HTTP_BAD_REQUEST`, `HTTP_UNAUTHORIZED`, `HTTP_FORBIDDEN`, `HTTP_NOT_FOUND`, `HTTP_OTHER_4XX`, `HTTP_SERVER_ERROR` (FFERRTAG values, computed in Swift from the four-char tags, since the macros don't import) | `.http` |
| log `Connection refused`, `Connection timed out`, `Operation timed out`, `Failed to resolve hostname`, `Network is unreachable`, `No route to host`, `Host is down`, `Connection reset by peer`, `TLS`/`SSL`/`gnutls` handshake errors; AVERROR(`ECONNREFUSED` 61, `ETIMEDOUT` 60, `ENETUNREACH` 51, `EHOSTUNREACH` 65, `ECONNRESET` 54, `EHOSTDOWN` 64, `EIO` 5 at open); `NSURLErrorDomain` −1001, −1003, −1004, −1005, −1009, −1200…−1206 with `origin: .remote` (with `.loopback` any `NSURLErrorDomain` code → `.noMedia`, [C-7]) | `.network` |
| mpv watchdog fired with no HTTP line in the ring | `.network` |
| log `Invalid data found when processing input`, `Failed to recognize file format`, `could not find codec`, `No video or audio streams selected`; AVERROR_INVALIDDATA, `AVERROR_DECODER_NOT_FOUND`, `AVERROR_DEMUXER_NOT_FOUND`; CoreMedia decode/format errors | `.decode` |
| AVERROR_EXIT (our interrupt), or a failure after `stop()` | `.cancelled` |
| `pathSatisfied == false` | `.offline` (overrides everything) |
| nothing matched | `.unknown` |

TLS counts as network on purpose: on a TV the usual causes are the viewer's network (captive portal, intercepting router, clock skew), not the link. `EIO` at open counts as network because FFmpeg's TCP layer maps a resolve failure to `EIO`. Anywhere past the open, `EIO` stays `.unknown`.

**Policy and call sites.**

- `PlaybackFailoverPolicy.shouldReject` (`PlaybackModels.swift:170-172`) as in §1.1.
- `StreamPickerView.handlePlaybackFailure` (`:1055-1076`): the existing `if shouldReject` block also skips `DirectDebridPlaybackResolver.invalidate` on a non-remembered kind (the link is fine and its 15-minute resolve is still good). New log line when skipped: `[Failover] reject key=… kind=network transient=1 skipped`. The `[Failover] failure …` line gains `kind=`.
- `FirstPlayAutoPlay.beginResolve` (`:280-299`): the resolve timeout becomes `rejectsLink: false` (log `transient=1 skipped`), and the thrown-error branch uses `PlaybackFailureClassifier.fromNSError(error, origin: .remote).kind.remembersLink`, so a `URLError` network code no longer rejects. [C-6] That alone misses the main offline case: every debrid provider catches its own exceptions and returns `DirectDebridResolveResult.Error()` (`shared/…/debrid/DebridProviderApis.kt:263-266`, `:528`), which `outcome(from:)` maps to `rejectsLink: true` (`:540-542`), so an offline TV still blacklists every cached link for 8 h. `Deps` gains `networkSatisfied: () -> Bool` (live: `NetworkPathMonitor.shared.isSatisfied`), and `finishResolve` remembers only when `rejectsLink && deps.networkSatisfied()`, logging `transient=1 offline=1 skipped` otherwise. Telling a network `Error()` from a provider refusal while online needs a Kotlin change (a reason on `Error`); that is a follow-up, not P4.
- The walk itself (`tryNext`, `response(for:)`) is untouched: a transient failure still moves to the next candidate.

## 9. Strings

Every new user-visible string, English. All `String(localized:)` / `LocalizedStringResource`. At the end of wave 2, agent C runs `scripts/populate-localizable-xcstrings.py` and then `merge-translations-into-xcstrings.py` to fill de/es/fr/it/vi.

| Key (English) | Where |
|---|---|
| "Episodes", "Sources" | menu items (already in the catalog from `MPVPlaybackTab`) |
| "Playback Speed" | reused |
| "Finding the next episode's source…" | `PlayerSourcesColumn` busy state (BUG-129) |
| "Checking the stream…", "Connecting…", "Loading subtitles…", "Buffering…", "Buffering %lld %%" | `PlayerLoadingOverlay` |
| "Preparing playback…", "Preparing Dolby Vision…" | reused (`NativePreparingLabel`) |
| "Loading Screen", "Show the poster and what is happening while a video starts" | Settings row |
| description `player.loadingScreen` | `SettingsDescriptions` |
| "Show the title, source and time remaining after a short pause" | Pause Info Card subtitle (was "…(mpv player)") |
| "Shows the title, source and time left after you have been paused for a while. Works in both players. On by default." | `player.pauseInfoCard` description (changed) |
| Subtitle Position description gains " (mpv player)" | `SettingsDescriptions` (agent C, find the row; there is no `subtitles.position` description today, so it may be a subtitle on the row itself) |
| Outline description (`subtitles.outline`, `SettingsDescriptions.swift:368`): outline colour and width are mpv-only, the on/off works in both; add "Colour and width apply in the mpv player." if those rows exist [C-21] | `SettingsDescriptions` |
| "Harvest Screenshot Path (A/B)", "Software for SDR", "Video Renderer", description `dev.harvestScreenshotPath` | Developer row (P3-F9) [C-12] |
| "Chapter %lld" | reused (`PlayerChapters.displayTitle`) |

The new Settings row needs the `SettingsDescriptionID` case and its description (§8.3). The changed descriptions keep their IDs. Release notes name **Loading Screen (on by default)** and say that the Pause Info Card now works on native.

## 10. Tests

### 10.1 Unit (`iosApp/NuvioTVTests/`)

- `NativeSubtitleStyleTests` (B): the defaults give foreground `[1,1,1,1]`, no character-background key (alpha 0), edge Uniform, no bold key and no size key. Outline off with a 0x80000000 background gives edge None and a character background of `[0.502, 0, 0, 0]` (± 0.002). 36 sp → 200, 6 sp → 65 (clamp), 60 sp → 222 (clamp), 18 sp → no key. Bold on → `kCFBooleanTrue`. `rules` returns one rule.
- `PlaybackFailureClassifierTests` (B): every row of the §8.4 table, plus these. Mixed ring (a `Connection refused` line, then `HTTP error 404`) → `.http` 404, because HTTP evidence wins. The `XX` forms → 400/500. The offline override turns `.http` into `.offline`. `remembersLink` truth table. `NSError` nested in `NSUnderlyingErrorKey` is found.
- `PlaybackFailoverPolicyTests` (B), additions: `shouldReject` false for `.network`, `.offline` and `.cancelled` at 0 s played; true for `.http`, `.decode` and `.unknown` under 300 s; false for every kind at 300 s.
- `FirstPlayAutoPlayControllerTests` (B): **change** `testResolveDeadlineMovesOnAndIgnoresTheLateAnswer` (`:204-213`). The timed-out "SLOW" link is now NOT in `rejectedByTitle`, and the walk still moves on. New `testThrownNetworkErrorIsNotRemembered` (a resolver that throws `URLError(.notConnectedToInternet)`) and `testOfflineResolveErrorIsNotRemembered` (`.failed(rejectsLink: true)` with `networkSatisfied = { false }` → not in `rejectedByTitle`, the walk moves on) [C-6].
- `NativeChapterMarkersTests` (B): seconds math (time base 1/1000 with start 90000 and origin 0 → 90.0; origin 1.0 → 89.0; origin 0.083 → 89.917) [C-4]. `groups` builds one marker per chapter, each time range ending at the next start and the last at the duration. An empty title → "Chapter 2". An empty list → `[]`.
- `LateSubtitlePlanTests` (B): `merge` continues indices from the max, dedupes "English" against an existing "English" → "English 2", and keeps existing entries untouched. `decide` returns `.autoRebuild` only with untouched + nothing showing + a late DEFAULT + no prior rebuild, and `.publishOnly` for each single condition broken.
- `LocalHLSServerSubtitleTests` (B, no listener needed): `renderedPlaylist(named: "master.m3u8")` before and after `setSubtitles` → the new `EXT-X-MEDIA` line appears with the new index and name, and existing lines are byte-identical. `renderedPlaylist(named: "sub-<new>.m3u8")` resolves. [C-1][C-2] `setStartOffset(312.5)` → the master carries `#EXT-X-START:TIME-OFFSET=312.500,PRECISE=YES` right after `#EXT-X-VERSION`; `setStartOffset(nil)` → byte-identical to the pre-change render. With `selectedAudio` returning the second track, that track's `EXT-X-MEDIA` line has `DEFAULT=YES` and the first has `DEFAULT=NO`; with `selectedAudio` nil the stored flags are used.
- `NextEpisodeEngineTests` (A), BUG-129: (1) `forceSearchingForTesting()`, then `loadSources()` → `sourcesBlockedBySearch == true`, `sourcesLoading == false`, and the `clearStreams` spy count stays 0. (2) Generation: capture the search callback from the `watchStreams` spy, call `tearDownSearch` via `cancel()`, then invoke the old callback with a non-empty state → `phase` stays `.hidden` and no selection happens. (3) Without a search, `loadSources()` calls `clearStreams` once and installs a watcher. (4) `noteSourceListClosed()` with preload on clears `preloaded`, and the next `onProgress` past the preload lead re-issues `loadStreams` once (spy count 2): `sourceListClosed` itself only invalidates, the re-issue happens on the next tick [C-15].
- `NativePauseCardRuleTests` (A): hidden before 1.5 s; visible at 1.5 s with the bar known hidden; hidden while the bar is unknown (no callback yet this pause) [C-5], visible, the panel is open, the setting is off, a rebuild is running, or the phase is not playing.
- `NativeNowPlayingMetadataTests` (B): identifiers present; the subtitle is "S1 · E4 · Name" for a series context and the stream label for a movie; description omitted when the synopsis is nil; artwork item `dataType` is JPEG.
- `PlayerLoadingStageTests` (C): `statusText` for every case; the mpv reducer (FILE_LOADED → buffering; a restart before the resume seek does not start; the restart after it does; the position-advance backstop).
- Existing suites stay green, `NativePreparingLabelTests` and `ChapterListParsingTests` included.

### 10.2 UI legs (`iosApp/NuvioTVUITests/`)

**Native rig.** `-debug.remuxSmokeURL` is headless: it drives a `NativePlaybackCoordinator` with no screen (`RemuxSmokeTest.swift:6-14`). It is the rig for B's console checks (chapters, late subtitles, style log), but it cannot run panel legs. Screen legs launch the real `PlayerScreen` through `MPVSmokeModifier` (`MPVSmokeTest.swift:18-60`) with a new DEBUG knob `-debug.mpvSmokeEngine native|mpv`, which sets `ctx.forcedEngine` (agent A adds it). A forced native engine skips the probe and the silent fallback (`PlayerScreen.swift:41-43`), so a leg cannot quietly pass on mpv. New file `NativePlayerParityUITests.swift`, gated on `PLAYER_NATIVE_PROBE=1` and `PLAYER_SMOKE_URL`, launching `-debug.mpvSmokeURL <url> -player.nativeDolbyVision YES -debug.mpvSmokeEngine native -debug.mpvSmokeStartOver YES`, and waiting for `player.native`. Agent A adds a DEBUG probe label `debug_nativeProbe` in `NativePlayerScreen` (top-trailing, 1 pt, like `SeekProbeLabel`): `pos= speed= paused= bar= card= stage= chapters= subs= late=`.

| Leg | Owner | Drives | Oracle | Proves |
|---|---|---|---|---|
| `testNativePlaybackTabSpeed` | A | Down → panel; Right ×3 → `player.panel.tab.playback` selected; Down, Right ×2 to `player.panel.speed.1.5`, Select; Menu | probe `speed=1.5` (the probe reads `player.rate` while playing, not `selectedSpeed`); reopen → `player.panel.speed.1.5` has `accessibilityValue == "selected"` [C-16] | A8 tab + selectSpeed sync |
| `testNativeSourcesColumnPresent` | A | open Playback tab | `Sources` caption and "No alternate sources found yet." exist | columns wired, `canSwitchStreams` |
| `testNativeMenuItemOpensSources` | A | Select to raise the bar; navigate to the "Sources" menu item (XCUIRemote, label match); Select | `player.panel` exists with the Playback tab selected | `transportBarCustomMenuItems` → panel |
| `testNativePauseCard` | A | `.playPause`; wait up to 12 s | probe `paused=1`; `card=1` never while `bar≠0`; if `bar=0` is seen, `card=1` must follow within 2 s and one press → `card=0`; if `bar=0` never appears in 12 s, `XCTSkip("sim bar never hides while paused")` rather than pass [C-19] | B16 rule; records the sim's bar behaviour |
| `testMpvPlaybackTabUnchanged` | A | mpv harness (`PlayerTransportUITests.launch`), open Playback | the speed, `player.panel.diagnostics` and Audio Delay rows exist; pick 1.25 → `player.panel.speed.1.25` reads `selected` | regression only (it also passes before the change; it guards the extraction) |
| `testNativeChaptersTab` | B (run in B's step 8) | `PLAYER_SMOKE_CHAPTERS_URL`; Down; Right to Chapters; Select row 3 | `player.panel.chapter.2` exists; probe `chapters=5`; probe `pos` within ±2 s of 240 (the fixture's chapter 3; an XCUITest cannot read the console) [C-10] | A6-native |
| `testNativeLateSubtitleLazyPick` | B (run in B's step 8) | DEBUG `-debug.nativeLateSubtitleURL http://127.0.0.1:8000/test.srt -debug.nativeLateSubtitleDelaySec 6` plus `-debug.nativeSubsGateSec 0`; open Subtitles; pick the new row | probe `late=published` and the row exists before the pick; after it the row's value is "selected" within 4 s; probe `late=rebuilt`, `pos` within 3 s of the pre-pick position | B17 lazy path. [C-14] The knob keeps its file in a separate `debugLateSubtitles` list merged in `checkLateSubtitles`: the add-on watcher reassigns `addonSubtitles` on every emission, empty ones included (`:245-251`), and would erase an injected entry. If the fixture profile prefers a subtitle language and the probe shows `late=rebuilt` before the pick, the leg asserts the auto path instead and says so |
| `testNativeLoadingOverlay` | C | launch (forced native) | `player.loadingOverlay` exists within 1 s of the cover appearing; after `pos > 1` it is gone and `debug_loadingHistory` reads `connecting>…>buffering>started` with no `checking` (forced native skips the probe, `PlayerScreen.swift:41-43`) [C-9] | B24 native |
| `testMpvLoadingOverlay` | C | `-player.nativeDolbyVision YES`, no forced engine (the probe runs and routes the SDR fixture to mpv) | history `checking>connecting>buffering…>started`, overlay gone after `pos > 1` | B24 mpv + router spinner replaced |
| `testLoadingOverlayOff` | C | the setting is profile-scoped, so the leg toggles Settings › Playback › Loading Screen off, runs the smoke, and turns it back on in `tearDown` (FA87 is the shared fixture) [C-18] | no `player.loadingOverlay`; the spinner path runs | setting wired |

`test.srt` is a new 20-cue fixture under `build/smoke/` beside `test-long.mkv` (agent B creates it, plain ASCII). The P1/P2/P3 legs are re-run unchanged at the end of each wave.

## 11. Code-vs-plan findings

1. **`customInfoViewControllers` is the wrong surface on tvOS 26.** It renders as pills under the seek bar (`NativePlayerScreen.swift:19-22`, `:325-326`). The Playback tab goes into the existing app panel as `extraTab` (D1). `speeds` and `transportBarCustomMenuItems` stay as the plan says.
2. **The panel already exists on native.** The plan lists `Player/PlayerPanelHost.swift` as if it were the AVPVC configuration. It is the app-drawn panel host (`NativePlayerHostController`, `PlayerPanelHostController`) with Info · Subtitles · Audio, and the plan's research row ("App top panel … Info · Subtitles · Audio only", research §2.3) is still right about the missing Playback tab.
3. **`externalMetadata` is an `AVPlayerItem` property**, so it belongs with item creation in the coordinator, not with the view controller (D6).
4. **"Coordinator:156-186 pattern" no longer exists as an item rebuild.** Those lines are now the B3 delay comment block. The delay works by reselect, the audio switch by renditions, and the only `replaceCurrentItem` is the pre-play signaling retry (`:632-671`). B17's rebuild is the first mid-play item swap in the codebase (§5.1).
5. **The subtitle gate is 8 s from poll start, not "settles or 3 s"** (`:469`). This spec moves to first segment + 3 s, capped at 8 s (D12).
6. **"Addon subtitles arriving after the master are lost"** is right, but they are not silently lost: the watcher logs "(after master, too late this session)" (`:257`).
7. **`SubtitleStyleState` colours are `SubtitleColor` ARGB `Int64`s**, and three of its fields (outline colour, outline width, bottom offset) have no `AVTextStyleRule` equivalent (§3.4). The plan's "size as a fraction of the display" is `RelativeFontSize` relative to the system default here, which is what keeps the 18 sp default at the system size.
8. **The plan lists `Screens/SubtitleVTT.swift` for the style helper.** The helper is a separate pure file (`NativeSubtitleStyle.swift`) with its own test. `SubtitleVTT` stays a VTT converter.
9. **A third startup spinner exists:** `PlayerScreen`'s `.deciding` case (`:70-75`) during the MediaProbe. Without covering it, B24's "no flash of the old spinner" cannot hold (D14).
10. **`PlaybackContext` has no logo** (D15).
11. **mpv's pause card does not appear at 1.5 s.** It appears when the mpv bar hides, which is 5 s after the last input when paused with the card on (`TransportHideRule.delay`, `PlayerTransportBar.swift:166-168`), with a 0.25 s fade delay (`:3930`). The native rule is the plan's 1.5 s plus bar hidden. The engines will differ in timing, which matches the plan's wording.
12. **`showLoadingOverlay` is stored and synced but has no tvOS row** (§8.3), and `pauseOverlayEnabled`'s row says "(mpv player)" (`PlayerSettingsPane.swift:50`, `SettingsDescriptions.swift:328`).
13. **BUG-143 has a second path the master plan did not name:** the stream picker's first-play controller rejects resolve timeouts and thrown resolve errors (`FirstPlayAutoPlay.swift:287`, `:297`), so a slow debrid API on a bad evening blacklists links for 8 h before a player ever opens. Its existing test asserts that behaviour (`FirstPlayAutoPlayControllerTests.swift:204-213`) and changes with this batch.
14. **mpv END_FILE errors carry only `mpv_error_string`** ("loading failed"), so the classifier needs the log ring (§8.4). The remux's `fail(stage)` drops the AVERROR code, so `lastErrorCode` is added.
15. **The native engine has no FEAT-49 layer-2 re-preload**: `sourceListClosed` is wired only through mpv's `panelOpen` (`NextEpisodeAutoPlay.swift:160-173`). It becomes live on native with the Sources column (§7.2 item 3).
16. **Not in this spec, carried from P3:** P3-F5 (remux segment writes exceeding the daily disk-write allowance) and P3-F6 (TLS read CPU in the remux) are native-engine follow-ups the P3 record assigns to "P4". They change `RemuxSession`'s write and pacing paths, which B17 and A6 also touch, so they are better as a separate small batch after P4 merges. Agent B must not start them.

## P3-F9: harvest RSS growth (agent C, wave 2) [C-12]

Source: `docs/research/player-p4-rss-retention-2026-10-15.md` (about 3–5 MB of RSS per `screenshot-raw` capture on the Apple TV, best reading: mpv's VO screenshot path through libplacebo/MoltenVK; the Swift half is bounded). Its §3 steps 0, 1(i) and 2 and its §4 size knob are P4 work; step 3 (serve Harvest Only from the thumbnailer) is not. All edits are in `MPVPlayerView.swift` (C owns it in wave 2), plus one Developer row.

1. **Instrumentation (DEBUG).** Add `rss=\(ProcessMemory.footprintMB())` to the `[Harvest] stored` line in `harvestCaptured`'s `publish` (`:1981`). Log the VO once per file: read `getString("current-vo")` on `eventQueue` in the first `logStartupStatsIfNeeded` read (`:1801-1811`) and print `[MPVStats] vo=gpu|gpu-next` once.
2. **The fix candidate, option (i): `screenshot-sw=yes` for SDR only.** Before each real capture, on `eventQueue` inside `captureHarvestFrame` (`:1925`, after the synthetic and simulator early returns, so the simulator gate is untouched), read `video-params/gamma` and `video-params/colormatrix`; when the switch is on, gamma is known and is neither `pq` nor `hlg`, and colormatrix is not `dolbyvision`, `setMpvString("screenshot-sw", "yes")`; otherwise `"no"` (unknown gamma counts as HDR: keep the VO path). Write only on change (cache the last value on the controller, `eventQueue`-confined). Log `[Harvest] path=sw|vo gamma=…` once per change.
3. **The A/B switch.** UserDefaults key `debug.harvestScreenshotSW`, read in every build (this is the shipping fix, not a DEBUG knob) in `viewDidLoad` beside `debug.harvestSynthetic` (`:502`) and stored on the controller. **Default: on** (unset = on) for SDR content. Developer row "Harvest Screenshot Path (A/B)" in `DeveloperSettingsPane.swift` after Thumbnail Harvest: Software for SDR (default) / Video Renderer. New `SettingsDescriptionID.devHarvestScreenshotPath = "dev.harvestScreenshotPath"`, description "An A/B switch for how the mpv player copies a frame for the seek preview. Software for SDR copies it without the video renderer, which uses less memory over a long playback. Video Renderer is the old path. Applies to the next playback.", added to the "Applies to the next playback." case list (`SettingsDescriptions.swift:425`); `SettingsDescriptionsTests` covers it.
4. **Swift hygiene (§3 step 2).** Scale inside `screenshotRaw`'s `read` closure, straight from the node's `ba.data` (wrap it as `Data(bytesNoCopy:count:deallocator: .none)` or `withUnsafeBytes`, used only inside the closure, before `mpv_free_node_contents`), so only the ~171 KB thumbnail leaves `eventQueue`; wrap capture + scale in `autoreleasepool { }`. `harvestCaptured` then receives the scaled image (or `MPVRawFrame` keeps a `thumb` field), and the utility block only encodes and inserts. This is hygiene, not the fix: say so in the commit message.
5. **Synthetic size knob (DEBUG).** `debug.harvestSyntheticSize` = `WxH` (e.g. `2560x1070`), parsed in `viewDidLoad`, used by `syntheticHarvestFrame` (`:1959-1965`) instead of 640×360. Simulator oracle: `-debug.harvestSynthetic YES -debug.harvestSyntheticSize 2560x1070 -debug.harvestIntervalSec 5`, 40 captures; `rss=` on `[Harvest] stored` grows < 10 MB from capture 3 to 40.
6. **Regression legs that must stay green:** `testHarvestPlumbingSynthetic`, `testDecodeOffByMode`, the P2 harvest legs.

Device oracle (step 7 of §13): **< 10 MB RSS growth over 20 captures from capture 3** with the switch on, on the SDR file.

## 12. Agent briefs

**Common.** Clone `~/Claude/Projects/NuvioMobile-player-p4`, branch `claude/player-p4` (it exists; do not create another, because `git checkout -b` refuses over the MPVKit symlink). MPVKit is a symlink over the gitlink: stage by explicit paths, never `git add -A`, and ignore `git status` errors on MPVKit. **One build at a time across all agents. An agent builds only when the orchestrator says the build lock is free.** A build is already running in the clone as this spec is written. Commands run from `~/Claude/Projects/NuvioMobile-player-p4/iosApp`, with the Bash sandbox OFF for `xcodebuild test`. Simulator `FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E`.

- Build: `xcodebuild -project iosApp.xcodeproj -scheme NuvioTV -configuration Debug -destination 'platform=tvOS Simulator,id=FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E' -derivedDataPath build/DerivedData build` (Release: `-configuration Release`).
- Unit: `xcodebuild test -project iosApp.xcodeproj -scheme NuvioTVTests -destination '<same>' -derivedDataPath build/DerivedData -collect-test-diagnostics never -only-testing:NuvioTVTests/<Class>`.
- Smoke server: `cd build/smoke && python3 range_server.py 8000 .` (background). [C-10] This clone's `build/smoke` has `test-long.mkv` and `range_server.py` but NOT `test-long-chapters.mkv`, and the old copy source does not exist any more. Rebuild it with the P2 recipe (`docs/research/player-p2-spec-store.md:344`): an `;FFMETADATA1` file with Opening 0, Act One 90, Act Two 240, Act Three 390, Credits 540 (`TIMEBASE=1/1000`, last ends 600000), then `~/bin/ffmpeg -i test-long.mkv -i chapters.txt -map 0 -map_metadata 1 -map_chapters 1 -c copy test-long-chapters.mkv`; check with `~/bin/ffprobe -v error -show_chapters -of compact test-long-chapters.mkv` (5 lines).
- Strings scripts live at the submodule root: `python3 ../scripts/populate-localizable-xcstrings.py` then `python3 ../scripts/merge-translations-into-xcstrings.py` from `iosApp/` [C-10].
- UI: `TEST_RUNNER_PLAYER_NATIVE_PROBE=1 TEST_RUNNER_PLAYER_BAR_PROBE=1 TEST_RUNNER_PLAYER_SMOKE_URL=http://127.0.0.1:8000/test-long.mkv TEST_RUNNER_PLAYER_SMOKE_CHAPTERS_URL=http://127.0.0.1:8000/test-long-chapters.mkv xcodebuild test -project iosApp.xcodeproj -scheme NuvioTVUITests -destination '<same>' -derivedDataPath build/DerivedDataUITests -collect-test-diagnostics never -only-testing:NuvioTVUITests/<Class>/<test>`. The simulator wedges after about six UI runs: `xcrun simctl shutdown` then `boot` the UDID.
- Commits: stage explicit paths only, and commit only while holding the orchestrator's lock (A and B share one index while they run in parallel) [C-11].
- Report: commits (hash + one line), gates with counts, the final probe line of every leg, the console lines named in §13 from one smoke run, deviations from this spec with the reason, and open questions.

**Agent B (wave 1, first; commit prefix `player P4 B:`).** Owns: `Screens/MPVPlayerView.swift` (failure producers, log ring and the extraction only), new `Screens/Player/PauseInfoCard.swift`, `Screens/NativePlaybackCoordinator.swift`, `Screens/RemuxSession.swift`, `Screens/LocalHLSServer.swift`, `Screens/Player/NativePlayerPanelAdapter.swift`, `Screens/Player/PlayerTopPanelModel.swift` (comment), `Screens/PlaybackModels.swift`, `Screens/RejectedStreamLinks.swift` (log only, if needed), `Screens/StreamPickerView.swift` (`handlePlaybackFailure` only), `Screens/FirstPlayAutoPlay.swift` (`beginResolve` only), `NuvioTVApp.swift` (one line: touch `NetworkPathMonitor.shared`), and the new `NativeSubtitleStyle.swift`, `NativeNowPlayingMetadata.swift`, `NativeChapterMarkers.swift`, `LateSubtitlePlan.swift`, `PlaybackFailureClassifier.swift`, `NetworkPathMonitor.swift` under `Screens/Player/`. Also the B tests of §10.1, the legs `testNativeChaptersTab` and `testNativeLateSubtitleLazyPick`, the `test.srt` fixture, and the DEBUG knobs `-debug.nativeSubsGateSec`, `-debug.nativeLateSubtitleURL` and `-debug.nativeLateSubtitleDelaySec`. Must not touch `NativePlayerScreen.swift`, `PlayerPanelHost.swift`, `NextEpisodeAutoPlay.swift` or the Settings files.
Order: (0) `PauseInfoCard` extraction, pure move, build; (1) `PlayerLoadingStage` + `PlaybackFailureKind` + `PlaybackFailure` fields in `PlaybackModels.swift`, plus the coordinator's `loadingStage` transitions and `durationSec`, build (this unblocks A and C); (2) `NativeSubtitleStyle` + tests + `decorate(_:)` + the style on every item; (3) `NativeNowPlayingMetadata` + artwork task + tests; (4) chapters: remux read, the timeline check on the headless rig, markers + tests, coordinator + adapter; (5) B17: server `setSubtitles` + tests, `LateSubtitlePlan` + tests, gate change, coordinator late path + rebuild, adapter rows, DEBUG knobs, leg; (6) BUG-143: monitor, classifier + tests, remux `lastErrorCode`, mpv ring + producers, coordinator `failureKind`, policy, picker + first-play call sites, the changed and new controller tests; (7) the whole NuvioTVTests scheme, Debug + Release, the P1/P2/P3 transport legs (`PlayerTransportUITests`) re-run; (8) after A's step 6 has landed: append its two legs to `NativePlayerParityUITests.swift` (A creates the file) and run them. One commit per step. [C-11] B's step 5 must also prove the rebuild start position on the headless rig before wiring the panel rows ([C-1]); if neither `EXT-X-START` nor a pre-ready seek keeps the new item off t=0, stop and report.

**Agent A (wave 1, after B's steps 0–1 have landed, then in parallel with B under the build/commit lock; commit prefix `player P4 A:`).** Owns: `Screens/NativePlayerScreen.swift`, `Screens/Player/PlayerPanelHost.swift`, `Screens/Player/MPVPlaybackTab.swift`, new `Screens/Player/PlayerPlaybackColumns.swift`, `Screens/Player/NativePlaybackTab.swift`, `Screens/Player/NativePauseCardRule.swift`, `Screens/NextEpisodeAutoPlay.swift`, `Screens/MPVSmokeTest.swift` (`-debug.mpvSmokeEngine`), `NuvioTVTests/NextEpisodeEngineTests.swift`, `NativePauseCardRuleTests`, new `NuvioTVUITests/NativePlayerParityUITests.swift` (A's legs, and B's two legs added to the same file by B afterwards; if A creates it first, B appends). It reads the coordinator API from B (`durationSec`, `failureKind`, `isPaused`, `lastPositionSec`) and does not edit B's files. **It must not touch `MPVPlayerView.swift`.**
Order: (1) extract the columns, refactor `MPVPlaybackTab`, build, run `testMpvPlaybackTabUnchanged`; (2) BUG-129 (seams, guards, `noteSourceListClosed`) + engine tests; (3) host: `onOpenPanel(tab:column:)`, delegate, `onAnyPress`, `openPanel`; (4) container: speeds, menu items, `NativePlaybackTab`, `NativeSpeedModel`, `kind:` on the failure; (5) pause card rule + tests + screen wiring + logs; (6) `debug_nativeProbe`, `-debug.mpvSmokeEngine`, A's legs; (7) the whole unit scheme, Debug + Release, mpv regression legs.

**Agent C (wave 2, after A and B; commit prefix `player P4 C:`).** Owns: new `Screens/Player/PlayerLoadingOverlay.swift`, `Screens/PlayerScreen.swift` (`.deciding` only), `Screens/NativePlayerScreen.swift` (`.preparing` / overlay layering only), `Screens/MPVPlayerView.swift` (startup stage, `cache-buffering-state`, the spinner gate at `:3910`, the overlay layer in `MPVPlayerScreen`), `Screens/Settings/PlayerSettingsPane.swift`, `Screens/Settings/SettingsDescriptions.swift`, `Screens/SettingsViewModel.swift`, `Localizable.xcstrings` (the populate + merge scripts at the end), `PlayerLoadingStageTests`, the three overlay legs. It also takes P3-F9 if the note prescribes a change in `MPVPlayerView.swift` or `SeekPreviewStore.swift` (see the placeholder).
Order: (1) overlay view + stage text + tests; (2) native layering + `PlayerScreen.deciding`; (3) mpv stage producer + overlay + spinner gate; (4) Settings row, copy changes and descriptions; (5) the legs; (6) P3-F9 per the section below (it now owns `Screens/Settings/DeveloperSettingsPane.swift` too) [C-12]; (7) the strings scripts, the whole unit scheme, Debug + Release, all P4 legs plus the P1/P2/P3 regression legs, `testHarvestPlumbingSynthetic` and `testDecodeOffByMode` included.

After wave 2: W3 review rounds (read-only Opus until Codex's 10-29 reset), then the device pass (§13), then merge on Christian's go. Not cut alone (one rc after P5, per the 10-06 release model, unless the master plan's checkpoint rule says otherwise).

## 13. Device pass (Living Room Apple TV, **Test 2 profile**, console attached via the rig)

A dev build on `com.youngchris29.NuvioTV`. The rig (`docs/device-rig-2026-10-15.md`) drives presses, screenshots and `console.sh`. Note that the free-team profile is good for 7 days. Every step names its console oracle.

1. **Playback tab + speeds + metadata (DV title on native).** Open a DV P8.1 title, which routes native (`[PlayerRouter] native`). Oracle: `[NativePlayer] avpvc speeds=0.5,0.75,1,1.25,1.5,1.75,2 menu=Episodes,Sources delegate=1` (movie: `menu=Sources`). Raise the bar: screenshot shows the title above the scrubber and the Sources item in the bar. Open the speed pill: 0.5×…2×. Swipe down: the Info · Subtitles · Audio · Playback tabs. Playback tab: pick 1.25× → `[NativePlayer] speed → 1.25 (tab)`, and the system pill now shows 1.25×. Pick the Sources menu item → the panel opens on Playback with focus in Sources. For a series, the Episodes column lists the season and its current row has the play glyph. `[NativePlayer] artwork attached (N KB)` within 5 s of start. The Info area shows the synopsis.
2. **Subtitle style.** In Settings › Subtitles set the text to yellow, the size to 24 sp and bold on. Play a native title with an add-on subtitle. Oracle: `[Subs] style rule fg=#FFFFFF00 bg=#00000000 edge=uniform bold=1 size=133%`. Screenshot: yellow, larger, bold cues. Reset the style afterwards.
3. **Pause card.** Pause; leave the remote. Oracle: `[NativePlayer] bar visible=0`, then `[NativePlayer] pause card shown after 1.5s` (or after the bar hides, whichever is later). Any press → `pause card hidden reason=press`. If `bar visible=0` never appears while paused, the card is dropped for native per §4.2 (`NativePauseCardRule.supported = false`, copy keeps "(mpv player)") and Christian decides on the `contentOverlayView` follow-up [C-5]. Also confirm no card ever draws while the bar is up.
4. **Late add-on subtitles.** Use a title whose add-on subtitle fetch is slow (OpenSubtitles plus a second subtitle add-on), or set `-debug.nativeSubsGateSec 0` from Developer launch args, which forces every add-on subtitle late. Oracle: `[NativePlayer] subs gate lapsed … gate=0.0s`, then `[Subs] late renditions +N`, then either `[Subs] late mode=auto` + `[Subs] late rebuild reason=auto at …s took=…s` (Test 2 has a preferred subtitle language set) or `mode=lazy`, with the rebuild on pick. Watch the swap: one short freeze (record `took=`), the same position, the same audio, the speed kept. The subtitle shows in the same session. [C-1][C-2] Run it once on a resumed title (resume > 5 min) after switching audio to a second track: the console shows no `[Remux] reposition` and no `audio selection → stream` line during the rebuild, and the first media request after the swap is the playhead's segment.
5. **Chapters.** An MKV with chapters on native. Oracle: `[Chapters] native n=… first=…`. Swipe down: a Chapters tab. Pick chapter 3: the position lands on its start. The system bar shows chapter marks (screenshot; record what tvOS 26 draws).
6. **Loading overlay.** Cold-open a native title and an mpv title. Oracle: `[Loading] engine=native stage=connecting … preparing … buffering … started` and `[Loading] engine=mpv stage=connecting … buffering(…) … started`. A screenshot burst (`rec.sh`) of the first 3 s shows poster + title + status from the first frame, with no bare spinner frame. A forced native → mpv fallback (a P7 FEL file with the FEL setting on) keeps the overlay across the hand-off. Toggle Settings › Playback › Loading Screen off → the plain spinner returns.
7. **Harvest RSS (P3-F9) [C-12].** Same Dune 2560×1070 HEVC 10-bit SDR file on mpv (native off), Seek Preview Frames = Harvest Only, `-debug.harvestIntervalSec 10` (backs off to 30 s). Run A: Developer › Harvest Screenshot Path = Video Renderer, play 12 min (20+ captures). Run B: Software for SDR. Oracle: `[MPVStats] vo=` recorded; `[Harvest] path=sw` in B; per-capture `rss=` on `[Harvest] stored`; **B grows < 10 MB over 20 captures from capture 3**, A is expected to grow ~60–100 MB; `took=` and `underruns=0` recorded for both. Then close the player after A, wait 30 s, and read the next player's first `[Mem]` line (close test). Then one HDR10 title with B: `[Harvest] path=vo gamma=pq` (the HDR path is unchanged).
8. **BUG-129.** On a series near the end, wait for "Finding source…" (the up-next search), then swipe down → Playback. Oracle: `[UpNext] source list deferred: up-next search in flight`; the Sources column shows "Finding the next episode's source…"; the up-next card still counts down and plays the next episode. Repeat on mpv.
9. **BUG-143.** With Wi-Fi off on the Apple TV, start a source from the picker. Oracle: `[Failover] mpv failure: … kind=offline` and `[Failover] reject … transient=1 skipped`. Wi-Fi back on: the same link is not captioned "Failed recently". [C-6] Repeat with Auto-Play Best Source on a title with cached debrid links and Wi-Fi off: `[AutoPlay] … transient=1 offline=1 skipped` per candidate, and none is "Failed recently" afterwards. A known-dead debrid link (404) → `kind=http http=404` and remembered.
10. **Regression.** The P1/P2/P3 mpv transport checks on one title (swipe scrub, hold step, chapters tab on mpv, seek preview). The native transport-bar Subtitles and Audio popovers still work, and Menu with the up-next chip still dismisses it.
