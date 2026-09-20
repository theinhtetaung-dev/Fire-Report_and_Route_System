import json
from django.test import TestCase, Client
from django.urls import reverse
from DataAccess.models import Role, User

class UserServiceAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.role1 = Role.objects.create(role_name="Admin", description="Administrator")
        self.role2 = Role.objects.create(role_name="Operator", description="Dispatch Operator")
        self.user1 = User.objects.create(
            role=self.role1,
            username="admin_user",
            email="admin@fireapp.com",
            password_hash="hashed_pw_1",
            phone_number="091234567",
            status="Active"
        )

    def test_role_list(self):
        url = reverse('api_role_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['role_name'], "Admin")
        self.assertEqual(data[1]['role_name'], "Operator")

    def test_role_create(self):
        url = reverse('api_role_list_create')
        payload = {
            'role_name': 'Citizen',
            'description': 'Reporter / Citizen User'
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['role_name'], "Citizen")
        self.assertTrue(Role.objects.filter(role_name="Citizen").exists())

    def test_role_create_duplicate(self):
        url = reverse('api_role_list_create')
        payload = {
            'role_name': 'Admin',
            'description': 'Duplicate'
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertIn('error', data)

    def test_role_retrieve(self):
        url = reverse('api_role_detail', kwargs={'pk': self.role1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['role_name'], "Admin")

    def test_role_update(self):
        url = reverse('api_role_detail', kwargs={'pk': self.role1.pk})
        payload = {
            'role_name': 'SuperAdmin',
            'description': 'Updated description'
        }
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['role_name'], "SuperAdmin")
        self.assertEqual(data['description'], "Updated description")

    def test_role_delete(self):
        url = reverse('api_role_detail', kwargs={'pk': self.role2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Role.objects.filter(pk=self.role2.pk).exists())

    def test_user_list(self):
        url = reverse('api_user_list_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['username'], "admin_user")

    def test_user_create(self):
        url = reverse('api_user_list_create')
        payload = {
            'role_id': self.role2.pk,
            'username': 'operator_1',
            'email': 'op1@fireapp.com',
            'password_hash': 'hashed_op_pw',
            'phone_number': '097776665',
            'status': 'Active'
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        self.assertEqual(data['username'], "operator_1")
        self.assertTrue(User.objects.filter(username="operator_1").exists())

    def test_user_create_missing_field(self):
        url = reverse('api_user_list_create')
        payload = {
            'role_id': self.role2.pk,
            'username': 'operator_2'
            # Missing email and password_hash
        }
        response = self.client.post(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_user_retrieve(self):
        url = reverse('api_user_detail', kwargs={'pk': self.user1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['username'], "admin_user")

    def test_user_update(self):
        url = reverse('api_user_detail', kwargs={'pk': self.user1.pk})
        payload = {
            'role_id': self.role1.pk,
            'username': 'admin_user_updated',
            'email': 'admin_new@fireapp.com',
            'password_hash': 'new_hash_pw',
            'phone_number': '090000000',
            'status': 'Suspended'
        }
        response = self.client.put(url, data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['username'], "admin_user_updated")
        self.assertEqual(data['status'], "Suspended")

    def test_user_delete(self):
        url = reverse('api_user_detail', kwargs={'pk': self.user1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())


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
        self.assertContains(response, "CAD Officer Login")

    def test_login_post_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'cad_op',
            'password': 'DisptachSecret123',
        })
        self.assertRedirects(response, reverse('dashboard'))
        # Verify session
        self.assertEqual(int(self.client.session['_auth_user_id']), self.user.id)

    def test_login_post_valid_credentials_with_next_param(self):
        url = reverse('login') + '?next=' + reverse('triage_queue')
        response = self.client.post(url, {
            'username': 'cad_op',
            'password': 'DisptachSecret123',
        })
        self.assertRedirects(response, reverse('triage_queue'))

    def test_login_post_invalid_password(self):
        response = self.client.post(reverse('login'), {
            'username': 'cad_op',
            'password': 'BadPassword',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid credentials or account is inactive.")

    def test_logout_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('_auth_user_id', self.client.session)


class RoleAuthorizationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_role = Role.objects.create(role_name="Administrator")
        self.dispatcher_role = Role.objects.create(role_name="Dispatcher")
        self.responder_role = Role.objects.create(role_name="Firefighter")
        self.citizen_role = Role.objects.create(role_name="Citizen")

        self.admin_user = User.objects.create(
            role=self.admin_role,
            username="admin_test",
            email="admin@test.gov",
            status="Active"
        )
        self.admin_user.set_password("AdminPass1")
        self.admin_user.save()

        self.dispatcher_user = User.objects.create(
            role=self.dispatcher_role,
            username="disp_test",
            email="disp@test.gov",
            status="Active"
        )
        self.dispatcher_user.set_password("DispPass1")
        self.dispatcher_user.save()

        self.responder_user = User.objects.create(
            role=self.responder_role,
            username="resp_test",
            email="resp@test.gov",
            status="Active"
        )
        self.responder_user.set_password("RespPass1")
        self.responder_user.save()

        self.citizen_user = User.objects.create(
            role=self.citizen_role,
            username="citizen_test",
            email="citizen@test.gov",
            status="Active"
        )
        self.citizen_user.set_password("CitizenPass1")
        self.citizen_user.save()

    def test_unauthenticated_user_redirected_from_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_public_report_fire_accessible_without_auth(self):
        """Preserve public emergency fire intake without authentication."""
        response = self.client.get(reverse('report_fire'))
        self.assertEqual(response.status_code, 200)

    def test_citizen_forbidden_from_cad_dashboard(self):
        self.client.force_login(self.citizen_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Restricted Access", status_code=403)

    def test_citizen_forbidden_from_triage_queue(self):
        self.client.force_login(self.citizen_user)
        response = self.client.get(reverse('triage_queue'))
        self.assertEqual(response.status_code, 403)

    def test_responder_can_access_dashboard_but_forbidden_from_user_admin(self):
        self.client.force_login(self.responder_user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 403)

    def test_dispatcher_can_access_triage_queue(self):
        self.client.force_login(self.dispatcher_user)
        response = self.client.get(reverse('triage_queue'))
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_user_and_role_management(self):
        self.client.force_login(self.admin_user)
        response_users = self.client.get(reverse('user_list'))
        self.assertEqual(response_users.status_code, 200)

        response_roles = self.client.get(reverse('role_list'))
        self.assertEqual(response_roles.status_code, 200)

