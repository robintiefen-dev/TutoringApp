from django.test import TestCase
from django.core.exceptions import ValidationError
from .forms import TASignUpForm
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import TAProfile, Course, TutoringHour


# Create your tests here.
class TASignUpFormTests(TestCase):

    def test_form_has_correct_fields(self):
        form = TASignUpForm()

        self.assertIn("username", form.fields)
        self.assertIn("password1", form.fields)
        self.assertIn("password2", form.fields)

    def test_passwords_do_not_match(self):
        form = TASignUpForm(
            data={
                "username": "TestTutor123",
                "password1": "ExamplePass123!",
                "password2": "DifferentPass2026!",
            }
        )

        self.assertFalse(form.is_valid())

    def test_valid_signup_form(self):
        form = TASignUpForm(
            data={
                "username": "TestTutor123",
                "password1": "ExamplePass123!",
                "password2": "ExamplePass123!",
            }
        )

        self.assertTrue(form.is_valid())


class TADashboardPermissionTests(TestCase):

    def test_regular_user_cannot_access_dashboard(self):
        user = get_user_model().objects.create_user(
            username="RegularUser", password="ExamplePass2026!"
        )

        self.client.force_login(user)

        response = self.client.get(reverse("ta_dashboard"))

        self.assertEqual(response.status_code, 403)

    def test_ta_can_access_dashboard(self):
        user = get_user_model().objects.create_superuser(
            username="Jimothy", password="ExamplePass2026!"
        )
        TAProfile.objects.create(user=user)

        self.client.force_login(user)

        response = self.client.get(reverse("ta_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("ta_dashboard"))
        self.assertRedirects(response, "/accounts/login/?next=/tutoring/dashboard/")


class TASignUpViewTests(TestCase):

    def test_signup_creates_user_without_ta_permissions(self):
        response = self.client.post(
            reverse("ta_signup"),
            {
                "username": "TestTutor456",
                "password1": "ExamplePass2026!",
                "password2": "ExamplePass2026!",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = get_user_model().objects.get(username="TestTutor456")

        self.assertFalse(TAProfile.objects.filter(user=user).exists())


class TAProfileModelTests(TestCase):
    def test_ta_can_tutor_multiple_courses(self):
        user = get_user_model().objects.create_user(
            username="Jimothy", password="ExamplePass2026!"
        )
        ta = TAProfile.objects.create(user=user)

        course1 = Course.objects.create(code="CSCI 150")
        course2 = Course.objects.create(code="CSCI 151")

        ta.courses.add(course1, course2)

        self.assertEqual(ta.courses.count(), 2)


class TADetailViewTests(TestCase):

    def test_ta_detail_page_displays_username(self):
        user = get_user_model().objects.create_user(
            username="Jimothy", password="ExamplePass2026!"
        )

        ta = TAProfile.objects.create(user=user)

        response = self.client.get(reverse("ta_detail", args=[ta.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jimothy")

    def test_ta_detail_displays_courses(self):
        user = get_user_model().objects.create_user(
            username="Jimothy", password="ExamplePass2026!"
        )
        ta = TAProfile.objects.create(user=user)

        course1 = Course.objects.create(code="CSCI 150")
        course2 = Course.objects.create(code="CSCI 151")

        ta.courses.add(course1, course2)

        response = self.client.get(reverse("ta_detail", args=[ta.pk]))

        self.assertContains(response, "CSCI 150")
        self.assertContains(response, "CSCI 151")


class HomePageTests(TestCase):
    def test_homepage_displays_ta_link(self):
        user = get_user_model().objects.create_user(
            username="Jimothy", password="ExamplePass2026!"
        )
        ta = TAProfile.objects.create(user=user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Jimothy")
        self.assertContains(response, reverse("ta_detail", args=[ta.pk]))


class TutoringHourValidationTests(TestCase):
    def test_end_time_before_start_time_is_invalid(self):
        user = get_user_model().objects.create_user(
            username="Jimothy", password="ExamplePass2026!"
        )
        ta = TAProfile.objects.create(user=user)

        shift = TutoringHour(
            ta=ta, weekday="Monday", start_time="15:00", end_time="13:00"
        )
        with self.assertRaises(ValidationError):
            shift.full_clean()

    def test_shift_requires_weekday_or_date(self):
        user = get_user_model().objects.create_user(
            username="Jimothy", password="ExamplePass2026!"
        )

        ta = TAProfile.objects.create(user=user)

        shift = TutoringHour(
            ta=ta, weekday="", date=None, start_time="10:00", end_time="12:00"
        )

        with self.assertRaises(ValidationError):
            shift.full_clean()
