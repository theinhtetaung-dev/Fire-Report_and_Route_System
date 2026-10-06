## Project Summary

The **Mandalay Fire Alarm Emergency System** uses Django, MySQL, and Leaflet.
Citizens and staff sign in to report fires using coordinates or a manual address.
An administrator confirms the location, jurisdiction, level, and vehicle selection
before dispatch orders are sent to stations. Station managers select available
on-duty personnel, record operational updates, and submit resource reports.

The demo includes local Dijkstra road routing, Myanmar PDF exports, scoped
staff management, and final incident review. Station data and response quantities
require local verification before use for actual emergency operations.

## Emergency demo

The new console is available at `/emergency/`. It includes Citizen registration,
phone or legacy username login, station permissions, duty and leave management,
temporary station managers, response plans, vehicle reservation, staff selection,
station reports, final review, posts, polling, and route PDFs.

From `fire_route_system`, using the repository's Python environment:

```powershell
..\.venv\Scripts\python.exe manage.py migrate
..\.venv\Scripts\python.exe manage.py seed_emergency_demo
..\.venv\Scripts\python.exe manage.py import_roads --download
..\.venv\Scripts\python.exe manage.py runserver
```

MySQL must be running with the database configured in the local `.env`.
For a separate SQLite demo, set `$env:DB_ENGINE='sqlite'` before running commands.
Local `.env` files and downloaded road data under `fire_route_system/runtime/`
are excluded from Git. Install dependencies from `Pipfile.lock` using `pipenv sync`.

New demo accounts are `demo_admin`, `demo_station`, `demo_firefighter`, and
`demo_citizen`, with initial password `DemoFire2026!`. Their phone numbers are
`09900000001` through `09900000004`. Re-running the seed preserves passwords
and existing response plans. Vehicles and response plans are demonstration data.

If Overpass is unavailable, import an Overpass JSON export using
`manage.py import_roads --file <path>`. Without a road graph, dispatch requires
a recorded manual-navigation reason. Route distances describe the road graph;
the console shows separate distances between map pins and the graph endpoints.
Map tiles require network access. PDF generation uses the bundled Noto Myanmar
and Latin fonts. Their licenses and rebuild instructions are in `Emergency/fonts/`.

Run workflow tests from `fire_route_system`:

```powershell
..\.venv\Scripts\python.exe -B manage.py test --noinput
```

The suite includes MySQL tests with separate concurrent connections for vehicle
and employee reservation; those checks are skipped under SQLite. Legacy
management writes are blocked in favor of the audited console. Existing account,
incident, and dispatch records remain available. See `Emergency/DEMO_STATUS.md`
for validation results and demo data limitations.
