from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Manufacturer

MANUFACTURER_LIST_VIEW_URL = reverse("taxi:manufacturer-list")
MANUFACTURER_CREATE_VIEW_URL = reverse("taxi:manufacturer-create")


class PublicManufacturerTest(TestCase):
    def test_login_required(self):
        response = self.client.get(MANUFACTURER_LIST_VIEW_URL)

        self.assertNotEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(MANUFACTURER_LIST_VIEW_URL)
        redirect_url = "/accounts/login/?next=/manufacturers/"

        self.assertRedirects(response, redirect_url)


class PrivateManufacturerTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test_password"
        )
        self.client.force_login(self.user)

        number_of_manufacturers = 3
        for num in range(number_of_manufacturers):
            Manufacturer.objects.create(
                name=f"Manufacturer {num}",
                country=f"Country {num}"
            )

    # ManufacturerListView section tests

    def test_pagination_is_two(self):
        response = self.client.get(MANUFACTURER_LIST_VIEW_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["manufacturer_list"]) == 2)

    def test_list_all_manufacturer_is_displayed(self):
        # Get second page and confirm it has (exactly) remaining 1 items
        response = self.client.get(MANUFACTURER_LIST_VIEW_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["manufacturer_list"]) == 1)

    def test_retrieve_manufacturer(self):
        response = self.client.get(MANUFACTURER_LIST_VIEW_URL)
        manufacturers = Manufacturer.objects.all().order_by("name")[:2]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["manufacturer_list"]),
            list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/manufacturer_list.html")

    # ManufacturerCreateView section tests

    def test_create_manufacturer(self):
        form_data = {
            "name": "Test Manufacturer",
            "country": "Test Country"
        }

        response = self.client.post(MANUFACTURER_CREATE_VIEW_URL, data=form_data)

        self.assertRedirects(response, MANUFACTURER_LIST_VIEW_URL)

        new_manufacturer = Manufacturer.objects.get(name=form_data["name"])

        self.assertEqual(new_manufacturer.name, form_data["name"])
        self.assertEqual(new_manufacturer.country, form_data["country"])

    # ManufacturerUpdateView section tests

    def test_manufacturer_update(self):
        manufacturer_to_update = Manufacturer.objects.get(id=1)

        update_data = {
            "name": "New name",
            "country": "New country"
        }

        response = self.client.get(
            reverse("taxi:manufacturer-update", kwargs={"pk": manufacturer_to_update.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/manufacturer_form.html")

        response = self.client.post(
            reverse("taxi:manufacturer-update", kwargs={"pk": manufacturer_to_update.pk}),
            data=update_data
        )

        self.assertRedirects(response, MANUFACTURER_LIST_VIEW_URL)

        manufacturer_updated = Manufacturer.objects.get(id=1)

        self.assertEqual(manufacturer_updated.name, update_data["name"])
        self.assertEqual(manufacturer_updated.country, update_data["country"])

    # ManufacturerDeleteView section tests

    def test_manufacturer_delete(self):
        manufacturers_count_before_delete = Manufacturer.objects.count()
        manufacturer_to_delete = Manufacturer.objects.get(id=1)

        response = self.client.get(
            reverse("taxi:manufacturer-delete", kwargs={"pk": manufacturer_to_delete.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/generic_confirm_delete_form.html")

        response = self.client.post(
            reverse("taxi:manufacturer-delete", kwargs={"pk": manufacturer_to_delete.pk}),
        )

        self.assertRedirects(response, MANUFACTURER_LIST_VIEW_URL)

        manufacturers_count_after_delete = Manufacturer.objects.count()

        self.assertEqual(manufacturers_count_before_delete-1, manufacturers_count_after_delete)
