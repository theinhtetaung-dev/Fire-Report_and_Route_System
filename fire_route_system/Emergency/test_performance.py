import json
from django.test import RequestFactory, TestCase

from DataAccess.models import FireReport, FireStation, Role, User
from UserService.userapi import user_list_create
from . import api, views
from .models import PlanRequirement, Post, ResponsePlan, Vehicle, VehicleType
from .services import preview


class PerformanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.role=Role.objects.create(role_name='Administrator')
        cls.admin=User.objects.create(username='admin',role=cls.role)
        cls.citizen=User.objects.create(username='citizen',role=Role.objects.create(role_name='Citizen'))
        cls.station=FireStation.objects.create(name='Central',address='Mandalay',contact_number='1',latitude=21.97,longitude=96.08)
        cls.kind=VehicleType.objects.create(name='Engine')
        cls.incident=FireReport.objects.create(user_id=cls.citizen.pk,address='Visible fire',status='Confirmed',home_station=cls.station,lead_station=cls.station,coordinates_confirmed=True,latitude=21.97,longitude=96.08,fire_scale=1)
        cls.pending=FireReport.objects.create(address='Needle pending',status='Pending',fire_scale=0)
        for index in range(21):
            station=FireStation.objects.create(name=f'Station {index}',address='Mandalay',contact_number='1',latitude=21.97,longitude=96.08)
            kind=VehicleType.objects.create(name=f'Kind {index}')
            plan=ResponsePlan.objects.create(home_station=station,lead_station=station,level=1)
            PlanRequirement.objects.create(plan=plan,station=station,kind=kind,quantity=2)
            Vehicle.objects.create(registration=f'Engine {index}',station=station,kind=kind)
            User.objects.create(username=f'Staff {index}',role=cls.role,station=station)
            Post.objects.create(author=cls.admin,station=station,title=f'Post {index}',body='News',audience='Public')

    def request(self,path,user=None):
        request=RequestFactory().get(path)
        request.user=user or self.admin
        return request

    def test_bell_poll_uses_one_query_and_only_returns_count(self):
        with self.assertNumQueries(1):
            response=api.poll(self.request('/emergency/api/poll/?scope=notifications'))
        self.assertEqual(json.loads(response.content),{'unread':0})

    def test_map_poll_combines_requests_without_incident_list(self):
        with self.assertNumQueries(3):
            response=api.poll(self.request('/emergency/api/poll/?scope=notifications&map=1'))
        data=json.loads(response.content)
        self.assertEqual(set(data),{'unread','map'})
        self.assertEqual([row['id'] for row in data['map']['incidents']],[self.incident.pk])
        self.assertNotIn('reporter_phone',data['map']['incidents'][0])

    def test_list_query_count_is_bounded_for_twenty_related_rows(self):
        for kind in ['vehicles','requirements','staff']:
            with self.subTest(kind=kind),self.assertNumQueries(2):
                response=views.listing(self.request(f'/emergency/manage/{kind}/'),kind)
            self.assertEqual(response.status_code,200)
        with self.assertNumQueries(2):
            response=views.posts(self.request('/emergency/posts/'))
        self.assertEqual(response.status_code,200)

    def test_queue_poll_returns_filtered_fragment_and_rechecks_changes(self):
        request=self.request('/emergency/api/poll/?scope=queue&q=Needle')
        data=json.loads(api.poll(request).content)
        self.assertIn('Needle pending',data['queue_html'])
        self.assertNotIn('<html',data['queue_html'])
        self.assertNotIn('scope=queue',data['queue_html'])
        self.assertNotIn('incidents',data)
        FireReport.objects.filter(pk=self.pending.pk).update(status='Confirmed')
        self.assertNotIn('Needle pending',json.loads(api.poll(request).content)['queue_html'])
        self.assertEqual(api.poll(self.request('/emergency/api/poll/?scope=queue',self.citizen)).status_code,403)

    def test_queue_poll_preserves_pagination_and_search(self):
        for index in range(22):FireReport.objects.create(address=f'Needle {index}',status='Pending',fire_scale=0)
        data=json.loads(api.poll(self.request('/emergency/api/poll/?scope=queue&q=Needle&page=2')).content)
        self.assertIn('Needle 21',data['queue_html'])
        self.assertNotIn('Needle pending',data['queue_html'])
        self.assertIn('q=Needle',data['queue_html'])
        self.assertNotIn('scope=queue',data['queue_html'])

    def test_incident_poll_still_enforces_user_visibility(self):
        data=json.loads(api.poll(self.request(f'/emergency/api/poll/?scope=incident&incident={self.incident.pk}',self.citizen)).content)
        self.assertEqual(data['incident']['id'],self.incident.pk)
        self.assertNotIn('incidents',data)
        self.assertNotIn('notices',data)
        self.assertNotIn('deployments',data)
        self.assertNotIn('incident',json.loads(api.poll(self.request(f'/emergency/api/poll/?scope=incident&incident={self.pending.pk}',self.citizen)).content))

    def test_preview_batches_availability_and_preserves_counts(self):
        plan=ResponsePlan.objects.create(home_station=self.station,lead_station=self.station,level=1)
        kinds=list(VehicleType.objects.all())
        for kind in kinds:
            PlanRequirement.objects.create(plan=plan,station=self.station,kind=kind,quantity=2)
            Vehicle.objects.create(station=self.station,kind=kind,registration=f'Preview {kind.pk}')
        with self.assertNumQueries(4):plan,rows=preview(self.incident)
        self.assertEqual(len(rows),len(kinds))
        self.assertTrue(all(row['available']==1 and row['needed']==2 for row in rows))
        self.station.status='Inactive';self.station.save()
        self.assertTrue(all(row['available']==0 for row in preview(self.incident)[1]))

    def test_legacy_user_api_does_not_query_each_role(self):
        with self.assertNumQueries(2):response=user_list_create(self.request('/api/users/'))
        self.assertEqual(len(json.loads(response.content)),23)
        self.assertEqual(response['X-Total-Count'],'23')

    def test_legacy_pagination_caps_results_and_keeps_array_contract(self):
        User.objects.bulk_create([User(username=f'Extra {index}',role=self.role) for index in range(110)])
        response=user_list_create(self.request('/api/users/?page_size=10000'))
        self.assertEqual(len(json.loads(response.content)),100)
        self.assertEqual(response['X-Page-Size'],'100')
        self.assertEqual(response['X-Total-Pages'],'2')
        self.assertIn('rel="next"',response['Link'])
        second=user_list_create(self.request('/api/users/?page=2'))
        first_ids={row['id'] for row in json.loads(response.content)}
        self.assertFalse(first_ids.intersection(row['id'] for row in json.loads(second.content)))
        self.assertEqual(len(json.loads(second.content)),33)
        for size in ['invalid','0','-2']:
            self.assertEqual(user_list_create(self.request('/api/users/?page_size='+size)).status_code,200)

    def test_pages_configure_one_poll_with_the_required_scope(self):
        response=views.map_view(self.request('/emergency/map/'))
        self.assertContains(response,'scope=notifications&map=1')
        self.assertNotContains(response,'setInterval(updateMap')
        response=views.incident_queue(self.request('/emergency/queue/?q=Needle'))
        self.assertContains(response,'q=Needle&scope=queue')
        self.assertNotContains(response,'fetch(location.href)')
