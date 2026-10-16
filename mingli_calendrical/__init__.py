# -*- coding: utf-8 -*-
"""mingli-calendrical — historical DST + true-solar-time engine for Chinese metaphysics apps.

Born in the clocks of Hong Kong / Macau / Taiwan / mainland China: if your user
was born while the clock was shifted, the *hour pillar* (and therefore the whole
chart) is wrong unless you subtract DST first, then correct to true solar time.

    >>> dst_minutes("1965-07-01", "hk")
    60
    >>> true_solar_time("1990-05-15", "12:10", lng=114.17, tz=8)
    ('1990-5-15', 6, '11:58', -12.3...)   # clock noon ≠ solar noon

Tables: IANA tzdb Asia/Hong_Kong · Asia/Macau · Asia/Taipei + PRC 1986–1991.
EU/US/AU/NZ rules are the common approximations (see docstring of dst_minutes).

Zero dependencies. MIT license.
Live demo: https://purpleking.net/ziwei
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path

__version__ = "0.1.0"

__all__ = [
    "DST_CN", "DST_HK", "DST_MO", "DST_TW",
    "time_to_index", "dst_cn_minutes", "dst_hkmo_tw_minutes", "dst_minutes",
    "equation_of_time", "true_solar_time",
    "city_geo", "city_longitude",
]

_DATA = Path(__file__).resolve().parent / "data" / "birth_cities.json"


def time_to_index(hhmm: str) -> int:
    """'HH:MM' -> 时辰序号 0..12 (子=0/12, 23:00 归晚子时=12)."""
    h = int(hhmm.split(":")[0])
    if h == 23:
        return 12
    return (h + 1) // 2


# ---------------- China DST (1986-1991) ----------------
# Clock +1h windows each year. Births inside need -60min before casting.
DST_CN = [
    ((1986, 5, 4), (1986, 9, 14)),
    ((1987, 4, 12), (1987, 9, 13)),
    ((1988, 4, 10), (1988, 9, 11)),
    ((1989, 4, 16), (1989, 9, 17)),
    ((1990, 4, 15), (1990, 9, 16)),
    ((1991, 4, 14), (1991, 9, 15)),
]


def dst_cn_minutes(date_str: str) -> int:
    """公历日期是否处于中国夏令时(1986-1991);是则返回60(分钟)。"""
    try:
        y, m, d = [int(x) for x in date_str.replace("/", "-").split("-")[:3]]
    except ValueError:
        return 0
    dt = (y, m, d)
    for (s, e) in DST_CN:
        if s <= dt <= e:
            return 60
    return 0


# Hong Kong / Macau / Taiwan DST windows (IANA tzdb Asia/Hong_Kong,
# Asia/Macau, Asia/Taipei). Unrelated to PRC 1986-91; HK/MO had no DST
# after 1979.
DST_HK = [
    ((1946, 4, 21), (1946, 11, 30)), ((1947, 4, 13), (1947, 11, 29)),
    ((1948, 5, 2), (1948, 10, 30)), ((1949, 4, 3), (1949, 10, 29)),
    ((1950, 4, 2), (1950, 10, 28)), ((1951, 4, 1), (1951, 10, 27)),
    ((1952, 4, 6), (1952, 11, 1)), ((1953, 4, 5), (1953, 10, 31)),
    ((1954, 3, 21), (1954, 10, 30)), ((1955, 3, 20), (1955, 11, 5)),
    ((1956, 3, 18), (1956, 11, 3)), ((1957, 3, 24), (1957, 11, 2)),
    ((1958, 3, 23), (1958, 11, 1)), ((1959, 3, 22), (1959, 10, 31)),
    ((1960, 3, 20), (1960, 11, 5)), ((1961, 3, 19), (1961, 11, 4)),
    ((1962, 3, 18), (1962, 11, 3)), ((1963, 3, 24), (1963, 11, 2)),
    ((1964, 3, 22), (1964, 10, 31)), ((1965, 4, 18), (1965, 10, 16)),
    ((1966, 4, 17), (1966, 10, 15)), ((1967, 4, 16), (1967, 10, 21)),
    ((1968, 4, 21), (1968, 10, 19)), ((1969, 4, 20), (1969, 10, 18)),
    ((1970, 4, 19), (1970, 10, 17)), ((1971, 4, 18), (1971, 10, 16)),
    ((1972, 4, 16), (1972, 10, 21)), ((1973, 4, 22), (1974, 10, 19)),
    ((1975, 4, 20), (1975, 10, 18)), ((1976, 4, 18), (1976, 10, 16)),
    ((1979, 5, 13), (1979, 10, 20)),
]

DST_MO = [
    ((1946, 5, 1), (1946, 9, 30)), ((1947, 4, 20), (1947, 11, 30)),
    ((1948, 5, 3), (1948, 10, 31)), ((1949, 4, 3), (1949, 10, 29)),
    ((1950, 4, 2), (1950, 10, 28)), ((1951, 4, 1), (1951, 10, 28)),
    ((1952, 4, 6), (1952, 11, 1)), ((1953, 4, 5), (1953, 10, 31)),
    ((1954, 3, 21), (1954, 10, 30)), ((1955, 3, 20), (1955, 11, 5)),
    ((1956, 3, 18), (1956, 11, 3)), ((1957, 3, 24), (1957, 11, 2)),
    ((1958, 3, 23), (1958, 11, 1)), ((1959, 3, 22), (1959, 10, 31)),
    ((1960, 3, 20), (1960, 11, 5)), ((1961, 3, 19), (1961, 11, 4)),
    ((1962, 3, 18), (1962, 11, 3)), ((1963, 3, 24), (1963, 11, 2)),
    ((1964, 3, 22), (1964, 10, 31)), ((1965, 4, 18), (1965, 10, 16)),
    ((1966, 4, 17), (1966, 10, 15)), ((1967, 4, 16), (1967, 10, 21)),
    ((1968, 4, 21), (1968, 10, 19)), ((1969, 4, 20), (1969, 10, 18)),
    ((1970, 4, 19), (1970, 10, 17)), ((1971, 4, 18), (1971, 10, 16)),
    ((1972, 4, 16), (1972, 10, 21)), ((1973, 4, 22), (1973, 10, 20)),
    ((1973, 12, 30), (1974, 10, 19)), ((1975, 4, 20), (1975, 10, 18)),
    ((1976, 4, 18), (1976, 10, 16)), ((1979, 5, 13), (1979, 10, 20)),
]

DST_TW = [
    ((1946, 5, 15), (1946, 9, 30)), ((1947, 4, 15), (1947, 10, 31)),
    ((1948, 5, 1), (1948, 9, 30)), ((1949, 5, 1), (1949, 9, 30)),
    ((1950, 5, 1), (1950, 9, 30)), ((1951, 5, 1), (1951, 9, 30)),
    ((1952, 3, 1), (1952, 10, 31)), ((1953, 4, 1), (1953, 10, 31)),
    ((1954, 4, 1), (1954, 10, 31)), ((1955, 4, 1), (1955, 9, 30)),
    ((1956, 4, 1), (1956, 9, 30)), ((1957, 4, 1), (1957, 9, 30)),
    ((1958, 4, 1), (1958, 9, 30)), ((1959, 4, 1), (1959, 9, 30)),
    ((1960, 6, 1), (1960, 9, 30)), ((1961, 6, 1), (1961, 9, 30)),
    ((1974, 4, 1), (1974, 9, 30)), ((1975, 4, 1), (1975, 9, 30)),
    ((1979, 7, 1), (1979, 9, 30)),
]


def dst_hkmo_tw_minutes(date_str: str, region: str) -> int:
    """hk/mo/tw DST table lookup -> 60|0. region∈('hk','mo','tw')."""
    try:
        y, m, d = [int(x) for x in date_str.replace("/", "-").split("-")[:3]]
    except ValueError:
        return 0
    dt = (y, m, d)
    for (s, e) in {"hk": DST_HK, "mo": DST_MO, "tw": DST_TW}.get(region, []):
        if s <= dt <= e:
            return 60
    return 0


# ---------------- True solar time ----------------

def equation_of_time(y: int, m: int, d: int, h: int, mi: int) -> float:
    """NOAA equation-of-time approximation (minutes).
    Positive = apparent solar time ahead of mean solar time."""
    days_in_year = 366 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 365
    doy = (datetime(y, m, d) - datetime(y, 1, 1)).days
    gamma = (2 * math.pi / days_in_year) * (doy + (h + mi / 60 - 12) / 24)
    return 229.18 * (0.000075 + 0.001868 * math.cos(gamma) - 0.032077 * math.sin(gamma)
                     - 0.014615 * math.cos(2 * gamma) - 0.040849 * math.sin(2 * gamma))


def true_solar_time(date_str: str, hhmm: str, lng: float, tz: float = 8):
    """Clock time -> apparent solar time.

    `tz` = the standard-time meridian offset of the birthplace in hours
    (China 8, UK 0, New York -5).
    Returns (corrected_date 'Y-M-D', time_index, corrected 'HH:MM', corr_minutes).
    """
    y, m, d = [int(x) for x in date_str.replace("/", "-").split("-")]
    h, mi = [int(x) for x in hhmm.split(":")[:2]]
    corr = (lng - tz * 15) * 4 + equation_of_time(y, m, d, h, mi)
    total = h * 60 + mi + corr
    day_shift = math.floor(total / 1440)
    rem = total - day_shift * 1440
    nh, nmi = int(rem // 60), int(rem % 60)
    nd = datetime(y, m, d) + timedelta(days=day_shift)
    tidx = 12 if nh == 23 else (nh + 1) // 2
    return f"{nd.year}-{nd.month}-{nd.day}", tidx, f"{nh:02d}:{nmi:02d}", corr


def _nth_weekday(y: int, m: int, weekday: int, n: int) -> int:
    """Day-of-month of the n-th `weekday` (0=Mon..6=Sun) in month m."""
    d = 1
    while datetime(y, m, d).weekday() != weekday:
        d += 1
    return d + 7 * (n - 1)


def _last_weekday(y: int, m: int, weekday: int) -> int:
    if m == 12:
        nm, ny = 1, y + 1
    else:
        nm, ny = m + 1, y
    d = (datetime(ny, nm, 1) - timedelta(days=1)).day
    while datetime(y, m, d).weekday() != weekday:
        d -= 1
    return d


def dst_minutes(date_str: str, region: str) -> int:
    """Regional DST rules -> 60 (minutes) if the date falls inside DST, else 0.

    hk/mo/tw/cn: exact historical tables (see module constants).
    eu: last Sun of Mar .. last Sun of Oct (EU, 1996+)
    us: 2007+ 2nd Sun Mar .. 1st Sun Nov; 1987-2006 1st Sun Apr .. last Sun Oct
    au: 1st Sun Oct .. 1st Sun Apr (NSW/VIC/SA/TAS etc.)
    nz: last Sun Sep .. 1st Sun Apr
    Historical rules have shifted; these are the common approximations —
    verify boundary days against tzdb if precision matters.
    """
    try:
        y, m, d = [int(x) for x in date_str.replace("/", "-").split("-")[:3]]
    except ValueError:
        return 0
    if y < 1940 or y > 2100:
        return 0
    if region == "cn":
        return dst_cn_minutes(date_str)
    if region in ("hk", "mo", "tw"):
        return dst_hkmo_tw_minutes(date_str, region)
    dt = (m, d)
    if region == "eu":
        s = (3, _last_weekday(y, 3, 6)); e = (10, _last_weekday(y, 10, 6))
        return 60 if s <= dt < e else 0
    if region == "us":
        if y >= 2007:
            s = (3, _nth_weekday(y, 3, 6, 2)); e = (11, _nth_weekday(y, 11, 6, 1))
        elif y >= 1987:
            s = (4, _nth_weekday(y, 4, 6, 1)); e = (10, _last_weekday(y, 10, 6))
        else:
            return 0
        return 60 if s <= dt < e else 0
    if region == "au":
        s = (10, _nth_weekday(y, 10, 6, 1))
        e = (4, _nth_weekday(y, 4, 6, 1))
        return 60 if dt >= s or dt < e else 0
    if region == "nz":
        s = (9, _last_weekday(y, 9, 6))
        e = (4, _nth_weekday(y, 4, 6, 1))
        return 60 if dt >= s or dt < e else 0
    return 0


_WORLD_FLAT: dict | None = None


def _world_flat() -> dict:
    """Bundled city DB flattened to {city:{lng,tz,dst,country}} (+ 'C|P|city' keys)."""
    global _WORLD_FLAT
    if _WORLD_FLAT is not None:
        return _WORLD_FLAT
    flat = {}
    if _DATA.exists():
        data = json.loads(_DATA.read_text(encoding="utf-8"))
        for c in data:
            for r in c.get("regions", [c]):
                for ct in r["cities"]:
                    rec = {"lng": ct["lng"], "tz": ct["tz"],
                           "dst": ct.get("dst", ""), "country": c["name"],
                           "country_en": c.get("en", "")}
                    flat.setdefault(ct["name"], rec)
                    if ct.get("en"):
                        flat.setdefault(ct["en"].lower(), rec)
                    key = f"{c['name']}|{r['name']}|{ct['name']}" if "regions" in c \
                        else f"{c['name']}|{ct['name']}"
                    flat[key] = rec
                    flat.setdefault(r["name"] + ct["name"], rec)
    _WORLD_FLAT = flat
    return flat


def city_geo(name: str) -> dict | None:
    """City name / 'country|province|city' / English name -> {lng,tz,dst,country}."""
    if not name:
        return None
    flat = _world_flat()
    if name in flat:
        return flat[name]
    low = name.lower()
    if low in flat:
        return flat[low]
    if "|" in name:
        tail = name.split("|")[-1]
        if tail in flat:
            return flat[tail]
        if tail.lower() in flat:
            return flat[tail.lower()]
    for k, v in flat.items():
        if k == name or name in k or k.startswith(name):
            return v
    return None


def city_longitude(name: str) -> float | None:
    """City name -> longitude. Convenience wrapper over city_geo()."""
    g = city_geo(name)
    return g["lng"] if g else None
