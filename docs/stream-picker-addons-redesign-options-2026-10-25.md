# Stream picker and Add-ons page: redesign directions (2026-10-25)

Research note for Christian. Three directions each for the stream picker and the Add-ons page, drawn from Fusion, Omni, Vidi, Teevo, StremioX, Nuvio Mobile (upstream `composeApp`), Nuvio Android TV (`NuvioMedia/nuviotv`) and the NuvioMobile-Enhanced fork, mapped against what the tvOS app does today. Nothing here is planned or started; it is options only.

"Arebio TV" did not resolve to any app I could find (searches return a Martinique biology association). The Apple TV Stremio-addon clients in circulation are Fusion, Omni, Vidi, Teevo, Stremio Lite and StremioX, so Omni and Vidi are covered below as the likely candidates. If Arebio is something else, name it and I will add it.

## 1. Where we are today (tvOS)

Stream picker (`iosApp/NuvioTV/Screens/StreamPickerView.swift`, 1915 lines):
- Single vertical column on a flat black background. No backdrop, no poster, no metadata line; only the title logo header.
- One collapsed disclosure row per add-on ("Comet  6 streams"), expanded on Select. Only a lone add-on auto-expands.
- Row = add-on's `name` as the title, add-on's `description` as a 3-line caption (whole text after a 0.5 s focus dwell), size chip plus badge-pack chips below. No parsed quality, codec, audio or seeders fields; whatever the add-on wrote in its description is shown verbatim.
- No on-screen sort or filter. Sort, minimum resolution, DV/HDR and Cached-only live in Settings › Sources and apply globally.
- Auto-Play Best Source (off by default) ranks by resolution, HDR/DV, cached, size (`shared/.../StreamAutoPlayRanking.kt`) and shows a black cover with the pulsing logo.
- Focus is the legacy `.settingsRow` white platter. The HIG contract (`docs/design/hig-hybrid-contract.md:62-67`) already lists this screen and AddonsView as owing a native-List pass.
- The shared code already carries things the view ignores: `backgroundMode` Normal/Cinematic, `selectedFilter`/`filteredGroups` (mobile's per-add-on chips), `streamCodecFilter`, `streamMaxResults`, `Theme.Surface.panel` ("stream picker" in its doc comment).

Add-ons page (`Screens/AddonsView.swift`, 157 lines):
- Large grey system title, "Install from manifest URL" text field plus Install button, then an "Installed" list of rows: check glyph, name, raw manifest URL, "Enabled/Disabled". Select toggles, long-press shows Remove.
- No logo, description, version, resource types, catalog count, configure link, refresh, error state or reorder, although the manifest model has all of those and `AddonRepository.moveAddon` exists unused. Add-on order drives the picker's group order, so the user cannot change picker order on tvOS at all.
- Catalog enable/reorder lives in Settings › Home Screen behind a long-press menu.

## 2. What the other apps do

| App | Stream picker | Add-ons page |
|---|---|---|
| **Fusion** (tvOS, free) | Title centred at top, one chip row ("All"), stacked dark cards on a blurred poster-colour backdrop. Each card: bold `[TB⚡] TorBox 2160p` title, then emoji metadata lines (source/codec/group, size + bitrate + seeders/indexer, HDR, audio, languages), then the filename. Right side: poster panel with title and a big "61 Sources" count. | Settings two-pane: big app-style icon on the left, right column of pills: Add Addon field, Installed Addons rows ("AIOStreams \| ElfHosted  On" with a chevron that expands description, version, `stream, catalog, meta`), Addon Timeout, Import Addons. Long-press for more. |
| **Omni** (tvOS/iOS, paid) | Marketed on "Auto-Play Best Stream" and "Custom Regex Tags" that filter and label streams; iOS 26 glass look, floating pill tab bar, per-profile add-on setups synced via iCloud. Reviewers call it the most "Apple-feeling". | Catalog groups (combine catalogs under one shelf), profiles per Apple TV user. |
| **Vidi** (tvOS/iOS) | Closest to vanilla Stremio: a flat list per add-on, long-press to copy URL, addon subtitles grouped by language. | Minimal: view/copy URLs in Settings. |
| **StremioX** (tvOS, open source) | Decision-first: the detail page has **Watch in 4K** (ranked best source, greyed with a live add-on counter until sources finish), a **Quality** picker (tier 4K/1080p/720p/Other, then flavor DV/DTS-HD/BluRay/Atmos/WEB with file size, duplicates collapsed) and **All sources · 955** for the full ranked list with the top few per add-on so one add-on cannot bury the rest. Per-series quality memory. | Flat full-width rows: puzzle icon, name, `Catalogs · Metadata · Subtitles`, host in monospace, a red Remove pill. |
| **Teevo** (tvOS, coming) | "Watch From" lists every copy of a title across sources; one page per title. | Sources list mixing Stremio add-ons, Plex, IPTV, folders: name plus a one-line summary ("Stremio add-on · Streams for films"). |
| **Nuvio Mobile** (upstream `composeApp/.../streams`) | Blurred backdrop at 22 dp with 82-90 % black; hero block (logo or S/E thumbnail); resume banner; chip row (Refresh, All, one chip per add-on); flat card list grouped by add-on with section headers and a "Fetching…" spinner per add-on; cards 12 dp radius, white 5 %, bold 14 pt name + 12 pt subtitle, badge row top or bottom, optional 28 dp add-on logo column, " - RD Instant" suffix. Long-press sheet: copy link, download, open externally. Tablet: 40/60 two-pane, right pane a 24 dp-radius haze panel (56 dp blur, black 36 %). | Overview card (counts), Add-addon card, Installed cards: 44 dp logo, title, version, enable switch, ↑ ↓ refresh configure delete icon buttons, divider, badges (Active, N resources, N catalogs, Configurable), description, manifest summary. |
| **Nuvio Android TV** (`NuvioMedia/nuviotv`) | 40/60 two-pane on a full-bleed backdrop with a horizontal scrim solid at both edges and open in the middle. Left: 120 dp logo, S/E, episode name, runtime. Right: one 16 dp-radius haze panel (26 dp blur, #1C1C1E at 65 %) holding a resume pill, a chip row whose chips **show status** (shimmer while loading, red shake on error, removed after 1.6 s), and a flat list of 12 dp cards (#1A1A1A, title, plugin source line, full description, badge marquee on focus, 32 dp add-on logo at right). D-pad Left/Right on the list switches the source chip. Skeleton list while loading. Focus restored to the same row after the player. Group plugin providers by repository. | Single column: Install card, entry cards (Manage from phone via QR, Reorder home catalogs, Collections, Refresh Addons), then add-on cards with name, version, Disabled badge, enable switch, ↑ ↓, Remove (confirm dialog), description, base URL, "Catalogs: N - Types: movie, series". Separate Catalog Order screen with "Follow addons order". Plugins screen with repository cards and provider cards carrying movie/series type badges and a Test button. |
| **NuvioMobile-Enhanced** fork | Pinned sources: long-press a stream or its source header to pin that add-on or scraper to the top, per profile. | Same as upstream. |
| **Community** (r/Nuvio) | Badge packs are the house style: JSON rule sets ("Badger" web tool) that turn regex matches into image chips for resolution, HDR, audio, release group. We already render them. | — |

Patterns that repeat across the good ones: a backdrop or poster so the screen is not a black list; a chip row for source filtering instead of collapsed groups; structured metadata lines instead of raw description blobs; a "best" shortcut (Omni auto-play, StremioX Watch Now, our Auto-Play Best Source); and the add-ons page as a proper management surface with logo, types, reorder and remove.

## 3. Stream picker: three directions

### Direction A. Cinematic two-pane (port of Nuvio TV / tablet layout)

Closest to the family look and to our own Detail Cinematic page.

```
┌──────────────────────────────────────────────────────────────────────┐
│ backdrop, horizontal scrim (solid left + right, open centre)         │
│                                   ┌─────────────────────────────────┐ │
│   [DUNE logo 180 slot]            │ ▸ Resume from 1:12:04           │ │
│   S1 · E3 · "Double Cross"        │ (↻)(All)(Comet)(Torrentio)(AIO…) │ │
│   45 min · 2026                   │ ┌─────────────────────────────┐ │ │
│   [poster, 2:3, 260 wide]         │ │ 4K TB Instant   REMUX DV    │ │ │
│                                   │ │ 58.9 GB · FraMeSToR · HEVC  │ │ │
│   "Finding streams… 3 of 4"       │ │ [2160p][DV][TrueHD]  Comet ▫│ │ │
│                                   │ ├─────────────────────────────┤ │ │
│                                   │ │ …                           │ │ │
│                                   └─────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

- Left 40 %: title logo (same `TitleLogoHeader`), S/E and episode name or genres · year, runtime, poster, live progress line. Static, non-focusable.
- Right 60 %: one rounded panel on `Theme.Surface.panel` (`.thick`, the token already reserved for this screen) with a resume pill, a `FilterPills` chip row (Refresh, All, one chip per add-on with the Android TV status states: shimmer while loading, red pulse on error) and a flat `LazyVStack` of cards. The shared `selectedFilter`/`filteredGroups` already implement the per-add-on filter; tvOS just never bound it.
- Left/Right on the list swaps the chip, as on Android TV. Up from the first card lands on the selected chip.
- Backdrop honours the unported `backgroundMode` Normal/Cinematic setting (Normal = plain black, today's look). The scrim is the Android TV horizontal gradient, not the Detail left-to-right one, so both panes read.
- Cards keep today's row anatomy (title, description, size chip, badge packs, optional add-on logo column) so badge packs and the BUG-207 `StreamRowModel` work carry over unchanged.
- What it borrows: layout and status chips from Nuvio TV, resume pill from upstream mobile, panel material from our Detail page.
- Cost: medium. Mostly view work plus binding two shared fields. Risk is perf on the material over a backdrop (we dropped Liquid Glass on Detail for that reason); mitigate with a pre-blurred backdrop image and `.thick` material rather than live blur, and keep rows `.equatable()`.

### Direction B. Decision-first: Best source, quality tiers, full list (StremioX / Omni)

Treats picking a stream as a three-step funnel instead of a list, which suits the 10-foot ethos of fewer, bigger choices.

```
┌──────────────────────────────────────────────────────────────────────┐
│ backdrop + Detail scrim          DUNE                                 │
│                                                                      │
│  ┌──────────────── BEST SOURCE ────────────────┐                     │
│  │ ▶ Play 4K · Dolby Vision · REMUX · 58.9 GB  │  ← one prominent    │
│  │   TorBox cached · Comet                     │    `.borderedProminent` card │
│  └─────────────────────────────────────────────┘                     │
│  QUALITY                                                              │
│  [ 4K · 12 ] [ 1080p · 41 ] [ 720p · 9 ] [ Other · 4 ]   ← tier chips │
│  ┌ DV REMUX 58 GB ┐ ┌ HDR10 WEB 14 GB ┐ ┌ SDR BluRay 22 GB ┐ …      │
│  └────────────────┘ └─────────────────┘ └──────────────────┘         │
│  ( All sources · 155 )   ( Sort: Quality ▾ )   ( Cached only ● )      │
└──────────────────────────────────────────────────────────────────────┘
```

- Best source card: the top of `StreamQualityRank.rankBest`, the same ranking Auto-Play Best Source already uses, shown instead of auto-started. Greyed with "3 of 4 add-ons answered" until the fan-out finishes (StremioX's live counter), so it never plays the best of what loaded first.
- Quality tiers: resolution chips, each opening a horizontal row of "flavor" cards (DV / HDR10 / SDR × REMUX / BluRay / WEB × Atmos / DTS-HD / TrueHD) labelled with size and cached state, duplicates collapsed. Per-series memory of the last tier played (StremioX) is a natural follow-on.
- "All sources" opens today's grouped list (Direction A or C as the fallback view), so nothing is lost for power users; "top N per add-on" (StremioX) and the unexposed `streamMaxResults` keep one add-on from burying the rest.
- On-screen Sort and Cached-only pills mirror Settings › Sources, so the global settings stop being the only control.
- Omni's regex tags map onto our badge-pack rules: a user-defined pattern can become a chip and a filter, not just a chip.
- Cost: high. Needs structured parsing (resolution, HDR/DV, source type, audio, codec, size, cached) in shared Kotlin. Debrid-managed streams already have this through the formatter templates; add-on and plugin streams need a parser over name/description, which the Android TV `qualityValue` and our badge rules partly provide. Pays off beyond the picker: the same fields feed FEAT-22 auto quality and Up Next release matching.

### Direction C. Dense cards with a side panel (Fusion, in place)

Modernises the existing single-column list without changing its skeleton. Lowest risk, fastest to ship.

```
┌──────────────────────────────────────────────────────────────────────┐
│  poster-colour blurred backdrop                                       │
│   DUNE                      (All)(Comet)(Torrentio)(AIO Streams)      │
│  ┌───────────────────────────────────────┐   ┌───────────────────┐  │
│  │ [TB⚡] TorBox 2160p   - TorBox Instant│   │                   │  │
│  │ BluRay REMUX · HEVC · FraMeSToR       │   │   [poster]        │  │
│  │ 58.9 GB (81.6 Mbps) · 217 seeds · DV  │   │                   │  │
│  │ English · Italian                     │   │ Dune              │  │
│  │ [2160p][DV][TrueHD][58.9 GB]  comet ▫ │   │ 155 sources       │  │
│  ├───────────────────────────────────────┤   │ 3 of 4 add-ons    │  │
│  │ …                                     │   │ Sort ▾  Cached ●  │  │
│  └───────────────────────────────────────┘   └───────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

- Replace the collapsed disclosure headers with a chip row (same shared filter binding as A). Groups still exist as section headers in the "All" view, with upstream's per-add-on "Fetching…" spinner.
- Cards become 12 dp-radius surfaces on `surface` (#1A1A1A), focus lifts to the white platter (or the opt-in accent ring), 1.02 scale. Three structured lines (source · codec · group; size · bitrate · seeders; HDR · audio · languages) parsed from the description where the add-on writes them, falling back to the raw text when it does not. The filename stays as the last caption line, expanding on dwell as today (BUG-16).
- Right panel: poster, title, source count, progress, and the Sort / Cached-only pills, so the current global settings get an on-screen mirror (Fusion shows poster plus count; the pills are ours).
- Badge packs sit where they do now; Fusion's emoji lines are not copied, we render the same facts as text and chips.
- Pinned sources (Enhanced fork) fit here as a long-press action on a chip: "Pin to top", stored per profile.
- Cost: low to medium. View and view-model work, one parser helper, no layout re-architecture, keeps every tracker fix (BUG-174/183/207) intact.

Suggested read: C is the safe beta.20 move, A is the "make it look like the family" move, B is the differentiator and would come after a structured-metadata port that A and C can also use. A and B are compatible: B's funnel can sit on top of A's two-pane.

## 4. Add-ons page: three directions

### Direction A. Settings-style two-pane (Fusion tvOS)

```
┌──────────────────────────────────────────────────────────────────────┐
│                       ADD ADDON                                      │
│   ┌────────────┐      [ https://…/manifest.json        ] (+ Add)     │
│   │            │      INSTALLED ADDONS                               │
│   │  puzzle    │      [⧉ AIOStreams | ElfHosted     On  ▾]           │
│   │  icon      │        v2.26.0 · stream, catalog, meta              │
│   │            │      [⧉ Torrentio                  On  ▾]           │
│   └────────────┘      SETTINGS                                       │
│   4 add-ons · 3 on     [ Addon Timeout        30 seconds  ›]         │
│   12 catalogs          [ Refresh Add-ons                   ›]        │
│   refreshed 2 h ago    IMPORT                                        │
│                        [ Import / Export Add-ons           ›]        │
└──────────────────────────────────────────────────────────────────────┘
```

- Left: a static identity panel (large glyph, counts, last refresh), like Fusion's and like tvOS Settings itself.
- Right: the native `List` kit we already use on the Settings panes (`SettingsRowViews.swift`), which clears the HIG-contract debt in the same change. Rows: Add field, installed rows with the manifest logo, name, an On/Off trailing glyph and a chevron that expands to description, version, resource types and catalog count (Fusion's expand). Long-press: Move Up, Move Down, Refresh, Configure (when `behaviorHints.configurable`), Remove. Hook up the unused `moveAddon`.
- Addon Timeout, Refresh Add-ons and Import/Export become rows, which takes "Refresh Add-ons" out of Settings › Home Screen.
- Cost: low. Mostly a port onto the Settings kit plus binding model fields that already exist.

### Direction B. Card gallery (StremioX / upstream mobile)

```
┌──────────────────────────────────────────────────────────────────────┐
│  Add-ons                                   ( + Install ) ( ↻ Refresh )│
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ [logo] Comet                                v1.4.2   ● Active  │  │
│  │        Streams · Catalogs · Subtitles      comet…midnightignite.me │
│  │        Torrent and debrid streams from … (1 line)   (⋯)        │  │
│  └────────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │ [logo] Torrentio                            v0.0.14  ○ Disabled│  │
│  └────────────────────────────────────────────────────────────────┘  │
│  Catalogs  ──────────────────────────────  8 of 12 on home   ›       │
└──────────────────────────────────────────────────────────────────────┘
```

- Full-width cards on `surface` at 12 dp radius, same card language as the stream picker Direction C and as the Home rows. 44 dp logo (falls back to the puzzle glyph), name, version, status pill (Active / Disabled / Refreshing / Unavailable in `error`), type chips in the Library `FilterChip` style, host in secondary text, one description line, a trailing `(⋯)` that opens a menu: Enable/Disable, Move Up, Move Down, Refresh, Configure, Remove.
- Install moves into a sheet opened by a `.borderedProminent` Install button, so the page leads with what is installed rather than with a text field.
- The Catalogs disclosure moves here from Settings › Home Screen (it is an add-ons concern), keeping Hero Sources where it is.
- Cost: medium. New card component, one menu, a sheet, and the catalog section move.

### Direction C. Sources hub (Nuvio Android TV / Teevo)

```
┌──────────────────────────────────────────────────────────────────────┐
│  Sources                                                              │
│  ┌ Add-ons ──────────┐ ┌ Catalogs ────────┐ ┌ Debrid ─────────────┐ │
│  │ 4 installed, 3 on │ │ 8 of 12 on Home  │ │ TorBox connected    │ │
│  │ [logo][logo][logo]│ │ Reorder ›        │ │ Manage ›            │ │
│  └───────────────────┘ └──────────────────┘ └─────────────────────┘ │
│  ┌ Manage from phone ─┐ ┌ Import / Export ─┐ ┌ Refresh all ───────┐ │
│  │ [QR]  scan to edit │ │ Import add-ons   │ │ Updated 2 h ago    │ │
│  └────────────────────┘ └──────────────────┘ └────────────────────┘ │
│  Installed add-ons                                                    │
│  ┌ Comet   v1.4.2   [On]  [↑][↓]  [Remove]                         ┐ │
│  │ Streams · Catalogs   comet…me                                   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

- The tab becomes a hub for everything that feeds content: add-ons, catalogs, debrid, and plugins/repositories when `AppFeaturePolicy` allows them on tvOS. Entry cards at the top (Android TV's pattern), installed add-on cards below with the controls inline (switch, ↑ ↓, Remove) instead of behind long-press, since tvOS testers have had trouble discovering long-press menus.
- "Manage from phone": the Android TV QR flow (local web page served by the app, changes confirmed on the TV). This is the single biggest usability win for manifest URLs, which today have to be typed with the Siri Remote or pasted from Continuity. It is also the most work: an on-device HTTP server and a confirm dialog.
- Teevo's one-line source summaries ("Stremio add-on · Streams for films") become the subtitle of each card.
- Cost: high. New screen architecture plus the phone server. Can be staged: hub cards and inline controls first, QR management later.

Suggested read: A is the cheap, Apple-correct fix and retires a known HIG debt; B gives us the richest add-on card and matches picker Direction C; C is the long-term shape and the only one that fixes URL entry.

## 5. Foundations any direction needs

1. Structured stream metadata in shared Kotlin (resolution, HDR/DV, source type, codec, audio, size, seeders, cached, languages) parsed from name and description, with the debrid formatter output as the first source. Picker directions B and C depend on it; A benefits.
2. Bind the shared per-add-on filter (`selectedFilter`/`filteredGroups`) and `backgroundMode` on tvOS.
3. Add-on reorder on tvOS via the existing `moveAddon`, because order drives picker group order.
4. The native-List pass the HIG contract already asks for on both screens.
5. UI legs: the picker and Add-ons tab both have NuvioTVUITests coverage to extend, and any backdrop or material change needs a BUG-207-style scroll check on the device.

## 6. Sources

- Fusion: Troypoint install guide screenshots (tvOS streams page, tvOS and iOS Addons pages, 2026-03/04), techkings "Stremio alternatives on Apple TV" thread, App Store id 6759285919 (tvOS listing not fetchable), r/FusionTheApp excerpts (badges under streams, starter-kit widgets).
- Omni: omni.stkc.win feature list (Auto-Play Best Stream, Custom Regex Tags, Catalog Groups, profiles), r/OmniContentHub and r/ixtream review excerpts.
- Vidi: App Store listing and release notes (Plata o Plomo AB, 1.8.2), vidi.plomo.se.
- Teevo: amberlake.co.uk/teevo/sources/stremio.
- StremioX: github.com/yvdjee/stremiox README and the `streams.png` / `addons.png` screenshots.
- Nuvio Mobile: `NuvioMobile/composeApp/src/commonMain/kotlin/com/nuvio/app/features/streams/*` and `addons/AddonsScreen.kt` at the vendored upstream commit.
- Nuvio Android TV: read-only shallow clone of `NuvioMedia/nuviotv` (`app/src/main/java/com/nuvio/tv/ui/screens/stream/StreamScreen.kt`, `addon/AddonManagerScreen.kt`, `plugin/PluginScreen.kt`), plus issue #4068 / PR #4119 (resume pill and provider names).
- NuvioMobile-Enhanced: README (pinned sources).
- Ours: `StreamPickerView.swift`, `StreamsViewModel.swift`, `StreamBadges.swift`, `FirstPlayAutoPlay.swift`, `AddonsView.swift`, `Theme.swift`, `FlatControlStyles.swift`, `docs/design/hig-hybrid-contract.md`, tracker items FEAT-2, BUG-16, BUG-174/183/207, BUG-214, device shots in `docs/research/p5-device-pass-2026-10-20/` and `docs/research/batch-b-device-2026-10-16/`.
