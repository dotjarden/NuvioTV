# Add-ons hub C — Wave H5 spec (UI legs + a DEBUG seam), 2026-10-26

Plan §4 "Wave H5". Branch `addons-hub-c` in `~/Claude/Projects/NuvioMobile-addons-hub` (H4 committed `9ce71f9b6`). Files: `iosApp/NuvioTVUITests/AddonsHubUITests.swift` (three legs added; keep the three that exist), `iosApp/NuvioTV/Screens/Addons/AddonInstallSheet.swift` (one DEBUG seam), `iosApp/NuvioTV/Screens/StreamPicker/…` untouched. Write only; no build, test, commit, `git add`. Report every judgment call.

## 0. Why a seam
`DebugConfig.manifestURL` is a compile-time constant (empty on this build) and typing into the tvOS field from XCUITest is unreliable (`BatchAFolderUITests` skipped on most runs). Add, DEBUG only, `-debug.installPrefillUrl <url>`: `AddonInstallSheet` reads `UserDefaults.standard.string(forKey: "debug.installPrefillUrl")` in `#if DEBUG` on appear and prefills `newUrl` with it (never persisted, never written back). The sheet's doc comment names the knob and the leg that uses it.

## 1. Stub add-ons
As `StreamPickerUITests` (copy its `manifest(id:name:)` / `streams(…)` helpers and the media-stub pattern; keep this file self-contained): two stream add-ons `zz.hub.a` "ZZ Hub A" (`/hub-zz-a/`, two streams) and `zz.hub.b` "ZZ Hub B" (`/hub-zz-b/`, one stream) on one `DiscoveryStubServer`, remove knob `/hub-zz-`, cleanup launch in a teardown block registered before the seed launch (the P5 rule), stubs stopped in teardown blocks. Common launch args as the existing hub legs plus `-debug.streamAutoPlayModeOverride MANUAL`.

## 2. `testInstallReorderPickerAndRemove` (one leg, the plan's install → card → ↓ → picker order → remove)
1. Seed launch: `-debug.addonManifestRemoveMatching /hub-zz- -debug.addonManifestUrls <A manifest>`; `pause(14)`; terminate.
2. Leg launch with `-debug.installPrefillUrl <B manifest>`. Open the Add-ons tab (`openTab`), focus `addons_hub_action_install` (the hub-leg walk: Down only while no summary card has focus, then Down once more to the action row, Right/Left to the Install card), Select. Assert `addons_hub_install_field` has focus and (soft) its value contains "hub-zz-b". Press Down/Right until `addons_hub_install_button` has focus, Select. Assert `addons_hub_install_modal` appears within 20 s and its label contains "Installed" (poll; "Checking" first is fine). Assert `addons_hub_install_done` has focus; Select. Assert the sheet is gone and the card labelled with "ZZ Hub B" exists: find the index i such that `addons_hub_card_<i>` label contains "ZZ Hub B"; assert it has focus (the H3 focus-to-new-card rule). Print `[HubLeg] installed B at card <i> of <n>`.
3. Reorder: Right along B's card to `_up` (B was appended last; A is above it, and Cinemeta above A), Select on `_up`; wait until the card labelled "ZZ Hub B" has index i-1 and `addons_hub_card_<i-1>_up` has focus (the H2 focus-return rule); print the new order (labels' first words only).
4. Picker order follows: terminate, relaunch with the common args + `-debug.openDeepLink nuviotv://title?id=tt1160419&type=movie&name=Dune` + `-detail_layout cinematic` + `-home_upcoming_row_enabled NO` + `-debug.trailerForceNoTrailer YES`; wait for `detail_hero` / `detail_action_play`; verify Play has focus; Select; wait for `stream_picker_source_panel`; assert the chip labels (`stream_picker_chip_0`, `_1`, by position) read B before A ("ZZ Hub B, 1 source" before "ZZ Hub A, 2 sources"). Press Menu to leave the picker.
5. Remove: back on the hub (openTab "Add-ons"), walk to B's card, Right to `_remove`, Select; assert the alert "Remove ZZ Hub B?" (an `app.alerts` or the "Remove" button exists), press its "Remove" (Right/Select as the verified-focus rule allows: read focus first); assert no card labelled "ZZ Hub B" within 10 s and the toast `addons_hub_toast` says "Removed ZZ Hub B."; print the focused card.
Skips: Detail never appearing (network). Fails on everything else with identifiers and the focus dump; never a label with a URL in prints (card labels hold the host only; fine).

## 3. `testCatalogToggleShowsDisabledOnHome`
Open the catalogs page from the Catalogs card (the H4 walk). Walk to row 0, Right to `_toggle`, record its accessibility value ("enabled"/"disabled"), Select; assert the value flipped and that `addons_hub_catalog_0` label contains "Disabled on Home" when now disabled (or lost it when now enabled); Select again to restore; assert restored. Menu back. (Home reflection is checked on the device pass, not here.)

## 4. `testRefreshAllTogglesTheSpinnerAndStamps`
On the hub with A installed (seed as in §2 step 1 plus a plain leg launch): focus `addons_hub_action_refresh`, Select; assert within 15 s that `addons_hub_toast` appeared with "Refreshing" or "Refreshed", and that the Refresh card's label no longer says "Not refreshed yet" (contains "Updated") within 20 s.

## 5. Report
Files with line counts, every judgment call, anything in the kit that did not fit. Do not run anything.
