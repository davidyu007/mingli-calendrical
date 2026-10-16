# mingli-calendrical

**Historical daylight-saving-time + true-solar-time engine for Chinese metaphysics / astrology apps.**

If your user was born in Hong Kong, Macau, Taiwan, or mainland China while the
clock was shifted, the birth **hour pillar is wrong** unless you subtract DST
first — then correct clock time to true solar time (longitude + equation of
time). One hour of clock error = wrong 時辰 = a completely different chart.

Zero dependencies. MIT license.

```bash
pip install -e .
```

```python
from mingli_calendrical import dst_minutes, true_solar_time, city_geo

# Was 1965-07-01 inside Hong Kong DST? Yes → subtract 60 min first.
dst_minutes("1965-07-01", "hk")          # 60
dst_minutes("1988-06-01", "cn")          # 60  (PRC 1986-1991)
dst_minutes("1995-06-01", "hk")          # 0   (HK dropped DST after 1979)

# Clock noon in Hong Kong (114.17°E, tz +8) is ~11:45 true solar time.
true_solar_time("1990-05-15", "12:10", lng=114.17, tz=8)
# ('1990-5-15', 6, '11:58', -12.3)

# Bundled city DB (21 countries, Chinese + English names)
city_geo("香港")        # {'lng': 114.17, 'tz': 8, 'dst': 'hk', 'country': '中国香港', ...}
city_geo("hong kong")  # same record — English names work too
```

## Why this exists

Most BaZi / Zi Wei Dou Shu calculators silently assume the clock time on a
birth certificate equals solar time. It doesn't. Two corrections are required
and most open-source projects skip one or both:

1. **Historical DST.** Hong Kong ran DST in 36 separate windows between
   1946–1979 (IANA `Asia/Hong_Kong`), Macau and Taiwan had their own tables,
   and mainland China ran DST 1986–1991. ~36 million births were affected in
   the PRC window alone.
2. **True solar time.** Standard time is pinned to a zone meridian
   (e.g. 120°E for UTC+8). Every degree of longitude off that meridian shifts
   solar noon by 4 minutes; the equation of time adds up to ±16 minutes more.
   Chengdu (104°E) solar noon is ~64 minutes behind Beijing clock noon.

This package encodes both, table-driven and deterministic — the same tables
that power [purpleking.net](https://purpleking.net/ziwei), where every chart
is cast under these corrections and cross-checked against a 518,400-chart
reference set.

## API

| Function | Returns |
|---|---|
| `dst_minutes(date, region)` | `60` or `0` — regions: `hk` `mo` `tw` `cn` `eu` `us` `au` `nz` |
| `dst_cn_minutes(date)` | `60` or `0` — PRC 1986–91 table only |
| `dst_hkmo_tw_minutes(date, region)` | `60` or `0` — HK/MO/TW tables only |
| `true_solar_time(date, "HH:MM", lng, tz)` | `(date, hour_index, "HH:MM", corr_minutes)` |
| `equation_of_time(y, m, d, h, mi)` | minutes (NOAA approximation) |
| `time_to_index("HH:MM")` | 時辰 index `0..12` (23:00 → 12, late-子) |
| `city_geo(name)` / `city_longitude(name)` | bundled city DB lookup |

## Caveats

- EU/US/AU/NZ rules are the *common* approximations. Historical edge cases
  (e.g. US pre-1987, AU state-level variation) are not covered — verify
  boundary days against tzdb if precision matters.
- DST tables mark the *date* of transition; exact switch-over hours are not
  modeled (births within ±1h of a transition should be double-checked).

## 中文

香港、澳門、台灣、中國大陸在不同年代都行過夏令時間——出世紙上的鐘點
唔減返夏令時、唔校正真太陽時，時辰就可能錯，成張盤都唔同。呢個庫
將港澳台同大陸嘅歷史夏令時表 + 均時差校正打包成零依賴嘅 Python 包。
Live demo: https://purpleking.net/ziwei

## License

MIT © Ming Luo Pan (purpleking.net)
