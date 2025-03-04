import mysql.connector
from mysql.connector import Error

def create_connection():
    """ MySQL 데이터베이스와 연결을 생성하는 함수 """
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='server',
            password='dltmxm1234',
            database='dataset'
        )
        if connection.is_connected():
            print("MySQL 데이터베이스에 연결되었습니다.")
    except Error as e:
        print(f"연결 실패: {e}")
    return connection
