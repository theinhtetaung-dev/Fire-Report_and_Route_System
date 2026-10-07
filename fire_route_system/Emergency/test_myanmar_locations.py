import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from DataAccess.models import FireReport, FireStation, Role, User
from .models import MyanmarLocation, ResponsePlan, Vehicle


class MyanmarLocationSeedTests(TestCase):
    def seed(self, **options):
        call_command('seed_myanmar_locations', stdout=StringIO(), **options)

    def record(self, pcode='MMR010001'):
        return {'pcode':pcode,'kind':'township','name_en':'Aungmyaythazan','name_my':'အောင်မြေသာစံ',
            'region_pcode':'MMR010','region_name_en':'Mandalay','district_pcode':'MMR010D001',
            'district_name_en':'Mandalay','township_pcode':pcode,'latitude':None,'longitude':None}

    def export(self, records):
        folder=tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path=Path(folder.name)/'locations.json'
        path.write_text(json.dumps({'source':{'url':'https://www.themimu.info/gis-resources'},'locations':records}),encoding='utf-8')
        return path

    def test_bundled_seed_has_source_names_and_coordinates_without_operational_data(self):
        self.seed()
        self.assertEqual(MyanmarLocation.objects.filter(kind='township').count(),28)
        self.assertEqual(MyanmarLocation.objects.filter(kind='town').count(),35)
        self.assertFalse(MyanmarLocation.objects.filter(kind='township',latitude__isnull=False).exists())
        town=MyanmarLocation.objects.get(pcode='MMR010006701')
        self.assertEqual(town.name_en,'Amarapura Town')
        self.assertEqual(town.name_my,'အမရပူရ')
        self.assertAlmostEqual(town.latitude,21.90314)
        self.assertAlmostEqual(town.longitude,96.04948)
        self.assertEqual(town.source_data['source_sheet'],'04_Town')
        self.assertEqual(town.source_data['release'],'9.7 (January 2026)')
        city=MyanmarLocation.objects.get(pcode='MMR010000777')
        self.assertEqual(city.name_en,'Mandalay City')
        self.assertEqual(city.township_pcode,'MMR010001')
        self.assertEqual((User.objects.count(),FireStation.objects.count(),Vehicle.objects.count(),FireReport.objects.count(),ResponsePlan.objects.count()),(0,0,0,0,0))

    def test_rerun_preserves_local_edits(self):
        self.seed()
        reference=MyanmarLocation.objects.get(pcode='MMR010001')
        reference.name_en='Locally reviewed';reference.save()
        self.seed()
        reference.refresh_from_db()
        self.assertEqual(reference.name_en,'Locally reviewed')
        self.assertEqual(MyanmarLocation.objects.count(),63)

    def test_dry_run_does_not_write(self):
        self.seed(dry_run=True)
        self.assertFalse(MyanmarLocation.objects.exists())

    def test_invalid_record_rolls_back_complete_seed(self):
        for changes in [{'latitude':90,'longitude':96},{'latitude':21,'longitude':None},{'name_en':'x'*151},{'region_pcode':'MMR011'}]:
            with self.subTest(changes=changes):
                valid=self.record()
                bad=dict(self.record('MMR010002'),**changes)
                with self.assertRaises(CommandError):self.seed(file=self.export([valid,bad]))
                self.assertFalse(MyanmarLocation.objects.exists())

    def test_duplicate_pcode_is_rejected(self):
        with self.assertRaises(CommandError):self.seed(file=self.export([self.record(),self.record()]))
        self.assertFalse(MyanmarLocation.objects.exists())

    def test_station_form_offers_myanmar_township_suggestions(self):
        self.seed()
        user=User.objects.create(username='admin',role=Role.objects.create(role_name='Administrator'))
        self.client.force_login(user)
        response=self.client.get('/emergency/manage/stations/new/')
        self.assertContains(response,'list="myanmar-townships"')
        self.assertContains(response,'အောင်မြေသာစံ')
        self.assertContains(response,'MMR010001')
