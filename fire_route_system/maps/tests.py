from django.test import TestCase
from DataAccess.models import Role,User,FireStation,FireReport

class MapViewTests(TestCase):
    def setUp(self):
        self.user=User.objects.create(role=Role.objects.create(role_name='Citizen'),username='citizen',email=None)
        self.active=FireStation.objects.create(name='Central',address='Mandalay',contact_number='1',latitude=21.97,longitude=96.08)
        FireStation.objects.create(name='Inactive',address='Mandalay',contact_number='2',latitude=21.98,longitude=96.09,status='Inactive')
    def test_map_requires_login(self):
        self.assertEqual(self.client.get('/emergency/map/').status_code,302)
    def test_legacy_map_redirects_to_new_map(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get('/map/'),'/emergency/map/')
    def test_map_view_template(self):
        self.client.force_login(self.user)
        self.assertTemplateUsed(self.client.get('/emergency/map/'),'emergency/map.html')
    def test_map_data_has_active_stations_and_confirmed_incidents(self):
        self.client.force_login(self.user)
        FireReport.objects.create(address='Pending',latitude=21.97,longitude=96.08,fire_scale=0)
        confirmed=FireReport.objects.create(address='Confirmed',latitude=21.97,longitude=96.08,fire_scale=1,status='Confirmed',coordinates_confirmed=True,reporter_phone='private')
        data=self.client.get('/emergency/api/map/').json()
        self.assertEqual(len(data['stations']),1);self.assertEqual(data['stations'][0]['name'],'Central')
        self.assertEqual([i['id'] for i in data['incidents']],[confirmed.pk]);self.assertNotIn('reporter_phone',data['incidents'][0])
