import socket

def main():
    host = "192.168.94.48"  # 프린터의 IP 주소
    port = 6101              # 프린터의 포트 번호

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((host, port))  # 프린터에 연결
    print(f"프린터에 연결됨: {host}:{port}")

    zpl1 = """
        ^XA
        ^CF0,20
        ^FO145,25^A0N,40,32^FD 89411-P1ED0 ^FS
        ^FO145,70^A0N,20,22^FD D_RH NA TER RMT H1R ^FS
        ^FO145,100^A0N,25,23^FD 202412235215   1 ^FS
        ^FO145,130^A0N,25,23^FD DSC Co.Ltd,.^FS
        ^FO20,20^BXN,3,200^FH_^FD[)>_1D06_1EPB3189310GX300_1ES_1EE_1ET241122G1A1A0000001_1EA_1EC1.920.620.5_1E_1D_04^FS     
        ^XZ
    """

    server_socket.sendall(zpl1.encode('utf-8'))  # ZPL 코드 전송
    print("ZPL 코드 전송 완료")

    server_socket.close()
    print("서버 종료")

if __name__ == "__main__":
    main()
