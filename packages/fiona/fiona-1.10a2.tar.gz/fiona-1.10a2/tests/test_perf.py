"""Performance test."""

import fiona

with fiona.open(
    "/app/ne_10m_admin_0_countries_lakes/ne_10m_admin_0_countries_lakes.shp"
) as src:
    with fiona.open("/tmp/test_perf.shp", "w", **src.profile) as dst:
        dst.writerecords(src)
