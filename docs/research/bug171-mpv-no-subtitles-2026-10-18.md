# BUG-171: "No subtitles" ignored on mpv (root cause, 2026-10-18)

Tracker row BUG-171 (P3). Steven, DM 2026-10-17 02:07Z, rc4 build 136, mpv engine: with Preferred
Subtitle Language set to "No subtitles", a subtitle track is still on when playback starts and he
turns it off by hand. He called the results "pretty random".

Read-only analysis. Code is read at `claude/batch-e` tip `8deb74005` (the queue-stall fix, now
committed), compared with rc4 `975a7010`. No device repro was run: mpv's own source settles the
behaviour (quoted below). The fix's device check is listed at the end.

## Root cause

Two things combine. Neither one is a bug by itself.

**1. tvOS asks mpv to always pick some subtitle.** `setupMpv()` sets `subs-fallback=yes`
(`iosApp/NuvioTV/Screens/MPVPlayerView.swift:931`, there since the first tvOS commit `ccf626ead`,
copied from the phone bridge `iosApp/iosApp/Player/MPVPlayerBridge.swift:483`). tvOS never sets
`slang` or `sid`, so `sid` stays `auto`. mpv 0.41 `player/loadfile.c` `select_default_track()`:

```c
// lines 572-575: empty slang → OS languages, os_langs = true (subs-match-os-language defaults to yes)
bool lang_match = !os_langs && mp_match_lang(langs, track->lang) > 0;            // 601: always false here
bool subs_fallback = (track->is_external && !track->no_default) || opts->subs_fallback == 2 || ...; // 602
...
if (subs_matching_audio && ((!pick && (forced || lang_match || subs_fallback)) || ...)) pick = track; // 606
```

`subs_fallback == 2` is "yes" (`options/options.c:636`; the default is 1, "default"). So at load,
any subtitle track counts as a candidate, and mpv keeps the best by `compare_track`, which favours
the device language because of `os_langs`. When the file has any embedded subtitle, one is on from
the first frame. Add-on subtitles are never part of this pick: they go in with
`sub-add <url> auto …` (`MPVPlayerView.swift:1845`, rc4 `:1517/:1524`), and in
`command.c cmd_track_add` the `auto` flag sets `t->no_default = true`, so they never auto-select.

So which track turns on depends on what the file carries (embedded subtitles or none, which
language, default flags). That is the "pretty random" Steven describes.

**2. The tvOS auto-selection never turns that pick off for "none".** For "No subtitles" with no
secondary language:

- `resolvePreferredSubtitleLanguageTargets` returns `[]`
  (`shared/.../player/PlayerLanguagePreferences.kt:344-349`).
- `resolveSubtitleAutoSelectionPlan` returns a NON-nil plan, `targets = []`, `NORMAL_ONLY`
  (`shared/.../player/PlayerTrackSelection.kt:100-139`). The plan is nil only when "Use forced
  subtitles" is on and the audio track is unknown. With forced on and the audio in a preferred
  language, the result is a `FORCED_ONLY` plan in the audio's language.
- `findPreferredSubtitleTrackIndex` over `[]` returns -1.
- rc4 (`975a7010` `MPVPlayerView.swift:1155-1161`): `if match >= 0 { sid = … } else if plan.mode ==
  .forcedOnly { sid = no }`. A NORMAL plan with no match does nothing, so mpv's pick from step 1
  stays on.
- Current tree: `MPVSubtitleAutoSelectGate.decide` (`Player/MPVSubtitleSideLoadQueue.swift:121-125`)
  returns `.wait` while side-loads run, then `.done`. The `.done` case (`MPVPlayerView.swift:1290`)
  leaves mpv's selection alone. The outcome is the same.

The phone's runtime and the tvOS native engine both handle the empty plan. The tvOS mpv port is
the one that drops it:

- Upstream compose runtime, `composeApp/.../player/PlayerScreenRuntimeTrackActions.kt:246-250`:
  `if (selectionPlan.targets.isEmpty()) { disableAutomaticSubtitleSelection(); … }`, and
  `:369-376` selects track -1 when anything is selected. The same file also disables on a nil
  plan (`:242-245`).
- tvOS native engine, `Screens/NativePlaybackCoordinator.swift:383-384`:
  `plan.subtitlesOff = shared.targets.isEmpty`. That clears the legible criteria (`:410-412`) and
  makes every non-forced rendition `AUTOSELECT=NO` (`:441`). On AVPlayer, "none" works.

## Does the queue-stall change alter it?

No. With the gate, the empty-plan case ends in `.done`, the same as rc4. The bug is still there at
`8deb74005`. The gate only delays the no-op: the decision stays open until the side-loads drain.
That changes nothing, since add-on files can never match an empty target list and never
auto-select anyway (`no_default`).

## Other cases from the same cause (same fix)

- Primary "none", "Use forced subtitles" ON, audio language unknown: nil plan → `return`
  (`MPVPlayerView.swift:1246`) → mpv's fallback pick stays. The tvOS comment calls this "leave mpv's
  own defaults untouched". With `subs-fallback=yes`, mpv's default is any track. Upstream turns
  subtitles off here.
- A preferred language with no matching track (e.g. French preferred, the file only has English)
  also ends in `.done` and keeps mpv's fallback (English). That is arguably intended ("show
  something"). It matches the phone, which also sets `subs-fallback=yes`, but upstream's runtime
  turns its own selection off only when the plan is empty or nil, not on a miss. **Not part of this
  fix.**
- Primary "none" plus a secondary language: targets = `[secondary]`, a normal plan. That is shared
  semantics on every engine. Not a bug.

## Proposed fix (not applied)

Put the rule in the gate so it can be unit-tested beside the existing gate tests:

1. `MPVSubtitleAutoSelectGate.decide` gets `noTargets: Bool`, checked first:
   `if noTargets { return .off(final: true) }`. An empty plan is final on the first walk: no load
   can change it.
2. In `autoSelectPreferredTracks` (`MPVPlayerView.swift:1240-1293`):
   - nil plan → `didAutoSelectSubtitles = true` + `sid=no` (upstream parity: forced on with an
     unknown audio language means off, not mpv's fallback pick);
   - pass `noTargets: plan.targets.isEmpty` (a `FORCED_ONLY` plan always has one target, so this
     only fires for NORMAL plans).
   The `.off` branch already writes `sid=no` once through `didApplyAutoSubtitleOff`. `final: true`
   latches `didAutoSelectSubtitles`, so a later user pick (`didUserSelectSubtitle`) is never
   overridden.
3. Ordering nit: the `guard !subInfos.isEmpty` at `:1236` runs before the plan. For an empty plan
   with no subtitle tracks yet there is nothing to turn off, so the existing early return is fine.
4. Optional, removes a flash: mpv makes its pick at `loadfile`, and the first track walk runs
   ~0.05 s+ after FILE_LOADED. An embedded subtitle can draw for a moment before `sid=no` lands.
   If that shows on the device, also set the `sid` property to `no` before `loadfile` when
   `preferredSubtitleTargetsForSettings(settings)` is empty and `useForcedSubtitles` is off (both
   known synchronously in `setupMpv()`, next to the `alang` re-apply). Check first that nothing
   reuses the handle across files with a user's later `sid` pick; each playback builds its own
   handle today.
5. Do NOT change `subs-fallback=yes` globally: that would change the "preferred language missing"
   case above for every user.

Tests: `testGateNoTargetsTurnsSubtitlesOffAtOnce` (final, with side-loads still active), plus one
case each for `noTargets` ignoring a match and `sideLoadActive`. The `MPVPlayerView` wiring is not
unit-testable (same gap as `matchIsFinal`, noted in the queue-stall README).

Device check (Test 2 only, never Chris): Settings → Playback → Preferred Subtitle Language =
No subtitles, Use forced subtitles OFF; play a title whose file carries embedded full subtitles (a
remux) on mpv. Expected: no subtitle at start, the Subtitles tab shows Off, and a manual pick still
works. Repeat with Use forced subtitles ON. Before the fix, the same steps reproduce BUG-171.

## OUTCOME (2026-10-18 afternoon): built and device-checked, not merged

Christian's go, the same afternoon. Fix steps 1 and 2 above, on `claude/batch-e` (NuvioMobile),
committed locally on top of `8deb74005`. Not pushed, not merged, not cut.

- `Player/MPVSubtitleSideLoadQueue.swift`: `MPVSubtitleAutoSelectGate.decide(…, noTargets:)`
  returns `.off(final: true)` first.
- `MPVPlayerView.swift`: the nil-plan branch writes `sid=no` once (`didApplyAutoSubtitleOff`), and
  the gate call passes `noTargets: plan.targets.isEmpty`.
- Test `testGateNoTargetsTurnsSubtitlesOffAtOnce` (an empty plan is off and final even with loads
  running and a stray match).
- Optional step 4 (pre-`loadfile` `sid=no`) NOT built. The rig can't see a frame-level flash. If
  Steven reports one, add it.

Gates: NuvioTVTests 1853 / 0 failures (5 skipped); Debug device build green.

Device (Living Room Apple TV, profile **Test 2**, evidence `bug171-device-2026-10-18/`, console
redacted). Settings › Subtitles & Audio › Subtitles = **Off** (Test 2's existing value, `b5`). The
native player was switched OFF for the walk (`b9`) and back ON afterwards (`e6`). Played Lizzie
Borden Took an Ax, Comet "1080p AMZN WEB-DL … Rus.Eng.DD.5.1.mkv" (`c3`), on mpv (`c5`). The file
carries embedded `eng · Full (subrip)`, `eng · SDH (subrip)` and a CEA-608 track, plus three
OpenSubtitles add-on files. That is exactly the case where `subs-fallback=yes` turned on an English
track before the fix.
- Start: the Subtitles tab shows **Off** checked (`c6`). PASS.
- Manual pick `eng · Full`: it takes, and still holds 15 s later while add-on loads finish, with
  the subtitle on screen (`c8`). PASS.
- Clean exit to the Sources picker (`d2`, `terminate_destroy took=168ms`). Replay: **Off** again
  (`e1`). PASS.
- Not walked: "Use forced subtitles" ON. That row is hidden while Subtitles is Off. The nil-plan
  path only runs with it on and an unknown audio language, and it is covered by the code read only.
- No before/after A/B on the box: the pre-fix behaviour comes from mpv's source and Steven's
  report, not a replay of the old build.
