from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import ctypes
import mysql.connector

app = Flask(__name__)
CORS(app)

# 창 설정
kernel32 = ctypes.WinDLL("kernel32")
user32 = ctypes.WinDLL("user32")
hWnd = kernel32.GetConsoleWindow()
user32.MoveWindow(hWnd, 1100, 400, 800, 300, True)

# 데이터베이스 연결 설정
db_config = {
    'user': 'server',
    'password': 'dltmxm1234',
    'host': 'localhost',
    'database': 'dataset'
}

def get_code_from_db(third_value, data2, data10):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # id 범위 설정
        id_range = None
        if data10.startswith("ST1"):
            id_range = (1, 32)
        elif data10.startswith("ST2"):
            id_range = (33, 64)
        elif data10.startswith("ST3"):
            id_range = (65, 96)
        elif data10.startswith("ST4"):
            id_range = (97, 128)
        else:
            return None, None

        if third_value == '3':
            query = "SELECT lh_code, id FROM index_code WHERE lh_code = %s AND id BETWEEN %s AND %s"
        elif third_value == '4':
            query = "SELECT rh_code, id FROM index_code WHERE rh_code = %s AND id BETWEEN %s AND %s"
        else:
            return None, None

        print(f"Executing query: {query}, with data: {data2}, id range: {id_range}")
        cursor.execute(query, (data2, id_range[0], id_range[1]))
        result = cursor.fetchone()
        
        return result if result else (None, None)
    except Exception as e:
        print(f"Database Error: {str(e)}")
        return None, None
    finally:
        cursor.close()
        conn.close()

def update_count_in_db(third_value, found_code, data10):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # id 범위 설정
        id_range = None
        if data10.startswith("ST1"):
            id_range = (1, 32)
        elif data10.startswith("ST2"):
            id_range = (33, 64)
        elif data10.startswith("ST3"):
            id_range = (65, 96)
        elif data10.startswith("ST4"):
            id_range = (97, 128)
        else:
            return None

        if third_value == '3':
            update_query = "UPDATE index_code SET lh_count = CAST(lh_count AS UNSIGNED) + 1 WHERE lh_code = %s AND id BETWEEN %s AND %s"
        elif third_value == '4':
            update_query = "UPDATE index_code SET rh_count = CAST(rh_count AS UNSIGNED) + 1 WHERE rh_code = %s AND id BETWEEN %s AND %s"
        else:
            return None

        cursor.execute(update_query, (found_code, id_range[0], id_range[1]))
        conn.commit()  # 변경사항 커밋
        
        # 영향을 받은 행 수 확인
        if cursor.rowcount == 0:
            print("No rows updated.")
    except Exception as e:
        print(f"Database Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.route('/print', methods=['POST'])
def print_label():
    try:
        data = request.get_json()

        if data is None:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        data2 = data['data2']
        data2_value = data['data2']
        if len(data2_value) > 5:
            data2_value = data2_value[:5] + "-" + data2_value[5:]

        data5_value = data['data5'][2:].replace("-", "")
        data10 = data['data10']  # data10 값 가져오기

        # ZPL 코드 생성
        zpl_code = f"""
        ^XA
        ^CF0,20
        ^FO145,20^A0N,40,32^FD {data2_value} ^FS
        ^FO145,65^A0N,20,22^FD  ^FS
        ^FO145,95^A0N,25,23^FD {data5_value}{str(int(data['data8'])).zfill(4)}   ST{data10} ^FS
        ^FO145,125^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DV{data['data1']}_1DP{data['data2']}_1DS{data['data3']}_1DE{data['data4']}_1DT{data5_value}{data['data6']}{data['data7']}{str(int(data['data8'])).zfill(7)}_1DA_1DC{data['data9']}_1D_1E_04^FS     
        ^XZ
        """

        # 소켓 연결 및 데이터 전송
        data11 = data['data11']  # data11 값 가져오기

        # host 설정
        if data11 == "1":
            host = "192.168.200.4"
        elif data11 == "2":
            host = "192.168.200.8"
        elif data11 == "3":
            host = "192.168.200.6"
        elif data11 == "4":
            host = "192.168.200.7"
        else:
            return jsonify({"status": "error", "message": "Invalid data11 value"}), 400

        port = 6101

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(zpl_code.encode('utf-8'))

        # 데이터베이스에서 값 검색
        third_value = data2[2]  # 세 번째 값
        found_code, found_id = get_code_from_db(third_value, data2, data10)

        if found_code:
            update_count_in_db(third_value, found_code, data10)  # 카운트 업데이트
            return jsonify({"status": "success", "found_code": found_code}), 200
        else:
            return jsonify({"status": "success", "message": "No matching code found"}), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
