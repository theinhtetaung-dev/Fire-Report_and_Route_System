# Mandalay real-world reference seed

## Township and town references

`mandalay_locations_mimu.json` contains 28 township and 35 town records extracted
from MIMU's **PCode release 9.7, January 2026**, downloaded on 7 October 2026:

https://www.themimu.info/sites/themimu.info/files/documents/Myanmar_PCodes_Release_9.7_Jan2026_Mandalay.xlsm

Catalog: https://www.themimu.info/gis-resources

The JSON retains Myanmar/English names, Pcodes, the source hierarchy, town-point
coordinates, workbook sheet/row references, download date, and the workbook's
SHA-256 checksum. Township coordinates remain empty because the township sheet
does not provide them. Town points are not township boundaries or fire-station
locations. Station townships are not inferred from proximity to a town point.
Names and district groupings are retained exactly as published in this release.

Source: Myanmar Information Management Unit (MIMU). The source workbook requires
attribution and states that the data is free of charge, not for sale or commercial
use. Its VBA macros were not executed; only worksheet values were extracted.

Run from `fire_route_system` using the database used by your application (the
current local server uses SQLite):

```powershell
$env:DB_ENGINE='sqlite'
..\.venv\Scripts\python.exe -B manage.py migrate
..\.venv\Scripts\python.exe -B manage.py seed_myanmar_locations --dry-run
..\.venv\Scripts\python.exe -B manage.py seed_myanmar_locations
..\.venv\Scripts\python.exe -B manage.py seed_real_world
```

The location seed stores 63 `MyanmarLocation` references and matches by Pcode.
Reruns preserve local edits. Duplicate Pcodes, incomplete/invalid coordinates,
invalid field values, and inconsistent hierarchy roll back the entire import.
`--file path/to/reference.json` imports a replacement snapshot in the same format.
The station create/edit form offers township name suggestions from this catalog,
while allowing existing local names. Review a station's actual jurisdiction before
assigning one of the suggestions.

## Fire-station references

Run from `fire_route_system`:

```powershell
..\.venv\Scripts\python.exe -B manage.py migrate
..\.venv\Scripts\python.exe -B manage.py seed_real_world --dry-run
..\.venv\Scripts\python.exe -B manage.py seed_real_world
```

`mandalay_fire_stations_osm.json` contains eight named fire-station nodes downloaded
from the primary OpenStreetMap API on 7 October 2026. Each record retains its OSM
ID, raw tags, coordinates, version, and last-modified timestamp. Contributor user
names and user IDs were omitted. This is a partial reference dataset, not an
official inventory or confirmation that every station currently operates.

Sources: https://api.openstreetmap.org/api/0.6/nodes.json?nodes=2702239050,4323722048,4903110921,8070903288,8070921886,12063096247
and https://api.openstreetmap.org/api/0.6/nodes.json?nodes=8070921785,8070921885

© OpenStreetMap contributors. Data licensed under ODbL 1.0:
https://www.openstreetmap.org/copyright

Unknown phones, addresses, and townships remain blank rather than being guessed.
The station readiness state is `Unknown`. Admin must verify readiness and the
township before using these records operationally. In particular, `opening_hours`
does not establish vehicle availability. Some OSM records were last edited years
ago; inspect each record's source link when reviewing it.

The seeder matches only stable OSM IDs and preserves local edits on repeat runs.
It does not merge by similar station names or replace existing historical records.
The station list offers a source filter and labels records without source metadata
as Demo / unverified. Source records may duplicate legacy demo locations; review
and deactivate the demo entry manually after resolving historical relationships.

Vehicle counts, registrations, personnel, incidents, and Level 0–5 response plans
are not publicly verified by this dataset and are not generated. Obtain these
from the responsible stations before entering them as real operational data.
`seed_emergency_demo` remains a separate demonstration command and excludes
source-backed stations from automatic demo resource/plan creation.

For later imports, use `--file path/to/export.json` with an Overpass-format export
containing named `amenity=fire_station` objects inside latitude 21.7–22.3 and
longitude 95.9–96.3. Invalid records roll back the entire import. Dry run also
rolls back all records.
