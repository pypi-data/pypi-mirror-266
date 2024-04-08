import random

import sqlalchemy
from clickzetta.client import Client
from clickzetta.table import Table
from clickzetta.enums import LoginParams, QueryApiMethod
from clickzetta.dbapi.connection import Connection
from clickzetta.dbapi.cursor import Cursor
from datetime import datetime


def test_login() -> str:
    login_params = LoginParams("1", "Abc123456", "1")
    test_client = Client(login_params)
    return test_client.token


def test_select_table():
    login_params = LoginParams("1", "Abc123456", "1")
    test_client = Client(login_params)
    table = Table(1, 'default', 'regression_test', 'call_center', '1', 'cz_gp_daily')
    # select_sql = "select * from call_center;"
    # test_client.select_table(table, test_client.token, select_sql)
    test_client.show_table(table, test_client.token)


def test_connection():
    login_params = LoginParams("1", "Abc123456", "1")
    test_client = Client(login_params, '1', 'default', 'regression_test', '1', 'cz_gp_daily')
    connection = Connection(test_client)
    cursor = connection.cursor()
    cursor.execute(operation='select * from call_center;')
    print(cursor.fetchone())
    print(cursor.fetchmany(2))
    print(cursor.fetchall())
    connection.close()


def test_get_table_name_from_select():
    login_params = LoginParams("1", "Abc123456", "1")
    str_1 = '2023-02-05 13:23:44.675'
    print(str_1.replace('-', '').replace(':', '').replace('.', '').replace(' ', '') + str(random.randint(10000, 99999)))
    print((datetime(2023, 3, 20) - datetime(1970, 1, 1)).days)
    date_string = "2023-03-20"
    date_time = datetime.strptime(date_string, '%Y-%m-%d')
    print((date_time - datetime(1970, 1, 1)).days)