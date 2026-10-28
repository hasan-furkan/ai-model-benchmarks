//! Randomness helpers for the game server.
#![forbid(unsafe_code)]
#![deny(deprecated)]

/// Uniform integer in `lo..=hi` from the thread-local generator. Panics are not allowed; assume lo <= hi.
pub fn random_between(lo: i64, hi: i64) -> i64 {
    let _ = (lo, hi);
    unimplemented!()
}

/// True with probability `p` (0.0..=1.0) from the thread-local generator.
pub fn chance(p: f64) -> bool {
    let _ = p;
    unimplemented!()
}

/// A shuffled copy of `items`, reproducible for the same `seed` (use `StdRng`).
pub fn shuffled(items: &[u32], seed: u64) -> Vec<u32> {
    let _ = (items, seed);
    unimplemented!()
}

/// `k` distinct elements of `items` (all of them if k >= len), reproducible for the same `seed`.
pub fn pick_distinct(items: &[u32], k: usize, seed: u64) -> Vec<u32> {
    let _ = (items, k, seed);
    unimplemented!()
}

/// One element chosen uniformly, or None for an empty slice, reproducible for the same `seed`.
pub fn pick_one(items: &[u32], seed: u64) -> Option<u32> {
    let _ = (items, seed);
    unimplemented!()
}

/// A fresh 64-bit value straight from the operating system's random source (for session ids).
pub fn os_random_u64() -> u64 {
    unimplemented!()
}
