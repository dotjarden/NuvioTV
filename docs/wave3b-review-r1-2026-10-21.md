# Wave 3b review r1, 2026-10-21

Read-only Opus review of `git diff 823450355..HEAD` in `NuvioMobile-wave3b` (branch `claude/wave3b`, tip `1514b5ddd`, 19 commits: A1, A2, A3, B and three UI harnesses). Paths are relative to `iosApp/`. Spec: `docs/wave3-github-9-10-plan-2026-10-21.md` as corrected by `docs/wave3b-critique-2026-10-21.md` (the critique wins). Promises: `docs/comms-github-issues-9-10-replies-2026-10-21.md`. Nothing was built, run or edited.

**Verdict: FINDINGS (P1 2 / P2 4 / P3 11).** Both P1s and three P2s are in the UI evidence harnesses, not the app: five blind Selects (one of them is the path that opens the Profile tab) and three ways a harness can write to the synced profile. Delete the three harnesses before the merge. App code has one P2 (the new language pages draw no app background: BUG-214's defect on five new pages) and P3s. Every critique correction landed: released-episode lists, the label-state flag, `[MetaVideo]` bridging, a default-cell-only lift change with ring and No Zoom cells byte-identical, the `.manual` chip carve-out, 78 normalized codes, and the Off guard in one helper.

## 1. Safety: the UI harnesses (read first)

### Every Select in the three files

| File:line | What precedes it | Guard | Status |
|---|---|---|---|
| `NuvioTVUITests/Wave3bSettingsEvidenceTests.swift:73` | profile picker: waits for a "Chris" button, Left ×2 (:72) | none | **BLIND (S-P1-1)** |
| `Wave3bSettingsEvidenceTests.swift:87` | Up ×6, Right until `Settings.hasFocus`, at most 8 (:82-86) | the loop never stops the Select when the tab never took focus | **BLIND (S-P1-1).** Where `hasFocus` never reports (tvOS 27.0 runtime, memory note), Right ×8 runs past Settings (value 4) to Profile (value 5, the last tab, `ContentView.swift:498/:508`) and Selects it. The Up ×12 / Down / Down ×N / Select that follow (:89-91 then :98-100 or :111-116) walk the profile switcher. This is the "blind Select opened the Profile tab and created profiles" path. |
| `Wave3bSettingsEvidenceTests.swift:100` | `openPane`: Down × root index (:98) | none; the pane id is checked only AFTER the Select (:102) | **BLIND (S-P1-1)** |
| `Wave3bSettingsEvidenceTests.swift:116` | `clipEvidence`: Down ×6 (:111) | none; checked after (:118) | **BLIND (S-P1-1)** |
| `NuvioTVUITests/DetailLabelLiftMeasureUITests.swift:86` | profile picker: Left ×2 (:85) | none; the comment assumes default focus is on the first profile | **BLIND (S-P1-2)** |
| `NuvioTVUITests/Wave3bLanguageEvidenceUITests.swift:84` | Left until "Chris" `hasFocus` (:76-83) | verified focus | guarded (enters Chris, below) |
| `Wave3bLanguageEvidenceUITests.swift:104` | `Settings.hasFocus` (:101) | verified focus | guarded |
| `Wave3bLanguageEvidenceUITests.swift:116` | focused node `settings_category_<raw>` or its label (:111-115) | verified focus | guarded |
| `Wave3bLanguageEvidenceUITests.swift:177, :212, :228, :295, :326, :357, :373, :402` | `requireRow` (:129-133): explainer title == row title | **weak (S-P2-1)** | `settings_explainer_title` is sticky by design (`SettingsExplainerModel.swift:15-17`, F14: never cleared on blur). It proves the last DESCRIBED row, not the focused one. |
| `Wave3bLanguageEvidenceUITests.swift:368` | `requirePageRow` (:137-144): page up, a focused cell with a label | verified focus (any row) | guarded; its write is in-memory only if the seam is live (S-P2-2) |

Every other press in the three files is Up, Down, Left, Right or Menu; none activates a control. About 18 pre-existing suites (`BatchA*`, `Detail*`, `Hero*`, `Folder*`, `NavigationRailUITests`, …) use the same "Chris + Left ×2 + Select" entry. That is out of scope here; file one follow-up for a shared guarded `enterFixtureProfile`.

### Writes to the synced profile

- **S-P2-1: the sticky-explainer guard.** In the Subtitles pane, a mis-guarded Select on Bold, Outline or Strip SDH flips a synced subtitle-style setting. Fix, if the file is kept: `requireRow` also requires `focusedNodes(app)` to contain `label=<\(rowTitle)`, the check `openPane` already makes.
- **S-P2-2: the seam check can pass on real data.** `Wave3bLanguageEvidenceUITests.swift:354` tests `rowValue(...).contains(seedLabel)`. With seed `en` (:316) it cannot tell the DEBUG seam from a profile whose real Fallback Audio Language is English, which mobile can write. Without the seam (a Release-built host, say), the Select at :368 writes the pick through `SettingsViewModel.setSecondaryPreferredAudioLanguage` → `PlayerSettingsRepository` → the synced player settings. Fix, if kept: the seam publishes a DEBUG-only marker (an identifier on the row while `debugFallbackAudio != nil`), and the guard checks the marker, never the value.
- **S-P2-3: `-tmdb_enabled_1 YES` is exported.** `DetailLabelLiftMeasureUITests.swift:76`; the comments at :33-34 and :74-75 say "read, never written". `TmdbSettingsStorage.loadBoolean` reads `tmdb_enabled_<profileId>` through the argument domain (`shared/src/appleMain/.../TmdbSettingsStorage.apple.kt:150-157`), and `exportToSyncPayload` (:163-164) puts that value in the blob. Any profile-settings push during the run therefore uploads `tmdb_enabled=true` for profile 1: the local-change observer (`ProfileSettingsSync.kt:406-480`) or the deferred gated push after the first pull settles (:142-156). The override is not DEBUG-only either: the argument domain works in every configuration (harmless to users, who cannot pass launch arguments). Fix: drop it. Use a title on a profile that already has TMDB on, or add a DEBUG in-memory override.
- **Profile.** All three enter "Chris" (`Wave3bSettingsEvidenceTests.swift:69`, `Wave3bLanguageEvidenceUITests.swift:72`, `DetailLabelLiftMeasureUITests.swift:81`). On the fixture that is the real account's daily-use profile; tonight's junk profiles landed on that account. Any future harness that presses Select enters Test (or a local guest) and verifies it first.
- **Screenshots.** The Settings and Language harnesses write PNGs into the public outer repo by absolute path (`Wave3bSettingsEvidenceTests.swift:12`, `Wave3bLanguageEvidenceUITests.swift:15`). The Sources and Appearance shots show plugin repository and badge-pack URLs (`StreamBadgesSection.swift:62` prints `pack.sourceUrl`). They are untracked; never stage `docs/` wholesale (the rig-log staging rule).
- **Scheme.** `NuvioTVUITests.xcscheme` has one testable and skips nothing, so a full-target UI run executes all three harnesses.

### Recommendation per harness

| Harness | Do | Why |
|---|---|---|
| `Wave3bSettingsEvidenceTests.swift` | **Delete** | 4 blind Selects. Its evidence (W3-9 not reproduced, four swatch targets, the plugin and badge splits) is in `docs/open-items-plan-2026-10-21.md` and `docs/research/wave3b-sim-2026-10-21/`. |
| `Wave3bLanguageEvidenceUITests.swift` | **Delete** | Guarded entry, but a weak row guard, a seam check that passes on real data, and the Chris profile. Its readings (Menu opens on the first entry, pages open on the checked row, the end-of-list quirk) are recorded. |
| `DetailLabelLiftMeasureUITests.swift` | **Delete** from this branch | 1 blind Select and the exported TMDB override. The readings live in `DetailLabelLift`'s doc (`DetailView.swift:3220-3246`); `CompanyChipLiftTests` pins the ×1.12 math. If a BUG-200 geometry leg is wanted later, re-land it with a verified Test-profile entry and without `-tmdb_enabled_1`. |

The `DebugAXIdentifier("cast_artwork")` probe it added (`DetailView.swift:3317`) is DEBUG-only (`PosterCard.swift:75-90`); keep it or drop it with the harness.

## 2. Findings (app code)

**P2-1: The pushed language pages draw no app background.** `NuvioTV/Screens/Settings/SettingsRowViews.swift:695-724` (`SettingsListPickerPage.body`).
- Panes draw it themselves (`SettingsPaneScaffold.swift:62`). `SettingsView.swift:84` puts it on the root view inside the stack, and pushed destinations do not inherit that.
- So OLED True Black and the theme background never reach Audio, Fallback Audio, Subtitles, Fallback Subtitle and Metadata Language: the defect BUG-214 fixes for Add-ons in this same branch.
- Fix: `.background(Theme.Palette.background.ignoresSafeArea())` on the page, outside the `ScrollViewReader`, before `.navigationTitle`. `CustomPostersSettingsView`, the shape this copies, has the same gap: fix it in the same commit or file a row. Add the pages to the OLED device check.

**P3-1: On a language page, the first Up from a row in the last half-screen jumps 5–6 rows.** `SettingsRowViews.swift:673-742`. A code read cannot settle the cause; the evidence narrows it:
- `.defaultFocus(.userInitiated)` alone is not it: it only names the initial target.
- The end placement is the only one where focus arrives by the LATE path. Per the agent's notes, the push transition took the first claim for Zulu, so focus reached Zulu through the 0.45 s re-claim (:737-739). That path scrolls to `.bottom` a SECOND time (:733) and moves focus programmatically from the transition's pick.
- It is also the only placement where the offset is clamped at the end of an 80-row lazy `List`, while the rows that have not been scrolled through are still at estimated heights.
- Both mean the list moves after focus is committed. The symptom fits: the engine searches from a stale focused frame until one move refreshes it. A hand walk realizes and measures every row in order, with no programmatic scroll, and is clean.
- Experiments, cheapest first (sim leg wb-10, then the box):
  1. Re-claim without re-scrolling: drop the `scrollTo` from the `settleCheck: false` pass.
  2. A fixed height on the page rows, so estimates equal measurements.
  3. One claim only, from `.task` once the push settles (~0.5 s): scroll inside a `Transaction` with animations disabled, then focus, and drop `.defaultFocus(.userInitiated)`.
  4. Fallback: a non-lazy page (80 rows is cheap), so `.defaultFocus` reaches the checked row and the engine does its own scroll.
- If the box does not show it, record "sim-only" and leave it.

**P3-2: `heldEpisodeId` can stay armed.** `NuvioTV/Screens/EpisodesSection.swift:32, :174, :216, :227, :229-232`.
- It clears only when `focusedEpisodeId` changes to non-nil.
- It stays armed if the menu action runs after focus has already returned to the card (context-menu handlers run as the menu dismisses), or if `focusedEpisodeId` never goes nil while the menu is up.
- Then `defaultFocus` keeps pointing at the held card, not next-up, and the `nextUpId` scroll stays suppressed until the user moves along the shelf.
- Fix: clear it on ANY `focusedEpisodeId` change after arming, plus a 1 s backstop in `willAct` (`Task { try? await Task.sleep(for: .seconds(1)); heldEpisodeId = nil }`).

**P3-3: The hide rule and the guard can drift.** `NuvioTV/Screens/Settings/SubtitlesAudioSettingsPane.swift:80` compares the raw value with `NONE`. `SubtitleFallbackGuard` (`Screens/Player/SubtitleFallbackGuard.swift:26-30`) normalizes and treats a blank primary as Off, so a blank primary shows the row while both players ignore it. Fix: one predicate (e.g. `SubtitleFallbackGuard.isOff(primary:)`) used by both.

**P3-4: VoiceOver reads a list-picker row's value twice.** `SettingsRowViews.swift:650` adds `.accessibilityValue(label(...))`, and `SettingsTrailingValue` (:262-282) already renders the value as visible, non-hidden text. Fix: drop :650, or hide that row's trailing `Text` from accessibility.

**P3-5: "Original" reads "Ordre original" in French.** `SettingsRowViews.swift:1126` reuses the catalog key `Original`, whose fr value is a sort-order phrase. It now shows on Audio and Fallback Audio (Audio is pre-existing). Fix in the catalog pass: a separate key for the language sentinel (e.g. `Original Language`) with its own translations.

**P3-6: The chip's default-cell focus cue is scale only.** `NuvioTV/Screens/DetailView.swift:3482`.
- `focusShadow` is false there, there is no ring, and `RingCardButtonStyle` with `.focusEffectDisabled(true)` removes the system motion. ×1.12 on a white 52 pt capsule (3 pt up and down) is the weakest focus cue on the page.
- The "dark slab" reason overstates the platter: it is the capsule's own shape (radius 26) behind a 0.92-white fill.
- Look on the box. If the cue reads weak, keep the shadow in the default cell (a shadow-only variant, or an opaque white fill so the black platter never tints the capsule).

**P3-7: Deleting a badge pack throws focus.** `NuvioTV/Screens/Settings/StreamBadgesSection.swift:74-80`. The focused Delete row and its pack row leave together, and nothing claims focus. Pre-existing (the trash button went too). Fix: arm `ClaimsFocusAfterSwap` on the next pack row or the Import field, as the key rows now do.

**P3-8: An episode with only one number never reads watched.** `EpisodesSection.swift:444-445`, `DesignSystem/TitleHoldMenu.swift:239-242`.
- `groupedEpisodes` (`EpisodesSection.swift:323-333`) keeps entries with a season OR an episode number, but `episodeKey` needs both.
- Such an entry always offers "Mark Episode Watched" and its label never flips. A Specials season that holds one never reads watched.
- Rare. Fix: omit the episode item when `episodeKey == nil`, unless mobile does something else.

**P3-9: A season with nothing released gets an empty menu.** `EpisodesSection.swift:545`, `:479-500`. Attaching the menu unconditionally is correct, but its content is empty. Check what a hold shows on the box. If it is an empty bubble, add a disabled "No released episodes" item (a new string), or accept it.

**P3-10: Confirm the menu bodies are evaluated at presentation.** The design depends on it (`EpisodesSection.swift:424-429`): the previous-episodes list is a shared sort over every episode, once per card. If tvOS evaluates `contextMenu` content with the row, that sort runs per card on every Left/Right (BUG-153). One DEBUG counter in `EpisodeHoldMenuItems.body` during a shelf walk settles it.

**P3-11: Stale docs and comments.**
- `NuvioTV/DesignSystem/PosterCard.swift:150-157` still lists `CastCard` on `PlainLabelRing.lift`.
- `NuvioTVTests/PlainLabelRingTests.swift:5-7` (header) has the same claim, and `:86-95` says "every label class" while looping `.card`/`.plain` only: add `.manual` → `.ring`, or say "except `.manual`".
- `NuvioTV/Screens/SettingsViewModel.swift:56` names `SettingsPickerRow`; the pane uses `SettingsListPickerRow`.

## 3. Answers to the brief (verified)

**FEAT-83, hold menus.**
- **Released lists.**
  - The episode menu uses `meta.previousReleasedEpisodesBefore(target:todayIsoDate:)`; the season menus use `meta.releasedEpisodesForSeason(seasonNumber:todayIsoDate:)`. Both take `CurrentDateProvider.shared.todayIsoDate()` (`EpisodesSection.swift:442-443, :486-488`), so unaired episodes are never marked or synced.
  - With nothing released, the season item is left out (`TitleHoldMenu.swift:231-235`).
  - "Season watched" = a non-empty released list with every key watched (`:245-254`). The keys already count completed progress (`DetailViewModel.swift:833-850`).
- **Label-state flag.** Every call passes `action.labelState`, the state its title was built from (`EpisodesSection.swift:452-462, :494-495`), and never re-reads. `testEveryDetailActionDoesWhatItsLabelSays` pins it.
- **Bridging.** The SharedCore header has `episodes:(id)` on both toggles and returns `NSArray<SharedCoreMetaVideo *>` from both helpers. The code hands the returned `[MetaVideo]` straight back, which crosses as `NSArray` and reaches Kotlin as a `List`. No cast risk.
- **Placement.**
  - Episode: after `.focused`, before `.id` (`:171-176`). Season poster: after `.focused` (`:545`). Text chips: `:116`. All attached unconditionally.
  - No `DetailViewModel` change; the existing watchers refresh the keys.
  - The `TitleHoldMenu.swift:16` doc is updated, Specials read through `seasonLabel`, and the "Mark Episode Watched" key is reused.
- **Previous episodes.** Left out on the first released episode. Flips to Unwatched once every previous episode is watched (mobile's rule). Spans earlier seasons.
- **Focus.** `heldEpisodeId` suppresses the `nextUpId` scroll and points `defaultFocus` at the held card (clear rule: P3-2).

**BUG-200, the default-cell lift.**
- **`CastCard`** resolves through `DetailLabelLift` = `CardFocusMode.resolve` (`DetailView.swift:3247-3251, :3279-3281`).
  - Default cell → `.systemLift` on the avatar: `.compositingGroup`, `.contentShape(.hoverEffect, radius 70)`, `.hoverEffect(.highlight)`. The caption drops 20 pt (`CardCaptionFocusDrop` pays for `.systemLift`, `PosterCard.swift:975`).
  - The ring cell and both No Zoom cells equal `PlainLabelRing.lift` (tested).
  - `.buttonBorderShape(.circle)` (`:2639`) is read only by `.borderless`; the ring and still styles are custom, so they render as before.
  - `liftedCastZIndex` already read `CardFocusMode.resolve`, so there is no zIndex in the default cell (the system lift composites in its own layer).
  - `PlainLabelRing.lift` is untouched for `FolderTile` (BUG-216 filed).
- **`CompanyChip`.**
  - `.manual` resolves to `.ring` in both zoom-on cells and `.still` with No Zoom (`PosterCard.swift:223-228`). `smallLabelLift` answers `.manualScale` / `.still` (`:456-458`).
  - The ring cell is `.manualScale` plus platter, as before. No Zoom is `.still(ringed:)`, and `.still` ignores `focusShadow` (`PosterCard.swift:921`). Both cells are byte-identical.
  - `.card` and `.plain` resolve as before for every other card (tested).
  - The zIndex is now raised in the default cell (SwiftUI draws the scale).
  - Growth is 12.7 pt per side inside the 16 pt gap; measured 12.5 pt, 3.5 pt clear of the neighbour. The HIG carve-out is in the outer doc (`3082948`).
- **Avatar measurement.** ×1.32 (22.6 pt per side) clears the 34 pt avatar gap by about 11 pt. It exceeds the 20 pt caption drop by 2.6 pt, so the name gap narrows, and the lifted top comes within about 1.4 pt of the "Cast" heading (16 + 8 pt). Device look.

**BUG-201.**
- The ring follows `SwatchLabel`'s rule with `strokeBorder`: selected 4 pt contrast, focused 3 pt contrast at 0.8, rest 1 pt.
- A private ×1.2 + shadow lift is added: 4.6 pt growth inside the 8 pt padding, no animation under Reduce Motion (`SubtitlesAudioSettingsPane.swift:211-261`).
- Focused + selected now differs from selected alone (the lift).
- The sim shows four separate targets (A2 note). `ProfileSelectionView.swift` is untouched.

**BUG-213, the row splits.**
- **`DebridKeyEntryRow`** (`SettingsRowViews.swift:990-1040`): the body is a `Group` of two rows, and `@State key` is kept. The field row wears `SettingsRestPlatter(explicitFocus: fieldFocused)`. Save is a `SettingsActionRow` that is never disabled. The dead `saveFocused` is gone.
- **Plugin and badge URL rows** split the same way (`SourcesSettingsPane.swift:592-634`, `StreamBadgesSection.swift:99-141`): no glass, no `.borderedProminent`, the spinner in `trailing:`, Install and Import never disabled. `manifestFieldFocused` stays on the field.
- **Per-pack row** is now the pack row plus a "Delete Badge Pack" row (`StreamBadgesSection.swift:53-81`).
- **Hand-offs in Sources.**
  - Save → the Remove row: `keyFocusHandOff` "tmdb:remove" / "mdblist:remove", armed only for a non-blank key, since both repositories trim and a blank key clears.
  - Remove → the field: "…:field", through `fieldFocusHandOff` on the field row's `onAppear`.
  - Both are flag-gated, cleared once used, and claim one runloop late.
- **Hand-offs in Services** (`ServicesSettingsPane.swift:383-420, :468-480`).
  - Save → the Connected or Session expired row (`claimsFocusAfterSwap(handOff(":connected"))`). Disconnect → the key field.
  - An alert Cancel disarms after 0.5 s while the provider is still connected.
  - Disconnect is synchronous Kotlin plus one main-queue hop (`DebridViewModel.swift:135-137`), so the 0.5 s check is safe on the confirm path. The observer sits on a row that survives Cancel, the only path that needs it; the Wave 3 r1 P2-1 trap does not apply.
- **Owner's call.** After Disconnect, focus goes to the key field (second row), not to Connect (first row, the primary action in the vacated slot). Both are defensible.

**BUG-214.** `AddonsView.swift:31`: the background sits on the `ScrollView` inside the stack, as specified.

**BUG-215 (W3-9).** No code. The sim did not reproduce it in Default or Minimal, root or pane (A2 note). That matches the critique: no fix without a reproduced clip. The device check stays; the #10 reply promised a check of the panes on sim and device.

**FEAT-84, languages.**
- **The list** (`SettingsRowViews.swift:1071-1170`):
  - 78 shared tags. Option codes are `normalizeLanguageCode(tag)` (`pt-br`, `zh-cn`, `zh-tw`, `es-419`), with a fixed-point test.
  - Labels come from the original tag in the app's UI locale (`Bundle.main.preferredLocalizations.first`), first letter capitalised with that locale, sorted with its collation. `zh-CN`/`zh-TW` are labelled through `zh-Hans`/`zh-Hant`.
  - TMDB takes the 74 bare codes (its readback keeps the primary subtag).
  - The lists are `static let`, with one code → name dictionary. The whole enum is `nonisolated`, and the builder takes an injected locale.
- **Unknown stored values** (mobile's `default`, `forced`, anything else) are inserted after the sentinels and labelled: "Default", "Forced", else the ICU name, else the code (`codes(_:keeping:pinned:)`).
- **Fallback rows.**
  - Fallback Audio offers None, Original, then the languages; Fallback Subtitle offers None, then the languages.
  - `""` ↔ nil through the shared secondary setters, with `@Published` mirrors assigned in the player watcher (`SettingsViewModel.swift:54-58, :196-197, :690-698`). The descriptions say "None by default".
  - The subtitle fallback row is hidden while Off: hidden, not disabled, and focus is on the Subtitles row when it goes.
- **Off guard.** `SubtitleFallbackGuard.effectiveSecondary` runs at both auto-selection sites (`MPVPlayerView.swift:1276-1284`, `NativePlaybackCoordinator.swift:369-377`). It is `nonisolated`, unit-tested with a round-trip through the shared resolver, and documents the five non-selecting consumers it does not cover.
- **Pushed list page.**
  - It replaces the Menu, decided on sim evidence: a tvOS `Menu { Picker }` opens on its first entry.
  - Focus is claimed on push: an async claim, one 0.45 s re-claim, and `.defaultFocus(.userInitiated)`. The checked row is scrolled in (top: no scroll; middle: centred; end: bottom).
  - Select stores the value (only if it changed) and pops; Menu pops back to the row (harness wb-4c).
  - Rows carry `.isSelected`; the checkmark is hidden from VoiceOver.
  - Gaps: P2-1, P3-1, P3-4.
- **The DEBUG seam.** `-debug.fallbackAudioSeed` is DEBUG-only: the state and the binding branch are both inside `#if DEBUG` (`SubtitlesAudioSettingsPane.swift:10-24`), and Release compiles to the model binding. It reads `UserDefaults.standard`, so a persisted value would also arm it in a Debug build; arguments-only would be safer (trivial).

**MainActor / `nonisolated`.**
- `LanguageOptions` and `SubtitleFallbackGuard` are `nonisolated enum`s: pure, with Sendable state (tuples of `String`).
- The pure `TitleHoldMenuPolicy` helpers are `nonisolated` (`episodeKey`, `areAllWatched`, `seasonIsWatched`). The members that build titles stay MainActor, and their tests are `@MainActor`.
- `EpisodeHoldMenuItems.key` is `nonisolated` over the `nonisolated` `KotlinInt.value`.
- The `DispatchQueue.main` claims follow the existing `ClaimsFocusAfterSwap` pattern. No `Task.detached`. Nothing found.

**Localization.** `Localizable.xcstrings` and `project.pbxproj` are untouched (`git diff --stat` is empty). New keys are in §5. Every reused key exists in the catalog with 5 localizations: Device, Off, Original (P3-5), Default, Forced, Mark Episode Watched, Save Key, Install Repository, Import Badge Pack, Delete Badge Pack, Active, Set Active, `%d filters · %@`, `1 filter · %@`, the Services row strings and the field placeholders.

**Tests.**
- **Added:** `CompanyChipLiftTests` (8), `DetailLabelLiftTests` (4), `LanguageOptionsTests` (15), `SubtitleFallbackGuardTests` (4), `TitleHoldMenuPolicyTests` (+11). `PlainLabelRingTests` changed its doc only. Together they cover the critique's §10 list.
- **Gone stale:** nothing fails; doc drift only (P3-11). test95's Sources budget re-ran green with the extra rows (B note). `test59` (ring mode) is unaffected.
- **Not covered:** `SettingsListPickerPage` placement (pure, extractable), the hand-off arming (device), the context-menu evaluation timing (P3-10).
- **Gate record for the tip:** Debug sim, the targeted suites above, test95. Not on record: the full `NuvioTVTests`, the Release sim build, `:shared:jvmTest` (no shared change, but the gate asks). Run them before the merge.

**Comms.** The #10 reply says 74 codes; the list is 78 (80 entries on Audio and Subtitles). The post-landing comments and the release notes should:
- say 78 languages;
- name Fallback Audio Language = None and Fallback Subtitle Language = None;
- say the language pickers now open as a page on the current value;
- mention the episode menu's Mark Previous Episodes item;
- report BUG-215 as "not reproduced on the simulator; device check owed".

## 4. What is good

- Every critique correction landed. The tests pin the relations, not just the values: button style ↔ label lift, label ↔ toggle flag.
- The chip fallback was decided on a measurement (×1.19), and the reason is recorded in the code and in the HIG contract.
- The language list gets the hard parts right: normalized codes, the TMDB readback, French case and collation, UI-locale labels, synced sentinels, and "Original" kept on Fallback Audio for mobile parity.
- The key-row hand-offs cover both directions in both panes, use the same gate as `ClaimsFocusAfterSwap`, and handle the Services Cancel path.
- The Off guard is one tested helper at both sites, with its limits written down.
- The language harness's later legs guard their Selects, and the blind-Select incident was recorded in the status doc, not buried.

**Verdict: FINDINGS: P1 2 (5 blind Select sites, harnesses only) / P2 4 (3 harness, 1 app: no background on the language pages) / P3 11.** Merge when four things are done: the three harnesses are deleted (that clears both P1s and S-P2-1 to S-P2-3), P2-1 is fixed, the full gate runs on the tip, and the device checks below pass. r2 then needs only a re-read of P2-1 and of whichever P3s are taken.

## 5. New string keys (catalog + MT pass; none is in `Localizable.xcstrings` yet)

1. `Fallback Audio Language` (`SubtitlesAudioSettingsPane.swift:62`)
2. `Fallback Subtitle Language` (`:82`)
3. `None` (`SettingsRowViews.swift:1128`): fr "Aucune" (a language)
4. `Mark Episode Unwatched` (`DesignSystem/TitleHoldMenu.swift:199`)
5. `Mark Previous Episodes Watched` (`:202`)
6. `Mark Previous Episodes Unwatched` (`:201`)
7. `Mark %@ Watched` (`:205`): `%@` is "Season 2" / "Specials", already localized; translate around a noun phrase
8. `Mark %@ Unwatched` (`:204`)
9. `If the video has no audio track in your Audio language, picks one in this language instead. None by default.` (`SettingsDescriptions.swift:393`)
10. `If no subtitle track is in your Subtitles language, picks one in this language instead. None by default. Hidden while Subtitles is Off, which always stays off.` (`:394`)

Plus the P3-5 split (e.g. `Original Language`) if it is taken. Language names come from ICU, not the catalog. Mobile's sentence-case strings will not match the Title Case keys in the harvest, so these need MT.

## 6. Device checks for the owner (Test 2 profile; name it before each step; remove what you add)

0. First: delete the two empty "Profile" profiles on the account the FA87 fixture is signed into (Christian). Then `scripts/device/ready.sh`.
1. **BUG-200, Cast.** Accent Focus Ring off, zoom on:
   - the whole avatar lifts as a circle, with no square platter corners at rest or focused;
   - name and role drop with it, and the name gap stays readable (22.6 pt lift vs a 20 pt drop);
   - the lifted top does not touch the "Cast" heading;
   - a no-photo (person glyph) avatar does not lift its glyph twice;
   - the first avatar against the Row Edge Fade.

   Then Accent Ring on, and No Zoom: unchanged from rc11.
2. **BUG-200, Production chips**, the same three settings: in the default cell the whole white capsule lifts ×1.12 with the logo inside; a name-only chip lifts; no neighbour is touched. Judge from the couch whether scale alone reads as focus (P3-6).
3. **BUG-201, Text Color:** Left/Right walks four separate swatches on hardware; focused, selected, and focused + selected all look different; with Reduce Motion on, there is no animation and the lift still applies.
4. **FEAT-83.**
   - Hold Select on an episode card, a season poster, and a season chip (on a title without season art).
   - Mark, then unmark. The watched tick and Continue Watching follow.
   - After each action, focus stays on the held card, not on the new next-up. A later Down from the season row lands on next-up (P3-2).
   - Mark Previous on S2 E3 also marks S1.
   - Hold on an announced season with nothing released (P3-9).
   - Leave nothing marked; check Trakt/Simkl if Test 2 is linked.
5. **BUG-213.** Step 0 first, then:
   - TMDB: Select on the key field opens the keyboard; Down lands on Save Key; saving a dummy key puts focus on "Remove Personal API Key"; Remove puts focus back on the field.
   - MDBList: the same.
   - Services, one debrid provider: a manual key Save puts focus on Connected; Disconnect → Cancel keeps focus on Connected; Disconnect → Confirm puts focus on the key field.
   - Plugins: the repository field and Install Repository are separate targets; W3-2's remove puts focus on the field.
   - Badges: the URL field and Import are separate targets; check Set Active on a pack row, and where focus goes after Delete Badge Pack (P3-7).
   - Remove every dummy key (they sync).
6. **BUG-214 and P2-1:** Add-ons with OLED on is pure black, off is the app grey. After P2-1 lands, the same on each language page and on Custom Posters.
7. **BUG-215:** a focused row in Sources with Settings Style Default and Minimal: clipped or whole?
8. **FEAT-84, pages.**
   - The Audio page opens on the checked row for a top, a middle and a last-half-screen value.
   - The first Up from a last-half-screen row: a jump, or one row (P3-1)?
   - Menu pops back to the row; Select on the checked row pops without writing.
   - French UI: labels capitalised, sorted A–Z in French.
   - The Fallback Subtitle row is hidden with Subtitles Off.
9. **FEAT-84, playback** (mpv and native):
   - Subtitles Off, with Fallback Subtitle set to a language in a two-subtitle MKV: no subtitle shows.
   - Subtitles set to a language the file lacks, with Fallback set to one it has: the fallback loads.
   - Fallback Audio likewise, with a file that lacks the primary audio language.
   - Reset both fallbacks to None (they sync).
   - Shoot 4K/HDR last (the box drops off Wi-Fi after 4K streams).
10. **VoiceOver** on one list-picker row: the value is read once (after P3-4).
