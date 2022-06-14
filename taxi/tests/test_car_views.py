from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from taxi.models import Car, Manufacturer, Driver

CAR_LIST_VIEW_URL = reverse("taxi:car-list")
CAR_CREATE_VIEW_URL = reverse("taxi:car-create")
PAGINATION_STEP = 2


class PublicCarTest(TestCase):
    def test_login_required(self):
        response = self.client.get(CAR_LIST_VIEW_URL)

        self.assertNotEqual(response.status_code, 200)

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(CAR_LIST_VIEW_URL)
        redirect_url = "/accounts/login/?next=/cars/"

        self.assertRedirects(response, redirect_url)


class PrivateCarTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test_user",
            password="test_password"
        )
        self.client.force_login(self.user)

        test_manufacturer = Manufacturer.objects.create(
            name=f"Manufacturer",
            country=f"Country"
        )

        number_of_cars = 3
        for num in range(number_of_cars):
            Car.objects.create(
                model=f"Model {num}",
                manufacturer=test_manufacturer,
            )

    # CarListView section tests

    def test_pagination_is_two(self):
        response = self.client.get(CAR_LIST_VIEW_URL)

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["car_list"]) == PAGINATION_STEP)

    def test_list_all_cars_is_displayed(self):
        # Get second page and confirm it has (exactly) remaining 1 items
        response = self.client.get(CAR_LIST_VIEW_URL + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"])
        self.assertTrue(len(response.context["car_list"]) == 1)

    def test_retrieve_cars(self):
        response = self.client.get(CAR_LIST_VIEW_URL)
        manufacturers = Manufacturer.objects.all()[:PAGINATION_STEP]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["car_list"]),
            list(manufacturers)
        )
        self.assertTemplateUsed(response, "taxi/car_list.html")

    def test_context_data_has_search_form(self):
        response = self.client.get(CAR_LIST_VIEW_URL)

        self.assertTrue(response.context["search_form"])

    def test_search_form(self):
        response1 = self.client.get(CAR_LIST_VIEW_URL + "?model=1")
        cars1 = Car.objects.filter(model__icontains="1")[:PAGINATION_STEP]

        response2 = self.client.get(CAR_LIST_VIEW_URL + "?model=mod")
        cars2 = Car.objects.filter(model__icontains="mod")[:PAGINATION_STEP]

        self.assertEqual(list(response1.context["car_list"]), list(cars1))
        self.assertEqual(list(response2.context["car_list"]), list(cars2))

    # CarCreateView section tests

    def test_create_car(self):
        test_manufacturer = Manufacturer.objects.first()
        test_driver = Driver.objects.first()

        form_data = {
            "model": "RS 5",
            "manufacturer": test_manufacturer.id,
            "drivers": test_driver.id,
        }

        response = self.client.post(CAR_CREATE_VIEW_URL, data=form_data)

        self.assertRedirects(response, CAR_LIST_VIEW_URL)

        new_car = Car.objects.get(model=form_data["model"])

        self.assertEqual(new_car.model, form_data["model"])
        self.assertEqual(new_car.manufacturer.id, form_data["manufacturer"])

    # CarUpdateView section tests

    def test_update_car(self):
        new_driver = Driver.objects.create_user(
            username="test_driver",
            password="test_password",
            license_number="AAA00011"
        )

        new_manufacturer = Manufacturer.objects.create(
            name="New Manufacturer",
            country="Never Land",
        )

        car_to_update = Car.objects.first()

        response = self.client.get(
            reverse("taxi:car-update", kwargs={"pk": car_to_update.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/car_form.html")

        update_data = {
            "model": "Update name",
            "manufacturer": new_manufacturer.id,
            "drivers": new_driver.id,
        }

        response = self.client.post(
            reverse("taxi:car-update", kwargs={"pk": car_to_update.id}),
            data=update_data
        )

        self.assertRedirects(response, CAR_LIST_VIEW_URL)

        car_updated = Car.objects.get(id=car_to_update.id)

        self.assertEqual(car_updated.model, update_data["model"])
        self.assertEqual(car_updated.manufacturer.id, update_data["manufacturer"])

    # CarDeleteView section tests

    def test_car_delete(self):
        cars_count_before_delete = Car.objects.count()
        car_to_delete = Car.objects.first()

        response = self.client.get(
            reverse("taxi:car-delete", kwargs={"pk": car_to_delete.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "taxi/generic_confirm_delete_form.html")

        response = self.client.post(
            reverse("taxi:car-delete", kwargs={"pk": car_to_delete.id}),
        )

        self.assertRedirects(response, CAR_LIST_VIEW_URL)

        cars_count_after_delete = Car.objects.count()

        self.assertEqual(cars_count_before_delete-1, cars_count_after_delete)
