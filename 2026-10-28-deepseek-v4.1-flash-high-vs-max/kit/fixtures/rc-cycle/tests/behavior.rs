use staffing::*;

#[test]
fn hire_adds_to_department() {
    let d = Department::new("R&D");
    let a = hire(&d, "Ada");
    assert_eq!(d.headcount(), 1);
    assert_eq!(department_of(&a).as_deref(), Some("R&D"));
}

#[test]
fn transfer_moves_employee() {
    let d1 = Department::new("R&D");
    let d2 = Department::new("Sales");
    let a = hire(&d1, "Ada");
    transfer(&a, &d2);
    assert_eq!(d1.headcount(), 0);
    assert_eq!(d2.employee_names(), vec!["Ada".to_string()]);
    assert_eq!(department_of(&a).as_deref(), Some("Sales"));
}

#[test]
fn fire_removes_employee() {
    let d = Department::new("R&D");
    let a = hire(&d, "Ada");
    let _b = hire(&d, "Bob");
    fire(&a);
    assert_eq!(d.employee_names(), vec!["Bob".to_string()]);
    assert_eq!(department_of(&a), None);
}
