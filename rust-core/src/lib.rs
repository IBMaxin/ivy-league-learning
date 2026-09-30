//! Crate root. Re-exports only — logic lives in modules.
pub mod mastery;
pub mod validate;

pub use mastery::{grade_quiz, mastery, pace_for, recommend_next, score_lab};
pub use validate::{validate, MAX_CHARS};
