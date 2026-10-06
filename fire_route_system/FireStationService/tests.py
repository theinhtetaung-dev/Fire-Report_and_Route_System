from django.test import TestCase
from DataAccess.models import Role,User,FireStation

class FireStationServiceAPITests(TestCase):
    def setUp(self):
        self.user=User.objects.create(role=Role.objects.create(role_name='Administrator'),username='admin',email=None)
        self.station=FireStation.objects.create(name='Central',address='Mandalay',contact_number='1',latitude=21.97,longitude=96.08)
    def test_station_api_requires_login(self):
        self.assertEqual(self.client.get('/api/firestations/').status_code,302)
    def test_admin_can_read_existing_station_api(self):
        self.client.force_login(self.user)
        response=self.client.get('/api/firestations/')
        self.assertEqual(response.status_code,200);self.assertEqual(response.json()[0]['name'],'Central')
    def test_legacy_mutations_do_not_change_station(self):
        self.client.force_login(self.user)
        for verb in ['post','put','patch','delete']:
            self.assertEqual(getattr(self.client,verb)(f'/api/firestations/{self.station.pk}/',data='{}',content_type='application/json').status_code,403)
        self.station.refresh_from_db();self.assertEqual(self.station.name,'Central')
    def test_console_station_create_update_and_deactivate(self):
        self.client.force_login(self.user)
        payload={'name':'New Station','address':'Mandalay','contact_number':'2','latitude':'21.98','longitude':'96.09','status':'Active'}
        self.assertEqual(self.client.post('/emergency/manage/stations/new/',payload).status_code,302)
        station=FireStation.objects.get(name='New Station');payload['status']='Inactive';payload['name']='Updated'
        self.assertEqual(self.client.post(f'/emergency/manage/stations/{station.pk}/',payload).status_code,302)
        station.refresh_from_db();self.assertEqual(station.name,'Updated');self.assertEqual(station.status,'Inactive')
