# Wave 3b critique (W3-4 … W3-10, GitHub #9 / #10), 2026-10-21

Read-only Opus critique of `docs/wave3-github-9-10-plan-2026-10-21.md`. It was checked against the clone `NuvioMobile-wave3b` on `claude/wave3b` @ `823450355`; that is the same tip as the plan's `claude/wave3`. Swift paths are relative to `iosApp/NuvioTV/`. Kotlin paths are relative to `shared/src/commonMain/kotlin/com/nuvio/app/`. Bridged Swift names come from the SharedCore header built in `NuvioMobile-wave3` at the same tip.

## Verdicts

| Item | Verdict |
|---|---|
| W3-4 BUG-200 | **The plan needs changes.** The symptom exists only in the default cell (ring off, zoom on), on both rows. Ring mode already moves the cast caption with the artwork, and the studio chip has no caption. `:3259` is the static band shrink, not the lift. Moving the scale to the outer `VStack`, or putting `DetailTileFocusLift` on the whole tile, brings back BUG-54/BUG-36. The fix is a one-cell change: default mode → `.systemLift` on the avatar and the capsule, with the caption drop. |
| W3-5 BUG-201 | **Holds, with one addition.** Copying the Appearance ring leaves a gap: a swatch that is focused AND selected looks the same as one that is only selected, and focus usually lands on the selected swatch. Add `SwatchFocusLift`'s scale and shadow. Check first that each swatch is its own focus target. |
| W3-6 FEAT-83 | **The plan needs changes.** Season and previous-episode actions must use the shared released-episode lists. "Every episode of that season" marks unaired episodes as watched and syncs them. No `DetailViewModel` wrappers are needed. The season chip row is missing from the plan. Focus can jump after an action. |
| W3-7 BUG-213 | **The shape holds.** Add the focus hand-off: Save swaps both rows out today, and Remove swaps them back. Add `ServicesSettingsPane.swift` to the file list. The badge pack row is a second multi-control row. |
| W3-8 BUG-214 | **Holds.** |
| W3-9 BUG-215 | **The plan needs changes.** The root and the panes have identical geometry, and the root does not clip on the device, so the diagnosis is unproven. `SettingsRowChromeMetrics` has no lift value. `.listRowInsets` does not move the focused cell. Use `.contentMargins` once a clip is reproduced. |
| W3-10 FEAT-84 | **The plan needs changes.** The shared list has **78** codes, not 74. Stored codes are normalized to lowercase, so `pt-BR`, `zh-CN` and `zh-TW` never show as selected. The TMDB readback truncates to the primary subtag. Locale labels come back lowercase in French. The computed `static var`s make label lookup O(n²). The Off guard is right; it belongs in one helper. |

## 1. Drift

| Plan says | Actually |
|---|---|
| `CastCard` `DetailView.swift:2622` | call site `:2622` in `castRow` (`:2605`, `LazyHStack(spacing: .lg)` `:2613`); struct `:3212` |
| ring mode "draws its own lift on the avatar circle (`:3259` `scaleEffect`), caption outside it" | `:3259-3261` is the **static, never-focus-linked band shrink** (BUG-64 `ringInset` rule). The lift is `CardArtworkFocusLift` `:3269-3279`, and the caption **already drops** with it (`CardCaptionFocusDrop` `:3297`, BUG-108). |
| `CompanyChip` `:2800+`, "the chip and any caption lift together" | call `:2821` in `companyLogosRow` `:2790`; struct `:3352`. It has no caption (`:3429`: "No `CardCaptionFocusDrop`"). |
| cast caption frame "at ×1.12" | the cast ring-mode scale is `1 + 2·20/140 = 1.286` (`cardLiftScale`, `DesignSystem/PosterCard.swift:485`). 1.12 is the chip's ceiling only (`smallLabelScaleCeiling` `:412`). |
| `SubtitleColorSwatch :165`, "and the background / outline colour rows if they share it" | `:165` is correct. The only use is Text Color (`:78-89`). Background is a `SettingsPickerRow` (`:99`) and Outline a toggle (`:113`). |
| Appearance swatch `:555-590` | `SwatchLabel` `:551-596`, inside `ThemePickerRow` `:497-548` (horizontal `ScrollView` at `:515`) |
| episode button `:140-153` | `Button` `:137`, chain `:151-160` (`.focused` `:153`, `.id` `:154`) |
| season button `:416-429` | `SeasonPosterRow` `:397`, Button `:413-438`. The plan misses the text season chips (`:100-106`), used by titles without season posters. |
| `HoldPlayChooseSourceMenu` `:3496` | `:3499` |
| `watchedEpisodeKeys` `:48`, "recomputes after each (`:584`)" | Correct, and already **flow-driven**: `watchedWatcher` and `progressWatcher` (`:230-246`) call `refreshFlags()`. No manual call is needed. |
| `DebridKeyEntryRow` `:793` | `:835-882` |
| call sites Sources `:126/203` | Sources `:130` (TMDB), `:207` (MDBList), Services `:449` |
| Plugins row `~540-575` | `PluginRepoEntryRow` `:553-594`, glass `:571`, `.borderedProminent` `:590`. Its call `:397` carries W3-2's `manifestFieldFocused` and the reconcile `.onChange`/`.onAppear` (`:405-406`). |
| Stream Badges import row, "confirm its shape first" | `BadgeUrlEntryRow` `StreamBadgesSection.swift:95-136`: the same field + button `VStack`, glass `:114`, `.borderedProminent` `:132`. The per-pack row `:50-80` has two buttons (Set Active and trash) in one List row. |
| `AddonsView.swift:13`, "twelve other screens" | Correct. About 20 sites draw the background. |
| `SettingsPaneScaffold.swift:45-58` | Correct. `SettingsRootView.swift:86-96` has the **identical** `HStack` + explainer + `List` geometry. |
| lift "from `SettingsRowChromeMetrics`" | `SettingsRowViews.swift:130-152` holds insets, radius, rest fill and `tintsMenuPill`, and **no lift value** |
| `LanguageOptions.languages` `:848`, 13 codes | `:896-925`, 13 codes (all in the shared list) |
| `AvailableLanguageOptionCodes` 74 | **78** (`player/PlayerLanguageOptionCodes.kt:6-85`): 74 bare codes plus `zh-CN`, `zh-TW`, `pt-BR`, `es-419` |
| pickers `:37/:44`, Sources `:160` | `:34-47`; Sources `:158-167` |
| players `MPVPlayerView.swift:1278`, `NativePlaybackCoordinator.swift:371` | Correct. Five non-selecting consumers of the secondary are not named: MPV `:1820/:1824`, Native `:331`, StreamPicker `:1773/:1785` (§W3-10 c). |
| descriptions in `SettingsExplainerModel.swift` | They live only in `SettingsDescriptions.swift` (enum `:22`, copy `:383-390`). |
| `NuvioTVUITests.swift:9615` | The Sources walk is `:9617-9622`: up to 24 Down presses to `settings.searchRowsMode`. |

## 2. W3-4 (BUG-200): Cast and Production rows

**What the code does, per cell.** `CardButtonStyleKind.resolve` is at `PosterCard.swift:209`, and `PlainLabelRing.lift` at `:391`.

| Cell | Button style | `CastCard` | `CompanyChip` |
|---|---|---|---|
| Default (ring off, zoom on) | `.borderless` | `artworkLift` (`:3233`) = `PlainLabelRing.lift` → `.still`, which is the no-op branch of `CardArtworkFocusLift`. `.borderless` lifts **only the `Image`** inside `CachedAsyncImage` (10-17 device finding; comment at `ProfileSelectionView.swift:598-601`). So the photo grows inside its static circle clip, and the caption drop is 0. | Only the logo `Image` lifts; the white capsule (`:3388`) stays put. A name-fallback chip (Text only) gets **no focus cue at all**. |
| Ring on, zoom on | `RingCardButtonStyle` | `.manualScale` 1.286 on the avatar. The caption drops 20 pt and follows. | `.manualScale` 1.12 on the whole capsule. |
| No Zoom | `StillCardButtonStyle` | Still ring; nothing moves, by design. | Still ring (dark neutral); nothing moves. |

So the defect is the default cell on both rows, as the #9 reply said ("only on the Accent Focus Ring path"). The plan's claim that "both paths show his symptom by construction" contradicts the code and the posted reply.

**Why the proposed fix is wrong.**
1. Moving `:3259` to the `VStack` shrinks the whole tile permanently by 132/140, and the ring then paints over the photo (BUG-64).
2. Moving `CardArtworkFocusLift(.manualScale)` to the outer `VStack`:
   - `manualLift` (`PosterCard.swift:882-899`) draws a black `RoundedRectangle(cornerRadius: 70)` with a 22 pt shadow at the **attached** bounds. That puts a dark pill behind the name and role: the BUG-36/54 "slab behind the title".
   - The scale is derived from `artworkHeight` 140 but applied about the taller `VStack`'s centre. The top edge then rises about 29 pt, not 20, and breaks the one-number contract with `CardCaptionFocusDrop` and `heroPinnedRowFocusLiftAllowance`.
   - The caption text gets scaled ×1.286. The HIG carve-out allows the manual scale only to carry the ring.
3. `DetailTileFocusLift` "as `EpisodeThumbCard` does" is not a whole-tile lift. `EpisodeThumbCard` puts it on the **artwork container** and drops its title separately with `CardCaptionFocusDrop(CardFocusMode.resolve…)`: "artwork lifts, caption follows". On a whole tile:
   - Its ring-off branch is `TileFocusLift`'s `.hoverEffect(.highlight)` on bounds that include the caption: the BUG-54 standing platter around avatar and name at rest.
   - Its No Zoom branch adds a rounded-rect still ring plus a shadow around the whole tile, on top of `CastCard`'s own circle ring: two rings.
   - Its ring branch applies the per-axis `bandScale` to the capsule, which `CompanyChip` `:3389-3398` rejects, and the flat 20 pt rise, which makes a 52 pt chip ×1.77 (the reason BUG-111 exists).
4. No zIndex work is needed. The new default cell is a system lift (`raisesFocusedCard == false`, its own layer), and the other two cells are unchanged.

**Smallest correct fix (`DetailView.swift` only).** `CastCard.artworkLift` (`:3233`) and `CompanyChip.artworkLift` (`:3369`) return `CardFocusMode.resolve(accentFocusRing:noZoomOnFocus:)` instead of `PlainLabelRing.lift(...)`.
- They differ in one cell: default → `.systemLift`. `CardArtworkFocusLift` (`:861-874`) renders that as `.compositingGroup()` + `.contentShape(.hoverEffect, RoundedRectangle(cornerRadius:))` + `.hoverEffect(.highlight)` on the avatar circle (radius 70) or the capsule (radius 26). That is `PosterCard`'s own default treatment under the same `.borderless` button (`PosterCard.swift:1026/1164`), proven on the device.
- `CastCard`'s existing `CardCaptionFocusDrop` (`:3297`) then drops name and role 20 pt in default mode too.
- The ring and No Zoom cells stay byte-identical.
- It is the system treatment, so it meets the HIG contract's default-mode MUST.
- **Drop plan Default 3** (the whole tile scales and captions skip the drop idiom). Use the drop idiom every other card uses. The reply promised "lift as one tile", and caption-follows delivers that.

**Doc and test fallout.**
- The doc on `PlainLabelRing.lift` (`PosterCard.swift:380-390`) and `PlainLabelRingTests.testPlainLabelNeverAsksForTheSystemHoverEffect` (`:67`) assume `.borderless` lifts the whole label. The 10-17 finding showed that is false.
- Leave `PlainLabelRing.lift` as it is for `FolderTile` (`CollectionsUI.swift:574`) so those tests stay green. Put the new resolver in `DetailView.swift` (e.g. `enum DetailLabelLift`) with its own test, and fix the doc wording only.
- `FolderTile` probably shows the same default-mode artifact. File a tracker row; it is out of scope here.

**Measure before landing** (sim, with test44's edge finder): the system lift on the 140 pt circle and on the 52 pt capsule.
- BUG-64's constant-rise model (20 pt, measured at 330 and 403 pt) gives the avatar ×1.286. That is 20 pt growth per side; the tile is 150 wide and the gap is 24, so it clears the neighbour's avatar by 9 pt. Fine.
- The same model gives the chip ×1.77, about 81 pt per side on the widest 212 pt chip against a 16 pt gap: overlap.
- If the chip measures above about 1.15, the fallback is the chip's own `.manualScale` + `smallLabelRise` in the default cell too. That needs a new `CardButtonLift` case so `CardFocusButtonStyle` drops `.borderless` there (`PosterCard.swift`, outside A1's file list and shared by every card) and a HIG-contract carve-out line. Decide on the sim numbers and record it in the review.
- On the device, confirm the standing platter (BUG-54: it follows the attached bounds) shows no square corners around the 140 pt avatar, at rest or focused.

## 3. W3-5 (BUG-201): subtitle swatches

- Confirmed: `@Environment(\.isFocused)` (`:171`) is never read, and the stroke tracks `isSelected` only.
- `SwatchLabel`'s rule (`:569-574`) checks `isSelected` before `isFocused`, so a **focused, selected** swatch shows no change. Focus usually lands there. On hardware `.borderless` gives a plain `Circle` nothing; `SwatchFocusLift` (`ProfileSelectionView.swift:602-612`) was added for exactly this.
- Fix:
  - Ring as `SwatchLabel`, using `strokeBorder` rather than `stroke`.
  - Plus a private copy of `SwatchFocusLift`: ×1.2 scale + shadow, 4.6 pt growth inside the existing 8 pt padding (`:183`). Do not touch `ProfileSelectionView.swift`.
  - Gate the animation on Reduce Motion (Motion row of the contract). `SwatchLabel` `:590` does not; don't copy that.
- Step 0: `controlRow` (`:141-149`) puts four Buttons in one List row, and the 10-17 review lists this row among the multi-control rows. On the sim and the device, check that Left/Right walks the four swatches and the explainer shows "Text Color". If the row is one focus target, wrap the `HStack` in a horizontal `ScrollView` like `ThemePickerRow` (`:515`), which is proven on the device.
- The only use is Text Color, so there is only one site to change.

## 4. W3-6 (FEAT-83): hold menu on season and episode covers

- **Bridging** (header): `WatchingActions.shared.toggleEpisodeWatched(meta:episode:isCurrentlyWatched:)`, `togglePreviousEpisodesWatched(meta:episodes:areCurrentlyWatched:)`, `toggleSeasonWatched(meta:episodes:areCurrentlyWatched:)`.
  - `episodes` is Kotlin `Collection<MetaVideo>`, which reaches Swift as `Any`. Pass a `[MetaVideo]` (bridged to `NSArray`, read as a Kotlin `List`). Nothing checks this at compile time; a wrong type is a Kotlin `ClassCastException` at runtime.
  - All three take an explicit flag. Pass the **label's** state (the `watchedAction(isWatched:)` rule) and never re-read the live state.
  - No Kotlin enum is involved.
- **Use the released lists, as mobile does** (`composeApp/.../MetaDetailsScreen.kt:1060-1171`): `meta.releasedEpisodesForSeason(seasonNumber:todayIsoDate:)` and `meta.previousReleasedEpisodesBefore(target:todayIsoDate:)` (`watched/WatchedEpisodeActions.kt:58-74`, bridged on `MetaDetails`), with `CurrentDateProvider.shared.todayIsoDate()`.
  - The plan's "every episode of that season" would mark unaired episodes watched and sync them to Trakt/Simkl.
  - It would also leave any season with an announced episode reading "unwatched" forever, so the label and the toggle direction would diverge from mobile.
- **Season watched** = the released list is non-empty and every released `"s:e"` is in `watchedEpisodeKeys`. Those keys already include completed progress (`DetailViewModel.swift:833-851`), the same rule as mobile's `areEpisodesWatchedForActions`. With no released episodes, leave the item out (the shared toggle returns early on an empty list).
- **Previous**: mobile omits it on the first episode and flips the label to "Mark previous as unwatched" once all previous episodes are watched. Take that rule, or define mark-only explicitly (always pass `false`, hide when all are watched). The list spans earlier seasons.
- **No `DetailViewModel` change.** `EpisodesSection` already has `meta` and `watchedEpisodeKeys`. A menu-items view can call `WatchingActions.shared` directly, as `TitleHoldMenuItems` calls the repositories (`TitleHoldMenu.swift:224-319`). The keys refresh through the watchers. This drops `DetailViewModel.swift` and the `DetailView.swift:742` threading. The plan's W3-6 file list omits `DetailView.swift`; that only matters if wrappers stay.
- **Placement.**
  - Episode: `.contextMenu` after `.focused` (`:153`) and before `.id` (`:154`), the Continue Watching precedent (`HomeView.swift:5302`), attached unconditionally.
  - Season: `SeasonPosterRow` (`:413-438`) has neither `meta` nor episodes. Pass a closure or builder.
  - Build the released lists **inside the menu-items view body**, which is evaluated at presentation (`TitleHoldMenu.swift:240-243`), never in the row body. The row body re-runs on every Left/Right (BUG-153).
  - Attach the same modifier to the text season chips (`:100-106`), or say why not.
- **Focus after an action.**
  - Marking the next-up episode changes `nextUpId`. `.onChange(of: nextUpId)` (`:190-197`) scrolls when `focusedEpisodeId == nil`, which is probably true while the menu holds focus.
  - `.defaultFocus(..., priority: .userInitiated)` (`:202`) may then pull focus to the new next-up on return.
  - Record the acted-on id, skip the scroll until focus returns to it, and check on the device where focus lands.
- **Docs and strings.**
  - `TitleHoldMenu.swift:16` says the menu is "Deliberately NOT attached to … episode cards". Update it.
  - Reuse the existing "Mark Episode Watched" key (`:123`) so its translations carry over.
  - Mobile's English is sentence case ("Mark as watched", "Mark %1$s as watched", `strings.xml:1346-1352`), so the populate script's exact-English harvest finds nothing for Title Case keys. Plan an MT pass (fr matters).
  - Season items: use `EpisodesSection.seasonLabel` so Specials reads right.

## 5. W3-7 (BUG-213): key field and Save in one row

- A `Group` body keeps `@State key`: the state belongs to the struct, and the List flattens its body into rows (the 10-18 "Group body" precedent).
  - `saveFocused` becomes dead.
  - The field row keeps `SettingsRestPlatter(explicitFocus: fieldFocused)`.
  - Make Save a kit row (`Button { } label: { SettingsRowChrome { SettingsRowLabel(...) } }`, as the repo header `SourcesSettingsPane.swift:432-451` does) so it gets the rest platter and ink flip.
- **Focus after Save is broken today, and the split keeps it broken.**
  - Sources: TMDB/MDBList `onSave` flips `tmdbHasPersonalKey`/`mdbListHasPersonalKey`, and the `if/else` (`:119-142`, `:185-224`) swaps both rows for "Remove … Key".
  - Services: `saveManualKey` swaps the rows for "Connected" (`:389-399`).
  - In both panes the focused Save leaves the hierarchy. This is the 10-17 open item "Settings Save Key", and the plan's "keep the never-disable guards" does not cover removal.
  - Fix with `ClaimsFocusAfterSwap` (`DesignSystem/FocusRow.swift:29`), set from the call site's `onSave` closure, so `DebridKeyEntryRow`'s API does not change. Services already has `activationFocusHandOff`/`handOff(_:)` (`:18-26`); Sources needs a `@State` flag. Do the reverse direction too (Remove → field).
  - **Add `ServicesSettingsPane.swift`** to the file list.
- **Plugin row**: split the same way.
  - Drop the glass (`:571`) and the `.padding(.lg)`; use `SettingsRestPlatter(explicitFocus: fieldFocused.wrappedValue)`.
  - Make Install a kit row with the `ProgressView` in `trailing:`.
  - Keep W3-2's `manifestFieldFocused` on the field.
  - The call-site `.onChange`/`.onAppear` (`:405-406`) will apply to both rows of the multi-row body, so `reconcilePendingRemoval` runs twice. That is safe because it clears pending first. Re-run W3-2's removal-focus device check.
- **Badges**: `BadgeUrlEntryRow` gets the same split. The per-pack row (`:50-80`, Set Active + trash) is the same defect class and appears in the 10-17 list. A2 owns the file: fix it, or file a row.
- **Step 0**: if Test 2 already has a TMDB personal key, the entry row is not shown; use MDBList or a debrid row instead. A dummy key syncs with the profile, so remove it before leaving.
- **UI test**: test95 (`:9617-9622`) has a budget of 24 Down presses. The split adds one row per visible key entry, so re-check the budget.

## 6. W3-8 (BUG-214): Add-ons background

Holds. Put `.background(Theme.Palette.background.ignoresSafeArea())` on the `ScrollView` inside the `NavigationStack` (`AddonsView.swift:14`), as `SettingsView.swift:84` does. Add-ons pushes no destinations. The root `.id(paletteKey)` (`AppThemeModel.swift:110-127`) rebuilds it on an OLED flip.

## 7. W3-9 (BUG-215): clipped pane row

- The root (`SettingsRootView.swift:86-96`) and the pane (`:45-59`) share identical geometry. The root is whole on the device. So "the lift grows past the List's bounds" is either sim-only or tied to a row type.
  - Step 0 must also shoot the **root on the sim**; erdist is on the sim.
  - If the root clips on the sim, the fix goes in both files. `SettingsRootView.swift` is outside A2's list.
  - If only panes clip, find the row type first. Candidates: the `SettingsPickerRow` Menu pill, the `TextField` rows, the custom swatch and plugin rows.
- There is no lift constant. Measure the system row lift from a screenshot, or pick a fixed margin.
- `.listRowInsets` moves the content, not the focused cell (the platter scales with the cell), so it cannot fix a clip.
  - Use `.contentMargins(.horizontal, m, for: .scrollContent)` on the List, and take `m` off the `HStack` spacing in Default.
  - Not `.scrollClipDisabled()`: rows scrolled past the top would draw over the pane title.

## 8. W3-10 (FEAT-84): languages, fallback rows, Off stays Off

**(a) The list.**
- **78 codes.** Audio and subtitle pickers get 80 entries; TMDB and the fallback rows get 79. The posted #10 reply says "74"; correct it in the post-landing comment and in the release notes.
- **Stored values are normalized.** The setters (`player/PlayerSettingsRepository.kt:487-522`) run `normalizeLanguageCode`, which lowercases through `LanguageCodeAliases` (`player/PlayerLanguagePreferences.kt:14-48`): `pt-BR`→`pt-br`, `zh-CN`→`zh-cn`, `zh-TW`→`zh-tw`.
  - With the raw codes as `options`, those three never get a checkmark, and the trailing value prints the raw code.
  - Build each option code as `PlayerLanguagePreferencesKt.normalizeLanguageCode(language:)` of the shared code, and label it from the original tag.
- **TMDB.** `tmdbLanguageSelection` keeps only the primary subtag (`SettingsViewModel.swift:232-235`).
  - So `zh-CN`, `zh-TW`, `pt-BR` and `es-419` read back as `zh`/`pt`/`es`, and the checkmark lands on the wrong row. TMDB has no `es-419` either.
  - Either TMDB takes the 74 bare codes, or the readback keeps the full tag when it is an option. Mobile's TMDB language is a free-text field, so neither choice breaks parity.
- **Labels.**
  - `localizedString(forIdentifier:)` returns lowercase names in fr/es/it/pt/vi ("anglais"), and Steven runs French. Capitalize the first letter with the locale.
  - Sort with locale collation (`localizedStandardCompare`), not `<`.
  - Use the app's UI locale (`Bundle.main.preferredLocalizations.first`), not `Locale.current`. Otherwise a device language the app doesn't ship (e.g. ja) puts Japanese names into an English UI.
  - `zh-CN`/`zh-TW` render as "Chinese (China)/(Taiwan)". Consider labelling them through `zh-Hans`/`zh-Hant` ("Chinese, Simplified/Traditional") and keeping the codes.
- **Performance.**
  - `audio`, `subtitle` and `tmdbMetadata` are computed `static var`s. `name(forCode:in: LanguageOptions.audio)` inside `label:` rebuilds and re-sorts the list for every option the Menu draws: O(n²), about 6,400 ICU lookups per menu.
  - Make them `static let` (a language change relaunches the app) plus a code→name dictionary.
  - Keep `name(forCode:in:)` for `librarySourceLabels`/`watchProgressSourceLabels` (`SourcesSettingsPane.swift:278/289`).
  - Make the pure builder `nonisolated`, with an injected `Locale`. The test target is not MainActor-default.
- **80-entry Menu.** It is unverified whether a tvOS `Menu { Picker }` opens focused on the checked entry. If it opens at the top, Zulu is about 79 swipes away; then use the pushed page with `.defaultFocus` on the current value.
- **Synced sentinels.** Player settings sync per profile (`PlayerSettingsStorage.apple.kt:988/1067`), and mobile's dialogs (`PlaybackSettingsPage.kt:1159-1235`) can store values tvOS has no option for: primary audio `default`, subtitle `forced`, secondary audio `original`. Today those show as raw codes. Add **Original** to Fallback Audio (mobile parity) and label unknown sentinels.

**(b) The rows.**
- Swift names: `PlayerSettingsRepository.shared.setSecondaryPreferredAudioLanguage(language:)` and `setSecondaryPreferredSubtitleLanguage(language:)` (nil = None). The UI state carries `secondaryPreferredAudioLanguage` / `secondaryPreferredSubtitleLanguage` as `String?`.
- `SettingsViewModel` needs two `@Published` mirrors, assigned in the player watcher (`:184-195`).
- `SettingsPickerRow<T: Hashable>` needs a non-optional `T`: use `""` for None and map it to nil.
- Add new `SettingsDescriptionID` cases. `SettingsDescriptionsTests` scans for usage, so each new ID must be used.

**(c) Off stays Off.**
- The guard is correct and sufficient for auto-selection. With primary `none` and the secondary passed as nil, mpv's `MPVSubtitleAutoSelectGate.decide(noTargets:)` returns `.off(final: true)` (`Screens/Player/MPVSubtitleSideLoadQueue.swift:127-134`), and native sets `subtitlesOff` (`:389`).
- Put the rule in one `nonisolated` helper, e.g. `SubtitleFallbackGuard.effectiveSecondary(primary:secondary:)`, compared against `SubtitleLanguageOption.shared.NONE`. Use it at both sites and unit-test it.
- What it does not cover: the secondary still reaches `filterAddonSubtitlesForSettings` and `preferredSubtitleTargetsForSettings` (MPV `:1820/:1824`, Native `:331`, StreamPicker `:1773/:1785`). These only filter and order lists. The native guard also empties `subtitleFilterLanguages` (`:376`), so with Off + a fallback + "Show only preferred languages" the native panel lists every embedded language while the add-on list keeps only the fallback language. Nothing auto-enables. Document it beside the upstream note.
- Hiding the row is safe: focus is on the Subtitles Menu when the row goes.

## 9. Risks

**P1**
1. W3-4 as written brings back BUG-54/BUG-36: a pill behind the caption, the standing platter around the caption, a double ring in No Zoom, a distorted chip, and the `:3259` misread.
2. W3-6 with all-episode lists marks unaired episodes watched, syncs them to Trakt/Simkl, and a season with an unaired episode never reads as watched.
3. W3-10 code mismatch: three normalized codes never select, and four TMDB regional codes read back wrong. Users see a missing or wrong checkmark and raw codes.

**P2**
4. W3-10 lowercase labels in French, Spanish, Italian, Portuguese and Vietnamese, and O(n²) label lookups.
5. W3-7 focus is thrown after Save and after Remove, in both directions, in Sources and Services.
6. W3-6 shelf scroll and `defaultFocus` after a hold action may move focus off the held card.
7. W3-4 chip system-lift size is unmeasured (overlap risk), and the avatar circle may show square platter corners.
8. W3-5 a focused, selected swatch shows no change, and the four swatches may be one focus target.
9. W3-9 fix aimed at an unproven cause; `.listRowInsets` is ineffective.
10. A1 and A2 run in parallel, and both would rewrite `Localizable.xcstrings` if both run the populate script.

**P3**
11. W3-10 sentinel and edge cases: mobile-synced sentinels show raw codes; with Subtitles Off, the hidden fallback still filters the lists; `Locale.current` can differ from the app locale; the zh labels; the 80-entry Menu.
12. Title Case keys do not harvest mobile's sentence-case translations, so an MT pass is needed.
13. Housekeeping and follow-ups: the test95 press budget, the `TitleHoldMenu.swift:16` doc, the `PlainLabelRing.lift` doc, the same default-mode artifact on `FolderTile`, and the badge pack two-button row.
14. `Collection<MetaVideo>` arrives in Swift as `Any`, so the element type is checked only at runtime.
15. Comms: the #10 reply says 74 codes; the list has 78.

## 10. Tests

New test files go in the NuvioTVTests synchronized group, with no pbxproj edit. Add `@MainActor` where a test touches MainActor-default symbols.

**Unit tests**
- `DetailLabelLiftTests` (W3-4), over all four cells:
  - The default cell is `.systemLift`, exactly where `CardButtonStyleKind` is `.borderless`.
  - The ring and No Zoom cells equal `PlainLabelRing.lift`.
  - `raisesFocusedCard` is false in the default cell.
  - The caption drop is 20 in both zoom-on modes.
- `TitleHoldMenuPolicyTests` additions (W3-6):
  - Episode action order and label flips.
  - Previous is omitted when there are no previous episodes, and its label flips when all are watched.
  - The season item is omitted with no released episodes.
  - A pure `seasonIsWatched(releasedKeys:watchedKeys:)`.
  - Each action follows its label; titles are non-empty.
  - The existing CW tests stay untouched.
- `LanguageOptionsTests` (W3-10):
  - 78 codes, with each picker's sentinels first in order, and no duplicate codes.
  - Every audio/subtitle option code is a fixed point of `normalizeLanguageCode`.
  - en_US order: Afrikaans first, Zulu last.
  - fr: capitalized first letters, sorted by French collation.
  - Every code gets a label.
  - The TMDB rule: bare codes, or the readback round-trip.
  - `name(forCode:in:)` still serves the Sources library labels.
- `SubtitleFallbackGuardTests`: `none` → nil; `device`/`en` pass the secondary through; nil stays nil.
- `SettingsDescriptionsTests` covers the new IDs automatically.
- Kotlin: `:shared:jvmTest` should be unchanged, since there is no shared edit.

**Sim**
- W3-4: ring off / ring on / No Zoom on both rows, plus a person-fallback avatar and a name-fallback chip. Measure the lift on the 140 pt circle and the 52 pt capsule.
- W3-5: the per-swatch walk, and focused vs selected vs focused+selected.
- W3-6: hold on an episode, a season poster and a season chip; check where focus lands after the action.
- W3-7: each row is its own target; Select on the field opens the keyboard; Save → Remove focus; Remove → field focus; W3-2's plugin removal → field focus.
- W3-8: OLED on and off.
- W3-9: root and Sources, in Default and Minimal styles.
- W3-10: where the Menu opens, the 80-entry scroll, and French labels (`-AppleLanguages "(fr)"`).
- test95 still reaches `searchRowsMode`.

**Device (Test 2)**
- The plan's list.
- No square platter at the avatar corners.
- Focus stays on the held episode.
- The dummy key is removed before leaving.

## 11. File ownership (A1 / A2 / B)

- **A1**: `DetailView.swift` (W3-4, plus W3-6 only if wrappers stay), `EpisodesSection.swift`, `TitleHoldMenu.swift`, new `DetailLabelLiftTests`, `TitleHoldMenuPolicyTests`. `DetailViewModel.swift` is not needed. Stay out of `PosterCard.swift` and `PlainLabelRingTests.swift` unless the chip fallback is needed. If it is, serialize with S1/S2: `CardButtonStyleKind` is shared by every card.
- **A2**: `SubtitlesAudioSettingsPane.swift` (swatch only), `AddonsView.swift`, `SettingsPaneScaffold.swift`, `SourcesSettingsPane.swift` (plugin row), `StreamBadgesSection.swift`. Add `SettingsRootView.swift` if the root clips on the sim.
- **B**: `SettingsRowViews.swift` (`DebridKeyEntryRow`, `LanguageOptions`), `SubtitlesAudioSettingsPane.swift` (rows), `SettingsViewModel.swift`, `SettingsDescriptions.swift`, `MPVPlayerView.swift`, `NativePlaybackCoordinator.swift`, new language and guard tests. **Add** `SourcesSettingsPane.swift` (the TMDB/MDBList hand-off, and the TMDB list or readback) and `ServicesSettingsPane.swift` (the debrid hand-off). Both run after A2, so there is no overlap.
- **Conflicts**
  - `Localizable.xcstrings`: A1, B and possibly A2 all add strings. No agent runs `populate-localizable-xcstrings.py`; one catalog pass plus MT runs after Wave B.
  - A1 and A2 run in parallel in one clone: one build at a time, under the build lock.
  - `SourcesSettingsPane.swift`: A2, then B. B builds on A2's split and must keep W3-2's `manifestFieldFocused` wiring.
  - `SubtitlesAudioSettingsPane.swift`: A2, then B, as planned.
  - A1 and A2 share no files.
