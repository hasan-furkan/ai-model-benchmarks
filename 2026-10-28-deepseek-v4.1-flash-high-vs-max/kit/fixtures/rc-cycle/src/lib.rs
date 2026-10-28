//! Departments and employees for a long-running HR service.
#![forbid(unsafe_code)]

use std::cell::RefCell;
use std::rc::Rc;

pub struct Department {
    pub name: String,
    pub employees: RefCell<Vec<Rc<Employee>>>,
}

pub struct Employee {
    pub name: String,
    pub department: RefCell<Option<Rc<Department>>>,
}

impl Department {
    pub fn new(name: &str) -> Rc<Department> {
        Rc::new(Department {
            name: name.to_string(),
            employees: RefCell::new(Vec::new()),
        })
    }

    pub fn headcount(&self) -> usize {
        self.employees.borrow().len()
    }

    pub fn employee_names(&self) -> Vec<String> {
        self.employees
            .borrow()
            .iter()
            .map(|e| e.name.clone())
            .collect()
    }
}

/// Creates an employee inside `dept`.
pub fn hire(dept: &Rc<Department>, name: &str) -> Rc<Employee> {
    let employee = Rc::new(Employee {
        name: name.to_string(),
        department: RefCell::new(Some(Rc::clone(dept))),
    });
    dept.employees.borrow_mut().push(Rc::clone(&employee));
    employee
}

/// Name of the employee's current department, if any.
pub fn department_of(employee: &Employee) -> Option<String> {
    employee
        .department
        .borrow()
        .as_ref()
        .map(|d| d.name.clone())
}

/// Moves the employee from their current department to `to`.
pub fn transfer(employee: &Rc<Employee>, to: &Rc<Department>) {
    fire(employee);
    *employee.department.borrow_mut() = Some(Rc::clone(to));
    to.employees.borrow_mut().push(Rc::clone(employee));
}

/// Removes the employee from their department.
pub fn fire(employee: &Rc<Employee>) {
    let old = employee.department.borrow_mut().take();
    if let Some(dept) = old {
        dept.employees
            .borrow_mut()
            .retain(|e| !Rc::ptr_eq(e, employee));
    }
}
