from django.test import TestCase
from taxi.forms import DriverUserCreationForm, DriverLicenseUpdateForm, CarSearchForm
from taxi.models import Driver


class DriverUserCreationFormTest(TestCase):
    def test_driver_creation_with_license_number_is_valid(self):
        form_data = {
            "username": "user",
            "license_number": "AAA00000",
            "first_name": "FirstName",
            "last_name": "Name",
            "password1": "tA4gQKZq",
            "password2": "tA4gQKZq",
        }

        form = DriverUserCreationForm(data=form_data)

        self.assertTrue(form.is_valid())
        self.assertEqual(form_data, form.cleaned_data)


class DriverLicenseUpdateFormTest(TestCase):
    def test_model_is_correct(self):
        form_license_data = {"license_number": "AAA00012"}
        correct_model = Driver
        form = DriverLicenseUpdateForm(data=form_license_data)
        test_model = form._meta.model

        self.assertEqual(correct_model, test_model)

    def test_license_number_validation_ok(self):
        form_license_data = {"license_number": "AAA00012"}
        form = DriverLicenseUpdateForm(data=form_license_data)

        self.assertTrue(form.is_valid())

    def test_license_number_validation_failed_with_message(self):
        invalid_license_data = {"license_number": "AAfs0012"}
        expected_error_message = "Enter correct value like AAA00000"

        form_with_invalid_data = DriverLicenseUpdateForm(data=invalid_license_data)
        form_error_message = form_with_invalid_data.errors.as_data().get("license_number")[0].message

        self.assertFalse(form_with_invalid_data.is_valid())
        self.assertTrue(form_with_invalid_data.errors)
        self.assertEqual(expected_error_message, form_error_message)

    def test_license_number_update(self):
        correct_license_data = {"license_number": "ABC01234"}
        form_with_correct_license_date = DriverLicenseUpdateForm(data=correct_license_data)

        invalid_license_data = {"license_number": "ABcd324233"}
        form_with_invalid_data = DriverLicenseUpdateForm(data=invalid_license_data)

        self.assertTrue(form_with_correct_license_date.is_valid())
        self.assertEqual(form_with_correct_license_date.cleaned_data, correct_license_data)

        self.assertFalse(form_with_invalid_data.is_valid())
        self.assertNotEqual(form_with_invalid_data.cleaned_data, invalid_license_data)


class CarSearchFormTest(TestCase):
    def test_max_field_length_is_thirty(self):
        pass
