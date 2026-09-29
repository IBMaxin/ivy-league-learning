//! Crate root. Re-exports only — logic lives in modules.
pub mod mastery;
pub mod validate;

pub use mastery::{mastery, recommend_next};
pub use validate::{validate, MAX_CHARS};
