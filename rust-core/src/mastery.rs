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

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn picks_weak_first() {
        let avg = HashMap::from([("py-101".to_string(), 50.0)]);
        let out = recommend_next(&["py-101".to_string()], &[], &avg);
        assert_eq!(out, Some("py-101".to_string()));
    }
}
