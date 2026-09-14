from django.test import SimpleTestCase

from modules.userdata.domains.profile import ProfileDomain
from modules.userdata.serializers.profile import ProfileSerializer


class TestProfileModoOn(SimpleTestCase):
    def test_domain_defaults_to_off(self):
        profile = ProfileDomain()

        self.assertFalse(profile.modo_on)

    def test_domain_update_sets_modo_on(self):
        profile = ProfileDomain()
        profile.update({"modo_on": True})

        self.assertTrue(profile.modo_on)

    def test_serializer_includes_modo_on(self):
        profile = ProfileDomain(modo_on=True)

        serialized = ProfileSerializer().serialize(profile)

        self.assertIs(serialized["modo_on"], True)

    def test_domain_update_sets_salary_day(self):
        profile = ProfileDomain()
        profile.update({"salary_day": 5})

        self.assertEqual(profile.salary_day, 5)

    def test_serializer_includes_salary_day(self):
        profile = ProfileDomain(salary_day=5)

        serialized = ProfileSerializer().serialize(profile)

        self.assertEqual(serialized["salary_day"], 5)
