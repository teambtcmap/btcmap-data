# BTC Map Utilities

## Overview

Python utility scripts for working with BTC Map API data. Most need `BTCMAP_API_TOKEN`
(an admin-level API key) in the environment, and several write to production areas — read
the script before running it.

## Scripts

### Area management

- `create-area.py` — create a single area from a GeoJSON file. Computes the bbox, rewinds the
  ring and calls `add_area`. The RPC API has no CLI wrapper for area creation, so this is still
  the tool for it.
- `create-areas-from-files.py` — the bulk version: walks a directory of GeoJSON files.
- `patch-area.py` — patch tags across areas in bulk.
- `update-areas-with-km2.py` — backfill `area_km2` for every area of a given type.

### Reporting and exports

- `community-centres.py` — compute community centroids from a local `btcmap.db` (needs
  `shapely`).
- `get-community-contact-details.py` — export community contact details to `areas_data.csv`.

## Monthly blog post

The monthly update workflow lives with the thing it produces: `scripts/monthly-post.py` in the
[blog repo](https://github.com/teambtcmap/blog). It pulls the month's report, dashboard and
trending data, filters retired areas, resolves community flags by polygon, orders the activity
tables and sweeps the credit inputs from every repo, writing a `data.json` beside each post.

Retired here in October 2026, superseded by it:

- `rpc-reports.py` — figures, trending tables and active taggers
- `fetch-communities.py` — new communities for the month
- `generate-dashboard-chart.py` — the merchant charts (still used, from the blog repo)
- `run-reports.py` — the wrapper that ran `rpc-reports.py`

## Dependencies

See `requirements.txt` for Python package dependencies.
