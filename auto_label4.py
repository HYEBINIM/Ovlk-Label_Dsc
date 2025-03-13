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
# 현재 날짜와 시간을 가져옵니다.
now = datetime.now()

# 날짜와 시간을 문자열로 포맷합니다.
current_time = now.strftime("%Y-%m-%d %H:%M:%S")

lh_data = None
rh_data = None
lh_printed = False  # LH 프린트 상태
rh_printed = False  # RH 프린트 상태

def update_assy3read(id, is_lh=True):
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
        print(f"[{current_time}]Update Error: {str(e)}")
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
            # print(f"[{current_time}]LH 프린팅 신호 : {result[0]}")
            
            if result and result[0] == "1" and not lh_printed:  # 프린트가 실행되지 않은 경우
                lh_printed = True  # 프린트가 실행되었음을 기록
                time.sleep(1)
                lh_data = get_lh_num()
                time.sleep(1)
                print_lh(lh_data)  # 프린트 함수 호출

            elif result and result[0] == "0":  # 신호가 0으로 변경되면 리셋
                lh_printed = False

    except Exception as e:
        print(f"[{current_time}]LH DB연결 및 프린팅신호 수신 실패 : {str(e)}")
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
            # print(f"[{current_time}]RH 프린팅 신호 : {result[0]}")
            
            if result and result[0] == "1" and not rh_printed:  # 프린트가 실행되지 않은 경우
                rh_printed = True  # 프린트가 실행되었음을 기록
                time.sleep(1)
                rh_data = get_rh_num()
                time.sleep(1)
                print_rh(rh_data)  # 프린트 함수 호출

            elif result and result[0] == "0":  # 신호가 0으로 변경되면 리셋
                rh_printed = False

    except Exception as e:
        print(f"[{current_time}]RH DB연결 및 프린팅신호 수신 실패: {str(e)}")
    finally:
        cursor.close()
        conn.close()

def get_lh_num():
    conn_assy1 = None
    cursor_assy1 = None
    conn_assy3 = None
    cursor_assy3 = None

    try:
        conn_assy3 = mysql.connector.connect(**db_conn_assy3)
        cursor_assy3 = conn_assy3.cursor()

        query = "SELECT data0, data7 FROM assy_lh ORDER BY id DESC LIMIT 1"
        cursor_assy3.execute(query)

        res = cursor_assy3.fetchone()
        if res:
            lh_scan = res[0]
            lh_count = lh_scan[41:48]
            lh_code = lh_scan[14:24]
            lh_zig = res[1]

            if lh_count is not None:
                print(f"[{current_time}]카운트: {int(lh_count)} 제품: {lh_code} 지그: {lh_zig}")
            else:
                print("lh_count가 None입니다.")

            print(f"[{current_time}]LH스캔: {lh_scan}")

            try:
                conn_assy1 = mysql.connector.connect(**db_conn_assy1)
                cursor_assy1 = conn_assy1.cursor()

                query3 = "SELECT data7, data8 FROM assy_lh WHERE data0 = %s ORDER BY id DESC LIMIT 1"
                if lh_zig and lh_scan:
                    cursor_assy1.execute(query3, (lh_scan,))
                else:
                    print("lh_zig 또는 lh_scan이 None입니다.")

                res3 = cursor_assy1.fetchone()
                if res3:
                    lh_torq1 = res3[0]
                    lh_torq2 = res3[1]

                    print(f"[{current_time}]토크1: {lh_torq1} 토크2: {lh_torq2}")

                    return lh_scan, lh_count, lh_code, lh_zig, lh_torq1, lh_torq2
            except Exception as e:
                print(f"[{current_time}]Database Error: {str(e)}")
                return None, None, None, None, None, None
            finally:
                if cursor_assy1:
                    cursor_assy1.close()
                if conn_assy1:
                    conn_assy1.close()

    except Exception as e:
        print(f"[{current_time}]Database Error: {str(e)}")
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

    try:
        conn_assy3 = mysql.connector.connect(**db_conn_assy3)
        cursor_assy3 = conn_assy3.cursor()

        query = "SELECT data0, data7 FROM assy_rh ORDER BY id DESC LIMIT 1"
        cursor_assy3.execute(query)

        res = cursor_assy3.fetchone()
        if res:
            rh_scan = res[0]
            rh_count = rh_scan[41:48]
            rh_code = rh_scan[14:24]
            rh_zig = res[1]

            if rh_count is not None:
                print(f"[{current_time}]카운트: {int(rh_count)} 제품: {rh_code} 지그: {rh_zig}")
            else:
                print("rh_count가 None입니다.")

            print(f"[{current_time}]rh스캔: {rh_scan}")

            try:
                conn_assy1 = mysql.connector.connect(**db_conn_assy1)
                cursor_assy1 = conn_assy1.cursor()

                query3 = "SELECT data7, data8 FROM assy_rh WHERE data0 = %s ORDER BY id DESC LIMIT 1"
                if rh_zig and rh_scan:
                    cursor_assy1.execute(query3, (rh_scan,))
                else:
                    print("rh_zig 또는 rh_scan이 None입니다.")

                res3 = cursor_assy1.fetchone()
                if res3:
                    rh_torq1 = res3[0]
                    rh_torq2 = res3[1]

                    print(f"[{current_time}]토크1: {rh_torq1} 토크2: {rh_torq2}")

                    return rh_scan, rh_count, rh_code, rh_zig, rh_torq1, rh_torq2
            except Exception as e:
                print(f"[{current_time}]Database Error: {str(e)}")
                return None, None, None, None, None, None
            finally:
                if cursor_assy1:
                    cursor_assy1.close()
                if conn_assy1:
                    conn_assy1.close()

    except Exception as e:
        print(f"[{current_time}]Database Error: {str(e)}")
        return None, None, None, None, None, None
    finally:
        if cursor_assy3:
            cursor_assy3.close()
        if conn_assy3:
            conn_assy3.close()

def format_torque(value):
    if value is None:
        return "00.0"

    value = int(value)
    value = str(value)

    # 문자열 길이에 따라 처리
    if len(value) == 3:
        # 3자리 미만인 경우 맨 앞에 0을 붙이고 소수점 추가
        formatted_value = f"0" + value[:1] + '.' + value[-2:-1]
    elif len(value) == 4:
        # 오른쪽에서 두 번째 숫자 전에 .을 붙인다.
        formatted_value = value[:2] + '.' + value[-2:-1]
    else:
        # 5자리 이상인 경우 기본값으로 "00.0" 반환
        formatted_value = "00.0"

    return formatted_value


def print_lh(lh_data):
    try:

        # lh_data 값이 None일 경우 처리
        if lh_data is None:
            print("lh_data is None")
            return

        lh_scan, lh_count, lh_code, lh_zig, lh_torq1, lh_torq2 = lh_data  # unpacking

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

        if lh_code == "89311X9100":
            lh_detail = "RSAB RMT SKI SBR"
        elif lh_code == "89311X9110":
            lh_detail = "RSAB RMT SKI SBR HTR"
        elif lh_code == "89311X9300":
            lh_detail = "SKI SBR"
        elif lh_code == "89311X9310":
            lh_detail = "SKI SBR HTR"
        elif lh_code == "89311X9500":
            lh_detail = "RSAB CTR"
        elif lh_code == "89311X9510":
            lh_detail = "RSAB CTR HTR"
        else:
            lh_detail = ""

        # ZPL 코드 생성
        zpl_code = f"""
        ^XA
        ^CF0,20
        ^FO145,25^A0N,40,32^FD {lh_code_value} ^FS
        ^FO145,70^A0N,20,22^FD {lh_detail} ^FS
        ^FO145,100^A0N,25,23^FD {today}{str((int(lh_count))).zfill(4)}   ST{lh_zig} ^FS
        ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DVPB31_1DP{lh_code}_1DS_1DE_1DT{today}G1A1A{str((int(lh_count))).zfill(7)}_1DA_1DC{lh_torq1_str}{lh_torq2_str}_1D_1E_04^FS     
        ^XZ
        """
        print(f"[{current_time}]출력토크1: {lh_torq1_str} 출력토크2: {lh_torq2_str}")

        # 소켓 연결 및 데이터 전송
        host = "192.168.200.6"  # 프린터의 IP 주소
        port = 6101              # 프린터의 포트 번호

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(zpl_code.encode('utf-8'))

        update_assy3read(4, is_lh=True)  # LH의 경우 id=4
        print({"============================status": "success", "message": "LH 프린트 성공"})

    except Exception as e:
        print(f"[{current_time}]Error: {str(e)}")
        print({"============================status": "error", "message": "LH 프린터 출력 실패", "error": str(e)})  

def print_rh(rh_data):
    """ RH 라벨을 프린트하는 함수 """
    try:
        if rh_data is None:
            print("rh_data is None")
            return

        rh_scan, rh_count, rh_code, rh_zig, rh_torq1, rh_torq2 = rh_data  # unpacking

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

        # 오늘 날짜 가져오기 (YYMMDD 형식)
        today = datetime.now().strftime("%y%m%d")
        time = datetime.now().strftime("%H%M%S")

        if rh_code == "89411X9100":
            rh_detail = "RSAB RMT SBR"
        elif rh_code == "89411X9300":
            rh_detail = "SBR"
        elif rh_code == "89411X9500":
            rh_detail = "RSAB"
        elif rh_code == "89411X9510":
            rh_detail = "RSAB HTR"
        else:
            rh_detail = ""

        # ZPL 코드 생성
        zpl_code = f"""
        ^XA
        ^CF0,20
        ^FO145,25^A0N,40,32^FD {rh_code_value} ^FS
        ^FO145,70^A0N,20,22^FD {rh_detail} ^FS
        ^FO145,100^A0N,25,23^FD {today}{str((int(rh_count))).zfill(4)}   ST{rh_zig} ^FS
        ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,25^BXN,3,200^FH_^FD[)>_1E06_1DVPB31_1DP{rh_code}_1DS_1DE_1DT{today}G1A1A{str((int(rh_count))).zfill(7)}_1DA_1DC{rh_torq1_str}{rh_torq2_str}_1D_1E_04^FS     
        ^XZ
        """

        print(f"[{current_time}]출력토크1: {rh_torq1_str} 출력토크2: {rh_torq2_str}")


        # 소켓 연결 및 데이터 전송
        host = "192.168.200.7"  # 프린터의 IP 주소
        port = 6101              # 프린터의 포트 번호

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(zpl_code.encode('utf-8'))

        update_assy3read(8, is_lh=False)  # RH의 경우 id=8
        print({"============================status": "success", "message": "RH 프린트 성공"})

    except Exception as e:
        print(f"[{current_time}]Error: {str(e)}")
        print({"============================status": "error", "message": "RH 프린터 출력 실패", "error": str(e)})


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

