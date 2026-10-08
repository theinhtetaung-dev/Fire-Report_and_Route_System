import json
import tempfile
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.utils import timezone
from DataAccess.models import FireReport, Role, User
from .api import serialize
from .forms import ConfirmForm
from .models import Audit, Deployment, FinalReport, IncidentUpdate, Notice, StaffParticipation, VehicleParticipation


class HistoricalIncidentSeedTests(TestCase):
    def seed(self, **options):
        call_command('seed_myanmar_incidents', stdout=StringIO(), **options)

    def export(self, records):
        folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup)
        path=Path(folder.name)/'incidents.json'
        path.write_text(json.dumps({'incidents':records}),encoding='utf-8')
        return path

    def record(self, key='history:mm:2024-02-05:test'):
        return dict(key=key,occurred_at='2024-02-05T05:00:00+06:30',published_on='2024-02-06',
            url='https://www.gnlm.com.mm/fire-at-aung-mingala-coach-terminal-kills-3-men-destroys-some-bus-stations/',
            address='Historical test',fire_scale=None,latitude=None,longitude=None)

    def admin(self):
        user=User.objects.create(username='admin',role=Role.objects.create(role_name='Administrator'))
        self.client.force_login(user)
        return user

    def test_seed_preserves_event_years_and_unknowns(self):
        self.seed()
        years={year:FireReport.objects.filter(reported_at__year=year).count() for year in [2024,2025,2026]}
        self.assertEqual(years,{2024:3,2025:4,2026:3})
        incident=FireReport.objects.get(source_key='history:mm:2024-02-05:aung-mingala-terminal')
        self.assertEqual(timezone.localtime(incident.reported_at).isoformat(),'2024-02-05T05:00:00+06:30')
        self.assertIsNone(incident.fire_scale)
        self.assertIsNone(incident.user_id)
        self.assertIsNone(incident.reporter_phone)
        self.assertIsNone(incident.latitude)
        self.assertFalse(incident.coordinates_confirmed)
        self.assertIsNotNone(incident.closed_at)
        self.assertEqual(incident.status,'Resolved')
        self.assertEqual(incident.source_data['deaths_reported'],3)
        self.assertEqual(incident.source_data['published_on'],'2024-02-06')
        self.assertTrue(serialize(incident)['historical'])
        self.assertEqual(serialize(incident)['fire_scale'],None)
        self.assertIn('source_url',serialize(incident))
        self.assertNotEqual(incident.closed_at,incident.reported_at)
        for model in [User,Deployment,FinalReport,IncidentUpdate,Notice,Audit,StaffParticipation,VehicleParticipation]:
            self.assertEqual(model.objects.count(),0)

    def test_dry_run_and_year_selection(self):
        self.seed(dry_run=True)
        self.assertFalse(FireReport.objects.exists())
        self.seed(years=[2025])
        self.assertEqual(FireReport.objects.count(),4)
        self.assertFalse(FireReport.objects.exclude(reported_at__year=2025).exists())

    def test_repeat_seed_preserves_local_edits_and_dates(self):
        self.seed()
        incident=FireReport.objects.first();date=incident.reported_at;closed=incident.closed_at
        incident.address='Locally reviewed address';incident.save()
        self.seed();incident.refresh_from_db()
        self.assertEqual(FireReport.objects.count(),10)
        self.assertEqual(incident.address,'Locally reviewed address')
        self.assertEqual(incident.reported_at,date)
        self.assertEqual(incident.closed_at,closed)

    def test_invalid_record_rolls_back_entire_import(self):
        for changes in [{'occurred_at':'2024-02-05T05:00:00'}, {'fire_scale':6}, {'latitude':90,'longitude':96},
                        {'latitude':21,'longitude':None}, {'deaths_reported':-1}, {'url':'javascript:alert(1)'},
                        {'published_on':'2024-02-01'}, {'extinguished_at':'2024-02-04T23:00:00+06:30'}]:
            with self.subTest(changes=changes):
                valid=self.record();bad=dict(self.record('history:mm:2024-02-05:bad'),**changes)
                with self.assertRaises(CommandError):self.seed(file=self.export([valid,bad]))
                self.assertFalse(FireReport.objects.exists())

    def test_duplicate_source_keys_are_rejected(self):
        with self.assertRaises(CommandError):self.seed(file=self.export([self.record(),self.record()]))
        self.assertFalse(FireReport.objects.exists())

    def test_history_visible_in_list_reports_and_detail_but_not_live_map_or_queue(self):
        self.seed();self.admin()
        incident=FireReport.objects.filter(source_key='history:mm:2024-03-02:kanthaya-house').first()
        response=self.client.get(f'/emergency/incidents/{incident.pk}/')
        self.assertContains(response,'သမိုင်းမှတ်တမ်း')
        self.assertContains(response,incident.source_data['url'])
        self.assertNotContains(response,'name="vehicles"')
        self.assertContains(self.client.get('/emergency/incidents/?source=historical&start=2025-01-01&end=2025-12-31'),'ကေတုမတီ')
        self.assertNotContains(self.client.get('/emergency/incidents/?source=historical&start=2025-01-01&end=2025-12-31'),'ကန်သာယာ')
        self.assertEqual(self.client.get('/emergency/api/map/').json()['incidents'],[])
        self.assertNotContains(self.client.get('/emergency/queue/'),'ကန်သာယာ')
        self.assertContains(self.client.get('/emergency/reports/?source=historical'),'အဆင့် မသိရသေး')
        self.assertTrue(ConfirmForm.base_fields['fire_scale'].required)

    def test_historical_records_do_not_change_active_dashboard_count_or_allow_dispatch(self):
        self.seed();self.admin()
        self.assertEqual(self.client.get('/emergency/').context['active_count'],0)
        incident=FireReport.objects.first()
        response=self.client.post(f'/emergency/incidents/{incident.pk}/dispatch/',{'vehicles':[]})
        self.assertEqual(response.status_code,302)
        self.assertFalse(Deployment.objects.exists())
