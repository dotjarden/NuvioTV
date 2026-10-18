# mpv event-queue stall on DV P5 / gpu-next (2026-10-18)

Side session of the Batch E device pass. Living Room Apple TV, profile **Test 2**, Dune: Part One,
Torrentio "[2021 WEB-DL 2160p Dolby Vision TV]" 29.41 GB Rutracker (5th Torrentio stream) →
`[PlayerRouter] mpv — DV P5 in MP4`, `vo=gpu-next`. Logs are redacted (`/stremio/<redacted>/`).

## Root cause

Not a blocking property read and not DV-specific. In `onFileLoaded`, every prefetched add-on
subtitle was side-loaded with a **synchronous** `mpv_command("sub-add", url, "auto", …)` on the serial
`eventQueue`. A synchronous `sub-add` downloads and parses the file before it returns. Dune comes
back with 95–112 add-on subtitles (OpenSubtitles v3 95, plus 17 from an AIOStreams add-on); at about
1.2 s each the queue was busy for 130–150 s after FILE_LOADED. Everything queued behind them waited:
the display criteria (HDR late or never), `[MPVStats]`, the harvest, the unpause after the display
mode hold, the startup aspect, seeks, the first track walk.

Evidence in the Batch E logs (`../batch-e-device-pass-2026-10-18/`):
- 168e: `[MPVQueue] stats ran lag=129859ms`, and the whole backlog (criteria, every stats line, the
  startup aspect `[Aspect] fit`) ran at one instant, 12:28:57, while playback carried on to 600 s, so
  it was not the exit. The `[Aspect]` block is queued straight after the 112 `sub-add` blocks.
- The `[MPV]` log lines that kept arriving during the stall came from inside those blocks: each
  `sub-add` block drains events before and after its command. Their NSLog timestamps come in
  batches, one per block boundary.
- 168c (hold path): the unpause after the hold sat behind the sub-adds, so the picture stayed paused
  at reader-pts 12.68 for 2.5 minutes.
- 168b, the "healthy" run, also stalled for about 20 s (stats +5 s … +26 s all printed at 12:13:55).
  Its subtitles arrived 5 s late through the watcher, so fewer blocks were queued ahead.

## Fix (NuvioMobile working tree on `claude/batch-e`, uncommitted)

1. `MPVSubtitleSideLoadQueue` (new, `Screens/Player/`): side-loads go through `mpv_command_async`,
   one in flight at a time. The next one starts on its `MPV_EVENT_COMMAND_REPLY`, from a separate
   `eventQueue` block that drains first, so the log ring's subtitle attribution windows stay as
   before. Preferred-language files load first, by language rank.
2. `MPVSubtitleAutoSelectGate`: the first track walk now runs before add-on subtitles land, so the
   subtitle half of the auto selection waits for them. It takes a match at once only if it is final
   (top language, no pt/es tie-break, not a forced track that a full one could replace). Any other
   match waits for the preferred-language loads. With no match, it waits while anything is still
   loading, a hand-off is in transit, or the add-on search is still running. Audio is unchanged
   (decided on the first walk).
3. `applyDisplayCriteriaIfEnabled()` now polls for the colour params (the hold's poll, without the
   hold, 20 s) instead of one read at FILE_LOADED. run1 (fix 1 only) shows why: with the queue free,
   the one-shot read on gpu-next ran before the decoder reported params, giving
   `criteria … primaries=- gamma=-` (an SDR mode for an HDR title). The stall had been hiding this.

## Device results

| Run | Build | criteria | `[MPVStats]` | Harvest |
|---|---|---|---|---|
| run1 | fix 1 only | `primaries=- gamma=-` at load ✗ | from +4 s, lag 0 ms | stored at +10 s |
| run2 | final | `bt.2020 gamma=pq`, ~0.3 s after load | from +4 s, lag ≤1 ms | stored at +9.7 s |
| run3 | final | `gamma=pq` | lag 0 ms | stored at +9.7 s |
| run4 | final | `gamma=pq` | lag 0 ms | stored at +9.6 s |
| run5 | final | `gamma=pq` | lag 0 ms | stored at +9.8 s |

Side loads ran at 0.23–0.33 s each in the background (one took 5.8 s), with no errors. The exit with
loads in flight logged `terminate_destroy took=170ms`. The display mode switch itself (whether the
panel actually went to HDR/DV) cannot be seen from the rig; only the request line can.

Rig note: the Sources picker sometimes opens with focus on the first stream instead of the Comet
header, so a blind Select plays the wrong stream (it did twice). Screenshot before every Select.
