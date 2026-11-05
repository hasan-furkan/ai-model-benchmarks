"""Tiny JSON API. `handle` is called by the HTTP layer with the parsed request."""
from datetime import timezone

import db
from fmt import iso_utc, money


def error(status, message):
    return status, {"error": message}


def list_customers(query):
    city = query.get("city")
    rows = [c for c in db.CUSTOMERS if city is None or c["city"] == city]
    return 200, [
        {"id": c["id"], "name": c["name"], "balance": money(c["balance"]), "created_at": iso_utc(c["created_at"])}
        for c in rows
    ]


def get_customer(customer_id):
    for c in db.CUSTOMERS:
        if c["id"] == customer_id:
            return 200, {"id": c["id"], "name": c["name"], "balance": money(c["balance"]), "created_at": iso_utc(c["created_at"])}
    return error(404, "customer not found")


def handle(method, path, query):
    if method != "GET":
        return error(405, "method not allowed")
    if path == "/customers":
        return list_customers(query)
    if path.startswith("/customers/"):
        raw = path.removeprefix("/customers/")
        if not raw.isdigit():
            return error(400, "customer id must be a number")
        return get_customer(int(raw))
    return error(404, "not found")
