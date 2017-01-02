from glaze.tests.base import GlazeTestCase


class ProfileViewTest(GlazeTestCase):
    LOGIN = True

    def test_loads_profile_detail(self):
        response = self.client.get('/accounts/profile/')

        self.assertContains(response, self.user.profile.currency)


class ProfileUpdateTest(GlazeTestCase):
    LOGIN = True

    def test_loads_profile_edit_page(self):
        response = self.client.get('/accounts/profile/update/')

        self.assertContains(response, 'form')
        self.assertContains(response, self.user.profile.currency)

    def test_updates_profile(self):
        self.client.post('/accounts/profile/update/', {
            'currency': 'Whatup',
        })

        self.assertEqual(self.get_user().profile.currency, 'Whatup')
