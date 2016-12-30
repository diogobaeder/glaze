from contextlib import contextmanager
from os import makedirs
from os.path import abspath, exists, join
from shutil import copyfile

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from model_mommy import mommy

from recipes.models import Ingredient, Recipe


class RecipeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            'john', 'john.doe@example.com', 'test123!')
        self.another_user = User.objects.create_user(
            'alice', 'alice@example.com', 'test123!')

    def create_ingredient(self, **kwargs) -> Ingredient:
        kwargs.setdefault('user', self.user)
        return mommy.make(Ingredient, **kwargs)

    def create_recipe(self, **kwargs) -> Recipe:
        kwargs.setdefault('user', self.user)
        return mommy.make(Recipe, **kwargs)

    @contextmanager
    def fixture(self, *parts):
        dst_dir = abspath(join(settings.MEDIA_ROOT, 'fixtures', *parts[:-1]))
        if not exists(dst_dir):
            makedirs(dst_dir, 0o755)
        src = abspath(join(settings.BASE_DIR, 'fixtures', *parts))
        dst = abspath(join(settings.MEDIA_ROOT, 'fixtures', *parts))
        copyfile(src, dst)
        with open(dst, 'rb') as f:
            yield f
