import random

from komodo.shared.mssql.mssql import get_connection


def test_mssql():
    list_databases()
    list_tables()

    id = random.randint(10000, 99999)
    table_name = 'testtable_{}'.format(id)
    create_table(table_name)
    list_tables()

    insert_data(table_name)
    select_data(table_name)

    update_data(table_name)
    select_data(table_name)

    delete_data(table_name)
    select_data(table_name)

    drop_table(table_name)

    list_tables()


def create_database(db_name):
    with get_connection(autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE DATABASE {};".format(db_name))
            print('{} database is created.'.format(db_name))
            print('Done')


def list_databases():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT name, collation_name FROM sys.databases")
            row = cursor.fetchone()
            while row:
                print(str(row[0]) + " " + str(row[1]))
                row = cursor.fetchone()


def create_table(table_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("CREATE TABLE {} (id int, name varchar(255));".format(table_name))
            print('{} table is created.'.format(table_name))
            print('Done')


def list_tables():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
            row = cursor.fetchone()
            while row:
                print(str(row[0]))
                row = cursor.fetchone()


def insert_data(table_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO {} VALUES (1, 'test');".format(table_name))
            print('Data inserted.')
            print('Done')


def select_data(table_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM {};".format(table_name))
            row = cursor.fetchone()
            while row:
                print(str(row[0]) + " " + str(row[1]))
                row = cursor.fetchone()
            print('Done')


def update_data(table_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE {} SET name = 'test2' WHERE id = 1;".format(table_name))
            print('Data updated.')
            print('Done')


def delete_data(table_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM {} WHERE id = 1;".format(table_name))
            print('Data deleted.')
            print('Done')


def drop_table(table_name):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DROP TABLE {};".format(table_name))
            print('Table dropped.')
            print('Done')
