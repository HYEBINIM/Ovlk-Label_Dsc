from pylibdmtx import pylibdmtx
from PIL import Image

# 데이터 구성
data = (
    "[)>RS06\n"
    "PB31\n"
    "P89310GX300\n"
    "-\n"
    "-\n"
    "T241122\n"
    "G1A1\n"
    "A\n"
    "0000001\n"
    "C21.920.620.5\n"
    "RS\n"
    "EOT"
)

# Data Matrix 코드 생성
encoded = pylibdmtx.encode(data.encode('utf-8'))

# 이미지 저장
if len(encoded) > 0:
    # 첫 번째 인코딩 결과를 가져오기
    dm_data = encoded[0]
    
    # 이미지 생성
    image = Image.frombytes('RGB', (dm_data.width, dm_data.height), dm_data.data)
    
    # 이미지 저장
    image.save("data_matrix_code.png")
    print("Data Matrix 코드가 성공적으로 생성되었습니다.")
else:
    print("코드 생성 실패")
