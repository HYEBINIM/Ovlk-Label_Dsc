import os

def create_flask_project(project_name):
    # 프로젝트 디렉토리 생성
    os.makedirs(project_name, exist_ok=True)
    
    # 하위 디렉토리 생성
    os.makedirs(os.path.join(project_name, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(project_name, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(project_name, 'templates'), exist_ok=True)

    # app.py 파일 생성
    app_content = """from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
"""
    with open(os.path.join(project_name, 'app.py'), 'w') as f:
        f.write(app_content)

    # HTML 템플릿 파일 생성
    index_html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Flask App</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/styles.css') }}">
</head>
<body>
    <h1>Hello, Flask!</h1>
    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
"""
    with open(os.path.join(project_name, 'templates', 'index.html'), 'w') as f:
        f.write(index_html_content)

    # CSS 파일 생성
    styles_css_content = """body {
    font-family: Arial, sans-serif;
    background-color: #f8f9fa;
    text-align: center;
}
"""
    with open(os.path.join(project_name, 'static', 'css', 'styles.css'), 'w') as f:
        f.write(styles_css_content)

    # JavaScript 파일 생성
    script_js_content = """console.log("Hello from JavaScript!");
"""
    with open(os.path.join(project_name, 'static', 'js', 'script.js'), 'w') as f:
        f.write(script_js_content)

    # requirements.txt 파일 생성
    requirements_content = """Flask==2.2.2
"""
    with open(os.path.join(project_name, 'requirements.txt'), 'w') as f:
        f.write(requirements_content)

    print(f"Flask project '{project_name}' created successfully!")

if __name__ == "__main__":
    project_name = input("Enter the project name: ")
    create_flask_project(project_name)
