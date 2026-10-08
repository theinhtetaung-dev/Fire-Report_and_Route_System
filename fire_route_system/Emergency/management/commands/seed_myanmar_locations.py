import json
import math
import re
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from Emergency.models import MyanmarLocation


class Command(BaseCommand):
    help = 'Seed MIMU township and town references, preserving existing local edits.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=Path, default=Path(__file__).resolve().parents[2] / 'data' / 'mandalay_locations_mimu.json')
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            data = json.loads(options['file'].read_text(encoding='utf-8'))
            source, records = data['source'], data['locations']
            if not isinstance(source, dict) or not source.get('url') or not isinstance(records, list):
                raise ValueError('Expected source metadata and a locations list')
            seen = set()
            created = existing = 0
            fields = ['kind', 'name_en', 'name_my', 'region_pcode', 'region_name_en', 'district_pcode', 'district_name_en', 'township_pcode', 'latitude', 'longitude']
            for record in records:
                pcode = record['pcode']
                if pcode in seen:raise ValueError(f'Duplicate Pcode: {pcode}')
                seen.add(pcode)
                kind = record['kind']
                pattern = r'MMR\d{6}' if kind == 'township' else r'MMR\d{9}'
                if kind not in ['township', 'town'] or not re.fullmatch(pattern, pcode):
                    raise ValueError(f'Invalid kind/Pcode: {pcode}')
                # MIMU assigns some cities special codes (e.g. Mandalay City
                # MMR010000777); their township code is not a Pcode prefix.
                if not pcode.startswith(record['region_pcode']) or not record['township_pcode'].startswith(record['region_pcode']) or not re.fullmatch(r'MMR\d{6}',record['township_pcode']):
                    raise ValueError(f'Inconsistent location hierarchy: {pcode}')
                if kind=='township' and record['township_pcode']!=pcode:
                    raise ValueError(f'Invalid township reference: {pcode}')
                lat, lon = record['latitude'], record['longitude']
                if (lat is None) != (lon is None):raise ValueError(f'Incomplete coordinates: {pcode}')
                if lat is not None and (not math.isfinite(lat) or not math.isfinite(lon) or not (9 <= lat <= 29 and 92 <= lon <= 102)):
                    raise ValueError(f'Coordinates outside Myanmar: {pcode}')
                defaults = {field: record[field] for field in fields}
                defaults['source_data'] = dict(source, mapping_status=record.get('mapping_status'), source_sheet=record.get('source_sheet'), source_row=record.get('source_row'))
                MyanmarLocation(pcode=pcode, **defaults).full_clean(validate_unique=False, validate_constraints=False)
                _, added = MyanmarLocation.objects.get_or_create(pcode=pcode, defaults=defaults)
                created += int(added)
                existing += int(not added)
        except (OSError, KeyError, TypeError, ValueError, ValidationError) as error:
            raise CommandError(f'Invalid location reference data: {error}') from error
        if options['dry_run']:transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(f'{created} locations added, {existing} existing. Dry run: {options["dry_run"]}'))
