# BUG-208: search shows People but no titles; running it again works (2026-10-21)

Read-only investigation on `NuvioMobile-wave3` @ `8e16c2871` (`claude/wave3`). No source edits.
Evidence: Steven's rc11 photo (`steven-rc11-verdict-2026-10-21/photo-1.small.jpeg`): "Avatar" typed,
one suggestion chip (the quoted query), no Top result, no type rows, no "Searching…", no empty
state, "Personnes" row with six TMDB people. French locale, 8 add-ons, Grouped by type.

## 1. Keystroke to rows

1. `SearchQueryBox` text → `.onChange` → `SearchViewModel.queryChanged` (SearchView.swift:320-321).
2. `queryChanged` (SearchViewModel.swift:445-499) cancels the previous debounce Task, trims, applies
   `isTooShortToSearch` (1 ASCII char only, :440), flips `queryIsEmpty` on the edge, then a 450 ms
   debounce Task sets `activeQuery`/`displayQuery` and `activeRequestId = SearchRepository.search(...)`.
3. `SearchRepository.search` (SearchRepository.kt:82-270): builds the fan-out, `requestKey` (query
   lowercased + flags + catalog set, :138-162); same key and not forced → returns `lastRequestId`
   and publishes nothing (:167). Otherwise cancels `activeJob`, publishes a loading state with a new
   id, launches: TMDB people as a sibling (:183-195), one child per catalog with
   `withTimeoutOrNull(10 s)` (:197-211; `SEARCH_CATALOG_TIMEOUT_MS` :1134), results through a channel,
   progressive publishes only when sections are non-empty (:220-235), then one final publish
   (:250-268). Every write goes through `publish(myId)` (CAS on request id, :294-298).
4. Each child: `fetchOutcome` → `fetchCatalogPage` → `deduplicatedHttpGetText` →
   `CatalogInflightRequests.get` (CatalogData.kt:51-115) → Ktor Darwin `httpGetText`
   (AddonPlatform.apple.kt:87-101; a non-2xx is `error(...)`, so a 504 is a Failed outcome).
5. Swift `accept` (SearchViewModel.swift:221-250): drops other request ids, runs rows through
   `SearchRowsHold`, and adopts Top result, People and chips only from the emission whose rows are
   on screen (`adoptExtras`, :270-281). People and rows therefore always come from ONE emission.

## 2. What the photo pins down

- The chip row is visible, and it is hidden while `rows.isEmpty && isLoading` (SearchView.swift:423),
  so the search had SETTLED (`isLoading == false`).
- No empty state although nothing but People shows: the empty state needs `people.isEmpty`
  (SearchViewModel.swift:295), and Kotlin's `resolveEmptyState` returns null when `hasPeople`
  (SearchResultGrouping.kt:210; called at SearchRepository.kt:257-261).
- So the screen is the active request's FINAL emission with zero `Success` outcomes (groups come
  only from Success, SearchResultGrouping.kt:51-62) and TMDB people present.

## 3. Hypotheses, ranked

**H1 (top, confirmed upstream): Cinemeta's search origin fails transiently and People masks it.**
Cinemeta search URLs are Cloudflare-cached per exact URL (`cf-cache-status: HIT`, `max-age=86400`).
A miss goes to the origin. Measured from this Mac today (20 GETs: 17 first tries, 3 retries):
cached hits answer in ~0.15 s; misses take 2-6 s, and 5 of 20 returned **HTTP 504 after ~6.35 s**
(`Avata` series, `Avat` movie, `Avatar la` movie twice, a random `Avatar x…`); 2 of the 3 retries of
a 504 answered 200 in 2.6-6.2 s (origin warmed). Steven queries through a French edge, so a query
cached here can be a miss for him. With Cinemeta the only title source for "Avatar" (stream add-ons
return Empty or have no search catalogs), both Cinemeta catalogs failing leaves zero Success,
TMDB answers fast, and the page settles to exactly the photo: no error, no Retry. "Run it again" works
because the origin is warm and the CDN now holds the answer. Note the RequestFailed state is lost
twice: `allFailed` is false when any other catalog answered Empty (:248), and `hasPeople` nulls the
reason anyway. Retyping the identical query without clearing would not even refetch (same-key dedup,
:167); the Retry button (`retrySearch`, forceRefresh) is the only bypass, and People hides it.

**H2 (low): a cancelled shared future handed to a live waiter.** `CatalogInflightRequests.get`
removes the entry and cancels its job under the same mutex, only when `waiters` hits 0 and the result
is pending (CatalogData.kt:100-108); a later joiner either joined first (kept alive) or gets a fresh
entry. No path hands a cancelled deferred to a live waiter. Latent hazard if one ever appears: the
child rethrows any CancellationException (SearchRepository.kt:207), so that catalog's outcome would
vanish silently instead of becoming Failed.

**H3 (low, real but not this photo): debounce cancelled by `stop()`.** `stop()` cancels the debounce
(SearchViewModel.swift:199) and the field's `.onChange` does not refire on return, so a word finished
less than 450 ms before a tab switch is never searched; the page keeps the previous prefix's results
(titles present), so it does not match the photo.

**Ruled out:** too-short rule (1 ASCII char only); query/case/whitespace mismatch (Swift keys on
request id; Kotlin trims and lowercases only the dedup key); Swift stale-drop or hold (People and rows
are adopted from the same accepted emission); manifest-pending start (`isLoading` stays true and
"Searching…" shows); an exception publishing empty over the previous results (the hold keeps old rows
only while loading, by design, and the photo state is a settled final emission).

## 4. Proposed fix (smallest first)

1. **Retry a failed catalog once** (Kotlin, SearchRepository.kt:197-211): when the first attempt is
   `Failed` with a non-timeout error (504 lands at ~6.4 s), wait ~250 ms and retry once under its own
   `withTimeoutOrNull(SEARCH_CATALOG_TIMEOUT_MS)`. The failed shared fetch has already left the
   in-flight map, so the retry is a fresh request. Error text is localized (French), so classify by
   type (not message): skip only `SearchCatalogTimeoutException`. ~10 lines + a jvmTest with
   `searchPageFetcherForTest` failing the first call per catalog.
2. **Unmask the failure** (same batch): `resolveEmptyState` → `RequestFailed` when no outcome is
   Success and any is Failed, even with people; set `errorMessage` from the first failure in that
   case (not only `allFailed`). In Swift, let a `requestFailed` state render above the People row
   (drop `people.isEmpty` for that state in `refreshEmptyState`, keep it for `noResults`), so Retry
   is reachable. Retry already forces past the same-key dedup.
3. Optional: in `stop()`, keep a pending debounce's query and re-fire it from `start()` (H3).

## 5. Probe

- Already there (DEBUG): `[SearchPerf] results q="Avatar" first=-1 last=<ms>` — `first=-1` (no rows
  ever) with `last` ≈ 6300-6500 is Cinemeta's 504; ≈ 10000 is our timeout. `search_state … rows=0
  people=6 empty=-` is the photo state.
- Add (DEBUG, Kotlin `println`, Kermit is invisible on device): one line per non-Success child,
  `[SearchPerf] catalog q="Avatar" key=<manifestId:type:catalogId> outcome=failed|empty ms=<n>
  err=<class>` plus `retry=ok|failed` after fix 1. The fix is confirmed when a 504 line is followed by
  `retry=ok` and rows appear.

## 6. Simulator repro

1. Fixture sim, TMDB on, Cinemeta enabled, Grouped. Type a query that is a CDN miss: a fresh string
   such as `Avatar la` or `Avatar` + two random letters (any query searched before is cached for 24 h;
   check with `curl -sI …/catalog/movie/top/search=<q>.json | grep cf-cache-status`).
   Expect in ~1 of 3 tries: People row only, no error, `[SearchPerf] results first=-1 last≈6400`.
2. Deterministic: block or delay `v3-cinemeta.strem.io` (Proxyman/Charles map-remote to a 504, or
   Network Link Conditioner 100 % loss for that host) and search any word with people matches.
3. Controls (expected NOT to reproduce): fast typing then pause; tap the quoted chip (records history
   only); clear and retype the same word (fresh request id, refetches); retype the same word without
   clearing after a failure (deduped, keeps the empty page: shows why Steven had to "run it again").
