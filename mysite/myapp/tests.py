from django.contrib.auth import get_user_model
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from .models import Resume, UserProfiles
from .numbers import is_prime


class ResumeTests(TestCase):
    def setUp(self):
        self.url = reverse("about_jinja")
        self.data = {
            "surname": "Ivanov",
            "name": "Ivan",
            "age": "25",
            "profession": "Developer",
            "skills": "Python, Django",
        }

    def test_get_shows_empty_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_bound)
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_valid_post_renders_resume_and_preserves_input(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertRedirects(response, self.url)
        saved = Resume.objects.get()
        self.assertEqual(saved.age, 25)
        self.assertEqual(saved.surname, self.data["surname"])
        self.assertEqual(response.context["resume"].pk, saved.pk)
        self.assertContains(response, 'value="Ivanov"')
        self.assertContains(response, "Python, Django")

    def test_invalid_age_does_not_generate_resume(self):
        for age in ("-1", "100", "abc", "1.5", ""):
            with self.subTest(age=age):
                response = self.client.post(self.url, {**self.data, "age": age})
                self.assertIn("age", response.context["form"].errors)
                self.assertNotIn("resume", response.context)
                self.assertContains(response, 'value="Ivanov"')
                self.assertEqual(Resume.objects.count(), 0)

    def test_age_boundaries_are_valid(self):
        for age in ("0", "99"):
            with self.subTest(age=age):
                response = self.client.post(self.url, {**self.data, "age": age}, follow=True)
                self.assertEqual(response.context["resume"].age, int(age))

    def test_required_and_length_validation(self):
        for surname in ("", "   ", "x" * 101):
            with self.subTest(surname=surname):
                response = self.client.post(self.url, {**self.data, "surname": surname})
                self.assertIn("surname", response.context["form"].errors)
                self.assertNotIn("resume", response.context)
                self.assertEqual(Resume.objects.count(), 0)

    def test_output_is_escaped(self):
        response = self.client.post(
            self.url, {**self.data, "skills": "<script>alert(1)</script>"}, follow=True
        )
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_csrf_is_required_and_valid_token_is_accepted(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(self.url, self.data).status_code, 403)
        client.get(self.url)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.url, {**self.data, "csrfmiddlewaretoken": token}, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("resume", response.context)

    def test_refresh_and_number_selection_do_not_duplicate_resume(self):
        self.client.post(self.url, self.data, follow=True)
        saved = Resume.objects.get()
        response = self.client.get(self.url)
        self.assertEqual(response.context["resume"].pk, saved.pk)
        response = self.client.get(self.url, {
            "number_type": "even", "start": 1, "end": 6,
        })
        self.assertEqual(response.context["numbers"], [2, 4, 6])
        self.assertEqual(response.context["resume"].pk, saved.pk)
        self.assertEqual(Resume.objects.count(), 1)

    def test_other_browser_cannot_read_saved_resume(self):
        self.client.post(self.url, self.data)
        response = Client().get(self.url)
        self.assertNotIn("resume", response.context)
        self.assertNotContains(response, self.data["surname"])

    def test_deleted_resume_does_not_break_page(self):
        self.client.post(self.url, self.data)
        Resume.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("resume", response.context)

    def test_admin_can_view_saved_resumes(self):
        self.client.post(self.url, self.data)
        admin_url = reverse("admin:myapp_resume_changelist")
        self.assertEqual(self.client.get(admin_url).status_code, 302)
        admin = get_user_model().objects.create_superuser(
            username="test_admin", email="admin@example.com", password="test-password"
        )
        self.client.force_login(admin)
        response = self.client.get(admin_url)
        self.assertContains(response, self.data["surname"])


class UserProfileTests(TestCase):
    def test_original_profiles_are_loaded_from_database(self):
        for username, display_name in (("Ivan", "Иван/Ваня"),
                                       ("Dima", "Дима/Дмитрий"),
                                       ("Sergey", "Сергей/Серёжа")):
            with self.subTest(username=username):
                profile = UserProfiles.objects.get(username=username)
                self.assertEqual(profile.display_name, display_name)
                response = self.client.get(reverse("user_profile", args=[username]))
                self.assertContains(response, display_name)
                self.assertContains(response, profile.age)
                self.assertContains(response, profile.email)

    def test_database_changes_appear_on_page(self):
        profile = UserProfiles.objects.get(username="Ivan")
        profile.city = "Updated city"
        profile.email = "ivan@example.com"
        profile.save()
        response = self.client.get(reverse("user_profile", args=["Ivan"]))
        self.assertContains(response, "Updated city")
        self.assertContains(response, "ivan@example.com")

    def test_missing_and_guest_profiles_still_render(self):
        for url in (reverse("user_profile"), reverse("user_profile", args=["missing"])):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["username"], "?")

    def test_admin_can_create_profile(self):
        url = reverse("admin:myapp_userprofiles_add")
        self.assertEqual(self.client.get(url).status_code, 302)
        admin = get_user_model().objects.create_superuser(
            username="profile_admin", email="admin@example.com", password="test-password"
        )
        self.client.force_login(admin)
        response = self.client.post(url, {
            "username": "Anna", "display_name": "Анна", "age": "25",
            "city": "Алматы", "ip_address": "127.0.0.1",
            "about_me": "Изучаю Django", "email": "anna@example.com",
            "_save": "Save",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProfiles.objects.filter(username="Anna").exists())
        self.assertContains(self.client.get(reverse("user_profile", args=["Anna"])), "Анна")
        duplicate = self.client.post(url, {
            "username": "Anna", "display_name": "Другое имя", "age": "25",
            "city": "Алматы", "ip_address": "127.0.0.1",
            "about_me": "Test", "email": "anna@example.com",
        })
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(UserProfiles.objects.filter(username="Anna").count(), 1)


class NumberRangeTests(SimpleTestCase):
    def setUp(self):
        self.url = reverse("about_jinja")

    def test_filters_and_inclusive_bounds(self):
        cases = {
            "all": [-2, -1, 0, 1, 2, 3, 4, 5],
            "even": [-2, 0, 2, 4],
            "odd": [-1, 1, 3, 5],
            "prime": [2, 3, 5],
        }
        for kind, expected in cases.items():
            with self.subTest(kind=kind):
                response = self.client.get(self.url, {
                    "number_type": kind, "start": -2, "end": 5,
                })
                self.assertEqual(response.context["numbers"], expected)
                for number in expected:
                    self.assertContains(response, f"<li>{number}</li>", html=True)
                self.assertFalse(response.context["form"].is_bound)

    def test_invalid_ranges_and_choices(self):
        cases = [
            {"start": 5, "end": 1},
            {"start": 0, "end": 1000},
            {"start": "abc"}, {"end": "1.5"}, {"start": ""},
            {"start": -1000001}, {"end": 1000001},
            {"number_type": "unknown"}, {"number_type": ""},
        ]
        for changes in cases:
            with self.subTest(changes=changes):
                response = self.client.get(self.url, {
                    "number_type": "all", "start": 1, "end": 10, **changes,
                })
                self.assertTrue(response.context["number_form"].errors)
                self.assertNotIn("numbers", response.context)

    def test_empty_result(self):
        response = self.client.get(self.url, {
            "number_type": "prime", "start": -10, "end": 1,
        })
        self.assertEqual(response.context["numbers"], [])
        self.assertContains(response, "В этом диапазоне подходящих чисел нет.")

    def test_maximum_range_and_single_number(self):
        response = self.client.get(self.url, {
            "number_type": "all", "start": 1, "end": 1000,
        })
        self.assertEqual(len(response.context["numbers"]), 1000)
        response = self.client.get(self.url, {
            "number_type": "prime", "start": 2, "end": 2,
        })
        self.assertEqual(response.context["numbers"], [2])

    def test_prime_squares_and_larger_prime(self):
        for number in (-1, 0, 1, 4, 9, 25, 49, 1000000):
            with self.subTest(number=number):
                self.assertFalse(is_prime(number))
        self.assertTrue(is_prime(999983))

    def test_get_defaults_and_missing_fields(self):
        response = self.client.get(self.url)
        self.assertFalse(response.context["number_form"].is_bound)
        self.assertNotIn("numbers", response.context)
        response = self.client.get(self.url, {"number_type": "all"})
        self.assertIn("start", response.context["number_form"].errors)
        self.assertIn("end", response.context["number_form"].errors)

    def test_selection_and_bounds_are_preserved(self):
        response = self.client.get(self.url, {
            "number_type": "odd", "start": -3, "end": 7,
        })
        self.assertContains(response, 'value="-3"')
        self.assertContains(response, 'value="7"')
        self.assertEqual(response.context["number_form"]["number_type"].value(), "odd")
