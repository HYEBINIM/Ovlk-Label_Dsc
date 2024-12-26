from flask import Flask, render_template, jsonify
import subprocess
import socket

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/part')  # 부품 설정 라우트
def part():
    return render_template('part.html')

@app.route('/barcode')  # 바코드 설정 라우트
def barcode():
    return render_template('barcode.html')

@app.route('/print', methods=['POST'])  # 프린트 요청 라우트
def print_label():
    try:
        # label.py를 실행
        subprocess.Popen(['python', 'label.py'])  # label.py의 경로를 적절히 수정하세요.
        return jsonify({"status": "success", "message": "프린터에 출력 요청이 전송되었습니다."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
