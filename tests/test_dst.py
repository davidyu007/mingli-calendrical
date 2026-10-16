# -*- coding: utf-8 -*-
"""Smoke tests for mingli_calendrical — run with `python -m pytest` or plain."""
import mingli_calendrical as mc


def test_hk_dst():
    assert mc.dst_minutes("1965-07-01", "hk") == 60
    assert mc.dst_minutes("1965-01-15", "hk") == 0
    assert mc.dst_minutes("1995-07-01", "hk") == 0   # no DST after 1979
    assert mc.dst_minutes("1979-08-01", "hk") == 60  # last HK DST window


def test_cn_dst():
    assert mc.dst_minutes("1988-06-01", "cn") == 60
    assert mc.dst_minutes("1985-06-01", "cn") == 0
    assert mc.dst_minutes("1992-06-01", "cn") == 0


def test_mo_tw():
    assert mc.dst_minutes("1960-07-01", "mo") == 60
    assert mc.dst_minutes("1958-07-01", "tw") == 60
    assert mc.dst_minutes("1965-07-01", "tw") == 0   # TW gap 1962-1973


def test_tst():
    date, idx, clock, corr = mc.true_solar_time("1990-05-15", "12:10", 114.17, 8)
    assert idx in (5, 6)
    assert -90 < corr < 0  # HK is west of 120E meridian → negative correction


def test_cities():
    g = mc.city_geo("香港")
    assert g and abs(g["lng"] - 114.17) < 0.5 and g["dst"] == "hk"
    g2 = mc.city_geo("hong kong")
    assert g2 and g2["lng"] == g["lng"]
    assert mc.city_longitude("九龙")


def test_index():
    assert mc.time_to_index("23:30") == 12
    assert mc.time_to_index("00:30") == 0
    assert mc.time_to_index("12:00") == 6


if __name__ == "__main__":
    for f in dir():
        if f.startswith("test_"):
            globals()[f]()
            print(f, "ok")
    print("all pass")
