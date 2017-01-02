from django.contrib.auth.models import User

from glaze.tests.base import GlazeTestCase


class ProfileTest(GlazeTestCase):
    def test_makes_user_start_with_profile(self):
        user = User.objects.create_user('currencyfreak')

        self.assertEqual(user.profile.currency, 'USD')
