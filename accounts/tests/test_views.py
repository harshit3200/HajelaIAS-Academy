from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AccountsViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", 
            password="testpassword"
        )
        self.login_url = reverse('login')  # Adjust if using a different name for login view
        self.logout_url = reverse('logout')  # Adjust if using a different name for logout view
        self.password_reset_url = reverse('password_reset')

    def test_login_view(self):
        """Test the login view for valid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'testuser@example.com', 
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue(self.client.login(email='testuser@example.com', password='testpassword'))

    def test_login_view_invalid_credentials(self):
        """Test login view with invalid credentials."""
        response = self.client.post(self.login_url, {
            'username': 'wronguser@example.com', 
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)  # Should stay on the login page
        self.assertContains(response, "Invalid username or password")

    def test_logout_view(self):
        """Test logout functionality."""
        self.client.login(email='testuser@example.com', password='testpassword')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertRedirects(response, reverse('index'))

    def test_password_reset_view(self):
        """Test password reset view."""
        response = self.client.post(self.password_reset_url, {
            'email': 'testuser@example.com',
        })
        self.assertEqual(response.status_code, 302)  # Redirect to password reset done
