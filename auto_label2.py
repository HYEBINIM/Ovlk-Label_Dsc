# (LH) assy3read id=3 data1을 1초마다 지켜보다가 신호(1)들어오면 assy_lh id=최근 data10(인덱스) 읽고 index_code id와 매치되는 값 찾아서 형식에 맞게 한 번 프린트 후 assy3read id=4 data1에 0,contents1에 12 업데이트
# (RH) assy3read id=7 data1을 1초마다 지켜보다가 신호(1)들어오면 assy_rh id=최근 data10(인덱스) 읽고 index_code id와 매치되는 값 찾아서 형식에 맞게 한 번 프린트 후 assy3read id=8 data1에 0,contents1에 12 업데이트
from flask import Flask, request
from flask_cors import CORS
import socket
import mysql.connector
import ctypes
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 창 설정
kernel32 = ctypes.WinDLL("kernel32")
user32 = ctypes.WinDLL("user32")
hWnd = kernel32.GetConsoleWindow()
user32.MoveWindow(hWnd, 1100, 700, 800, 300, True)

# 데이터베이스 연결 설정
db_conn_kiosk = {
    'user': 'server',
    'password': 'dltmxm1234',
    'host': 'localhost',
    'database': 'dataset'  # 기본 데이터베이스
}

db_conn_assy1 = {
    'user': 'server',
    'password': 'dltmxm1234',
    'host': '192.168.200.9',  # assy_lh와 assy_rh 데이터베이스
    'database': 'dataset'
}

db_conn_assy3 = {
    'user': 'server',
    'password': 'dltmxm1234',
    'host': '192.168.200.10',  # assy_lh와 assy_rh 데이터베이스
    'database': 'dataset'
}

# 전역 변수
lh_data = None
rh_data = None
lh_printed = False  # LH 프린트 상태
rh_printed = False  # RH 프린트 상태

def update_assy3read(id, index, is_lh=True):
    try:
        
        conn = mysql.connector.connect(**db_conn_kiosk)
        cursor = conn.cursor()
        
        # assy3read 테이블 업데이트
        query = "UPDATE assy3read SET data1 = %s, contents1 = %s WHERE id = %s"
        cursor.execute(query, (0, 12, id))
        
        # # index_code 테이블의 카운트 업데이트
        # if is_lh:
        #     query_count_update = "UPDATE index_code SET lh_count = lh_count + %s WHERE id = %s"
        #     cursor.execute(query_count_update, (1, index))
        # else:
        #     query_count_update = "UPDATE index_code SET rh_count = rh_count + %s WHERE id = %s"
        #     cursor.execute(query_count_update, (1, index))
        
        conn.commit()  # 변경 사항 저장
    except Exception as e:
        print(f"Update Error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_lh_check():
    global lh_data, lh_printed
    try:
        with app.app_context():  # 애플리케이션 컨텍스트 설정
            conn = mysql.connector.connect(**db_conn_kiosk)
            cursor = conn.cursor()

            query = "SELECT data1 FROM assy3read WHERE id = %s"
            cursor.execute(query, (3,))
            result = cursor.fetchone()
            # print(f"LH 프린팅 신호 : {result[0]}")
            
            if result and result[0] == "1" and not lh_printed:  # 프린트가 실행되지 않은 경우
                lh_printed = True  # 프린트가 실행되었음을 기록
                lh_data = get_lh_num()
                time.sleep(1)
                print_lh(lh_data)  # 프린트 함수 호출

            elif result and result[0] == "0":  # 신호가 0으로 변경되면 리셋
                lh_printed = False

    except Exception as e:
        print(f"LH DB연결 및 프린팅신호 수신 실패 : {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_rh_check():
    global rh_data, rh_printed
    try:
        with app.app_context():  # 애플리케이션 컨텍스트 설정
            conn = mysql.connector.connect(**db_conn_kiosk)
            cursor = conn.cursor()

            query = "SELECT data1 FROM assy3read WHERE id = %s"
            cursor.execute(query, (7,))
            result = cursor.fetchone()
            # print(f"RH 프린팅 신호 : {result[0]}")
            
            if result and result[0] == "1" and not rh_printed:  # 프린트가 실행되지 않은 경우
                rh_printed = True  # 프린트가 실행되었음을 기록
                rh_data = get_rh_num()
                time.sleep(1)
                print_rh(rh_data)  # 프린트 함수 호출

            elif result and result[0] == "0":  # 신호가 0으로 변경되면 리셋
                rh_printed = False

    except Exception as e:
        print(f"RH DB연결 및 프린팅신호 수신 실패: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_lh_num():
    conn_assy1 = None
    cursor_assy1 = None
    conn_assy3 = None
    cursor_assy3 = None
    conn_kiosk = None
    cursor_kiosk = None
    
    try:
        conn_assy3 = mysql.connector.connect(**db_conn_assy3)
        cursor_assy3 = conn_assy3.cursor()
        
        # assy_lh 테이블에서 최근 data7, data10 가져오기
        query = "SELECT data0, data7, data10 FROM assy_lh ORDER BY id DESC LIMIT 1"
        cursor_assy3.execute(query)

        res = cursor_assy3.fetchone()
        if res:
            lh_scan = res[0]
            lh_count = lh_scan[41:48]
            lh_zig = res[1]
            lh_id = res[2]
            
            print(f"LH스캔: {lh_scan}")
            print(f"카운트: {int(lh_count)} 인덱스: {lh_id} 지그: {lh_zig}")
            try:
                conn_kiosk = mysql.connector.connect(**db_conn_kiosk)
                cursor_kiosk = conn_kiosk.cursor()

                query2 = "SELECT lh_code FROM index_code WHERE id = %s"
                cursor_kiosk.execute(query2, (lh_id,))
                res2 = cursor_kiosk.fetchone()
                if res2:
                    lh_code = res2[0]

                    print(f"LH제품코드: {lh_code}")
                    
                    try:
                        conn_assy1 = mysql.connector.connect(**db_conn_assy1)
                        cursor_assy1 = conn_assy1.cursor()

                        query3 = "SELECT data7, data8 FROM assy_lh WHERE data9 = %s and data10 = %s ORDER BY id desc limit 1"
                        cursor_assy1.execute(query3, (lh_zig, lh_id,))
                        res3 = cursor_assy1.fetchone()
                        if res3:
                            lh_torq1 = res3[0]
                            lh_torq2 = res3[1]

                            print(f"토크1: {lh_torq1} 토크2: {lh_torq2}")

                            return lh_code, lh_count, lh_id, lh_zig, lh_torq1, lh_torq2
                    except Exception as e:
                        print(f"Database Error: {str(e)}")
                        return None, None, None, None, None, None
                    finally:
                        if cursor_assy1:
                            cursor_assy1.close()
                        if conn_assy1:
                            conn_assy1.close()
            except Exception as e:
                print(f"index_code에서 LH 제품 찾을 수 없음: {str(e)}")
                return None, None, None, None, None, None
            finally:
                if cursor_kiosk:
                    cursor_kiosk.close()
                if conn_kiosk:
                    conn_kiosk.close()
        return None, None, None, None, None, None
    except Exception as e:
        print(f"Database Error: {str(e)}")
        return None, None, None, None, None, None
    finally:
        if cursor_assy3:
            cursor_assy3.close()
        if conn_assy3:
            conn_assy3.close()

def get_rh_num():
    conn_assy1 = None
    cursor_assy1 = None
    conn_assy3 = None
    cursor_assy3 = None
    conn_kiosk = None
    cursor_kiosk = None
    
    try:
        conn_assy3 = mysql.connector.connect(**db_conn_assy3)
        cursor_assy3 = conn_assy3.cursor()
        
        # assy_rh 테이블에서 최근 data7, data10 가져오기
        query = "SELECT data0, data7, data10 FROM assy_rh ORDER BY id DESC LIMIT 1"
        cursor_assy3.execute(query)

        res = cursor_assy3.fetchone()
        if res:
            rh_scan = res[0]
            rh_count = rh_scan[41:48]
            rh_zig = res[1]
            rh_id = res[2]
            
            print(f"rh스캔: {rh_scan}")
            print(f"카운트: {int(rh_count)} 인덱스: {rh_id} 지그: {rh_zig}")
            try:
                conn_kiosk = mysql.connector.connect(**db_conn_kiosk)
                cursor_kiosk = conn_kiosk.cursor()

                query2 = "SELECT rh_code FROM index_code WHERE id = %s"
                cursor_kiosk.execute(query2, (rh_id,))
                res2 = cursor_kiosk.fetchone()
                if res2:
                    rh_code = res2[0]

                    print(f"rh제품코드: {rh_code}")
                    
                    try:
                        conn_assy1 = mysql.connector.connect(**db_conn_assy1)
                        cursor_assy1 = conn_assy1.cursor()

                        query3 = "SELECT data7, data8 FROM assy_rh WHERE data9 = %s and data10 = %s ORDER BY id desc limit 1"
                        cursor_assy1.execute(query3, (rh_zig, rh_id,))
                        res3 = cursor_assy1.fetchone()
                        if res3:
                            rh_torq1 = res3[0]
                            rh_torq2 = res3[1]

                            print(f"토크1: {rh_torq1} 토크2: {rh_torq2}")

                            return rh_code, rh_count, rh_id, rh_zig, rh_torq1, rh_torq2
                    except Exception as e:
                        print(f"Database Error: {str(e)}")
                        return None, None, None, None, None, None
                    finally:
                        if cursor_assy1:
                            cursor_assy1.close()
                        if conn_assy1:
                            conn_assy1.close()
            except Exception as e:
                print(f"index_code에서 RH 제품 찾을 수 없음: {str(e)}")
                return None, None, None, None, None, None
            finally:
                if cursor_kiosk:
                    cursor_kiosk.close()
                if conn_kiosk:
                    conn_kiosk.close()
        return None, None, None, None, None, None
    except Exception as e:
        print(f"Database Error: {str(e)}")
        return None, None, None, None, None, None
    finally:
        if cursor_assy3:
            cursor_assy3.close()
        if conn_assy3:
            conn_assy3.close()
def format_torque(value):
    if value is None:
        return "00.0"

    value = float(value)  # 문자열을 실수형으로 변환

    # 100으로 나누고 소수점 한 자리까지 포맷팅
    value /= 100.0  # 100으로 나누기
    return f"{value:04.1f}"  # 소수점 한 자리까지 포맷팅 (총 4자리 중 1자리 소수점)


def print_lh(lh_data):
    try:

        # lh_data 값이 None일 경우 처리
        if lh_data is None:
            print("lh_data is None")
            return

        lh_code, lh_count, lh_id, lh_zig, lh_torq1, lh_torq2 = lh_data  # unpacking

        # 포맷팅 함수 호출
        lh_torq1_str = format_torque(lh_torq1)
        lh_torq2_str = format_torque(lh_torq2)

        if lh_code is None:
            lh_code_value = "UNKNOWN"  # 기본값 설정
        elif len(lh_code) > 5:
            lh_code_value = lh_code[:5] + "-" + lh_code[5:]
        else:
            lh_code_value = lh_code  # 기본값 설정

        # 오늘 날짜 가져오기 (YYMMDD 형식)

        today = datetime.now().strftime("%y%m%d")
        time = datetime.now().strftime("%H%M%S")

        # ZPL 코드 생성
        zpl_code = f"""
        ^XA
        ^CF0,20
        ^FO145,25^A0N,40,32^FD {lh_code_value} ^FS
        ^FO145,70^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
        ^FO145,100^A0N,25,23^FD {today}{str((int(lh_count))).zfill(4)}   ST{lh_zig} ^FS
        ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DVPB31_1DP{lh_code}_1DS_1DE_1DT{today}G1A1A{str((int(lh_count))).zfill(7)}_1DA_1DC{lh_torq1_str}{lh_torq2_str}_1D_1E_04^FS     
        ^XZ
        """
        print(f"{time} 출력토크1: {lh_torq1_str} 출력토크2: {lh_torq2_str}")

        # 소켓 연결 및 데이터 전송
        host = "192.168.200.6"  # 프린터의 IP 주소
        port = 6101              # 프린터의 포트 번호

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(zpl_code.encode('utf-8'))

        update_assy3read(4, lh_id, is_lh=True)  # LH의 경우 id=4
        print({"status": "success", "message": "LH 프린트 성공"})

    except Exception as e:
        print(f"Error: {str(e)}")
        print({"status": "error", "message": "LH 프린터 출력 실패", "error": str(e)})  

def print_rh(rh_data):
    """ RH 라벨을 프린트하는 함수 """
    try:
        if rh_data is None:
            print("rh_data is None")
            return

        rh_code, rh_count, rh_id, rh_zig, rh_torq1, rh_torq2 = rh_data  # unpacking

        # None 체크 및 형식 지정
        try:
            rh_torq1 = float(rh_torq1) if rh_torq1 is not None else 0.0
        except ValueError:
            rh_torq1 = 0.0
            
        try:
            rh_torq2 = float(rh_torq2) if rh_torq2 is not None else 0.0
        except ValueError:
            rh_torq2 = 0.0

        # 포맷팅 함수 호출
        rh_torq1_str = format_torque(rh_torq1)
        rh_torq2_str = format_torque(rh_torq2)

        if rh_code is None:
            rh_code_value = "UNKNOWN"  # 기본값 설정
        elif len(rh_code) > 5:
            rh_code_value = rh_code[:5] + "-" + rh_code[5:]
        else:
            rh_code_value = rh_code  # 기본값 설정

        # rh_id와 rh_zig 체크
        rh_id = rh_id if rh_id is not None else "UNKNOWN"  # 기본값 설정
        rh_zig = rh_zig if rh_zig is not None else 0  # 기본값 설정

        # 오늘 날짜 가져오기 (YYMMDD 형식)
        today = datetime.now().strftime("%y%m%d")
        time = datetime.now().strftime("%H%M%S")

        # ZPL 코드 생성
        zpl_code = f"""
        ^XA
        ^CF0,20
        ^FO145,25^A0N,40,32^FD {rh_code_value} ^FS
        ^FO145,70^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
        ^FO145,100^A0N,25,23^FD {today}{str((int(rh_count))).zfill(4)}   ST{rh_zig} ^FS
        ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DVPB31_1DP{rh_code}_1DS_1DE_1DT{today}G1A1A{str((int(rh_count))).zfill(7)}_1DA_1DC{rh_torq1_str}{rh_torq2_str}_1D_1E_04^FS     
        ^XZ
        """

        print(f"{time} 출력토크1: {rh_torq1_str} 출력토크2: {rh_torq2_str}")


        # 소켓 연결 및 데이터 전송
        host = "192.168.200.7"  # 프린터의 IP 주소
        port = 6101              # 프린터의 포트 번호

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(zpl_code.encode('utf-8'))

        update_assy3read(8, rh_id, is_lh=False)  # RH의 경우 id=8
        print({"status": "success", "message": "RH 프린트 성공"})

    except Exception as e:
        print(f"Error: {str(e)}")
        print({"status": "error", "message": "RH 프린터 출력 실패", "error": str(e)})

def monitor_database():
    while True:
        with app.app_context():  # 애플리케이션 컨텍스트 설정
            get_lh_check()
            get_rh_check()
        time.sleep(2)

if __name__ == '__main__':
    # 데이터베이스 모니터링 스레드 사용하면 안됨!!
    while True:
        monitor_database()

