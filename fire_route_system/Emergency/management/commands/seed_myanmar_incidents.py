import json
import math
import re
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import URLValidator
from django.db import transaction
from django.utils import timezone
from DataAccess.models import FireReport


class Command(BaseCommand):
    help = 'Import sourced Myanmar historical fires from 2024–2026, without live dispatches.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=Path, default=Path(__file__).resolve().parents[2] / 'data' / 'myanmar_historical_fires_2024_2026.json')
        parser.add_argument('--years', nargs='+', type=int, choices=[2024, 2025, 2026], default=[2024, 2025, 2026])
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        created = existing = 0
        imported_at = timezone.now()
        try:
            data = json.loads(options['file'].read_text(encoding='utf-8'))
            records = data['incidents']
            if not isinstance(records, list):raise ValueError('incidents must be a list')
            seen = set()
            for record in records:
                key = record['key']
                if not re.fullmatch(r'history:mm:\d{4}-\d{2}-\d{2}:[a-z0-9-]+',key) or key in seen:
                    raise ValueError(f'Invalid or duplicate incident key: {key}')
                seen.add(key)
                occurred = datetime.fromisoformat(record['occurred_at'])
                if timezone.is_naive(occurred) or occurred > imported_at:
                    raise ValueError(f'Invalid occurrence time: {key}')
                local_date = occurred.astimezone(ZoneInfo('Asia/Rangoon')).date()
                if local_date.year not in [2024,2025,2026] or local_date.isoformat() not in key:
                    raise ValueError(f'Key/date outside supported years: {key}')
                published = date.fromisoformat(record['published_on'])
                if published < local_date or published > timezone.localdate(imported_at):
                    raise ValueError(f'Invalid publication date: {key}')
                URLValidator(schemes=['https'])(record['url'])
                for field in ['extinguished_at','controlled_at']:
                    if record.get(field):
                        end = datetime.fromisoformat(record[field])
                        if timezone.is_naive(end) or end < occurred or end > imported_at:
                            raise ValueError(f'Invalid {field}: {key}')
                lat, lon = record.get('latitude'), record.get('longitude')
                if (lat is None)!=(lon is None):raise ValueError(f'Incomplete coordinates: {key}')
                if lat is not None and (not math.isfinite(lat) or not math.isfinite(lon) or not (9 <= lat <= 29 and 92 <= lon <= 102)):
                    raise ValueError(f'Coordinates outside Myanmar: {key}')
                scale = record.get('fire_scale')
                if scale is not None and (type(scale) is not int or scale not in range(6)):
                    raise ValueError(f'Invalid fire scale: {key}')
                for field in ['deaths_reported','injuries_reported']:
                    value = record.get(field)
                    if value is not None and (type(value) is not int or value < 0):raise ValueError(f'Invalid {field}: {key}')
                if local_date.year not in options['years']:continue
                source = dict(record, record_type='historical_reference', researched_on=data.get('researched_on'),
                    archived_at=imported_at.isoformat(), date_basis='Source-reported occurrence time; publication date stored separately',
                    closure_basis='Archived historical reference; closed_at is import time, not a reported extinguishing or approval time')
                defaults = dict(address=record['address'], fire_scale=scale, latitude=lat, longitude=lon,
                    coordinates_confirmed=False, status='Resolved', closed_at=imported_at, source_data=source)
                candidate = FireReport(source_key=key, **defaults)
                candidate.full_clean(exclude=['fire_scale'] if scale is None else [],validate_unique=False,validate_constraints=False)
                if not record['address'].strip():raise ValueError(f'Missing address: {key}')
                incident, added = FireReport.objects.get_or_create(source_key=key, defaults=defaults)
                if added:
                    # auto_now_add timestamps creation; historical charts need the
                    # source-reported event date instead of today's import date.
                    FireReport.objects.filter(pk=incident.pk).update(reported_at=occurred)
                created += int(added)
                existing += int(not added)
        except (OSError, KeyError, TypeError, ValueError, ValidationError) as error:
            raise CommandError(f'Invalid historical incident data: {error}') from error
        if options['dry_run']:transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(f'{created} historical incidents added, {existing} existing. Dry run: {options["dry_run"]}'))
        self.stdout.write('Source references archived. No accounts, notices, vehicle/staff assignments, dispatches, or official final reports created.')
