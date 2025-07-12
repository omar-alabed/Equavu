import pymysql
import os
import sys

db_name = os.environ.get('DB_NAME', 'equavu_hr')
db_user = os.environ.get('DB_USER', 'root')
db_password = os.environ.get('DB_PASSWORD', 'root')
db_host = os.environ.get('DB_HOST', 'localhost')
db_port = int(os.environ.get('DB_PORT', '3306'))

try:
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        port=db_port,
        autocommit=True
    )
    with connection.cursor() as cursor:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        )
    print(f"Database `{db_name}` ensured.")
except Exception as e:
    print(f"Error creating database: {e}")
    sys.exit(1)
finally:
    if 'connection' in locals():
        connection.close()
