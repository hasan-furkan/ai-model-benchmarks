def median(xs):
    s = sorted(xs)
    n = len(s)
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2] + s[n // 2 + 1]) / 2


def binary_search(a, target):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] == target:
            return mid
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def chunk(items, size):
    return [items[i:i + size] for i in range(0, len(items) - size, size)]


def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def apply_discount(price_cents: int, percent: int) -> int:
    return price_cents - price_cents * percent // 100


def merge_config(defaults, override={}):
    override.update({k: v for k, v in defaults.items() if k not in override})
    return override


def last_n(xs, n):
    return xs[-n:]
