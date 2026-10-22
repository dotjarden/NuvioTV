<!-- NOT RELEASED. Notes for tvos-v0.3.0-beta.19 (build 144), from NuvioMobile tvos-shared-extraction 0cf4a29eb (7acd8c008 + the build bump). Published notes = this file + compare link + install steps, with the generated commit list stripped as for beta.18. -->
## Highlights

beta 19 is the first public build since beta 18. Home opens in the new Stage layout and the description page in the Cinematic layout, each with its previous look one setting away.

### Home

- **Stage Home** (Settings › Home Screen › Home Layout, Stage by default). A fixed stage shows the focused title's art, logo and synopsis over **Ambient Background**, a wash of its colors (Home Screen, on by default). Below it, each press moves one whole row. **Classic** is the previous Home.
- With Trailers on Focus on, posters wait for **Trailer Start Delay** before their trailer plays (Home Screen, Automatic by default, or 1, 2 or 3 s).
- **Collections Layout** (Home Screen, Rows on Stage, Grid on Classic) opens collections as rows or a grid, and holding a collection on Home sets its own. Back from a collection or a film lands on the card you left.
- Catalogs with wide posters draw wide cards, watched titles carry a checkmark, and art is sharper on a 4K TV. Headings show the catalog name only (Appearance › Show Catalog Details in Headings, off, adds the add-on name and source count).
- Fixed: a doubled hero title, row headings that bounced or dropped, Up skipping a row after a collection, and trailers that stopped playing until a relaunch.

### Navigation and search

- **Rail** (Settings › Appearance › Navigation, Top Tabs by default) swaps the tab bar for a column of icons on the left. Rail is Always Visible by default (or Hide While Browsing or Hidden), Rail Position Centre (or Corner, flush top left), Rail Style Floating (or Edge, Centre only) and Rail Labels Shown (or Icons Only). Sidebar users move to the Rail.
- **Search** uses the Apple TV keyboard and updates as you type. Results group into Top result, Movies, Series and People (Settings › Sources › Search Results, Grouped by type by default, or One row per add-on), and a failed search retries once.
- **Discover** (Settings › Appearance › Discover, Own Tab by default, or Under Search or Off) opens on a poster grid filtered by type and genre.
- **Library**: list and sort pills, filters for type and watch state, and a hold menu.

### Description page

- **Cinematic layout** (Settings › Detail Page › Detail Layout, Cinematic by default, or Classic): logo, ratings and synopsis over a full-bleed backdrop. The action buttons are plain rather than glass, so the page scrolls more smoothly.
- Detail Page adds a switch per section (all on) and **Hide Spoilers in Unwatched Episodes** (off). **Start Over** shows when you have progress, and Corners set to Square make the buttons square.
- **Hold menus** on episodes and seasons mark them watched or unwatched, previous episodes included.
- Back from an actor, a biography or More Like This lands on the card you left, and biographies open in full. The full-screen trailer continues the background one without stalling, and Play on a series now stops the background trailer.
- Trailers, episodes and season posters get the focus ring, and cast and studio tiles lift as one piece.

### Playback and sources

- **Dolby Vision profile 5 MP4 files** play in the Apple TV player instead of mpv, unless the stream is slow to answer, and the remux no longer fails partway through some of those files. On mpv, profile 5 no longer plays green and magenta.
- **Player panel**: **Sync Line** sets the subtitle delay from the line being spoken. Also new: **Audio Mode** (Off by default, or Dialogue), **Boost** (Off by default, up to +10 dB) and **Remember Speed for This Show** (off, series only). The end screen shows More Like This.
- **mpv** gets a transport bar with chapters, an aspect pill and thumbnails while you scrub. Settings › Player adds Hold Left/Right (Step by default, or Scan), Left/Right Click (Skip 10 s by default, or Previous/Next Chapter) and Show Clock (off).
- **The Apple TV player** gains the Playback tab, a speed pill, styled subtitles and MKV chapters.
- **Loading Screen** (Settings › Player, on by default) pulses the title logo, in your language, while a video starts. Back from any player returns to where you started, and the player no longer traps you on its Info screen.
- The **Native Player** app (1.1.3 or newer) and **SenPlayer** join Settings › Player › Default Player, and Native Player hands your position back.
- **Auto-Play Best Source** ranks by resolution, then HDR or Dolby Vision, then cached, then size. Network failures no longer mark links bad, and the next episode prefers the same release.
- **Preload Next Episode Sources** (Settings › Player, off) and **Prepare Links for Instant Playback** (Settings › Services, Off by default, up to 5 debrid links) start work early.
- **Fallback Audio Language** and **Fallback Subtitle Language** (Settings › Subtitles & Audio, None by default). Language lists hold 78 languages, A to Z.
- Fixed: a late HDR switch and an ignored "No subtitles" on mpv, a crash after several failed sources, and choppy video behind the player menus.

### Accounts and metadata

- **Plugins**: one row per provider, so each switches on its own.
- **MDBList** external, dynamic and liked lists show in the Library. Settings › Services › Library lists picks which ones.
- Continue Watching keeps its shows when a Trakt load fails, and TorBox cloud lists load in full.
- **Open Last Profile at Launch** (Settings › Account & Profiles, off) skips the profile picker.

### Settings and appearance

- Settings is regrouped: Playback is now Player, and an explainer sits beside the list. API key fields and Save are separate rows, OLED True Black reaches Add-ons, and the subtitle color swatches show focus.
- **Typeface** (Appearance, System by default, or Open Sans) changes the app's font. **Depth Takes Poster Color** (Appearance, off) tints Card Depth edges with the poster's color. **Row Edge Fade** (Appearance, Off by default) now reaches every row.
- French, German, Italian, Spanish and Vietnamese cover every screen.

Known: the Watch Trailer button can vanish on a repeat visit to a title. The top of the description page can stay black for a few seconds after the full-screen trailer. With Trakt as the Watch Progress Source, a short session may not resume after a relaunch.
