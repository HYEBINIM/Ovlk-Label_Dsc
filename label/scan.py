import serial

def main():
    # COM5 포트와 통신 속도 설정
    port = "COM5"  # 시리얼 포트 이름
    baud_rate = 9600  # 보드레이트 (통신 속도)

    try:
        # 시리얼 포트 열기
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"{port} 포트에 연결되었습니다. 데이터를 기다리는 중입니다...")

        while True:

            try :
                # 수신된 데이터 읽기
                if ser.in_waiting > 0:  # 수신된 데이터가 있는지 확인
                    data = ser.readline().decode('utf-8').strip()  # 한 줄 읽기 및 디코딩
                    print(f"수신한 데이터: {data}")
            except Exception as e:
                pass

    except Exception as e:
        print(f"시리얼 통신 오류: {e}")

    finally:
        # 시리얼 포트 닫기
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print(f"{port} 포트를 닫았습니다.")

if __name__ == "__main__":
    main()
