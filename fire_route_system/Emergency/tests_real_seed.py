import json
import tempfile
from io import StringIO
from pathlib import Path
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from DataAccess.models import FireStation, User
from .models import Vehicle, ResponsePlan


class RealWorldSeedTests(TestCase):
    def export(self, elements):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / 'osm.json'
        path.write_text(json.dumps({'elements': elements, 'osm3s': {'timestamp_osm_base': '2026-10-07T00:00:00Z'}}), encoding='utf-8')
        return path

    def record(self, pk=1):
        return {'id': pk, 'type': 'node', 'lat': 21.97, 'lon': 96.08, 'tags': {'amenity': 'fire_station', 'name': 'Source station'}}

    def test_idempotent_preserves_edits_and_does_not_invent_resources(self):
        path = self.export([self.record()])
        call_command('seed_real_world', file=path, stdout=StringIO())
        station = FireStation.objects.get(source_key='osm:node:1')
        self.assertEqual(station.status, 'Unknown')
        self.assertEqual(station.contact_number, '')
        self.assertEqual(station.township, '')
        self.assertEqual(station.source_data['url'], 'https://www.openstreetmap.org/node/1')
        station.name = 'Locally reviewed'; station.save()
        call_command('seed_real_world', file=path, stdout=StringIO())
        station.refresh_from_db()
        self.assertEqual(station.name, 'Locally reviewed')
        self.assertEqual(FireStation.objects.count(), 1)
        self.assertEqual((User.objects.count(), Vehicle.objects.count(), ResponsePlan.objects.count()), (0, 0, 0))

    def test_dry_run_and_unnamed_skip(self):
        unnamed = self.record(2); unnamed['tags'].pop('name')
        path = self.export([self.record(), unnamed])
        call_command('seed_real_world', file=path, dry_run=True, stdout=StringIO())
        self.assertFalse(FireStation.objects.exists())

    def test_invalid_coordinate_rolls_back_entire_import(self):
        bad = self.record(2); bad['lat'] = 90
        with self.assertRaises(CommandError):
            call_command('seed_real_world', file=self.export([self.record(), bad]), stdout=StringIO())
        self.assertFalse(FireStation.objects.exists())
