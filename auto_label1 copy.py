# (LH) assy1read id=1 data0을 1초마다 지켜보다가 신호(1)들어오면 input1 id=5 data0(인덱스) 읽고 index_code id와 매치되는 값 찾아서 형식에 맞게 한 번 프린트 후 assy1read id=2 data0에 0,contents1에 11 업데이트
# (RH) assy1read id=5 data0을 1초마다 지켜보다가 신호(1)들어오면 input1 id=5 data2(인덱스) 읽고 index_code id와 매치되는 값 찾아서 형식에 맞게 한 번 프린트 후 assy1read id=6 data0에 0,contents1에 11 업데이트
from flask import Flask, request, jsonify
from flask_cors import CORS
import socket
import mysql.connector
import threading
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 데이터베이스 연결 설정
db_config = {
    'user': 'server',
    'password': 'dltmxm1234',
    'host': 'localhost',
    'database': 'dataset'
}

# 전역 변수
lh_data = None
rh_data = None

# 프린트 완료시 업데이트ㄱ
def update_assy1read(id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # data0을 0으로, contents1을 11로 업데이트
        query = "UPDATE assy1read SET data0 = %s, contents1 = %s WHERE id = %s"
        cursor.execute(query, (0, 11, id))
        conn.commit()  # 변경 사항 저장
    except Exception as e:
        print(f"Update Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_lh_check():
    global lh_data
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        query = "SELECT data0 FROM assy1read WHERE id = %s"
        cursor.execute(query, (1,))
        result = cursor.fetchone()
        print(f"LH 프린팅 신호 : {result[0]}")
        
        if result and result[0] == "1":
            # input1 테이블에서 lh_code 가져오기
            lh_data = get_lh_num()
    except Exception as e:
        print(f"Database Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_rh_check():
    global rh_data
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        query = "SELECT data0 FROM assy1read WHERE id = %s"
        cursor.execute(query, (5,))
        result = cursor.fetchone()
        print(f"RH 프린팅 신호 : {result[0]}")
        
        if result and result[0] == "1":
            # input1 테이블에서 rh_code 가져오기
            rh_data = get_rh_num()
    except Exception as e:
        print(f"Database Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_lh_num():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # input1 테이블에서 id=5의 data0, data1 가져오기
        query = "SELECT data0, data1 FROM input1 WHERE id = %s"
        cursor.execute(query, (5,))
        result = cursor.fetchone()
        if result:
            lh_id = result[0]
            lh_zig = result[1]
            
            try:
                query_lh = "SELECT lh_code, lh_count FROM index_code WHERE id = %s"
                cursor.execute(query_lh, (lh_id,))
                result_lh2 = cursor.fetchone()
                if result_lh2:
                    lh_code = result_lh2[0]
                    lh_count = result_lh2[1]
                    return lh_code, lh_count, lh_zig  # 모든 값 반환
            except Exception as e:
                print(f"index_code에서 LH 제품 찾을 수 없음: {str(e)}")
                return None, None, None
        return None, None, None
    except Exception as e:
        print(f"Database Error: {str(e)}")
        return None, None, None
    finally:
        cursor.close()
        conn.close()

def get_rh_num():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # input1 테이블에서 id=5의 data2, data3 가져오기
        query = "SELECT data2, data3 FROM input1 WHERE id = %s"
        cursor.execute(query, (5,))
        result = cursor.fetchone()
        if result:
            rh_id = result[0]
            rh_zig = result[1]

            try:
                query_rh = "SELECT rh_code, rh_count FROM index_code WHERE id = %s"
                cursor.execute(query_rh, (rh_id,))
                result_rh2 = cursor.fetchone()
                if result_rh2:
                    rh_code = result_rh2[0]
                    rh_count = result_rh2[1]
                    return rh_code, rh_count, rh_zig  # 모든 값 반환
            except Exception as e:
                print(f"index_code에서 RH 제품 찾을 수 없음: {str(e)}")
                return None, None, None
        return None, None, None
    except Exception as e:
        print(f"Database Error: {str(e)}")
        return None, None, None
    finally:
        cursor.close()
        conn.close()

def get_lh_check():
    global lh_data
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        query = "SELECT data0 FROM assy1read WHERE id = %s"
        cursor.execute(query, (1,))
        result = cursor.fetchone()
        print(f"LH 프린팅 신호 : {result[0]}")
        
        if result and result[0] == "1":
            # input1 테이블에서 lh_code 가져오기
            lh_data = get_lh_num()  # 모든 값을 가져오도록 수정

            try:

                # lh_data 값이 None일 경우 처리
                if lh_data is None:
                    return jsonify({"status": "error", "message": "lh_data is not available"}), 404

                lh_code, lh_count, lh_zig = lh_data  # unpacking

                # 오늘 날짜 가져오기 (YYMMDD 형식)
                today = datetime.now().strftime("%y%m%d")

                # ZPL 코드 생성
                zpl_code = f"""
                ^XA
                ^CF0,20
                ^FO145,25^A0N,40,32^FD {lh_code} ^FS
                ^FO145,70^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
                ^FO145,100^A0N,25,23^FD {today}{str(int(lh_count)).zfill(4)}   {lh_zig} ^FS
                ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
                ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DVPB31_1DP{lh_code}_1DS_1DE_1DT{today}G1A1A{str(int(lh_count)).zfill(7)}_1DA_1DC0.00.0_1D_1E_04^FS     
                ^XZ
                """

                # 소켓 연결 및 데이터 전송
                host = "192.168.200.6"  # 프린터의 IP 주소
                port = 6101              # 프린터의 포트 번호

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(zpl_code.encode('utf-8'))

                update_assy1read(2)  # LH의 경우 id=6
                return jsonify({"LH 프린트 출력 성공"}), 200

            except Exception as e:
                print(f"Error: {str(e)}")
                return jsonify({"status": "error", "message": "LH 프린터 출력 실패", "error": str(e)}), 500
            
    except Exception as e:
        print(f"LH DB연결 및 프린팅신호 수신 실패 : {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_rh_check():
    global rh_data
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        query = "SELECT data0 FROM assy1read WHERE id = %s"
        cursor.execute(query, (5,))
        result = cursor.fetchone()
        print(f"RH 프린팅 신호 : {result[0]}")
        
        if result and result[0] == "1":
            # input1 테이블에서 rh_code 가져오기
            rh_data = get_rh_num()  # 모든 값을 가져오도록 수정

            try:

                # rh_data 값이 None일 경우 처리
                if rh_data is None:
                    return jsonify({"status": "error", "message": "rh_data is not available"}), 404

                rh_code, rh_count, rh_zig = rh_data  # unpacking

                # 오늘 날짜 가져오기 (YYMMDD 형식)
                today = datetime.now().strftime("%y%m%d")

                # ZPL 코드 생성
                zpl_code = f"""
                ^XA
                ^CF0,20
                ^FO145,25^A0N,40,32^FD {rh_code} ^FS
                ^FO145,70^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
                ^FO145,100^A0N,25,23^FD {today}{str(int(rh_count)).zfill(4)}   {rh_zig} ^FS
                ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
                ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DVPB31_1DP{rh_code}_1DS_1DE_1DT{today}G1A1A{str(int(rh_count)).zfill(7)}_1DA_1DC0.00.0_1D_1E_04^FS     
                ^XZ
                """

                # 소켓 연결 및 데이터 전송
                host = "192.168.200.6"  # 프린터의 IP 주소
                port = 6101              # 프린터의 포트 번호

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(zpl_code.encode('utf-8'))

                update_assy1read(6)  # RH의 경우 id=6
                return jsonify({"RH 프린트 성공"}), 200
            except Exception as e:
                print(f"Error: {str(e)}")
                return jsonify({"status": "error", "message": "RH 프린터 출력 실패", "error": str(e)}), 500


    except Exception as e:
        print(f"RH DB연결 및 프린팅신호 수신 실패: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def monitor_database():
    while True:
        get_lh_check()
        get_rh_check()
        time.sleep(1)  # 1초마다 체크

if __name__ == '__main__':
    # 데이터베이스 모니터링 스레드 시작
    threading.Thread(target=monitor_database, daemon=True).start()
    app.run(host='0.0.0.0', debug=True)
