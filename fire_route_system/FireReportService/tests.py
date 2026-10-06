import json
from django.test import TestCase, Client
from django.urls import reverse
from DataAccess.models import FireReport, Role, User

class FireReportServiceAPITests(TestCase):
    def setUp(self):
        role=Role.objects.create(role_name='Citizen')
        self.user=User.objects.create(role=role,username='reporter',email=None,phone_number='09912345678')
        self.client.force_login(self.user)
        self.report=FireReport.objects.create(user_id=self.user.pk,latitude=21.97,longitude=96.08,fire_scale=0)
    def test_paginated_scoped_list(self):
        FireReport.objects.create(user_id=None,address='Other person',fire_scale=0)
        data=self.client.get(reverse('api_firereport_list_create')).json()
        self.assertEqual(data['count'],1);self.assertNotIn('reporter_phone',data['results'][0])
    def test_create_ignores_client_identity_and_severity(self):
        response=self.client.post(reverse('api_firereport_list_create'),data=json.dumps({'address':'Mandalay','user_id':999,'reporter_phone':'spoof','fire_scale':5,'status':'Resolved'}),content_type='application/json')
        self.assertEqual(response.status_code,201)
        obj=FireReport.objects.get(pk=response.json()['id']);self.assertEqual(obj.user_id,self.user.pk);self.assertEqual(obj.reporter_phone,self.user.phone_number);self.assertEqual(obj.fire_scale,0);self.assertEqual(obj.status,'Pending')
    def test_invalid_coordinates_rejected(self):
        response=self.client.post(reverse('api_firereport_list_create'),data=json.dumps({'latitude':100,'longitude':96}),content_type='application/json')
        self.assertEqual(response.status_code,400)
    def test_retrieve_owned_report_only(self):
        self.assertEqual(self.client.get(reverse('api_firereport_detail',kwargs={'pk':self.report.pk})).status_code,200)
        other=FireReport.objects.create(user_id=None,address='Other',fire_scale=0)
        self.assertEqual(self.client.get(reverse('api_firereport_detail',kwargs={'pk':other.pk})).status_code,404)
    def test_legacy_update_and_delete_blocked(self):
        url=reverse('api_firereport_detail',kwargs={'pk':self.report.pk})
        self.assertEqual(self.client.patch(url,data='{}',content_type='application/json').status_code,405)
        self.assertEqual(self.client.delete(url).status_code,405)
        self.assertTrue(FireReport.objects.filter(pk=self.report.pk).exists())



from DataAccess.models import Tbl_Notification

class FireReportTriageWorkflowTests(TestCase):
    def test_notification_created_on_pending_report(self):
        from DataAccess.models import Tbl_Notification
        report=FireReport.objects.create(address='Mandalay',fire_scale=0)
        self.assertTrue(Tbl_Notification.objects.filter(report=report).exists())
    def test_notification_not_created_on_other_statuses(self):
        from DataAccess.models import Tbl_Notification
        report=FireReport.objects.create(address='Mandalay',fire_scale=0,status='Confirmed')
        self.assertFalse(Tbl_Notification.objects.filter(report=report).exists())
    def test_legacy_confirmation_cannot_bypass_audited_workflow(self):
        role=Role.objects.create(role_name='Administrator');user=User.objects.create(role=role,username='admin',email=None);self.client.force_login(user)
        report=FireReport.objects.create(address='Mandalay',fire_scale=0)
        response=self.client.post(reverse('confirm_incident',kwargs={'notification_id':report.notifications.get().pk}))
        self.assertEqual(response.status_code,403);report.refresh_from_db();self.assertEqual(report.status,'Pending')



from django.core.exceptions import ValidationError

class FireReportFlexibleReportingTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_validation_gps_only_is_valid(self):
        """
        A report with GPS coordinates and no address is valid.
        """
        report = FireReport(
            latitude=21.9750,
            longitude=96.0830,
            fire_scale=2,
            status='Pending'
        )
        try:
            report.full_clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for GPS-only report!")

    def test_validation_address_only_is_valid(self):
        """
        A report with an address and no GPS coordinates is valid.
        """
        report = FireReport(
            address="Mandalay Palace, Mandalay",
            fire_scale=2,
            status='Pending'
        )
        try:
            report.full_clean()
        except ValidationError:
            self.fail("ValidationError raised unexpectedly for Address-only report!")

    def test_validation_neither_raises_error(self):
        """
        A report with neither GPS coordinates nor address raises ValidationError.
        """
        report = FireReport(
            fire_scale=2,
            status='Pending'
        )
        with self.assertRaises(ValidationError):
            report.full_clean()

    def test_authenticated_legacy_user_can_report_without_phone(self):
        role=Role.objects.create(role_name='Citizen');user=User.objects.create(role=role,username='legacy',email=None)
        self.client.force_login(user)
        response=self.client.post('/emergency/report/',{'latitude':'21.9928','longitude':'96.0964'})
        self.assertEqual(response.status_code,302)
        report=FireReport.objects.get(user_id=user.pk);self.assertEqual(report.fire_scale,0);self.assertIsNone(report.reporter_phone)




