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

from os.path import expanduser, join
from uuid import uuid4

import keyring
from fabric import colors
from fabric.api import (
    cd, env, prefix, put, run, shell_env, task, warn_only
)
from fabric.contrib.files import upload_template
from wfcli import WebFactionAPI, WebfactionWebsiteToSsl

from glaze import prod_settings


env.use_ssh_config = True
env.hosts = ['webfaction']
env.python_version = '3.5'
env.project = 'glaze'
env.parent_domain = 'diogobaeder.com.br'
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
env.load_users = True
env.statics = ['static', 'upload']


def info(*texts):
    text = ' '.join(texts)
    print(colors.magenta(text))


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
    def __init__(self):
        self.client = self._create_client()

    def _create_client(self) -> WebFactionClient:
        client = WebFactionClient(
            username=env.user, password=env.password)
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

    @property
    def git(self):
        return Git(self.client)

    @property
    def project(self):
        return Project(self.client)

    @property
    def cache(self):
        return Cache(self.client)


class Component:
    def __init__(self, client: WebFactionClient):
        self.client = client


class Domain(Component):
    def prepare(self):
        self.client.create_domain(env.parent_domain, [env.project])


class Database(Component):
    def prepare(self):
        if not self._has_user(env.db_user):
            self.client.create_db_user(env.db_user, env.db_pass, env.db_type)
        if not self._has_db(env.db_name):
            self.client.create_db(
                env.db_name, env.db_type, env.db_pass, env.db_user)

    def _has_user(self, user):
        return any(
            db['username'] == user for db in self.client.list_db_users())

    def _has_db(self, name):
        return any(db['name'] == name for db in self.client.list_dbs())


class Applications(Component):
    def prepare(self):
        self.create_app('git', 'git')
        run('mkdir -p {}'.format(join(env.home_dir, 'bin')))
        run('mkdir -p {}'.format(join(env.home_dir, 'tmp')))
        run('easy_install-{} --upgrade pip'.format(env.python_version))
        self.install('virtualenv', 'virtualenvwrapper', 'circus')
        app = self.create_app(env.project, 'custom_app_with_port')
        for static in env.statics:
            self.create_static(static)

    def create_static(self, static_name):
        path = join(env.project_dir, static_name)
        run('mkdir -p {}'.format(path))
        self.create_app(
            '{}_{}'.format(env.project, static_name), 'symlink_static_only',
            path)

    def install(self, *packages):
        run('pip{} install --user -U {}'.format(
            env.python_version, ' '.join(packages)))

    def create_app(self, app_name, app_type, extra_info=''):
        info('creating app', app_name)
        if app_name not in self.client.list_apps():
            return self.client.create_app(
                app_name, app_type, extra_info=extra_info)


class SSH(Component):
    def ensure_authorized_key(self):
        info('ensuring authorized key is set')
        with open(env.key_filename, encoding='utf-8') as f:
            key = f.read().strip()

        path = '/tmp/{}'.format(uuid4())
        self.client.write_file(path, key, 'w')
        self.client.command('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        self.client.command((
            'grep -a "`cat {0}`" ~/.ssh/authorized_keys || '
            'echo "\n`cat {0}`\n" >> ~/.ssh/authorized_keys'
        ).format(path))
        self.client.command('rm {}'.format(path))


class Git(Component):
    def prepare(self):
        if not self._has_working_tree():
            self.git(
                'init .',
                'remote add origin {}'.format(env.repository),
            )
        self.git(
            'fetch origin',
            'reset --hard origin/master',
        )

    def git(self, *commands):
        with cd(env.project_dir):
            for command in commands:
                run('git {}'.format(command))

    def _has_working_tree(self):
        with cd(env.project_dir), warn_only():
            result = run('test -d .git')
        return not result.failed


class Project(Component):
    def prepare(self):
        if not self._has_virtualenv():
            self._create_virtualenv()

        with shell_env(TMPDIR='~/tmp'):
            self.env_run('.env/bin/pip install -r requirements.txt')

        self._setup_django()
        port = self.client.list_apps()[env.project]['port']
        upload_template(
            'server.cfg.template', join(env.project_dir, 'server.cfg'), env)

    def _setup_django(self):
        settings_module_path = '{}.py'.format(
            env.django_settings_module.replace('.', '/'))
        put(settings_module_path,
            join(env.project_dir, settings_module_path))
        self.manage('migrate')
        self.manage('collectstatic --noinput')
        if env.load_users:
            self.manage('loaddata users.json')

    def _create_virtualenv(self):
        with cd(env.project_dir):
            run('virtualenv .env')

    def manage(self, command):
        with shell_env(DJANGO_SETTINGS_MODULE=env.django_settings_module):
            self.env_run('.env/bin/python manage.py {}'.format(command))

    def env_run(self, command):
        with cd(env.project_dir), prefix('source .env/bin/activate'):
            run(command)

    def _has_virtualenv(self):
        with cd(env.project_dir), warn_only():
            result = run('test -d .env')
        return not result.failed


class Cache(Component):
    COMMAND = (
        'memcached -d -m 50 -s $HOME/memcached.sock -P $HOME/memcached.pid')

    def prepare(self):
        self.client.create_cronjob('@reboot {}'.format(self.COMMAND))
        self.start()

    def start(self):
        if not run('pgrep memcached').strip():
            run(self.COMMAND)


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

    step('preparing website')
    maestro.project.prepare()

    success('website created!')
