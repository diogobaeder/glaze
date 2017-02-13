import os
from os.path import join
from uuid import uuid4

import keyring
from fabric import colors
from fabric.api import (
    cd, env, local, prefix, put, run, shell_env, task, warn_only
)
from fabric.contrib.files import upload_template, exists
from wfcli import WebFactionAPI, WebfactionWebsiteToSsl

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


os.environ['WEBFACTION_USER'] = env.user
os.environ['WEBFACTION_PASS'] = env.password


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

    @property
    def website(self):
        return Website(self.client)


class Component:
    def __init__(self, client: WebFactionClient):
        self.client = client

    def add_on_reboot(self, command):
        boot = '@reboot {}'.format(command)
        if boot not in run('crontab -l'):
            self.client.create_cronjob(boot)

    def is_running(self, program):
        with warn_only():
            result = run('pgrep {}'.format(program))
        if result.failed:
            return False
        return bool(result.strip())

    def all_subdomains(self):
        return [env.project] + self.static_subdomains()

    def static_subdomains(self):
        return [
            '{}{}'.format(env.project, static)
            for static in env.statics
        ]


class Domain(Component):
    def prepare(self):
        self.client.create_domain(env.parent_domain, self.all_subdomains())


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
        if not exists('~/.acme.sh'):
            run('curl https://get.acme.sh | sh')
        run('~/.acme.sh/acme.sh --upgrade')
        run('mkdir -p {}'.format(join(env.home_dir, 'bin')))
        run('mkdir -p {}'.format(join(env.home_dir, 'tmp')))
        run('easy_install-{} --upgrade pip'.format(env.python_version))
        self.install('virtualenv', 'virtualenvwrapper', 'circus', 'circus-web')
        self.create_app(env.project, 'custom_app_with_port')
        for static in env.statics:
            self.create_static(static)

    def create_static(self, static_name):
        path = join(env.project_dir, static_name)
        run('mkdir -p {}'.format(path))
        self.create_app(
            '{}{}'.format(env.project, static_name), 'symlink_static_only',
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
        self.fetch_latest()

    def fetch_latest(self):
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

        self.update_files_and_data()
        env.server_port = self.client.list_apps()[env.project]['port']
        upload_template(
            'server.cfg.template', join(env.project_dir, 'server.cfg'), env)

    def update_files_and_data(self):
        with shell_env(TMPDIR='~/tmp'):
            self.env_run('.env/bin/pip install -r requirements.txt')
        settings_module_path = '{}.py'.format(
            env.django_settings_module.replace('.', '/'))
        put(settings_module_path,
            join(env.project_dir, settings_module_path))
        self.manage('migrate')
        self.manage('collectstatic --noinput')
        self.manage('compilemessages')

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


class Website(Component):
    COMMAND = 'cd {} && circusd --daemon server.cfg'.format(env.project_dir)

    def prepare(self):
        for d in self.all_subdomains():
            self.create_website(d)

        self.add_on_reboot(self.COMMAND)
        if not self.is_running('circusd'):
            run(self.COMMAND)
        else:
            self.reload_config()

    def reload_config(self):
        with cd(env.project_dir):
            run('circusctl reloadconfig')

    def reload(self):
        with cd(env.project_dir):
            run('circusctl reload')

    def create_website(self, subdomain):
        info('creating website for:', subdomain)
        domain = '{}.{}'.format(subdomain, env.parent_domain)
        websites = [w['name'] for w in self.client.list_websites()]
        if subdomain not in websites:
            self.client.create_website(
                subdomain, env.ip, False, [domain], apps=(
                    [subdomain, '/'],
                ))
            if env.https:
                info('securing domain:', domain)
                ssl = WebfactionWebsiteToSsl(env.hosts[0])
                ssl.secure(domain, False)


class Cache(Component):
    COMMAND = (
        'memcached -d -m 50 -s $HOME/memcached.sock -P $HOME/memcached.pid')

    def prepare(self):
        self.add_on_reboot(self.COMMAND)
        self.start()

    def start(self):
        if not self.is_running('memcached'):
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
