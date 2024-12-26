from pylibdmtx import pylibdmtx
from PIL import Image, ImageDraw, ImageFont

# 매트릭스 코드로 변환할 데이터
data = (
    "[)>RS06\n"
    "PB31\n"
    "89310GX300\n"
    "-\n"
    "-\n"
    "241122\n"
    "G1A1\n"
    "A\n"
    "0000001\n"
    "21.920.620.5\n"
    "RSEOT"
)

# Data Matrix 코드 생성
encoded = pylibdmtx.encode(data.encode('utf-8'))

# 이미지 크기 설정
matrix_code_size = (50, 20)
image = Image.new('RGB', (matrix_code_size[0] + 250, matrix_code_size[1]), 'white')
draw = ImageDraw.Draw(image)

# 매트릭스 코드 그리기
matrix_image = Image.frombytes('RGB', matrix_code_size, encoded[0].data)
image.paste(matrix_image, (0, 0))

# 문자로 표시할 정보
text_info = [
    "89310-GX300",
    "D RH NA TER RMT H1R",
    "202412235215  1",
    "DSC Co.Ltd."
]

# 텍스트 위치 설정
text_x = matrix_code_size[0] + 10
text_y = 10

# 텍스트 그리기
for line in text_info:
    draw.text((text_x, text_y), line, fill='black')
    text_y += 30  # 줄 간격 조정

# 이미지 저장
image.save("matrix_code_with_text.png")
print("매트릭스 코드와 문자 정보가 저장되었습니다.")
