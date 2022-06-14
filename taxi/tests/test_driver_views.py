from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Driver

DRIVER_LIST_VIEW_URL = reverse("taxi:driver-list")
DRIVER_CREATE_VIEW_URL = reverse("taxi:driver-create")


class PublicDriverTest(TestCase):
    def test_login_required(self):
        response = self.client.get(DRIVER_LIST_VIEW_URL)

        self.assertNotEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(DRIVER_LIST_VIEW_URL)
        redirect_url = "/accounts/login/?next=/drivers/"

        self.assertRedirects(response, redirect_url)


class PrivateDriverTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test_password",
        )
        self.client.force_login(self.user)

        number_of_drivers = 2
        for num in range(number_of_drivers):
            Driver.objects.create(
                username=f"test_driver {num}",
                password=f"test_password {num}",
                license_number=f"AAA0000{num}",
            )

    # DriverListView section tests

    def test_pagination_is_two(self):
        response = self.client.get(DRIVER_LIST_VIEW_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["driver_list"]) == 2)

    def test_all_drivers_is_displayed(self):
        # Get second page and confirm it has (exactly) remaining 1 items
        response = self.client.get(DRIVER_LIST_VIEW_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["driver_list"]) == 1)

    def test_retrieve_drivers(self):
        response = self.client.get(DRIVER_LIST_VIEW_URL)
        drivers = Driver.objects.all().order_by("username")[:2]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["driver_list"]),
            list(drivers)
        )
        self.assertTemplateUsed(response, "taxi/driver_list.html")

    # DriverCreateView section tests

    def test_create_driver(self):
        driver_form_data = {
            "username": "TestDriver",
            "license_number": "AAA20000",
            "password1": "z}q)W76q",
            "password2": "z}q)W76q",
        }

        response = self.client.get(DRIVER_CREATE_VIEW_URL)

        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_form.html")

        response = self.client.post(DRIVER_CREATE_VIEW_URL, data=driver_form_data)

        self.assertTrue(response.status_code, 302)
        self.assertRedirects(response, DRIVER_LIST_VIEW_URL)

        new_driver = Driver.objects.get(username=driver_form_data["username"])

        self.assertEqual(new_driver.username, driver_form_data["username"])
        self.assertEqual(new_driver.license_number, driver_form_data["license_number"])

    # DriverLicenseUpdateView section tests

    def test_license_update(self):
        driver_to_update = Driver.objects.get(id=2)

        update_data = {"license_number": "AAA12345"}

        response = self.client.get(
            reverse("taxi:driver-license-update", kwargs={"pk": driver_to_update.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/driver_form.html")

        response = self.client.post(
            reverse("taxi:driver-license-update", kwargs={"pk": driver_to_update.pk}),
            data=update_data
        )

        self.assertRedirects(response, DRIVER_LIST_VIEW_URL)

        driver_updated = Driver.objects.get(id=2)

        self.assertEqual(driver_updated.license_number, update_data["license_number"])

    # DriverDeleteView section tests

    def test_driver_delete(self):
        drivers_count_before_delete = Driver.objects.count()
        driver_to_delete = Driver.objects.get(id=2)

        response = self.client.get(
            reverse("taxi:driver-delete", kwargs={"pk": driver_to_delete.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/generic_confirm_delete_form.html")

        response = self.client.post(
            reverse("taxi:driver-delete", kwargs={"pk": driver_to_delete.pk}),
        )

        self.assertTrue(response.status_code, 302)
        self.assertRedirects(response, DRIVER_LIST_VIEW_URL)

        drivers_count_after_delete = Driver.objects.count()

        self.assertEqual(drivers_count_before_delete - 1, drivers_count_after_delete)
