import json
import math
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from DataAccess.models import FireStation


class Command(BaseCommand):
    help = 'Import source-backed Mandalay OSM fire stations; no invented resources or operational plans.'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=Path, default=Path(__file__).resolve().parents[2] / 'data' / 'mandalay_fire_stations_osm.json')
        parser.add_argument('--dry-run', action='store_true')

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            data = json.loads(options['file'].read_text(encoding='utf-8'))
            elements = data['elements']
            if not isinstance(elements, list): raise ValueError('elements must be a list')
        except (OSError, ValueError, KeyError) as error:
            raise CommandError(f'Invalid OSM export: {error}')
        created = skipped = unnamed = 0
        for element in elements:
            tags = element.get('tags', {})
            if tags.get('amenity') != 'fire_station': continue
            name = tags.get('name:my') or tags.get('name') or tags.get('name:en')
            if not name:
                unnamed += 1
                continue
            position = element.get('center', element)
            try:
                lat, lon = float(position['lat']), float(position['lon'])
                if not math.isfinite(lat) or not math.isfinite(lon) or not (21.7 <= lat <= 22.3 and 95.9 <= lon <= 96.3):
                    raise ValueError('outside Mandalay import bounds')
                if element['type'] not in ['node', 'way', 'relation']: raise ValueError('invalid OSM type')
                key = f"osm:{element['type']}:{int(element['id'])}"
                address = tags.get('addr:full') or ', '.join(tags[k] for k in ['addr:housenumber', 'addr:street', 'addr:suburb', 'addr:city'] if tags.get(k))
                defaults = {
                    'name': name, 'address': address,
                    'township': tags.get('addr:township', ''),
                    'contact_number': tags.get('contact:phone') or tags.get('phone', ''),
                    'latitude': lat, 'longitude': lon, 'status': 'Unknown',
                    'source_data': {'url': f"https://www.openstreetmap.org/{element['type']}/{element['id']}",
                        'attribution': '© OpenStreetMap contributors, ODbL 1.0',
                        'snapshot_at': data.get('retrieved_at') or data.get('osm3s', {}).get('timestamp_osm_base'),
                        'osm_last_modified': element.get('timestamp'),
                        'tags': tags, 'coordinate_kind': 'point' if element['type'] == 'node' else 'geometry_center',
                        'verification': 'Community mapped; operational readiness and township require local confirmation'},
                }
                for field in ['name', 'township', 'contact_number']:
                    if len(defaults[field]) > FireStation._meta.get_field(field).max_length:
                        raise ValueError(f'{field} exceeds field length')
            except (KeyError, TypeError, ValueError) as error:
                raise CommandError(f"Invalid OSM record {element.get('id')}: {error}")
            # Never match on a guessed name/location or overwrite local edits/history.
            _, added = FireStation.objects.get_or_create(source_key=key, defaults=defaults)
            created += int(added)
            skipped += int(not added)
        if options['dry_run']: transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(f'{created} added, {skipped} existing, {unnamed} unnamed skipped. Dry run: {options["dry_run"]}'))
        self.stdout.write('OSM reference records only. Status Unknown; no accounts, passwords, vehicles, incidents, or response plans generated.')
