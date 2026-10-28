> Translated from the original Turkish prompt that the agents actually received.

This folder is a small JSON API (Python 3.11, standard library only). Requests are served by `app.handle(method, path, query)`.

**Wanted:** Add the `GET /orders?customer_id=<id>` endpoint: return that customer's orders (`id`, `total`, `created_at`) sorted newest to oldest. Write its tests. Do not add a new dependency.

**Definition of done:** the last line of `powershell -NoProfile -File check.ps1` is `CHECK PASSED`.

**Short report at the end:** what you added, which tests you wrote.
