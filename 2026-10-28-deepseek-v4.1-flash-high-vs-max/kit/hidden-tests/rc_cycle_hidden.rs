use staffing::*;
use std::rc::Rc;

#[test]
fn department_and_employee_are_freed() {
    let d = Department::new("R&D");
    let a = hire(&d, "Ada");
    let (wd, wa) = (Rc::downgrade(&d), Rc::downgrade(&a));
    drop(a);
    drop(d);
    assert!(wd.upgrade().is_none(), "department leaked");
    assert!(wa.upgrade().is_none(), "employee leaked");
}

#[test]
fn employee_stays_alive_while_department_holds_it() {
    let d = Department::new("R&D");
    let wa = Rc::downgrade(&hire(&d, "Ada"));
    assert!(wa.upgrade().is_some(), "department must keep its employees alive");
    assert_eq!(d.employee_names(), vec!["Ada".to_string()]);
}

#[test]
fn transfer_then_drop_frees_everything() {
    let d1 = Department::new("R&D");
    let d2 = Department::new("Sales");
    let a = hire(&d1, "Ada");
    transfer(&a, &d2);
    let ws = [Rc::downgrade(&d1), Rc::downgrade(&d2)];
    let wa = Rc::downgrade(&a);
    drop((a, d1, d2));
    assert!(ws.iter().all(|w| w.upgrade().is_none()), "department leaked after transfer");
    assert!(wa.upgrade().is_none(), "employee leaked after transfer");
}

#[test]
fn many_employees_do_not_leak() {
    let mut weak = Vec::new();
    for i in 0..10_000 {
        let d = Department::new("Temp");
        let e = hire(&d, &format!("e{i}"));
        weak.push((Rc::downgrade(&d), Rc::downgrade(&e)));
    }
    assert!(weak.iter().all(|(d, e)| d.upgrade().is_none() && e.upgrade().is_none()), "leak in loop");
}

#[test]
fn department_of_works_while_department_lives() {
    let d = Department::new("Ops");
    let a = hire(&d, "Ada");
    assert_eq!(department_of(&a).as_deref(), Some("Ops"));
    fire(&a);
    assert_eq!(department_of(&a), None);
}
