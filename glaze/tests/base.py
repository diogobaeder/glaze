from contextlib import contextmanager
from os import makedirs
from os.path import abspath, exists, join
from shutil import copyfile, rmtree

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase


class GlazeTestCase(TestCase):
    LOGIN = False

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_superuser(
            'john', 'john.doe@example.com', 'test123!')
        self.another_user = User.objects.create_user(
            'alice', 'alice@example.com', 'test123!')

        if self.LOGIN:
            self.client.force_login(self.user)

    @contextmanager
    def fixture(self, *parts):
        dst_dir = abspath(join(settings.MEDIA_ROOT, 'fixtures', *parts[:-1]))
        if exists(dst_dir):
            rmtree(dst_dir)
        makedirs(dst_dir, 0o755)
        src = abspath(join(settings.BASE_DIR, 'fixtures', *parts))
        dst = abspath(join(settings.MEDIA_ROOT, 'fixtures', *parts))
        copyfile(src, dst)
        with open(dst, 'rb') as f:
            yield f
