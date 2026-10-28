# Answer key (NOT given to the workers)
## Code (5 bugs, 2 traps)
- H1 median: for even lengths it must be s[n//2-1] and s[n//2] (s[n//2+1] is wrong, IndexError at n=2).
- H2 binary_search: must be `while lo <= hi`; in a single-element list / on the last candidate the target is missed.
- H3 chunk: must be range(0, len(items), size); the last partial chunk (and everything when len==size) is dropped.
- H4 merge_config: the mutable default argument `override={}` is shared between calls and mutated.
- H5 last_n: at n=0, xs[-0:] returns the whole list (an empty list is expected).
- T1 is_leap: CORRECT (trap).
- T2 apply_discount: CORRECT (integer cents, trap).
## Document (4 false)
- F3 IPv6 is not 64 bits, it is 128 bits.
- F6 UTF-8 is 1–4 bytes today (RFC 3629); 6 bytes is the old definition.
- F8 SQLite is not client-server, it is an embedded database.
- F11 Dijkstra does not work correctly with negative weights.

# Round 2
## Code2 (6 bugs, 3 traps)
- H1 LRUCache.get: no move_to_end; get does not count as a use and the wrong item is evicted.
- H2 Counter.increment: the write happens outside the lock; race (lost increment).
- H3 page: 1-based; the offset must be (number-1)*size, the first page is skipped.
- H4 mean_of_positive: the generator is consumed by sum; count is always 0 → returns 0.0.
- H5 is_expired: naive datetime.now() compared against an aware datetime → TypeError; must be datetime.now(timezone.utc).
- H6 round_half_even_cents: float error (e.g. 2.675*100=267.49999) — round() does banker's rounding but the float representation makes it wrong; Decimal is required. (subtle; an acceptable finding)
- T1 merge_intervals: CORRECT (<= merges touching intervals, as documented).
- T2 retry: CORRECT (raises on the last attempt, delay is bounded).
- T3 utc_now: CORRECT.
## Document2 (5 false)
- F5 In release, Rust overflow wraps by default; no panic.
- F6 In 3.13 the free-threaded build is optional/experimental; the GIL stays in the default installation.
- F8 The InnoDB default is REPEATABLE READ.
- F11 The reverse: DNS uses UDP 53 by default; TCP is for large responses / zone transfer.
- F12 JSON does not allow comments.
