"""
What to install/configure:
- Domain
- Postgres
- Git
- Website:
  Download
  Python dependencies
  Migrate database
  Collect static
- Static app
- Circus
  Memcache
  Website

"""

from os.path import expanduser
from uuid import uuid4

import keyring
from fabric import colors
from fabric.api import task, run
from wfcli import WebFactionAPI, WebfactionWebsiteToSsl

from glaze import prod_settings


PYTHON_VERSION = '3.5'
PROJECT_NAME = 'glaze'
PARENT_DOMAIN = 'diogobaeder.com.br'
USERNAME = 'diogobaeder'
SERVICE = 'webfaction'
DB_USER = prod_settings.DATABASES['default']['USER']
DB_PASS = prod_settings.DATABASES['default']['PASSWORD']
DB_NAME = prod_settings.DATABASES['default']['NAME']
DB_TYPE = 'postgresql'


class Caller:
    def __init__(self, server, session_id, method_name):
        self.server = server
        self.session_id = session_id
        self.method_name = method_name

    def __call__(self, *args):
        info('xmlrpc:', self.method_name)
        method = getattr(self.server, self.method_name)
        return method(self.session_id, *args)


class WebFactionClient(WebFactionAPI):
    def __getattr__(self, method_name):
        self.connect()
        return Caller(self.server, self.session_id, method_name)

    def command(self, command):
        print(command)
        return self.system(command)


class Maestro:
    def __init__(self, service, username, password):
        self.service = service
        self.username = username
        self.password = password
        self.client = self._create_client()

    def _create_client(self) -> WebFactionClient:
        client = WebFactionClient(
            username=self.username, password=self.password)
        client.connect()

        return client

    @property
    def domain(self):
        return Domain(self.client)

    @property
    def db(self):
        return Database(self.client)

    @property
    def apps(self):
        return Applications(self.client)

    @property
    def ssh(self):
        return SSH(self.client)


class Component:
    def __init__(self, client: WebFactionClient):
        self.client = client


class Domain(Component):
    def create_domain(self, domain, subdomain):
        self.client.create_domain(domain, [subdomain])


class Database(Component):
    def create_db(self, name, db_type, user, password):
        if not self._has_user(user):
            self.client.create_db_user(user, password, db_type)
        if not self._has_db(name):
            self.client.create_db(name, db_type, password, user)

    def _has_user(self, user):
        return any(
            db['username'] == user for db in self.client.list_db_users())

    def _has_db(self, name):
        return any(db['name'] == name for db in self.client.list_dbs())


class Applications(Component):
    def prepare_apps(self):
        self.create_app('git', 'git')
        self.client.command(
            'easy_install-{} --upgrade pip'.format(PYTHON_VERSION))
        self.pip('virtualenv', 'virtualenvwrapper', 'circus', 'chaussette')

    def pip(self, *packages):
        self.client.command('pip{} install --user {}'.format(
            PYTHON_VERSION, ' '.join(packages)))

    def create_app(self, app_name, app_type):
        info('creating app', app_name)
        if app_name not in self.client.list_apps():
            self.client.create_app(app_name, app_type)


class SSH(Component):
    def ensure_authorized_key(self, public_key_path):
        info('ensuring authorized key is set')
        with open(public_key_path, encoding='utf-8') as f:
            key = f.read().strip()

        path = '/tmp/{}'.format(uuid4())
        self.client.write_file(path, key, 'w')
        self.client.command('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        self.client.command((
            'grep -a "`cat {0}`" ~/.ssh/authorized_keys || '
            'echo "\n`cat {0}`\n" >> ~/.ssh/authorized_keys'
        ).format(path))
        self.client.command('rm {}'.format(path))


def step(*texts):
    text = ' '.join(texts)
    print(colors.blue(text, True))


def info(*texts):
    text = ' '.join(texts)
    print(colors.magenta(text))


def success(*texts):
    text = ' '.join(texts)
    print(colors.green(text, True))


@task
def create_website():
    password = keyring.get_password(SERVICE, USERNAME)
    maestro = Maestro(SERVICE, USERNAME, password)

    step('creating domain')
    maestro.domain.create_domain(PARENT_DOMAIN, PROJECT_NAME)

    step('creating database')
    maestro.db.create_db(DB_NAME, DB_TYPE, DB_USER, DB_PASS)

    step('adjusting for SSH')
    maestro.ssh.ensure_authorized_key(expanduser('~/.ssh/id_rsa.pub'))

    step('creating foundation applications')
    maestro.apps.prepare_apps()

    success('website created!')
