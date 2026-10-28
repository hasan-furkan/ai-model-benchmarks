> Translated from the original Turkish prompt that the agents actually received.

This folder is a small Rust library (`dice`): randomness helpers for a game server. The six functions in `src/lib.rs` have not been written yet (`unimplemented!()`).

**Wanted:** Write the six functions with the `rand` crate according to the behaviour in their documentation. Do NOT change the `rand` version or the dependencies in `Cargo.toml`. Do not remove the `#![deny(deprecated)]` line or silence it with `allow`. `tests/behavior.rs` must pass unchanged; add your own tests if needed.

**Definition of done:** the last line of `powershell -NoProfile -File check.ps1` is `CHECK PASSED`.

**Short report at the end:** which `rand` APIs you used, the problems you ran into.
