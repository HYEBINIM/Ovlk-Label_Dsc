from flask import Flask, render_template, request, jsonify
import subprocess
import mysql.connector  # MySQL 연결을 위한 라이브러리
from static.db.db import create_connection

app = Flask(__name__)

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
    except mysql.connector.Error as e:
        print(f"연결 실패: {e}")
    return connection

def part_data():  # 부품 - DB 데이터 가져오기
    """ product_list 테이블에서 데이터 가져오는 함수 """
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT data0, data1, data2, data3, data4 FROM product_list"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    if connection.is_connected():
        connection.close()
    return results

def torque_spec_data(): 
    """ torque_spec 테이블에서 데이터 가져오는 함수 """
    connection = create_connection()
    cursor = connection.cursor()
    query = "SELECT min1, max1, contents1 FROM torque_spec"
    cursor.execute(query)
    result = cursor.fetchone()  # 단일 행 반환
    cursor.close()
    if connection.is_connected():
        connection.close()
    return result

def get_barcode_positions():
    """ barcode_position 테이블에서 데이터 가져오고 product_list의 data1 가져오는 함수 """
    connection = create_connection()
    cursor = connection.cursor()
    
    # barcode_position 테이블에서 데이터 가져오기
    query = "SELECT data0, data1, data2, data3, data4, data5 FROM barcode_position"
    cursor.execute(query)
    barcode_positions = cursor.fetchone()  # 단일 행 반환
    
    # product_list 테이블에서 data0과 data1 가져오기
    query = "SELECT data0, data1 FROM product_list"
    cursor.execute(query)
    product_list = cursor.fetchall()  # 모든 data0과 data1 값을 가져오기

    print(product_list)  # 디버깅을 위해 콘솔에 출력
    
    cursor.close()
    if connection.is_connected():
        connection.close()
    
    return barcode_positions, product_list

@app.route('/')
def home():
    # 데이터베이스 연결
    connection = create_connection()
    if connection:
        connection.close()
    return render_template('index.html')

@app.route('/part')  # 부품 페이지 라우트
def part():
    data = part_data()
    torque_data = torque_spec_data()  # torque_spec 데이터 가져오기
    if torque_data is None:
        # torque_data가 None인 경우에 대한 처리
        torque_data = [None, None, None]  # 기본값 설정
    return render_template('part.html', data=data, torque_data=torque_data)

@app.route('/save_part_data', methods=['POST'])  # 데이터 저장 라우트
def save_part_data():
    min_value = request.form.get('min')
    max_value = request.form.get('max')
    unit_value = request.form.get('unit')

    print(f"Received values - MIN: {min_value}, MAX: {max_value}, UNIT: {unit_value}")  # 디버깅용 출력

    # product_list 테이블에서 체크박스 상태 업데이트
    connection = create_connection()
    cursor = connection.cursor()
    
    # 각 체크박스의 상태를 가져오고 업데이트
    for i in range(1, len(request.form) + 1):
        option_brk = request.form.get(f'option_brk_{i}')
        value = 1 if option_brk else 0
        query = "UPDATE product_list SET data4 = %s WHERE id = %s"
        cursor.execute(query, (value, i))  # id는 1부터 시작한다고 가정

    # torque_spec 테이블 업데이트
    query = "UPDATE torque_spec SET min1 = %s, max1 = %s, contents1 = %s"
    cursor.execute(query, (min_value, max_value, unit_value))

    connection.commit()
    cursor.close()
    if connection.is_connected():
        connection.close()
    
    return jsonify({"message": "데이터가 성공적으로 저장되었습니다."})

@app.route('/barcode')  # 바코드 페이지 라우트
def barcode():
    barcode_positions, product_list = get_barcode_positions()  # 바코드 위치 데이터와 product_list 가져오기
    
    if barcode_positions is None:
        return render_template('barcode.html', positions=[], product_list=[])  # 데이터가 없을 경우 빈 리스트 전달
    
    # 각 데이터에서 X, Y, W, H 값을 파싱
    parsed_positions = []
    if barcode_positions:
        for position in barcode_positions:
            x, y, w, h = map(int, position.split(','))
            parsed_positions.append((x, y, w, h))

    return render_template('barcode.html', positions=parsed_positions, product_list=product_list)

@app.route('/print_barcode', methods=['POST'])  # 바코드 프린트 요청 라우트
def print_barcode():
    positions = get_barcode_positions()
    
    if positions is None:
        return jsonify({"status": "error", "message": "바코드 위치 데이터를 가져오는 데 실패했습니다."})

    # 각 데이터에서 X, Y, W, H 값을 파싱
    barcode_data = []
    for position in positions:
        # 각 position의 값은 콤마로 구분되어 있음
        x, y, w, h = map(int, position.split(','))
        barcode_data.append((x, y, w, h))

    # label.py를 실행하고 인자로 전달
    try:
        subprocess.Popen(['python', 'label.py'] + [str(value) for pos in barcode_data for value in pos])  # X, Y, W, H 값을 전달
        return jsonify({"status": "success", "message": "바코드 출력 요청이 전송되었습니다."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    
@app.route('/save_barcode_positions', methods=['POST'])
def save_barcode_positions():
    positions = request.form.getlist('positions')  # POST 요청에서 positions 데이터 가져오기
    print(f"Received positions: {positions}")  # 수신된 데이터 로그로 출력

    # positions의 길이를 확인
    if len(positions) != 6:
        return jsonify({"status": "error", "message": "6개의 위치 데이터를 제공해야 합니다."})

    connection = create_connection()
    cursor = connection.cursor()

    # barcode_position 테이블 업데이트 (id가 1인 행)
    for i, pos in enumerate(positions):
        query = f"UPDATE barcode_position SET data{i} = %s WHERE id = 1"  # 모든 업데이트에서 id = 1 사용
        cursor.execute(query, (pos,))  # pos는 문자열 형식으로 되어 있으므로, 그대로 사용
        print(f"Updated data{i}: {pos}, Rows affected: {cursor.rowcount}")  # 디버깅용 출력

    connection.commit()
    cursor.close()
    if connection.is_connected():
        connection.close()

    return jsonify({"status": "success", "message": "바코드 위치 데이터가 성공적으로 저장되었습니다."})


@app.route('/print', methods=['POST'])
def print_label():
    date = request.form.get('date')
    lot_start = request.form.get('lotStart')
    part_number = request.form.get('partNumber')
    part_name = request.form.get('partName')  # 추가된 부분
    qty = request.form.get('qty')
    positions = request.form.getlist('positions')  # 바코드 위치 데이터 가져오기

    # 값 확인
    print(f"Date: {date}, Lot Start: {lot_start}, Part Number: {part_number}, Part Name: {part_name}, Qty: {qty}, Positions: {positions}")

    # ZPL 형식으로 변환
    zpl_commands = []
    for position in positions:
        x, y, w, h = position.split(',')  # X, Y, W, H 값을 분리
        zpl_commands.append(f'~FO{x},{y}~BCN,{w},{h},Y,N,N,N,D,{part_number}~FS')  # 바코드 ZPL 명령어

    # ZPL 명령어에 DATE, LOT START, QTY, PART NAME을 추가
    zpl_commands.append(f'~FDDATE: {date}~FS')  # DATE
    zpl_commands.append(f'~FDLOT START: {lot_start}~FS')  # LOT START
    zpl_commands.append(f'~FDQTY: {qty}~FS')  # QTY
    zpl_commands.append(f'~FDPART NUMBER: {part_number}, NAME: {part_name}~FS')  # PART NUMBER와 NAME 추가

    # label.py 실행
    try:
        # 모든 인자가 문자열인지 확인
        subprocess.Popen(['python', 'label.py', date, lot_start, part_number, part_name] + zpl_commands)  # ZPL 명령어를 인자로 전달
        return jsonify({"status": "success", "message": "프린터에 출력 요청이 전송되었습니다."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})



if __name__ == '__main__':
    app.run(debug=True)
