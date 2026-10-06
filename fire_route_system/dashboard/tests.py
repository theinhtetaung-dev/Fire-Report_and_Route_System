from django.test import TestCase
from DataAccess.models import Role,User,FireReport

class DashboardViewTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create(role=Role.objects.create(role_name='Administrator'),username='admin',email=None)
        self.citizen=User.objects.create(role=Role.objects.create(role_name='Citizen'),username='citizen',email=None)
        self.pending=FireReport.objects.create(user_id=self.citizen.pk,address='Pending',fire_scale=0)
        self.resolved=FireReport.objects.create(address='Resolved',fire_scale=2,status='Resolved')
    def test_dashboard_requires_login(self):
        self.assertEqual(self.client.get('/emergency/').status_code,302)
    def test_admin_dashboard_all_incident_kpis(self):
        self.client.force_login(self.admin)
        response=self.client.get('/emergency/')
        self.assertTemplateUsed(response,'emergency/dashboard.html');self.assertEqual(response.context['active_count'],1)
        self.assertEqual(len(response.context['incidents']),2)
    def test_citizen_dashboard_scoped_to_own_incidents(self):
        self.client.force_login(self.citizen)
        response=self.client.get('/emergency/')
        self.assertEqual(list(response.context['incidents']),[self.pending])
    def test_legacy_dashboard_redirect(self):
        self.client.force_login(self.admin);self.assertRedirects(self.client.get('/dashboard/'),'/emergency/')

class DashboardReportPortalTests(TestCase):
    def setUp(self):
        self.admin=User.objects.create(role=Role.objects.create(role_name='Administrator'),username='admin',email=None)
        for level in [0,1,2]:FireReport.objects.create(address='Report',fire_scale=level,status='Confirmed')
        self.client.force_login(self.admin)
    def test_day_month_year_report_grouping(self):
        for period in ['day','month','year']:
            response=self.client.get('/emergency/reports/',{'period':period})
            self.assertEqual(response.status_code,200);self.assertEqual(sum(r['total'] for r in response.context['page_obj']),3)
    def test_level_filter(self):
        response=self.client.get('/emergency/reports/',{'level':'1'})
        self.assertEqual(sum(r['total'] for r in response.context['page_obj']),1)
    def test_csv_download(self):
        response=self.client.get('/emergency/reports/',{'export':'csv','level':'2'})
        self.assertEqual(response.status_code,200);self.assertIn('text/csv',response['Content-Type']);self.assertIn(b'Report',response.content)
    def test_pdf_download(self):
        response=self.client.get('/emergency/reports/',{'export':'pdf'})
        self.assertEqual(response.status_code,200);self.assertTrue(response.content.startswith(b'%PDF'))
