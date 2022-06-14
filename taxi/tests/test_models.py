from django.contrib.auth import get_user_model
from django.test import TestCase

from taxi.models import Car, Manufacturer, Driver

# Manufacturer consts
MANUFACTURER_MODEL_LABELS = ("name", "country", )
MANUFACTURER_NAME_MAX_LENGTH = 30
MANUFACTURER_COUNTRY_MAX_LENGTH = 60

# Car consts
CAR_MODEL_LABELS = ("model", "manufacturer", "drivers")
CAR_MODEL_MAX_LENGTH = 30

# Driver consts
DRIVER_LICENSE_NUMBER_MAX_LENGTH = 8


class ManufacturerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Manufacturer.objects.create(
            name="Sherp",
            country="Ukraine"
        )

    def test_field_labels(self):
        manufacturer = Manufacturer.objects.get(id=1)

        field_labels = tuple(
            manufacturer._meta.get_field(field).verbose_name
            for field in MANUFACTURER_MODEL_LABELS
        )

        self.assertEquals(MANUFACTURER_MODEL_LABELS, field_labels)

    def test_name_max_length(self):
        manufacturer = Manufacturer.objects.get(id=1)

        max_length = manufacturer._meta.get_field("name").max_length

        self.assertEquals(MANUFACTURER_NAME_MAX_LENGTH, max_length)

    def test_country_max_length(self):
        manufacturer = Manufacturer.objects.get(id=1)

        max_length = manufacturer._meta.get_field("country").max_length

        self.assertEquals(MANUFACTURER_COUNTRY_MAX_LENGTH, max_length)

    def test_manufacturer_ordering_by_name(self):
        manufacturer = Manufacturer.objects.get(id=1)

        ordering = manufacturer._meta.ordering

        self.assertEquals("name", ordering[0])

    def test_manufacturer_model_str(self):
        manufacturer = Manufacturer.objects.get(id=1)

        self.assertEqual(f"{manufacturer.name} {manufacturer.country}", str(manufacturer))


class CarModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        manufacturer = Manufacturer.objects.create(
            name="Audi",
            country="Germany",
        )

        Car.objects.create(
            model="A4",
            manufacturer=manufacturer,
        )

    def test_field_labels(self):
        car = Car.objects.get(id=1)

        field_labels = tuple(
            car._meta.get_field(field).verbose_name
            for field in CAR_MODEL_LABELS
        )

        self.assertEquals(CAR_MODEL_LABELS, field_labels)

    def test_car_model_max_length(self):
        car = Car.objects.get(id=1)

        max_length = car._meta.get_field("model").max_length

        self.assertEqual(CAR_MODEL_MAX_LENGTH, max_length)

    def test_car_drivers_related_name(self):
        car = Car.objects.get(id=1)

        related_name = car._meta.get_field("drivers")._related_name

        self.assertEqual("cars", related_name)

    def test_car_ordering_by_model(self):
        car = Car.objects.get(id=1)

        ordering = car._meta.ordering

        self.assertEquals("model", ordering[0])

    def test_car_model_str(self):
        car = Car.objects.get(id=1)

        self.assertEqual(f"{car.manufacturer.name} {car.model}", str(car))


class DriverModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        username = "user1"
        password = "test pass"
        get_user_model().objects.create_user(
            username=username,
            password=password,
        )

    def test_license_number_labels(self):
        driver = Driver.objects.get(id=1)

        field_label = driver._meta.get_field("license_number").verbose_name

        self.assertEqual("license number", field_label)

    def test_create_driver_with_license_number(self):
        username = "user2"
        password = "test pass"
        license_number = "ABC02312"
        driver = get_user_model().objects.create_user(
            username=username,
            password=password,
            license_number=license_number,
        )

        self.assertEqual(username, driver.username)
        self.assertTrue(password, driver.check_password(password))
        self.assertEqual(license_number, driver.license_number)

    def test_license_number_is_unique(self):
        driver = get_user_model()

        unique = driver._meta.get_field("license_number").unique

        self.assertTrue(unique)

    def test_ordering_by_username(self):
        driver = get_user_model()

        ordering = driver._meta.ordering
        self.assertEqual("username", ordering[0])

    def test_verbose_name_and_verbose_name_plural(self):
        driver = get_user_model()

        verbose_name = driver._meta.verbose_name
        verbose_name_plural = driver._meta.verbose_name_plural

        self.assertEqual("driver", verbose_name)
        self.assertEqual("drivers", verbose_name_plural)

    def test_license_number_max_length(self):
        driver = get_user_model()

        max_length = driver._meta.get_field("license_number").max_length

        self.assertEqual(DRIVER_LICENSE_NUMBER_MAX_LENGTH, max_length)

    def test_get_absolute_url(self):
        driver = get_user_model().objects.get(id=1)

        self.assertEqual("/drivers/1/", driver.get_absolute_url())

    def test_driver_model_str(self):
        driver = get_user_model().objects.get(id=1)

        self.assertEqual(
            f"{driver.username} ({driver.first_name} {driver.last_name})",
            str(driver)
        )
