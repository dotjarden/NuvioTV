# Nuvio tvOS — Claude Code rules

History, run logs, releases and open action items: `docs/status.md` (moved out 2026-10-19). Daily upstream-check logs: `docs/upstream-port-plan-YYYY-MM-DD.md`. Keep this file rules-only.

## Repo layout
- Outer repo (this folder): fork wrapper on `main` — docs, scripts, the `NuvioMobile` submodule.
- `NuvioMobile/`: the KMP + native tvOS app on `tvos-shared-extraction` (`origin` = `youngchris29-art/NuvioMobile`; `upstream` = `NuvioMedia/NuvioMobile` `cmp-rewrite`, diffed daily by a scheduled task).
- `NuvioMobile/shared/`: Compose-free Kotlin; upstream ports land here. `NuvioMobile/iosApp/NuvioTV/`: SwiftUI tvOS frontend.

## Standing instructions
The shared rules (no sends without a go, no cuts unless told, ask before planning, model delegation) live in `~/.codex/AGENTS.md`, loaded globally by both tools. Project-specific additions:
- Comms drafts go in `docs/comms-*.md`, marked NOT SENT.
- Batch work records delegation rounds and findings in the batch doc.
- Release notes and tester DMs name every new setting and its default.

## Build and gates (in `NuvioMobile/`)
- Kotlin: `./gradlew :shared:jvmTest :shared:tvosSimulatorArm64Test :composeApp:iosSimulatorArm64Test`
- Sim builds (Debug + Release): `xcodebuild -project iosApp/iosApp.xcodeproj -scheme NuvioTV -configuration Release -destination 'platform=tvOS Simulator,id=FA87E9B6-F28D-4DF9-84E4-A5A4C5DBFC4E' -derivedDataPath iosApp/build/DerivedData` (the FA87 id, never `generic/platform=tvOS Simulator`: Release has no `ONLY_ACTIVE_ARCH`, so the generic destination links x86_64 against the arm64-only SharedCore and fails; 2026-10-22).
- NuvioTVTests + UI legs on the fixture sim (`FA87E9B6-…`): `xcodebuild test -scheme NuvioTVTests` (unit) / `-scheme NuvioTVUITests -only-testing:NuvioTVUITests/<Class>` (legs) `… -derivedDataPath iosApp/build/DerivedDataUITests -collect-test-diagnostics never` (the `NuvioTV` scheme has no testables: "not configured for the test action"), Bash sandbox OFF (sandboxed: exit 70 "Failed to prevent system sleep"; without the flag UI legs hang ~10 min).
- Device build: `-destination 'generic/platform=tvOS' -derivedDataPath iosApp/build/DerivedDataDevice -allowProvisioningUpdates` (7-day free-team profile; delete stale `youngchris29` profiles when it expires), install with `devicectl`.
- Gated = all of the above green on the tip plus the relevant UI legs, then a device pass in the Test profile.
- Keep only those three dirs plus `tvos-ipa` under `iosApp/build/`; delete one-off build dirs and `.xcresult` bundles once their gate is recorded.

## Release chain
1. Feature branch in a local clone of the submodule (never a worktree); review loop to CLEAN; gates green.
2. Fast-forward into `tvos-shared-extraction`, push, delete the branch (local + `origin`) and the clone.
3. Bump the outer pointer: `git add NuvioMobile`, commit, push outer `main`.
4. Cut only on Christian's explicit go: `scripts/cut-rc.sh beta.<n>-rc<m>` (preflight, build bump + tag, push, pointer commit, Release build, package, upload; `--preflight` checks only, `--from build|upload` resumes). Public betas: `NuvioMobile/scripts/release-beta.sh`.
5. Tester DM through the copy rule, sent only on his go.

## Device testing profile (standing, 2026-10-02)
All device testing runs in the app's **"Test" profile** ("Test 2" on the Living Room box), never the synced daily-use "Chris" profile: passes, repros, installing a tester's add-ons or collections. Name the profile before any device step; remove tester payloads afterwards. If a pass needs "Chris", say so and get his go first. Dev builds under `com.youngchris29.NuvioTV` share the account. Remote rig (`scripts/device/*.sh`, credentials in `~/.config/nuviotv-device/`): `docs/device-rig-2026-10-15.md`. Pre-flight before any pass or install: `scripts/device/ready.sh` (`--walk` adds the app/console/profile gate).

## Branch hygiene
- Outer `origin` carries `main`; cloud sweeps leave `claude/*` branches behind: delete each once it is an ancestor of `main` (one left 2026-10-22: `claude/kind-hypatia-d0wvc0`, not yet in `main`). Steady state is `main` only.
- Submodule `origin` holds `tvos-shared-extraction` and `cmp-rewrite` (stale mirror). Fork tags are `tvos-*`; never push upstream's `0.x` tags.
- Never `git worktree add`/`remove` on the submodule (`core.worktree` resolves back to `.git/modules/NuvioMobile`); a stray one is removed with `rm -rf` + `git worktree prune`. Isolated work goes in a clone `~/Claude/Projects/NuvioMobile-<task>`, landed with `git fetch <clone> <branch>:<branch>`; in a clone MPVKit is a symlink over the gitlink, so stage by explicit paths, never `git add -A`.
- Side clones now: none (the harness clone was deleted 2026-10-23 after its merge); delete each once its branch is fast-forwarded in.
- Commit the `docs/*.md` the checks and sweeps write.

## Reddit DM check (standing, 2026-10-08)
DMs are the sweep's third source (`docs/beta-feedback-sweep-instructions.md` §1b): local only via `scripts/reddit/fetch-dms.sh --since <watermark> --summary`; the tracker header holds the watermark. The sweep never sends a DM.

## Codex review (standing, 2026-10-01)
`.claude/skills/codex-review/tools/review.sh --repo NuvioMobile --base <sha-before-the-work>` (exit 0 CLEAN / 3 findings / 2 no verdict). Run unsandboxed, never piped; loop review → fix → re-review on the same `--base` until CLEAN, documenting declines. Codex quota resets 2026-10-29; until then an Opus read-only review agent stands in.

## Copy rule (standing, 2026-09-03)
Every user-facing draft (Reddit, DMs, README/INSTALL, release notes, GitHub text) goes through SlopMonster first: lint `python3 scripts/deslop/deslop.py <file>` → rewrite to 5/5 keeping every fact → cleanse with `~/.claude/skills/slopmonster/tools/cleanse.sh` when `codex` is available (diff every hunk, restore dropped facts) → re-lint; present at 5/5 with the score. No scorer tricks; legal/DMCA and quoted third-party text are never rewritten.
