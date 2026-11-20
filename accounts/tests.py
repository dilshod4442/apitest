from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class AuthenticationFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', password='TestPassword123!')
        self.client = APIClient()

    def test_registration_password_is_hashed(self):
        r = self.client.post('/api/register/', {'username': 'newstudent', 'email': 'new@example.com', 'password': 'VeryStrongPass123!', 'password_confirm': 'VeryStrongPass123!'}, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertTrue(User.objects.get(username='newstudent').check_password('VeryStrongPass123!'))
        self.assertNotIn('password', r.data)

    def test_basic_auth(self):
        import base64
        creds = base64.b64encode(b'student:TestPassword123!').decode()
        r = self.client.get('/api/basic/me/', HTTP_AUTHORIZATION='Basic ' + creds)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['method'], 'Basic')

    def test_session_auth(self):
        self.assertTrue(self.client.login(username='student', password='TestPassword123!'))
        self.assertEqual(self.client.get('/api/session/me/').status_code, 200)

    def test_token_login_and_logout(self):
        r = self.client.post('/api/token/login/', {'username': 'student', 'password': 'TestPassword123!'}, format='json')
        self.assertEqual(r.status_code, 200)
        token = r.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        self.assertEqual(self.client.get('/api/token/me/').status_code, 200)
        self.assertEqual(self.client.post('/api/token/logout/').status_code, 200)
        self.assertFalse(Token.objects.filter(key=token).exists())
        self.assertEqual(self.client.get('/api/token/me/').status_code, 401)

    def test_jwt_auth(self):
        r = self.client.post('/api/jwt/login/', {'username': 'student', 'password': 'TestPassword123!'}, format='json')
        self.assertEqual(r.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + r.data['access'])
        self.assertEqual(self.client.get('/api/jwt/me/').status_code, 200)

    def test_jwt_blacklist_refresh(self):
        refresh = str(RefreshToken.for_user(self.user))
        self.assertEqual(self.client.post('/api/jwt/logout/', {'refresh': refresh}, format='json').status_code, 200)
        self.assertEqual(self.client.post('/api/jwt/refresh/', {'refresh': refresh}, format='json').status_code, 401)

    def test_other_users_notes_hidden(self):
        from notes.models import Note
        other = User.objects.create_user(username='other', password='AnotherPass123!')
        note = Note.objects.create(owner=other, title='private')
        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access)
        self.assertEqual(self.client.get('/api/notes/').data, [])
        self.assertEqual(self.client.get(f'/api/notes/{note.pk}/').status_code, 404)
        self.assertEqual(self.client.post('/api/notes/', {'title': 'mine'}, format='json').status_code, 201)
