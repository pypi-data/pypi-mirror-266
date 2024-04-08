import pyodbc

from komodo.shared.utils.lambda_utils import lambda_fetch_secret


# Driver={ODBC Driver 18 for SQL Server};Server=tcp:komodo-test.database.windows.net,1433;Database=komodo-test-db;Uid=komodo-root;Pwd={your_password_here};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;

def get_connection_string():
    return get_connection_string_aurora_local()


def get_connection_string_azure_local():
    server = 'komodo-test.database.windows.net'
    database = 'komodo-test-db'
    username = 'komodo-root'
    password = lambda_fetch_secret("AZURE_SQLSERVER_PASSWORD")
    driver = '{ODBC Driver 18 for SQL Server}'
    return 'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


def get_connection_string_azure_from_lambda():
    server = lambda_fetch_secret("AZURE_SQLSERVER")
    database = lambda_fetch_secret("AZURE_SQLSERVER_DATABASE")
    username = lambda_fetch_secret("AZURE_SQLSERVER_USERNAME")
    password = lambda_fetch_secret("AZURE_SQLSERVER_PASSWORD")
    driver = '{ODBC Driver 18 for SQL Server}'

    return 'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


def get_connection_string_aurora_local():
    server = 'komodo-test-aurora-1.cbwitl5zmxin.us-east-1.rds.amazonaws.com'
    database = 'testdb_100'
    username = 'admin'
    password = lambda_fetch_secret("AURORA_SQLSERVER_PASSWORD")
    driver = '{ODBC Driver 18 for SQL Server}'
    return 'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=yes;Connection Timeout=30;'


def get_connection_string_aurora_from_lambda(database, trust_server_certificate="no"):
    server = lambda_fetch_secret("AURORA_SQLSERVER")
    username = lambda_fetch_secret("AURORA_SQLSERVER_USERNAME")
    password = lambda_fetch_secret("AURORA_SQLSERVER_PASSWORD")
    driver = '{ODBC Driver 18 for SQL Server}'

    return 'DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password + ';Encrypt=yes;TrustServerCertificate=' + trust_server_certificate + ';Connection Timeout=30;'


def get_connection(autocommit=False):
    conn_string = get_connection_string()
    return pyodbc.connect(conn_string, autocommit=autocommit)
