import keyring
from wfcli import WebFactionAPI, WebfactionWebsiteToSsl

from glaze import prod_settings


USERNAME = 'diogobaeder'
SERVICE = 'webfaction'
DB_USER = prod_settings.DATABASES['default']['USER']
DB_PASS = prod_settings.DATABASES['default']['PASSWORD']
DB_NAME = prod_settings.DATABASES['default']['NAME']


client = None


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


def get_client() -> WebFactionAPI:
    global client

    if client is None:
        password = keyring.get_password(SERVICE, USERNAME)
        client = AutoWebFactionClient(username=USERNAME, password=password)
        client.connect()

    return client


def create_db():
    client = get_client()
    if not any(db['name'] == DB_NAME for db in client.list_dbs()):
        client.create_db_user(DB_USER, DB_PASS, prod_settings.DB_TYPE)
        client.create_db(DB_NAME, prod_settings.DB_TYPE, DB_PASS, DB_USER)
