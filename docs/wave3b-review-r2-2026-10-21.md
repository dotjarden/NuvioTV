# Wave 3b review r2, 2026-10-21

Read-only Opus review of the r1 fix pass in `NuvioMobile-wave3b` (branch `claude/wave3b`, tip `00f542b6f`): `git diff 1514b5ddd..HEAD` (12 commits) against `docs/wave3b-review-r1-2026-10-21.md`, then the whole branch `git diff 823450355..HEAD` (now 24 files, no UI test files) for regressions. Paths are relative to `iosApp/` unless marked. Spec: `docs/wave3b-critique-2026-10-21.md`. Nothing was built, run or edited.

**Verdict: FINDINGS (P1 0 / P2 0 / P3 4).** Every r1 finding is fixed or answered, and the fixes broke nothing. Nothing blocks the merge. The four P3s are a two-line focus guard, a catalog-pass instruction for the new dotted key, stale doc lines, and an out-of-branch background gap. Fix or decline each with a reason; r3 then only needs to re-read those lines.

## 1. Findings (r2)

**P3-1: The 0.45 s re-check can pull focus into a page that is being popped.** `NuvioTV/Screens/Settings/SettingsRowViews.swift:752-758` (`claimCheckedRow`).
- `guard focused != current` treats "focus has left the page" the same as "the push transition put focus on another row". After Menu or Select inside the window, `focused` is nil. The closure then writes focus to the checked row of the departing page (`:754` while the row is still realized during the pop, else a scroll at `:756` plus an async write).
- What tvOS does with that request mid-pop is unverified. At worst focus drops off the pane's Audio/Subtitles row and lands wherever the engine puts it.
- Not introduced by the fix: r1's code had the same guard. The window is small, from the moment the push settles to 0.45 s after `onAppear`.
- Fix: `guard let now = focused, now != current else { return }`. Re-claim only when focus sits on ANOTHER row of this page, which is the observed Zulu case (wb-10: focus on the first row in view). A fast Up inside the window is still pulled back; accept that.

**P3-2: `settings.language.original` is harvested without its English value or comment.** `NuvioTV/Screens/Settings/SettingsRowViews.swift:1157-1162`; `NuvioMobile/scripts/populate-localizable-xcstrings.py:76-77, :98-110`. Note: the script lives in the submodule. There is no `scripts/populate-localizable-xcstrings.py` in the outer repo.
- **Harvested: yes.** The compiler emits it in the `Localizable` table. `Release-appletvsimulator/.../SettingsRowViews.stringsdata` has `key: settings.language.original`, `value: Original` and the comment. The script reads `entry["key"]` only.
- **English stays right.** The entry lands as `{}`. The compiled `en.lproj/Localizable.strings` in this clone's Release app holds only the 23 entries with an explicit `en` unit (the `detail.status.*` keys plus a few others), so a `{}` entry compiles to nothing for English. The runtime then returns `defaultValue` "Original" (fr likewise until translated).
- **What breaks.** `value` and `comment` are dropped. The mobile harvest matches on the key and finds nothing. `localizable-needs-translation.json` hands the MT pass `settings.language.original` as the source text, with no hint that it means the audio-track choice and not the TMDB sort order. That sort-order sense is exactly what r1 P3-5 removed.
- Fix (catalog pass): hand-write the entry the way `808e9ae4c` did for `detail.status.*`: `"extractionState": "manual"`, an `en` unit "Original", and fr/es/de/it/vi in the audio-language sense (fr: not "Ordre original"; e.g. "Version originale"). Or teach the script to write an `en` unit and the comment when `value != key`, and to report `value` plus the comment to MT.

**P3-3: Stale doc lines.**
- `SettingsRowViews.swift:679-680` says "Not yet re-checked: sim leg wb-10 and the device pass". wb-10 was the deleted `Wave3bLanguageEvidenceUITests` driving the deleted `-debug.fallbackAudioSeed` seam (`docs/research/wave3b-sim-2026-10-21/wb-10-deep-page.txt`: Fallback Audio seeded to Zulu). It cannot run any more. Say "the device pass".
- Outer `docs/open-items-plan-2026-10-21.md:71` says "the 0.45 s re-check never scrolls again". It does scroll when the checked row is not realized (`SettingsRowViews.swift:755-757`). The code comment (`:667-671`) is right; fix the plan line.
- `NuvioTV/Screens/EpisodesSection.swift:518-520` says "should the date roll over mid-visit it is still empty here, never a dead item". The reachable case is the reverse: `releasedSeasons` is cached per `MetaDetails` (`:74`), so a season whose first episode airs during the visit gets no menu until `meta` is republished. Reword.
- `NuvioTVTests/PlainLabelRingTests.swift:92`: `testDefaultModeIsBareBorderlessForEveryLabelClass` now also asserts `.manual` → `.ring`. The doc explains it, but the name still says "every". Optional rename.

**P3-4: The MDBList "Library lists" page draws no app background.** `NuvioTV/Screens/Settings/MdbListLibraryListsView.swift:116-152`. It is a pushed Settings destination (`ServicesSettingsPane.swift:256-263`) with a bare `List` and no `.background`: the r1 P2-1 defect, on a page this branch does not touch. Pre-existing. Fix: `.background(Theme.Palette.background.ignoresSafeArea())` before `.navigationTitle` (`:151`), or file a row. `ServerConnectionView` already draws its own (`ServerConnectionView.swift:39`).

## 2. The r1 findings, re-checked

| r1 | Status | Evidence |
|---|---|---|
| S-P1-1, S-P1-2, S-P2-1..3 (harnesses) | **Fixed** | `aa08cc41b` removes all three files. `git grep` on HEAD finds no `Wave3bSettingsEvidence`, `Wave3bLanguageEvidence`, `DetailLabelLiftMeasure`, `fallbackAudioSeed`, `debugFallbackAudio` or `tmdb_enabled_1`. `NuvioTVUITests` is a `PBXFileSystemSynchronizedRootGroup` (`project.pbxproj:144-147`), so no file references are left behind. No scheme or test plan names them. There are no untracked or ignored leftovers in the clone. Per the gate record, the UI target compiles. The `cast_artwork` probe stays, DEBUG plus `-debug.cardGeometryProbe` only (`DetailView.swift:3316-3318`). |
| Seam | **Gone** | `SubtitlesAudioSettingsPane.swift:10-12` binds straight to the model, with no `#if DEBUG` left. r1's "arguments-only" note no longer applies. |
| P2-1 | **Fixed** | `SettingsListPickerPage` `:739`: outside the `ScrollViewReader`, before `.navigationTitle`, the `SettingsPaneScaffold` shape (`SettingsPaneScaffold.swift:62`). One page type serves all five rows: Audio, Fallback Audio, Subtitles, Fallback Subtitle, and Metadata Language (`SourcesSettingsPane.swift:183`). Custom Posters: `CustomPostersSettingsView.swift:124-126`. The palette swap is a root `.id(paletteKey)` remount, so a static read is enough. |
| P3-1 | **Fixed as experiment 1; effect unverified** | One scroll before focus (`:749`). At 0.45 s the check does nothing if the checked row has focus, only moves focus while the row is realized (`:753-754`), and re-scrolls only when it is not (`:755-757`). `checkedRowOnScreen` is `@State` on the page: each push builds a new `SettingsListPickerPage`, so the state starts false every time and is never carried across pushes. Only the checked row writes it (`:729-730`). It is never read in `body`, so a write does not invalidate the page. The `asyncAfter` holds a struct copy and the proxy for 0.45 s, with no cycle. Whether the first-Up jump is gone is a device check (§5). |
| P3-2 | **Fixed** | `armHeldEpisode` (`EpisodesSection.swift:412-418`). Any `focusedEpisodeId` change clears it (`:239-244`). The backstop leaves a newer arm on another card alone (`:416`). Walked all three orders: the action runs while the menu holds focus, runs after focus is back, or focus never left. The `nextUpId` scroll can only run while focus is nil (`:226`), and the hold covers that span in every order and never outlives 1 s. A re-arm of the SAME card inside 1 s would be cleared early by the older task. That cannot happen in practice (a hold takes about 0.5 s, plus the menu walk); a token would close it. |
| P3-3 | **Fixed** | `SubtitleFallbackGuard.isOff` (`Screens/Player/SubtitleFallbackGuard.swift:29-33`) backs `effectiveSecondary` (`:36-38`) and the pane's `if` (`SubtitlesAudioSettingsPane.swift:69`). Both players still pass the raw `settings.preferredSubtitleLanguage` (`MPVPlayerView.swift:1279-1282`, `NativePlaybackCoordinator.swift:373-376`), the value the pane mirrors (`SettingsViewModel.swift:195`). `testIsOffMatchesTheGuard` pins the two to agree on 9 inputs. |
| P3-4 | **Fixed** | `.accessibilityValue` is gone (`SettingsRowViews.swift:648-651`). `SettingsTrailingValue`'s `Text` is not hidden (`:268-272`); the chevron is (`:278`). No UI test reads these rows' value. |
| P3-5 | **Fixed; pipeline note P3-2** | New key at `:1157-1162`. The bare `Original` key stays with the TMDB sort (`TmdbFilterEditorView.swift:105`), which is its right meaning. The test compares against the same `String(localized:defaultValue:)`. |
| P3-6 | **Comment corrected** | `DetailView.swift:3482-3483`, `PosterCard.swift:463-466`. The scale-only cue is still a device look. |
| P3-7 | **Fixed** | See §3. |
| P3-8 | **Fixed** (a broader fix than r1 suggested) | See §3. |
| P3-9 | **Fixed** | `releasedSeasons` (`EpisodesSection.swift:426-429`) comes from `releasedPlayableEpisodes` with the shared season normalization. That is the same filter `releasedEpisodesForSeason` applies (`shared/.../WatchedEpisodeActions.kt:39-74`), so the `if` (`:125`, `:591`) never hides a season the menu would fill and never shows one it would leave empty. The shape matches `HoldPlayChooseSourceMenu` (`DetailView.swift:3558-3572`), whose empty hold was device-verified inert on 10-01 (outer `docs/orivio-batch-plan-2026-10-01.md:100`). Cost: one shared sort and date filter per `MetaDetails` object, inside `EpisodeGroupingCache`, never per Left/Right. That still honours the critique's BUG-153 rule. |
| P3-10 | **Answered** | The cited logs say what the doc says. `rc5-promises-device-2026-10-17/console-a.log`: 525 lines, 2 `[HoldMenu] menu built` (lines 169 and 182, both around a hold). `bug170-device-2026-10-18/console-mpv.log`: 1 (line 63). The proof comes from the catalog cards' `TitleHoldMenuItems`, not the episode shelf, but it is the same `.contextMenu` mechanism. |
| P3-11 | **Fixed** | `PosterCard.swift:154-161`, the `PlainLabelRingTests` header and the `.manual` assertion, `SettingsViewModel.swift:56`. One leftover name: P3-3. |

## 3. Answers to the brief

**Badge-pack delete hand-off** (`NuvioTV/Screens/Settings/StreamBadgesSection.swift:93-99`).
- `next` is read before the delete, from the same order the `ForEach` uses. Both `@FocusState`s now live on the section. `BadgeUrlEntryRow` takes a `FocusState<Bool>.Binding` and reads `wrappedValue` for its platter and explainer (`:121`, `:134-137`). That is the same shape as this branch's plugin row (`SourcesSettingsPane.swift:594-610`), which the sim walked (`w7-plugin-*`).
- **Ordering.** `imports` reaches Swift through `FlowWatcher` on `Dispatchers.Main` (not `.immediate`), so the delete's emission is queued on the main queue before the hand-off block. Both run in the same drain, and SwiftUI applies the row removal and the focus write in one update. The target therefore exists both before and after the removal.
- **If the next pack row is not laid out.** A `@FocusState` write to an unrealized `List` cell is dropped. Focus then goes wherever the engine puts it when the Delete row leaves: the pre-fix behaviour, no worse. The target is the row directly below the focused Delete row (the next pack row, or the URL field after the last pack), inside the List's focus-scroll margin, so in practice it is realized. To harden it: keep the target in `@State` and re-assert it once in `.onChange(of: badges.imports.map(\.sourceUrl))`. Optional; device check §5.5.

**`episodeKey` = the shared `watchedKey` tail** (`NuvioTV/DesignSystem/TitleHoldMenu.swift:243-246`; `testEpisodeKeyIsTheSharedWatchedKeyTail` pins it against `WatchingPoliciesKt.watchedKey`).
- `DetailViewModel.computeWatchedEpisodeKeys` (`:835-860`) checks the mark through `WatchedRepository.isWatched` with the same nil. `watchedItemKeys` turns that into `-1`, the key `toggleEpisodeWatched` stores (`toEpisodeWatchedItem` keeps `video.season` as nil).
- The progress lookup uses the shared `buildPlaybackVideoId` rule (`:844-851`): `id:s:e` with both numbers, else `episode.id`. `resolveProgressForVideo` treats a nil season or episode as a wildcard and matches on `videoId`, the id `EpisodesSection.episodeVideoId` plays under. Nit: `isEmpty` against the shared `isNotBlank`; irrelevant.
- `EpisodesSection.isWatched` (`:404-407`) and both menus (`:483-486`, `:511-513`) all key through `episodeKey`.
- **No Detail/player mismatch.** `PlayerPlaybackColumns.sortedEpisodes` (`Screens/Player/PlayerPlaybackColumns.swift:67-75`) drops every entry without both numbers before keying, so the player's list never shows such an episode. `EpisodeSpoilerRules.airedUnwatchedCount` (`Screens/EpisodeSpoilerRules.swift:61`) skips them as before, so the "N aired unwatched" count never counted them. Both-number keys are `"s:e"` everywhere, unchanged.
- **Behaviour change worth a release-note line:** in Detail, an episode with only one number now gets the watched tick, the spoiler reveal, the rating rule and the next-up skip once marked or completed. Before, it never did.

**Language page:** one scroll, no second scroll while the row is realized, no state carried across pushes (§2 P3-1). Focus pull on Back: P3-1 above.

**MainActor.** The new `nonisolated static` helpers (`seasonsWithReleasedEpisodes`, `packFocusAfterDeleting`, `isOff`, `episodeKey`) are pure or call Kotlin only. The backstop is `Task { @MainActor in }`. There is no `Task.detached` and no new `@State` box holding a closure.

**Whole-branch sweep.** The fix pass touched only the files in §2. `MPVPlayerView`, `NativePlaybackCoordinator`, `ServicesSettingsPane`, `SourcesSettingsPane` and `AddonsView` are identical to r1's tip. No new string apart from the dotted key. Gate on record (outer `docs/open-items-plan-2026-10-21.md:71`): Debug and Release sim green, the UI target compiles, NuvioTVTests 2166 / 0. Kotlin is untouched, so the Kotlin legs stand as at base. The code docs cite `docs/research/wave3b-sim-2026-10-21/` in the outer repo, which is untracked; stage only the cited `wb-*` files after a look, never the directory (Sources/Appearance shots show URLs).

## 4. New string keys (catalog + MT pass; none is in `Localizable.xcstrings`)

1. `Fallback Audio Language` (`SubtitlesAudioSettingsPane.swift:50`)
2. `Fallback Subtitle Language` (`:71`)
3. `None` (`SettingsRowViews.swift:1165`): a language choice (fr "Aucune")
4. `Mark Episode Unwatched` (`DesignSystem/TitleHoldMenu.swift:199`)
5. `Mark Previous Episodes Unwatched` (`:201`)
6. `Mark Previous Episodes Watched` (`:202`)
7. `Mark %@ Unwatched` (`:204`): `%@` is "Season 2" / "Specials", already localized
8. `Mark %@ Watched` (`:205`)
9. `If the video has no audio track in your Audio language, picks one in this language instead. None by default.` (`SettingsDescriptions.swift:393`)
10. `If no subtitle track is in your Subtitles language, picks one in this language instead. None by default. Hidden while Subtitles is Off, which always stays off.` (`:394`)
11. `settings.language.original`: `defaultValue` "Original", comment "Audio language choice … Not the sort order." (`SettingsRowViews.swift:1158`). Hand-write it with an `en` unit (P3-2).

The `Text("…")` literals for 9 and 10 go through `LocalizedStringResource`; all eleven reach the `Localizable` table.

## 5. Device checks for the owner

Run in the **Test 2** profile and name it before each step. Run `scripts/device/ready.sh` first; if it refuses, stop. Everything set below syncs to Test 2: put it back afterwards.

1. **FEAT-84 page (r1 P3-1 and r2 P3-1).**
   - Note Test 2's Audio value. Set Audio to Zulu, leave, and reopen the Audio page: it opens on Zulu. The first Up moves ONE row (Welsh, as in the hand walk `wb-12-manual-walk.txt`), not five or six (Turkish, wb-10).
   - Repeat with a middle value (English) and a top value (Device).
   - Reopen and press Menu as soon as the page settles: focus returns to the Audio row.
   - Select on the checked row pops without a change.
   - Restore Audio.
2. **OLED (r1 P2-1).** OLED on: each language page (Audio, Fallback Audio, Subtitles, Fallback Subtitle, Sources > Metadata Language) and Custom Posters are pure black. OLED off: the app grey. If P3-4 lands, MDBList > Library lists too.
3. **Fallback Subtitle row** is hidden with Subtitles Off and back with any language.
4. **VoiceOver** on one list-picker row: the value is read once.
5. **Badge packs (r1 P3-7).** Import two dummy packs.
   - Delete the first: focus lands on the second pack's row.
   - Delete the last: focus lands on the URL field, and the field shows its focused platter.
   - Leave no dummy pack behind.
6. **FEAT-83 (r1 P3-2, P3-8, P3-9).**
   - Mark and unmark an episode: focus stays on the held card.
   - After an action, leave the remote alone for more than 1 s, then go Up to the season row and Down again: you land on next-up.
   - Hold on a season with nothing released: nothing opens, and a plain press still selects the season.
   - If an add-on in Test 2 numbers episodes with one number only (some anime add-ons), mark one: the tick appears in Detail.
   - Leave nothing marked.
7. **Still owed from r1 §6:**
   - BUG-200 cast avatars and studio chips in all three focus settings.
   - BUG-201 swatches, with Reduce Motion as well.
   - BUG-213 key rows: TMDB, MDBList, debrid, plugins.
   - BUG-214 Add-ons with OLED.
   - BUG-215 (Default and Minimal).
   - FEAT-84 playback on mpv and native: Off stays off; the fallbacks load.
   - Reset both fallbacks to None. Shoot 4K/HDR last.

**Verdict: FINDINGS: P1 0 / P2 0 / P3 4** (P3-1 focus guard, P3-2 dotted-key catalog entry, P3-3 stale docs, P3-4 MDBList background, pre-existing). No blocker: merge once each P3 is fixed or declined with a reason and the §5 device checks pass.
