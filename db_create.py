# 처음 테이블 생성하기 위한 코드

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

def create_table():
    """ product_list 테이블을 생성하는 함수 """
    connection = create_connection()
    cursor = connection.cursor()
    
    sql = """
CREATE TABLE barcode_data (
    id INT,
    `date` DATE,
    `time` TIME,
    mc_code VARCHAR(50),
    lot_code VARCHAR(50),
    contents1 VARCHAR(50)
);

    """

    try:
        cursor.execute(sql)
        print("테이블이 생성되었습니다.")
    except Error as e:
        print(f"테이블 생성 실패: {e}")
    finally:
        cursor.close()
        if connection.is_connected():
            connection.close()

if __name__ == "__main__":
    create_table()
