from django.test import TestCase
from DataAccess.models import Role,User,FireStation,FireReport,Dispatch

class DispatchServiceAPITests(TestCase):
    def setUp(self):
        self.user=User.objects.create(role=Role.objects.create(role_name='Administrator'),username='admin',email=None)
        self.station=FireStation.objects.create(name='Central',address='Mandalay',contact_number='1',latitude=21.97,longitude=96.08)
        self.report=FireReport.objects.create(address='Fire',fire_scale=0)
        self.dispatch=Dispatch.objects.create(report=self.report,station=self.station,operator=self.user,resources_deployed='Legacy preserved')
    def test_legacy_history_requires_login(self):
        self.assertEqual(self.client.get('/api/dispatches/').status_code,302)
    def test_admin_can_read_preserved_legacy_history(self):
        self.client.force_login(self.user)
        response=self.client.get('/api/dispatches/')
        self.assertEqual(response.status_code,200);self.assertEqual(response.json()[0]['resources_deployed'],'Legacy preserved')
    def test_legacy_dispatch_writes_cannot_bypass_reservation(self):
        self.client.force_login(self.user)
        for verb in ['post','put','patch','delete']:
            self.assertEqual(getattr(self.client,verb)(f'/api/dispatches/{self.dispatch.pk}/',data='{}',content_type='application/json').status_code,403)
        self.assertEqual(Dispatch.objects.count(),1)
