# GitHub #9 (BUG-200 / BUG-201 / FEAT-83) and #10 (untriaged) replies — drafted 2026-10-21 — POSTED

**Status: POSTED 2026-10-21 18:58:44Z / 18:58:45Z** on Christian's go: #9 https://github.com/youngchris29-art/NuvioTV/issues/9#issuecomment-6324076852, #10 https://github.com/youngchris29-art/NuvioTV/issues/10#issuecomment-6324077201 (`gh issue comment --body-file`), both verified identical to the drafts through the API (only the trailing newline differs). #5 held on his call. Was: NOT POSTED. Both issues are erdist's on youngchris29-art/NuvioTV: [#9](https://github.com/youngchris29-art/NuvioTV/issues/9) filed 2026-10-21T08:43:50Z (three items, triaged by the morning sweep as BUG-200, BUG-201, FEAT-83), [#10](https://github.com/youngchris29-art/NuvioTV/issues/10) filed 2026-10-21T14:39:27Z (four items, after the morning sweep, not yet in the tracker). Neither has a comment yet. erdist builds from source and tests on the tvOS simulator (#10 says so outright), and he attached the Plugins patch on #7, so "next build" to him means the next push to `tvos-shared-extraction`, not a public beta.

Post only on Christian's go: `gh issue comment <n> --repo youngchris29-art/NuvioTV --body-file <file>`, then verify through `gh issue view`.

Lint: both bodies 5/5 (`python3 scripts/deslop/deslop.py`); cleanse skipped (Codex quota out until 10-29).

Not owed right now, for the record: #3, #5, #6 and #8 have our comment last (the #5 refresh is in `docs/comms-github-issue5-reply-2026-10-21.md`); #4 ends on mikeyunk saying he will send the info; #7 ends on erdist's thanks with no ask. The "shipped" notes on #7 and #8 wait for the next public beta (rc11 is private).

## #9 — Detail Production/Cast focus, subtitle colour swatches, hold menu on season/episode covers

Facts behind the draft:
- BUG-200: the focused artwork lifts while the tile's own frame stays put, the BUG-108 class. The tracker records that class fixed for cast avatars and folder tiles **in ring mode** (`d1c3c7ee`, rc10 build 127). `Screens/Detail/DetailTileFocus.swift` keeps two paths (ring on: `RingCardButtonStyle`; ring off: the old `TileFocusLift`), so his Accent Focus Ring and No Zoom on Focus settings decide which path he is on. The Production (studios) row is not on either fix. Simulator vs Apple TV is unknown.
- BUG-201: `SubtitlesAudioSettingsPane.swift` draws Text Color as a custom `SubtitleColorSwatch` row whose ring marks **selection**; the Appearance theme swatches (`AppearanceSettingsPane.swift`, `ThemePickerRow`) carry their own focus treatment. Copying that over is the fix.
- FEAT-83: `DesignSystem/TitleHoldMenu.swift` already has `CWAction.markEpisodeWatched` on Continue Watching cards (Home), and shared `WatchingActions` has `toggleEpisodeWatched` and `toggleSeasonWatched`. The work is attaching a hold menu to `SeasonPosterCard` and `EpisodeThumbCard` in Detail.

What the draft promises: both rows lift as one tile on both ring settings; swatches get the Appearance focus treatment; the hold menu is "on the list for a coming build" (no build named). It asks three things: Accent Focus Ring on/off, No Zoom on Focus on/off, simulator or Apple TV.

```
Thanks, three good ones. In order:

Production and Cast rows. Confirmed from your screenshots: the picture lifts on focus and the item under it stays where it was, so the eye has to find the caption on its own. The Cast row got a fix for this a few builds back, but only on the Accent Focus Ring path, and the Production row never got it. Two questions so I know which path you are on: in Settings › Appearance, is Accent Focus Ring on or off, and is No Zoom on Focus on? And is this the simulator or an Apple TV? Either way I'll make both rows lift as one tile on both ring settings.

Text Color swatches. Agreed. The Appearance theme swatches have a focus treatment of their own and the subtitle swatches never got it. They get the same one.

Hold menu on season and episode covers. The pieces exist. The menu Continue Watching uses already has a Mark Episode Watched entry, and the shared code has the matching season action, so this is attaching that menu to the season posters and the episode cards on the Detail page: Mark Season Watched or Unwatched on a season cover, Mark Episode Watched or Unwatched on an episode. It's on the list for a coming build.
```

## #10 — Settings: key fields unfocusable, OLED on Add-ons, clipped focused row, languages

Facts behind the draft:
1. `DebridKeyEntryRow` (`Settings/SettingsRowViews.swift`) is a `VStack` of a `TextField` and a Save `Button` inside the pane's native `List`, with two `@FocusState`s (the V2 comment says "the row holds two focusables"). The #7 diagnosis we accepted (one List row = one focus target) applies to it as well. No device pass has typed a key through it (the Test profile is signed in, keys come from the account), so hardware behaviour is unverified. The TMDB and MDBList keys use the same row (`SourcesSettingsPane.swift:126/203`); the repository URL + Install and badge pack URL + Import rows are the same field-plus-button shape.
2. `Screens/AddonsView.swift` is a `NavigationStack` over a `ScrollView` with no `.background(Theme.Palette.background.ignoresSafeArea())`; the twelve other screens draw it. `Theme.Palette.background` is what `applyOled` swaps to pure black (FEAT-38).
3. Device screenshots from today's passes (`docs/research/wave3-device-pass-2026-10-21/17-settings-sources.png`, `docs/research/batch-p-w2-device-pass-2026-10-21/41-settings-down6.png`) show the root list's focused row whole on the Apple TV, lift included. The panes (`SettingsPaneScaffold.swift`: explainer column + `List` in an `HStack`) were not checked. The explainer column drops with Settings › Appearance › Settings Style = Minimal.
4. tvOS `LanguageOptions.languages` has 13 entries in no order (`SettingsRowViews.swift:848`); shared `AvailableLanguageOptionCodes` has 74. `MPVPlayerView.swift` and `NativePlaybackCoordinator.swift` already pass `settings.secondaryPreferredAudioLanguage` / `secondaryPreferredSubtitleLanguage` into shared track selection; no tvOS setting writes them. Shared `resolvePreferredSubtitleLanguageTargets` (`PlayerLanguagePreferences.kt:332`) returns the secondary even when the primary is NONE, so his edge case is real in shared and the tvOS setting has to guard it.

What the draft promises: field and Save split into separate rows (plus the two sibling rows); the Add-ons background line; a check of the panes on simulator and device; the full A–Z list; a fallback row under each picker; Off stays Off. No build named. It asks two things: which pane clips, and whether Minimal style still clips.

```
Thanks for the detail and the cause notes. They hold up against the code. One by one:

1. API key fields. Same shape as the Plugins block: the field and Save sit in one List row, and on tvOS a List row is one focus target, so Select lands on the row and not on the field. The row was written as two focus targets, so I want to see what hardware does with it, but the fix is the same either way: the field and Save become separate rows. The repository URL and Install row and the badge pack URL and Import row get the same pass.

2. OLED on Add-ons. Confirmed. Add-ons is the one tab that never draws the app background itself, so you see the system one, and the OLED switch only swaps the app's. One line.

3. Clipped focused row. On my Apple TV the root list's focused row stays whole, lift and all, so this may be simulator-only or pane-specific. Two things would help: which pane shows it, and whether it still clips with Settings › Appearance › Settings Style set to Minimal, which drops the explainer column. I'll check the panes on both.

4. Languages. Agreed on all three. The shared list has 74 codes and tvOS shows 13 of them, so the pickers get the full list, sorted A to Z. The fallback is the easy half: the tvOS player already reads the shared second preference for audio and subtitles, it just has no setting to write it, so that becomes a second row under each. And Off stays Off. The shared resolver would apply a subtitle fallback even when the first choice is Off, so on tvOS the fallback row only counts when a first language is chosen.
```
