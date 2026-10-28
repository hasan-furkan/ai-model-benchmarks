use dice::*;

#[test]
fn random_between_stays_in_range() {
    for _ in 0..1000 {
        let v = random_between(-3, 3);
        assert!((-3..=3).contains(&v));
    }
}

#[test]
fn chance_extremes() {
    assert!(!chance(0.0));
    assert!(chance(1.0));
}

#[test]
fn shuffled_is_a_reproducible_permutation() {
    let items: Vec<u32> = (0..50).collect();
    let a = shuffled(&items, 7);
    assert_eq!(a, shuffled(&items, 7));
    let mut sorted = a.clone();
    sorted.sort();
    assert_eq!(sorted, items);
}

#[test]
fn pick_distinct_gives_k_unique_items() {
    let items: Vec<u32> = (0..20).collect();
    let mut p = pick_distinct(&items, 5, 1);
    assert_eq!(p.len(), 5);
    p.sort();
    p.dedup();
    assert_eq!(p.len(), 5);
    assert_eq!(pick_distinct(&items, 50, 1).len(), 20);
}

#[test]
fn pick_one_handles_empty() {
    assert_eq!(pick_one(&[], 3), None);
    assert!(pick_one(&[4, 5], 3).is_some());
}

#[test]
fn os_random_values_differ() {
    assert_ne!(os_random_u64(), os_random_u64());
}
