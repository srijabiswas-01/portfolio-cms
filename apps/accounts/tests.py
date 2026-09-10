from unittest.mock import patch

from django.conf import settings
from django.test import Client, SimpleTestCase, override_settings
from django.urls import reverse


@override_settings(
    SECURE_SSL_REDIRECT=False,
    TEMPLATES=[{
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "OPTIONS": {"loaders": [("django.template.loaders.locmem.Loader", {
            "admin/login.html": "<form method='post'>{% csrf_token %}</form>",
        })]},
    }],
)
class LoginCsrfTests(SimpleTestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.url = reverse("admin_login")

    def test_other_apps_cookies_do_not_invalidate_login_form(self):
        self.assertEqual(settings.CSRF_COOKIE_NAME, "portfolio_csrftoken")
        self.assertEqual(settings.SESSION_COOKIE_NAME, "portfolio_sessionid")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        token = self.client.cookies[settings.CSRF_COOKIE_NAME].value
        self.client.cookies["csrftoken"] = "A" * 32
        self.client.cookies["sessionid"] = "another-app-session"
        with patch("apps.accounts.views.authenticate", return_value=None) as authenticate:
            response = self.client.post(self.url, {
                "username": "example", "password": "invalid", "csrfmiddlewaretoken": token,
            })
        self.assertEqual(response.status_code, 200)
        authenticate.assert_called_once()

    def test_wrong_token_is_still_rejected(self):
        self.client.get(self.url)
        with patch("apps.accounts.views.authenticate") as authenticate:
            response = self.client.post(self.url, {"csrfmiddlewaretoken": "B" * 32})
        self.assertEqual(response.status_code, 403)
        authenticate.assert_not_called()

    def test_login_form_is_not_cached(self):
        response = self.client.get(self.url)
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertIn("private", response.headers["Cache-Control"])

    def test_refresh_recovers_from_token_rotation(self):
        self.client.get(self.url)
        old_token = self.client.cookies[settings.CSRF_COOKIE_NAME].value
        self.client.cookies[settings.CSRF_COOKIE_NAME] = "C" * 32
        with patch("apps.accounts.views.authenticate", return_value=None) as authenticate:
            rejected = self.client.post(self.url, {"csrfmiddlewaretoken": old_token})
            self.assertEqual(rejected.status_code, 403)
            authenticate.assert_not_called()
            refresh = self.client.get(reverse("login_csrf_token"))
            self.assertIn("no-store", refresh.headers["Cache-Control"])
            response = self.client.post(self.url, {
                "username": "example", "password": "invalid",
                "csrfmiddlewaretoken": refresh.json()["csrfToken"],
            })
            self.assertEqual(response.status_code, 200)
            authenticate.assert_called_once()

    def test_refresh_does_not_bypass_origin_validation(self):
        refresh = self.client.get(reverse("login_csrf_token"))
        with patch("apps.accounts.views.authenticate") as authenticate:
            response = self.client.post(self.url, {
                "csrfmiddlewaretoken": refresh.json()["csrfToken"],
            }, HTTP_ORIGIN="https://untrusted.example")
        self.assertEqual(response.status_code, 403)
        authenticate.assert_not_called()
