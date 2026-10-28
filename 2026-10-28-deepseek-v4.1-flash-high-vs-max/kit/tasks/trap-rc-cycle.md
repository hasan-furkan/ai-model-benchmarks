> Translated from the original Turkish prompt that the agents actually received.

This folder is a small Rust library (`staffing`): departments and employees. It is used in a long-running HR service.

**User report:** After the service runs for days, memory keeps growing; even though departments and employees are deleted, the memory does not seem to come back.

**Wanted:** Find the problem and fix it at the root (restructure the types if necessary). The public API must stay the same: `Department::new`, `headcount`, `employee_names`, `hire`, `department_of`, `transfer`, `fire` must keep working with the same signatures and `tests/behavior.rs` must pass unchanged. Add tests proving your fix. Do not add a new dependency, no `unsafe`.

**Definition of done:** the last line of `powershell -NoProfile -File check.ps1` is `CHECK PASSED`.

**Short report at the end:** root cause, the change you made, the tests you added.
