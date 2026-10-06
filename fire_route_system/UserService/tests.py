import json
from django.test import TestCase, Client
from django.urls import reverse
from DataAccess.models import Role, User

class UserServiceAPITests(TestCase):
    def setUp(self):
        self.role = Role.objects.create(role_name='Administrator')
        self.user = User.objects.create(role=self.role, username='legacy_admin', email=None)
    def test_anonymous_account_api_requires_login(self):
        self.assertEqual(self.client.get(reverse('api_user_list_create')).status_code, 302)
    def test_admin_can_read_legacy_account_and_role_api(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('api_user_list_create')).status_code, 200)
        self.assertEqual(self.client.get(reverse('api_role_list_create')).status_code, 200)
    def test_legacy_account_mutations_blocked_without_changes(self):
        self.client.force_login(self.user)
        for verb in ['post','put','patch','delete']:
            response=getattr(self.client,verb)(reverse('api_user_detail',kwargs={'pk':self.user.pk}),data='{}',content_type='application/json')
            self.assertEqual(response.status_code,403)
        self.user.refresh_from_db();self.assertEqual(self.user.username,'legacy_admin')
    def test_legacy_role_mutations_blocked(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.post(reverse('api_role_list_create'),data='{}',content_type='application/json').status_code,403)
        self.assertEqual(Role.objects.count(),1)
    def test_console_account_create_and_deactivate(self):
        citizen=Role.objects.create(role_name='Citizen');self.client.force_login(self.user)
        response=self.client.post('/emergency/manage/staff/new/',{'full_name':'Citizen','username':'new_citizen','role':citizen.pk,'phone_number':'09999999999','status':'Active','password':'StrongDemo2026!'})
        self.assertEqual(response.status_code,302)
        created=User.objects.get(username='new_citizen');self.assertTrue(created.check_password('StrongDemo2026!'))
        response=self.client.post(f'/emergency/manage/staff/{created.pk}/',{'full_name':'Citizen','username':'new_citizen','role':citizen.pk,'phone_number':'09999999999','status':'Inactive'})
        self.assertEqual(response.status_code,302);created.refresh_from_db();self.assertFalse(created.is_active)



class UserAuthModelTests(TestCase):
    def setUp(self):
        self.admin_role = Role.objects.create(role_name="Administrator", description="Admin")
        self.disp_role = Role.objects.create(role_name="Dispatcher", description="CAD Operator")
        self.user = User.objects.create(
            role=self.admin_role,
            username="sec_admin",
            email="sec_admin@example.com",
            phone_number="09111222333",
            status="Active"
        )
        self.user.set_password("AntigravityPass#2026")
        self.user.save()

    def test_password_hashing_and_verification(self):
        self.assertTrue(self.user.password_hash.startswith("pbkdf2_sha256$"))
        self.assertTrue(self.user.check_password("AntigravityPass#2026"))
        self.assertFalse(self.user.check_password("WrongPassword"))

    def test_session_auth_hash(self):
        auth_hash = self.user.get_session_auth_hash()
        self.assertIsNotNone(auth_hash)
        self.assertGreater(len(auth_hash), 10)

    def test_role_properties_and_checks(self):
        self.assertTrue(self.user.is_admin)
        self.assertFalse(self.user.is_dispatcher)
        self.assertTrue(self.user.has_role("administrator", "admin"))
        self.assertFalse(self.user.has_role("citizen"))

        # Switch role to dispatcher
        self.user.role = self.disp_role
        self.user.save()
        self.assertTrue(self.user.is_dispatcher)
        self.assertFalse(self.user.is_admin)


class LoginLogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.role = Role.objects.create(role_name="Dispatcher", description="Dispatcher")
        self.user = User.objects.create(
            role=self.role,
            username="cad_op",
            email="cad_op@emergency.gov",
            status="Active"
        )
        self.user.set_password("DisptachSecret123")
        self.user.save()

    def test_login_get_renders_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "အကောင့်ဝင်ရန်")

    def test_login_post_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'cad_op',
            'password': 'DisptachSecret123',
        })
        self.assertRedirects(response, reverse('emergency:dashboard'))
        # Verify session
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_post_valid_credentials_with_next_param(self):
        url = reverse('login') + '?next=' + reverse('emergency:posts')
        response = self.client.post(url, {
            'username': 'cad_op',
            'password': 'DisptachSecret123',
        })
        self.assertRedirects(response, reverse('emergency:posts'))

    def test_login_post_invalid_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'cad_op',
            'password': 'BadPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "အကောင့်အချက်အလက်မမှန်ပါ သို့မဟုတ် အကောင့်ပိတ်ထားသည်။")

    def test_logout_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class RoleAuthorizationViewTests(TestCase):
    def setUp(self):
        self.users={name:User.objects.create(username=name,role=Role.objects.create(role_name=name),email=None) for name in ['Administrator','Dispatcher','Firefighter','Citizen']}
    def test_anonymous_dashboard_and_intake_require_login(self):
        for path in ['/emergency/','/emergency/report/']:
            self.assertEqual(self.client.get(path).status_code,302)
    def test_each_role_has_dashboard_and_authenticated_intake(self):
        for user in self.users.values():
            self.client.force_login(user)
            self.assertEqual(self.client.get('/emergency/').status_code,200)
            self.assertEqual(self.client.get('/emergency/report/').status_code,200)
            self.assertRedirects(self.client.get('/dashboard/'),'/emergency/')
    def test_citizen_and_legacy_dispatcher_cannot_manage_accounts(self):
        for name in ['Citizen','Dispatcher','Firefighter']:
            self.client.force_login(self.users[name])
            self.assertEqual(self.client.get(reverse('user_list')).status_code,403)
            self.assertEqual(self.client.get('/emergency/manage/plans/').status_code,403)
    def test_admin_can_manage_accounts(self):
        self.client.force_login(self.users['Administrator'])
        self.assertEqual(self.client.get('/emergency/manage/staff/').status_code,200)
