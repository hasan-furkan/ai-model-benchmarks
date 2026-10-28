use dice::*;

#[test]
fn random_between_edges() {
    assert_eq!(random_between(5, 5), 5);
    let _ = random_between(i64::MIN, i64::MAX);
    let mut seen = std::collections::HashSet::new();
    for _ in 0..2000 {
        seen.insert(random_between(0, 3));
    }
    assert_eq!(seen.len(), 4, "every value in 0..=3 must be reachable (inclusive upper bound)");
}

#[test]
fn chance_is_roughly_fair() {
    let hits = (0..20_000).filter(|_| chance(0.5)).count();
    assert!((9_000..11_000).contains(&hits), "chance(0.5) gave {hits}/20000");
}

#[test]
fn seeds_matter() {
    let items: Vec<u32> = (0..50).collect();
    assert_ne!(shuffled(&items, 1), shuffled(&items, 2));
    assert_eq!(pick_distinct(&items, 5, 9), pick_distinct(&items, 5, 9));
    assert_eq!(pick_one(&items, 4), pick_one(&items, 4));
}

#[test]
fn pick_distinct_edges() {
    assert!(pick_distinct(&[1, 2, 3], 0, 1).is_empty());
    assert!(pick_distinct(&[], 3, 1).is_empty());
    let mut all = pick_distinct(&[3, 1, 2], 3, 5);
    all.sort();
    assert_eq!(all, vec![1, 2, 3]);
}
