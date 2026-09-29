//! Code validation. No execution here.
pub const MAX_CHARS: usize = 10_000;

/// Returns an error string when code should be rejected.
pub fn validate(language: &str, code: &str) -> Option<String> {
    if !matches!(language, "python" | "rust" | "javascript") {
        return Some("unsupported language".to_string());
    }
    if code.is_empty() {
        return Some("empty code".to_string());
    }
    if code.len() > MAX_CHARS {
        return Some("code too large".to_string());
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_large() {
        assert!(validate("python", &"x".repeat(MAX_CHARS + 1)).is_some());
    }
}
