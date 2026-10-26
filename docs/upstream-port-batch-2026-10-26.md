# Upstream port batch — 2026-10-26 (plan, NOT STARTED)

Source: `docs/upstream-port-plan-2026-10-26.md` addendum. Baseline upstream `7de46ead`, fork submodule `773e48732`. Four `shared/`-only ports, no new setting, no UI. Budget ~3 h wall, one session.

## Roles
- **Orchestrator (Fable):** runs this file top to bottom, spawns workers with the briefs below verbatim (plus the "Rules for every worker" block), reads only their reports and the final diff, runs the review loop and landing. Does not edit code itself.
- **Workers:** Sonnet for T1–T3 (hand ports), Haiku for T0, T4, T5 (mechanical). Each worker gets one brief, works only in the clone, reports: files touched, test names added, test command + result, anything it had to decide. No prose beyond that.
- **Reviewer:** `.claude/skills/codex-review/tools/review.sh --repo <clone> --base <sha-before-the-work>` once Codex quota is back (2026-10-29); before that an Opus read-only review agent over `git diff <base>` with the same CLEAN/findings verdict.

## Rules for every worker (paste into each brief)
- Work in `~/Claude/Projects/NuvioMobile-upstream-ports` on branch `upstream-ports-2026-10-26`. Never touch `~/Claude/Projects/NuvioTV/NuvioMobile` directly. Never `git worktree`. Stage by explicit path, never `git add -A` (MPVKit is a symlink over the gitlink).
- Upstream code lives at `composeApp/src/commonMain/kotlin/com/nuvio/app/...` on `upstream/<sha>`; the fork's copy of the same file is `shared/src/commonMain/kotlin/com/nuvio/app/...` (tests: `composeApp/src/commonTest` -> `shared/src/commonTest`). Read upstream hunks with `git show <sha> -- <upstream path> | grep '^[+-@]'`, not the full file.
- Keep fork-only code intact. Where a hunk's context does not match, adapt; do not rewrite surrounding code. Add no behaviour upstream did not add.
- Test gate per task: `./gradlew :shared:jvmTest --tests '<TestClass>'` (fast), green before reporting. Full gate is T5's job.
- One commit per task, message `port(<area>): <upstream subject> (upstream <sha>)`.

## T0 — clone + branch (Haiku, 5 min)
```
cd ~/Claude/Projects && git clone ~/Claude/Projects/NuvioTV/NuvioMobile NuvioMobile-upstream-ports
cd NuvioMobile-upstream-ports
git remote add upstream https://github.com/NuvioMedia/NuvioMobile.git && git fetch upstream cmp-rewrite
git checkout -b upstream-ports-2026-10-26 773e48732
cp ../NuvioTV/NuvioMobile/local.properties . 2>/dev/null; ls -la MPVKit
git rev-parse HEAD   # BASE for review/graph-impact; report it
./gradlew :shared:jvmTest --tests 'com.nuvio.app.features.debrid.DebridStreamPresentationAllStreamsTest'   # proves the toolchain
```
Report BASE sha and whether `MPVKit` is a symlink (expected) or empty.

## T1 — debrid language words + title strip (Sonnet, ~75 min)
Upstream `6eb35df0` (language aliases) then `4b79c43c` (strip title words), both in `features/debrid/DebridStreamPresentation.kt` + `DebridStreamPresentationTest.kt`.
Fork anchors in `shared/.../debrid/DebridStreamPresentation.kt` (object `DebridStreamMetadata`):
- ~L323 `DebridStreamLanguage.entries.filter { searchText.hasToken(it.code) }` -> `languageRegexes.filter { regex.containsMatchIn(languageSearchText(stream)) }`.
- ~L448 `languageFor(value)` -> also accept `languageAliases[it]`, `trim()` first.
- ~L495 `streamSearchText(stream)` -> split into `streamTexts(stream): List<String>` + parsed-texts tail exactly as upstream, add `languageSearchText(stream)` and `titleRegex(title)`; upstream strips `parsed?.parsedTitle` and `resolve?.title`. Confirm both fields exist on the fork's `StreamClientResolveParsed`/`StreamClientResolve` (grep `shared/.../streams/StreamModels.kt`); if `parsedTitle` is missing, strip `resolve?.title` only and say so.
- Add `languageAliases` map, `languageRegexes`, `nonAlphanumericRunRegex` as `private val`s on the object, copied from upstream.
Tests: new `shared/src/commonTest/kotlin/com/nuvio/app/features/debrid/DebridStreamPresentationLanguageTest.kt` with upstream's six language cases (`reads languages from release name words…`, `accepts release name words in parsed languages`, `required language keeps streams whose release name only has the language word`, `does not read title words…`, `does not read the parsed title…`, `required language hides streams whose title only has the language word`). Copy the fixture helpers (`localTorboxStream`, `premiumizeDirectStream`) from upstream's test or reuse those in `DebridStreamPresentationAllStreamsTest.kt`. Add one tvOS case: with `allStreams = true` and no resolver, a passthrough stream named `Movie.2024.1080p.ITA.ENG` passes `requiredLanguages = [IT]`.
Acceptance: new test class green; `DebridStreamPresentationAllStreamsTest` still green.

## T2 — debrid regex cache + single facts pass (Sonnet, ~45 min, after T1)
Upstream `def203a96`: `DebridStreamPresentation.kt` + `DebridStreamFormatter.kt`.
- `DebridStreamMetadata`: hoist `dolbyVisionRegex`, `hdrRegex`, `releaseGroupRegex`, `nonAlphanumericRegex`, `nonAlphanumericOrPlusRegex`, `resolutionTokens` list to `private val`s; `hasToken` uses `tokenRegexCache` behind `SynchronizedObject` (`kotlinx.atomicfu.locks`, already used elsewhere in `shared/`). Fork anchors ~L387-389 (DV/HDR), ~L456 (release group), ~L471-482 (`hasResolutionToken`/`hasToken`/`isDolbyVisionToken`/`isHdrToken`). Note upstream's `hasToken` drops the receiver `lowercase()`: keep the fork's callers lowercase (they are) or keep the call, whichever is a no-op.
- `DebridStreamPresentation.apply`: debrid branch ~L55 `formatter.format(stream, settings)` -> `format(stream, settings, facts)` fed by a new `applyPreferencesWithFacts` (fork's `applyPreferences` ~L109 already pairs `stream to facts` and drops with `.map { it.first }` at ~L123: split it as upstream does). Leave the fork-only `applyPassthroughPreferences` (~L81-106) alone; it already computes facts once.
- `DebridStreamFormatter.format`: add the `facts: DebridStreamFacts?` overload, `buildValues` takes `facts` instead of `settings`, `whitespaceRegex` val. Fork anchor L13 / L47.
Tests: port upstream case `formats filtered debrid streams with the facts computed while filtering` into `DebridStreamPresentationLanguageTest.kt` (rename the class to `DebridStreamPresentationPortTest` if that reads better) or a new `DebridStreamFactsReuseTest.kt`.
Acceptance: all `features.debrid.*` tests green.

## T3 — Trakt paging test cases (Sonnet, ~30 min, parallel with T1)
Upstream `TraktProgressPagingTest.kt` (on `upstream/cmp-rewrite`) tests helpers `readAllTraktPages` and `collectRecentTraktEpisodeHistory` that the fork does not have. Fork equivalents: `collectTraktHiddenShowIds` and `requireTraktProgressPageSuccess` (`shared/.../trakt/TraktProgressRepository.kt` ~L1679-1700), exercised by `shared/src/commonTest/.../trakt/TraktProgressFetchFailureTest.kt`.
1. Read how the fork's hidden-shows and history page loops react to a page that returns 200 with an undecodable body. If it is swallowed as an empty page, make it throw like a failed page (this is upstream's "undecodable page drops the whole list" behaviour) and say so in the report; if it already throws, add only the test.
2. Add to `TraktProgressFetchFailureTest.kt`: `undecodablePageFailsTheList`, `historyKeepsTheNewestEpisodePerShow` (only if the fork has a reachable helper for it; otherwise report "not testable without refactor" and skip), `errorStatusOnFirstHistoryPageFails`. No production refactor beyond step 1.
Acceptance: test class green.

## T4 — badge-rule compile cache (Haiku, ~15 min, parallel)
Upstream `a0735005d`. Fork `shared/.../streams/StreamBadgePresentation.kt` is byte-identical to upstream's parent, so:
```
git show a0735005d -- composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/StreamBadgePresentation.kt \
 | sed 's#composeApp/src/commonMain#shared/src/commonMain#g' | git apply --3way
```
Test: the fork has no `StreamBadgePresentationTest`; create `shared/src/commonTest/kotlin/com/nuvio/app/features/streams/StreamBadgePresentationTest.kt` with only upstream's `applies new rules after reusing the previous ones` case (copy from `upstream/cmp-rewrite`, same path under `composeApp`; it imports `DebridProviders`, which the fork has).
Acceptance: `git apply` clean, test green.

## T5 — gates + impact table (Haiku, ~20 min, after T1–T4)
In the clone:
```
./gradlew :shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test
xcodebuild -project iosApp/iosApp.xcodeproj -scheme NuvioTV -configuration Debug   -destination 'platform=tvOS Simulator,id=FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E' -derivedDataPath iosApp/build/DerivedData build
xcodebuild -project iosApp/iosApp.xcodeproj -scheme NuvioTV -configuration Release -destination 'platform=tvOS Simulator,id=FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E' -derivedDataPath iosApp/build/DerivedData build
```
Then from `~/Claude/Projects/NuvioTV`: `scripts/graph-impact.sh <BASE>` (run against the clone if the script takes a repo arg; otherwise after landing). Paste the table into this file under "Run log". Report pass/fail per command with the failing test name if any. NuvioTVTests/UI legs are not needed: no Swift changed (confirm `git diff --stat <BASE> -- iosApp` is empty).

## Review loop (orchestrator)
`review.sh --repo ~/Claude/Projects/NuvioMobile-upstream-ports --base <BASE>` (or the Opus stand-in) -> fix via the task's worker -> re-review on the same base until CLEAN. Record declines here.

## Landing (orchestrator, per CLAUDE.md release chain)
1. In `~/Claude/Projects/NuvioTV/NuvioMobile`: `git fetch ~/Claude/Projects/NuvioMobile-upstream-ports upstream-ports-2026-10-26:upstream-ports-2026-10-26 && git merge --ff-only upstream-ports-2026-10-26 && git push origin tvos-shared-extraction && git branch -d upstream-ports-2026-10-26 && graphify update .`
2. `rm -rf ~/Claude/Projects/NuvioMobile-upstream-ports`.
3. Outer: `git add NuvioMobile docs/upstream-port-batch-2026-10-26.md`, commit `Upstream ports landed: NuvioMobile -> <sha> (debrid languages, regex caches, Trakt tests)`, push `main`.
4. Mark the four items closed in the next `docs/upstream-port-plan-*.md`; carry player badges, hwdec fallback, hero ratings, MDBList, TorBox.
5. No cut. Release-note line for the next cut: "Stream language filters now recognise ITA/ENG/FRENCH/GER-style words in release names and no longer read title words (The French Dispatch) as a language. No new settings."

## Run log
(empty)
