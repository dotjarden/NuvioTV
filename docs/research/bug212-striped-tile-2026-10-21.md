# BUG-212 "striped Netflix tile" — investigation (2026-10-21)

Read-only investigation on `NuvioMobile-wave3` (`claude/wave3`, `8e16c2871`), against the photo
`docs/research/steven-rc11-verdict-2026-10-21/photo-2-axientt66vwh1.jpeg` (rc11, `6baddab46`).

## Verdict: not a rendering bug; this is the Netflix folder's animated focus cover

We triaged this exact image as a non-bug on **2026-10-02**, from his rc1 video:

- `docs/research/steven-beta19-rc1-video-triage-2026-10-02.md:69`: "The striped 'Netflix' tile in
  Services de Streaming is an animated cover. It cycles N logo → coloured vertical ribbons → N
  about every 2 s (2:34–2:37, 2:56–3:03)". Frame: `docs/research/steven-beta19-rc1-video/0156-netflix-tile-animated-cover-stripes.jpg`.
  The ribbons come from Netflix's own intro, which also plays in Infuse at 4:10 in that video.
- `docs/beta-feedback-tracker.md` (BUG-133 row): "Not a bug: the striped Netflix tile … is an
  animated cover (the reply explains it)". `docs/comms-dm-drafts-2026-10-04-rc2-reply.md:18` then
  told Steven so.
- `docs/steven-parked-feats-plan-2026-09-05.md:211` (FEAT-33 probe): on his "Services de Streaming"
  row, `gif=1` on **every** tile, so every folder there has a focus GIF.

The 0156 frame and the rc11 photo show the same thing: red/orange/white ribbons on the left, blue
on the right, vertical, filling the tile, on the focused Netflix tile only. Steven did not report
the stripes himself. The verdict doc files BUG-212 as our own reading of the photo
(`docs/steven-beta19-rc11-verdict-2026-10-21.md:34`, "In the same photo…"); his message was about
BUG-211.

## (1) How the focused folder tile differs from the unfocused one (`Screens/CollectionsUI.swift`)

- Static cover: `CachedAsyncImage(string: cover, decodeSize: .points(...))` at **:759** is mounted
  for the tile's whole lifetime in both states (BUG-19). Its `.onImageLoaded` (**:763**) only asks
  `ArtworkColorStore` for a rail colour.
- Focus GIF: `if folder.focusGifEnabled, let gifUrl` at **:803** → `AnimatedGifImage(..., isAnimating:
  isFocused, ...)` at **:816–819**, layered OVER the cover. In `DesignSystem/AnimatedGifImage.swift`,
  `gifVisible = isAnimating && loader.image != nil` (**:79**) drives `.opacity` (**:95**), and the
  decode is deferred to the first focus (**:107–110**). **The GIF is the only layer that shows when
  focused and not when unfocused.** That explains why only the focused tile looks different, and why
  the hero (static `heroBackdrop`/logo) shows the NETFLIX logo correctly.
- The other focus-only effects are geometric or overlays: the depth rail `.nuvioCardDepth` (**:850**),
  the ring-band `.scaleEffect`, the ring `strokeBorder` overlay, and `CardArtworkFocusLift` (**:905**;
  `PosterCard.swift` `manualLift`: black platter + shadow + `scaleEffect`; `.systemLift`:
  `.compositingGroup()` + `.hoverEffect`). None of them resample the picture's pixels into a
  1-D pattern.

## (2) Could a pipeline stage produce vertical stripes?

| Hypothesis | Evidence against | Rank |
|---|---|---|
| H0: GIF frame content (Netflix ribbon intro) | Matches the 10-02 video, where the stripes cycle with the N logo every ~2 s; `gif=1` on this row; the effect is on the focused tile only | **1 (confirmed by the earlier video)** |
| H1: partially decoded GIF frame | `AnimatedGifImage.swift:792` requires `CGImageSourceGetStatusAtIndex == .statusComplete` per frame and fails the whole decode otherwise (the "magenta garbage" fix). Frames come from `CGImageSourceCreateThumbnailAtIndex` (:796), which owns its stride | 2 (very low) |
| H2: wrong `bytesPerRow` CGImage | Every hand-built CGContext (`ArtworkColorStore.swift:249–258`, `ArtworkLetterbox.swift:71–80`) draws into a private scratch buffer and returns **numbers** (a mean colour, a zoom factor). No CGImage built from those buffers is ever displayed | 3 (none) |
| H3: Batch P W1 `nonisolated` sampling hands a still-filling buffer to the tile | `ArtworkColorStore.swift:150` `Task.detached { meanChroma(of: image) }` reads an already-decoded immutable `CGImage` and returns `Mean?`; the tile only receives a `Color` (`depthRailTint`). No buffer crosses back | none |
| H4: CoreImage/Metal filter, P3/16-bit | No CIFilter/`drawingGroup` on the folder tile; CIContext appears only in the QR screens | none |
| H5: `ArtworkLetterbox` zoom on freed memory | Not used by `FolderTile`; its scan also returns a scalar | none |

## (3) Batch P W1

It cannot cause this. The detached work returns value types only, and the 10-02 frame predates
Batch P by more than two weeks (rc1, build 133).

## (4) Smallest sim repro

There is no defect to reproduce. To *show* the effect: in a guest-sim collection (the BUG-38 seeding
recipe), give a folder `focusGifEnabled = true` and point `focusGifUrl` at a GIF of the Netflix
intro ribbons. Focus the folder: the cover cross-fades to the GIF, and ~half its frames are
vertical ribbons.

## Proposed fix

**No code change.** Close BUG-212 as "not a bug: animated focus cover (same as the 2026-10-02
finding)". Correct the record:
- Tracker BUG-212 row → ✅ not a bug, cross-reference BUG-133's note and this doc.
- The rc11 reply already SENT (`docs/comms-dm-drafts-2026-10-21-rc11-reply.md:36`) told him "the
  striped tile is the one I want to find first". The next DM should carry one line saying it is the
  Netflix cover's animation (his own GIF), the same one we noted on rc1. Draft it through
  SlopMonster; send only on Christian's go.

A **product** follow-up, if wanted (not a fix): the GIF fades in over the static cover only when
focused, so a still photo of a focused tile can catch a mid-animation frame that reads as broken.
Nothing to change unless Steven himself says the stripes bother him.

## One device confirmation (only if anyone doubts it)

The existing log line already settles it. `AnimatedGifImage.swift:868` prints
`[GifDecode] side=… sourceFrames=… keptFrames=… file=…` when the Netflix tile first takes focus.
On the rig, with his collections installed in the **Test** profile, focus the Netflix folder and
`grep '\[GifDecode\]'` in the console stream. A line naming the Netflix GIF (keptFrames > 1),
plus a screenshot every 0.5 s showing N logo ↔ ribbons, confirms H0. No new log line is needed.
