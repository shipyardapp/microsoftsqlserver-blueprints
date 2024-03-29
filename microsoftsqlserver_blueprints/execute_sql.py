import argparse
import os
from sqlalchemy import create_engine, text


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', dest='username', required=False)
    parser.add_argument('--password', dest='password', required=False)
    parser.add_argument('--host', dest='host', required=False)
    parser.add_argument('--database',
                        dest='database', required=False)
    parser.add_argument('--port', dest='port', default='1433', required=False)
    parser.add_argument('--url-parameters',
                        dest='url_parameters', required=False)
    parser.add_argument('--query', dest='query', required=True)
    parser.add_argument(
        '--db-connection-url',
        dest='db_connection_url',
        required=False)
    args = parser.parse_args()

    if not args.db_connection_url and not (
            args.host or args.database or args.username) and not os.environ.get('DB_CONNECTION_URL'):
        parser.error(
            """This Blueprint requires at least one of the following to be provided:\n
            1) --db-connection-url\n
            2) --host, --database, and --username\n
            3) DB_CONNECTION_URL set as environment variable""")
    if args.host and not (args.database or args.username):
        parser.error(
            '--host requires --database and --username')
    if args.database and not (args.host or args.username):
        parser.error(
            '--database requires --host and --username')
    if args.username and not (args.host or args.username):
        parser.error(
            '--username requires --host and --username')
    return args


def create_connection_string(args):
    """
    Set the database connection string as an environment variable using the keyword arguments provided.
    This will override system defaults.
    """
    if args.db_connection_url:
        os.environ['DB_CONNECTION_URL'] = args.db_connection_url
    elif (args.host and args.username and args.database):
        os.environ['DB_CONNECTION_URL'] = f'mssql+pyodbc://{args.username}:{args.password}@{args.host}:{args.port}/{args.database}?driver=ODBC+Driver+17+for+SQL+Server&{args.url_parameters}'

    db_string = os.environ.get('DB_CONNECTION_URL')
    return db_string


def main():
    args = get_args()
    query = text(args.query)

    db_string = create_connection_string(args)
    try:
        db_connection = create_engine(db_string)
    except Exception as e:
        print(f'Failed to connect to database {args.database}')
        raise(e)

    db_connection.execute(query)
    print('Your query has been successfully executed.')
    db_connection.dispose()


if __name__ == '__main__':
    main()
