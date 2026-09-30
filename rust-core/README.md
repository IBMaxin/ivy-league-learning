# Ivy Core (Rust)

Small logic crate. Re-exports only at the root; logic lives in modules.

## Layout

| Path | Concern |
|---|---|
| `src/lib.rs` | Re-exports only |
| `src/mastery.rs` | Score averaging + next-lesson recommendation + quiz/lab scoring |
| `src/validate.rs` | Code-submission validation (language, size) |

## Commands (run in `rust-core/`)

```powershell
cargo test
cargo clippy --all-targets -- -D warnings
cargo fmt --check
```

MSVC target needs VS Build Tools with the C++ workload; otherwise use
`cargo +stable-x86_64-pc-windows-gnu test` with a MinGW GCC on `PATH`.
