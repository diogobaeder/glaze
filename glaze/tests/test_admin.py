from glaze.tests.base import GlazeTestCase


class AdminTest(GlazeTestCase):
    LOGIN = True

    def test_shows_profiles(self):
        response = self.client.get('/admin/glaze/profile/')

        self.assertContains(response, self.user)
        self.assertContains(response, self.user.profile.currency)
