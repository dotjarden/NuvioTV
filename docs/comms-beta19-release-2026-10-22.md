# beta 19 public release messages (NOT SENT, NOT POSTED)

**Status: every draft below is NOT SENT / NOT POSTED.** Christian posts each one himself or gives a go per item. Release: tag `tvos-v0.3.0-beta.19`, build 144 (`0cf4a29eb`), the first public build since beta 18, download `https://github.com/youngchris29-art/NuvioTV/releases/latest` (asset `NuvioTV.ipa`). The release is not published yet. The texts are written as if it is, so post none of them before it is live.

Lint: the file lint (`python3 scripts/deslop/deslop.py docs/comms-beta19-release-2026-10-22.md`) skips fenced blocks, so each body was also scored on its own from a plain copy. Every body scores 5/5. Word counts are `wc -w` of the body.

## 1. Reddit "Latest build" block for the post body (NOT POSTED)

**NOT POSTED.** Goes into the body of r/NuvioForks post `1wtmutc` in place of the beta 18 block. The paste copy, with nothing else in it, is `docs/comms-reddit-beta19-block.md`. Apply on Christian's go from `NuvioMobile/` with `python3 scripts/update-reddit-beta-post.py --changelog ../docs/comms-reddit-beta19-block.md --dry-run`, then without `--dry-run`, keep the four image lines, and screenshot the post afterwards.

Facts behind it: shape copied from the beta 18 block in `docs/comms-reddit-beta18-changelog.md`, with the opening and closing lines the script anchors on (`BLOCK_START`, `BLOCK_END`) · features, setting paths and defaults from `docs/comms-beta19-highlights.md` · 78 languages counted in `PlayerLanguageOptionCodes.kt` · About line = 0.3.0 (144) plus the tag.

Body (198 words):

```text
**Latest build: beta 19 (build 144)**

What's new in beta 19 (first public build since beta 18; Home and the description page have new layouts, the old ones a setting away):

* Stage Home (Settings > Home Screen > Home Layout): the focused title's art, logo and synopsis sit on a fixed stage, and each press moves one whole row. Classic is the old Home.
* Rail (Settings > Appearance > Navigation): icons down the left edge instead of the tab bar.
* Cinematic description page (Settings > Detail Page > Detail Layout): logo, ratings and synopsis over a full-bleed backdrop. Hold an episode or season to mark it watched.
* Search uses the Apple TV keyboard, updates as you type and groups results by type. Discover is a poster grid filtered by type and genre.
* Dolby Vision profile 5 MP4 files play in the Apple TV player instead of mpv. The player panel adds Sync Line for subtitle timing, a Dialogue audio mode and Boost.
* Fallback audio and subtitle languages, 78 languages in the lists, and French, German, Italian, Spanish and Vietnamese on every screen.

Settings -> About should read 0.3.0 (144), beta tag tvos-v0.3.0-beta.19.
```

## 2. Reddit announcement comment on the thread (NOT POSTED)

**NOT POSTED.** Top-level comment on post `1wtmutc`, after the block swap.

Facts behind it: release URL and asset from the brief and `README.md` · eleven release candidates = builds 133 to 143 (`docs/status.md`) · features from `docs/comms-beta19-highlights.md` · install and About lines follow the beta 18 comment in `docs/comms-reddit-beta18-comment.md` · the 7 day signature from the README's free Apple ID note · no names, no dates, no debrid brand names.

Body (234 words):

```text
beta 19 is up: https://github.com/youngchris29-art/NuvioTV/releases/latest (build 144).

It is the first public build since beta 18. In between, eleven release candidates went through one tester's Apple TV, and this build carries all of that work.

The block at the top of the post has the list. The short version: Home opens in the new Stage layout, with the focused title on a fixed stage and each press moving one whole row. The Rail swaps the tab bar for a column of icons on the left. The description page opens in the Cinematic layout, logo and synopsis over a full-bleed backdrop. The old Home and the old description page are each one setting away (Classic). Search uses the Apple TV keyboard and updates as you type. Dolby Vision profile 5 MP4 files now play in the Apple TV player instead of mpv. The player panel gains Sync Line for subtitle timing, a Dialogue audio mode and Boost. Language lists hold 78 languages with a fallback for audio and subtitles, and French, German, Italian, Spanish and Vietnamese cover every screen.

Same install as always: download NuvioTV.ipa, sideload with Sideloadly or atvloadly, trust the certificate on first launch. Settings > About should read 0.3.0 (144). A free Apple ID signature lasts 7 days, so sideloading again every week is normal.

If something broke for you since beta 18, say so here or open an issue at https://github.com/youngchris29-art/NuvioTV/issues.
```

## 3. Steven DM, one bubble — SENT 2026-10-22T21:47:26Z

**SENT 2026-10-22T21:47:26Z** on Christian's go (pre-send fetch 21:46:31Z quiet: nothing after his own 12:21Z message; `~/Library/Logs/NuvioDM/beta19-send.js`, gated on the newest bubble being that message; verified by the send walk: `youngchris2989 said 1 minute ago, Hi Steven, beta 19 is public …`). Watermark → the send time. One bubble in his Reddit chat room. Before sending, run `scripts/reddit/fetch-dms.sh --since 2026-10-22T12:21:38.223Z --summary` and fold in anything new.

Facts behind it: no DM since the reply sent at 02:12Z (`docs/comms-dm-drafts-2026-10-21-rc11-reply2.md`), and the rc12 draft went unsent because rc12 was never cut · items from `docs/comms-dm-drafts-2026-10-22-beta19-rc12.md`, checked against the submodule log: Corner rail `b840a3bb0`, icon size `dc1f23a22`, Back from an actor `0bed3fa4e` (verified on the box), plain Cinematic action row `79e1a33cb`, Classic heading and logo `BUG-209` / `BUG-211` with `BUG-210` not reproduced, Search retry `BUG-208`, stream row dwell of 500 ms in `StreamPickerView.swift` · the cheaper Card Depth was pulled by `7239c706c` (`BUG-221`), and the last DM had called it in testing · open asks: mpv at once or after seconds, the `BUG-165` short Back · the README note is in `README.md` and `NuvioMobile/README.md`.

Body (243 words):

```text
Hi Steven, beta 19 is public: https://github.com/youngchris29-art/NuvioTV/releases/latest (build 144). Thank you for the eleven release candidates before it: a lot of this build is there because you tested them.

Your items in it:
- The Corner rail sits flush in the top left corner and opens downward.
- The three icons next to Play are one size.
- Back from an actor takes one move: focus no longer jumps up to Play first.
- The Cinematic page scrolls more smoothly: the action buttons are plain now, not glass, which was the biggest cost I measured.
- Classic Home: the row heading no longer lands high and drops, and the catalog name under the logo is gone, with the logo bigger. The logo over old text I could not reproduce.
- Search retries once when it comes back empty and shows the failure instead of a blank page. Voice search is filed with it.
- The stream list is lighter, and a row expands half a second after you rest on it.

The cheaper depth effects crashed on Home, so they did not make it.

Two things if you have a minute. When an HDR film plays in mpv, is mpv there from the first frame or does it take over a few seconds in? And a short Back press in the player on your remote, since I cannot make it eject here.

For your own build, the README now covers the local.properties file.
```

## 4. GitHub #5, SenPlayer — POSTED 2026-10-22T21:45:52Z (https://github.com/youngchris29-art/NuvioTV/issues/5#issuecomment-6352014389, left open)

**NOT POSTED.** Comment on youngchris29-art/NuvioTV #5: `gh issue comment 5 --repo youngchris29-art/NuvioTV --body-file <file>`, then check it with `gh issue view`. Leave the issue open until the reporter answers.

Facts behind it: adapted from the held refresh in `docs/comms-github-issue5-reply-2026-10-21.md` · SenPlayer rode the release candidates from rc5 and reaches a public build for the first time · the Default Player path is from `docs/comms-beta19-highlights.md` · the caveat is unchanged: built against the Outplayer and VidHub parameter names, never run on hardware here · the reporter never answered the version question · close offered, not done.

Body (148 words):

```text
SenPlayer is in beta 19, which is out now: https://github.com/youngchris29-art/NuvioTV/releases/latest

With SenPlayer installed on the Apple TV it shows up under Settings > Player > Default Player, and in the hold menu on any source row, the same as Infuse and VidHub. The handoff sends the link, the title, the resume position and the add-on subtitle, and NuvioTV listens for the position SenPlayer reports when you come back.

I built it against the parameter names Outplayer and VidHub use, since SenPlayer doesn't publish its scheme, and I don't have SenPlayer on my own Apple TV to check it end to end. Once you've tried it, tell me whether it started at your resume point, whether the subtitle showed, and whether your position carried back to NuvioTV when you exited. If it all works, say so and I'll close this. If any of it misses, I'll adjust the handoff.
```

## 5. GitHub #7 and #8, shipped — POSTED 2026-10-22T21:45:53Z / 21:45:54Z (#7 issuecomment-6352014716, #8 issuecomment-6352014942), both CLOSED

**NOT POSTED.** One comment each on youngchris29-art/NuvioTV, posted with `gh issue comment <n> --repo youngchris29-art/NuvioTV --body-file <file>` and checked with `gh issue view`. Close each after posting with `gh issue close <n> --repo youngchris29-art/NuvioTV`.

Facts behind it: both fixes are in `c7c49686c`, carried since rc11 · that commit carries `Co-authored-by: erdist`, which is the credit the comment names · Plugins sit in Settings > Sources (`SourcesSettingsPane.swift`) · the posted replies in `docs/comms-github-issues-7-8-replies-2026-10-21.md` promised the next build · Play on a series stopping the trailer is in the highlights.

### #7, Plugins one row per provider (75 words)

```text
This is in beta 19, which is out now: https://github.com/youngchris29-art/NuvioTV/releases/latest

Each plugin provider has its own row under Settings > Sources > Plugins, so Select flips one provider and not the whole repository. It went in with your patch, credited to you on the commit, along with the collapse and the A to Z order. Thanks again for doing the work. I'll close this one. If a provider row misbehaves on your setup, reopen it.
```

### #8, trailer under Play on a series (58 words)

```text
Fixed in beta 19, which is out now: https://github.com/youngchris29-art/NuvioTV/releases/latest

Play on a series now stops the background trailer the same way Play on a film does, so with Trailer Sound on you no longer hear it under the episode. I'll close this one. If a trailer still plays on after Play, reopen it with the title you used.
```

## 6. GitHub #9 and #10, in beta 19 — POSTED 2026-10-22T21:45:55Z / 21:45:56Z (#9 issuecomment-6352015165, CLOSED; #10 issuecomment-6352015427, open)

**NOT POSTED.** One comment each, posted the same way. #9 offers a close with the release. #10 waits on the reporter's hardware check of the key fields.

Facts behind it: reworded from `docs/comms-github-issues-9-10-landed-2026-10-22.md` with the tip commit dropped · that work merged in `fccfabb3b`, an ancestor of build 144 · the key field split was exercised on the simulator only, and #10 says so · the clipped row did not reproduce on the simulator or the box · 78 languages counted in `PlayerLanguageOptionCodes.kt` (the landed draft's notes said 77, the review and the highlights say 78) · #10 now says three of the four are in, since item 3 did not reproduce.

### #9, Production and Cast rows, swatches, hold menus (190 words)

```text
All three are in beta 19, which is out now: https://github.com/youngchris29-art/NuvioTV/releases/latest

Production and Cast rows. The caption now drops with the picture on both rows in the cell you were on (Accent Focus Ring off, No Zoom on Focus off), so the tile moves as one piece. The ring path was already whole. Measured, the avatar grows by about a third and the studio chip by about a tenth, which is where the system lift puts them.

Text Color swatches. Each swatch is its own focus target now, with the Appearance ring and lift, so you can see which one you are on before you pick it.

Hold menu on covers. Hold on an episode card for Mark Episode Watched or Unwatched and Mark Previous Episodes Watched or Unwatched. Hold on a season poster or a season chip for Mark Season Watched or Unwatched. Focus stays on the cover you acted on.

If you build from source: the README now has the local.properties step a fresh clone needs before sign-in works.

I'll close this with the release. If any of the three still looks wrong on your setup, reopen it.
```

### #10, key fields, OLED on Add-ons, clipped row, languages (297 words)

```text
Three of the four are in beta 19, which is out now: https://github.com/youngchris29-art/NuvioTV/releases/latest. Item 3, the clipped row, I could not reproduce.

1. API key fields. The field and Save are separate rows now, for the TMDB and MDBList keys, the plugin repository URL and Install, and the badge pack URL and Import. After Save, focus lands on Remove, and after Remove, on the field. I could only exercise this on the simulator, because my Apple TV profile already has keys saved and its rows show Remove only. If the field still refuses focus on your hardware, tell me and I will look at the row again.

2. OLED on Add-ons. Add-ons draws the app background now. The new language pages and the MDBList lists page had the same gap and got the same line.

3. Clipped focused row. I could not reproduce it. On the simulator and on the Apple TV the focused row's platter overhangs the list edge uncut, in Default and in Minimal style, root list and panes. A screenshot with the pane name would let me find it.

4. Languages. The pickers show all 78 languages, sorted A to Z by name, on a page of their own with the current choice scrolled into view, since a menu that long opens at its first entry rather than the current one. Fallback Audio Language and Fallback Subtitle Language sit under the first-choice pickers, both None by default. Off stays Off: the subtitle fallback row is hidden while Subtitles is Off, and the player ignores it then.

If you build from source: the README now has the local.properties step a fresh clone needs before sign-in works.

Once you have tried the key fields on your side, tell me how they behave and I'll close this.
```
