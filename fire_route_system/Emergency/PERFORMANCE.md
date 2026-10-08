# Page and API performance

The console uses one polling request per visible page, scheduled 10 seconds
after the previous request completes. Hidden tabs pause polling. Failed requests
back off up to 60 seconds, requests time out after 15 seconds, and authentication
failures stop polling. Unchanged responses do not trigger page updates.

Each page selects the data it needs through `/emergency/api/poll/`:

| Page | Query parameters | Response data |
| --- | --- | --- |
| Dashboard | `scope=dashboard&map=1` | Notifications, recent incidents, map |
| Map | `scope=notifications&map=1` | Unread count, map |
| Incident detail | `scope=incident&incident=<id>` | Unread count, permitted incident/deployment updates |
| Verification queue | `scope=queue` plus search/page filters | Unread count, queue HTML fragment |
| Other console pages | `scope=notifications` | Unread count |

Omitting `scope` preserves the original dashboard response. Queue polling
requires an administrator. Incident details retain the existing visibility
rules; map data retains its public fields and excludes pending incidents.

## Measured query reductions

Measurements use the local SQLite dataset and Django's query capture around
rendering/serialization. They exclude authentication/session middleware queries.

| Operation | Before | After |
| --- | ---: | ---: |
| Vehicle listing, 20 rows | 44 queries | 2 queries |
| Requirement listing, 20 rows | 84 queries | 2 queries |
| Notification-only refresh | 3 queries, 7,585 bytes | 1 query, 13 bytes |
| Legacy user list API | 7 queries | 2 queries |

Listings join their related records; incident details prefetch vehicle and staff
participation; response-plan previews count available vehicles in one grouped
query. Map markers are rebuilt only when map data changes. Queue polling returns
only the result fragment instead of fetching a second complete page.

## Legacy list API pagination

User, station, dispatch, and legacy report list views preserve their JSON array
format and return at most 100 records per request. Use `page` and `page_size`
(1–100). Invalid page sizes fall back to 100; values outside the allowed range
are clamped. Response headers expose `X-Total-Count`, `X-Page`, `X-Page-Size`,
`X-Total-Pages`, and next/previous `Link` URLs. Clients that need all records must
follow the pages. The legacy station map now does this. The active report API
uses the Emergency API's existing 20-record pagination and visibility rules.

Map data is intentionally complete for all active stations and confirmed open
incidents, so its payload grows with the number of visible map points.

## Regression checks

From `fire_route_system`, run:

```powershell
$env:DB_ENGINE='sqlite'
..\.venv\Scripts\python.exe -B manage.py test Emergency.test_performance
```

The checks cover bounded query counts, notification payloads, combined map
polling, filtered/paginated queue fragments, visibility rules, batched vehicle
availability, and legacy API pagination. The wider suite checks audited
incident and dispatch workflows. SQLite skips MySQL concurrency tests.
