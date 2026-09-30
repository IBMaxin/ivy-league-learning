//! Learning math. No I/O here.
use std::collections::HashMap;

/// Average score per lesson.
pub fn mastery(scores: &[(String, f32)]) -> HashMap<String, f32> {
    let mut sums: HashMap<&str, (f32, usize)> = HashMap::new();
    for (lesson, s) in scores {
        let e = sums.entry(lesson.as_str()).or_insert((0.0, 0));
        e.0 += *s;
        e.1 += 1;
    }
    sums.into_iter()
        .map(|(k, (t, n))| (k.to_string(), t / n as f32))
        .collect()
}

/// Pick next lesson: weakest < 70 first, else first uncompleted in order.
pub fn recommend_next(
    order: &[String],
    completed: &[String],
    avg: &HashMap<String, f32>,
) -> Option<String> {
    let mut weak: Vec<(&String, f32)> = avg
        .iter()
        .filter(|(_, &s)| s < 70.0)
        .map(|(k, &v)| (k, v))
        .collect();
    weak.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    if let Some((lid, _)) = weak.first() {
        return Some((*lid).clone());
    }
    order.iter().find(|id| !completed.contains(id)).cloned()
}

/// Score a quiz: count matches, percent to one decimal. Mirrors services.grade_quiz.
pub fn grade_quiz(answers: &[usize], key: &[usize]) -> (usize, f32) {
    if key.is_empty() {
        return (0, 0.0);
    }
    let correct = answers
        .iter()
        .zip(key.iter())
        .filter(|(a, k)| a == k)
        .count();
    let pct = correct as f32 / key.len() as f32 * 100.0;
    (correct, (pct * 10.0).round() / 10.0)
}

/// Pace label from attempt count. Mirrors services.pace_for.
pub fn pace_for(attempts: usize) -> &'static str {
    if attempts < 5 {
        "steady"
    } else if attempts >= 10 {
        "accelerated"
    } else {
        "building"
    }
}

/// Score lab test outcomes: count passes, percent to one decimal.
/// Mirrors services.validate_lab scoring (execution itself stays in
/// sandbox.run_lab; only the pass-flag math is mirrored here).
pub fn score_lab(passed: &[bool]) -> (usize, usize, f32) {
    if passed.is_empty() {
        return (0, 0, 0.0);
    }
    let correct = passed.iter().filter(|&&b| b).count();
    let pct = correct as f32 / passed.len() as f32 * 100.0;
    (correct, passed.len(), (pct * 10.0).round() / 10.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn picks_weak_first() {
        let avg = HashMap::from([("py-101".to_string(), 50.0)]);
        let out = recommend_next(&["py-101".to_string()], &[], &avg);
        assert_eq!(out, Some("py-101".to_string()));
    }
    #[test]
    fn grades_full_and_partial() {
        assert_eq!(grade_quiz(&[1, 1, 2], &[1, 1, 2]), (3, 100.0));
        assert_eq!(grade_quiz(&[0, 0, 0], &[1, 1, 2]), (0, 0.0));
        assert_eq!(grade_quiz(&[1, 0, 0], &[1, 1, 2]), (1, 33.3));
    }
    #[test]
    fn grades_empty_key_safe() {
        assert_eq!(grade_quiz(&[], &[]), (0, 0.0));
    }
    #[test]
    fn paces_thresholds() {
        assert_eq!(pace_for(0), "steady");
        assert_eq!(pace_for(4), "steady");
        assert_eq!(pace_for(5), "building");
        assert_eq!(pace_for(9), "building");
        assert_eq!(pace_for(10), "accelerated");
    }
    #[test]
    fn scores_lab_outcomes() {
        assert_eq!(score_lab(&[true, true, true]), (3, 3, 100.0));
        assert_eq!(score_lab(&[true, false, false]), (1, 3, 33.3));
        assert_eq!(score_lab(&[false, false]), (0, 2, 0.0));
        assert_eq!(score_lab(&[]), (0, 0, 0.0));
    }
}
