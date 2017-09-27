import os
from os.path import join

import keyring
from diogobaeder.webfaction.tools import Maestro
from fabric import colors
from fabric.api import (
    env,
    local,
    task,
)

from glaze import prod_settings


env.use_ssh_config = True
env.hosts = ['webfaction']
env.ip = '207.38.86.14'
env.python_version = '3.5'
env.project = 'glaze'
env.parent_domain = 'diogobaeder.com.br'
env.statics = ['static', 'uploads']
env.subdomains = [env.project] + [
    '{}{}'.format(env.project, static)
    for static in env.statics
]
env.user = 'diogobaeder'
env.password = keyring.get_password('webfaction', env.user)
env.db_user = prod_settings.DATABASES['default']['USER']
env.db_pass = prod_settings.DATABASES['default']['PASSWORD']
env.db_name = prod_settings.DATABASES['default']['NAME']
env.db_type = 'postgresql'
env.home_dir = '/home/diogobaeder'
env.key_filename = '/home/diogobaeder/.ssh/id_rsa.pub'
env.webapps = '/home/diogobaeder/webapps'
env.repository = 'git@github.com:diogobaeder/glaze.git'
env.project_dir = join(env.webapps, env.project)
env.django_settings_module = 'glaze.prod_settings'
env.server_processes = 5
env.server_port = None
env.https = True
env.logoutput = join(
    env.home_dir, 'logs', 'user', '{}.log'.format(env.project))
env.socat_version = '1.7.3.2'


os.environ['WEBFACTION_USER'] = env.user
os.environ['WEBFACTION_PASS'] = env.password


def step(*texts):
    text = ' '.join(texts)
    print(colors.blue(text, True))


def success(*texts):
    text = ' '.join(texts)
    print(colors.green(text, True))


@task
def create_website():
    maestro = Maestro()

    step('adjusting for SSH')
    maestro.ssh.ensure_authorized_key()

    step('creating domain')
    maestro.domain.prepare()

    step('creating database')
    maestro.db.prepare()

    step('creating foundation applications')
    maestro.apps.prepare()

    step('preparing working tree')
    maestro.git.prepare()

    step('preparing cache')
    maestro.cache.prepare()

    step('preparing project')
    maestro.project.prepare()

    step('preparing website')
    maestro.website.prepare()

    success('website created!')


@task
def deploy():
    maestro = Maestro()

    step('fetching changes')
    local('git ps')
    maestro.git.fetch_latest()

    step('updating dependencies, files and data')
    maestro.project.update_files_and_data()

    step('reloading server')
    maestro.website.reload()


@task
def load_data(fixture_file):
    maestro = Maestro()

    step('loading data:', fixture_file)
    maestro.project.manage('loaddata {}'.format(fixture_file))
