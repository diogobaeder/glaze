import keyring
from wfcli import WebFactionAPI, WebfactionWebsiteToSsl

from glaze import prod_settings


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
        method = getattr(self.server, self.method_name)
        return method(self.session_id, *args)


class AutoWebFactionClient(WebFactionAPI):
    def __getattr__(self, method_name):
        self.connect()
        return Caller(self.server, self.session_id, method_name)


class Maestro:
    def __init__(self, service, username, password):
        self.service = service
        self.username = username
        self.password = password
        self.client = self._create_client()

    def _create_client(self) -> AutoWebFactionClient:
        client = AutoWebFactionClient(
            username=self.username, password=self.password)
        client.connect()

        return client

    @property
    def db(self):
        return Database(self.client)


class Database:
    def __init__(self, client: AutoWebFactionClient):
        self.client = client

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


def create_website():
    password = keyring.get_password(SERVICE, USERNAME)
    maestro = Maestro(SERVICE, USERNAME, password)

    maestro.db.create_db(DB_NAME, DB_TYPE, DB_USER, DB_PASS)
