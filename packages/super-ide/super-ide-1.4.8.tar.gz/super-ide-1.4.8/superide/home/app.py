from flask import Flask ,render_template
from flask_socketio import SocketIO, emit

import git
import os
import subprocess

from superide.home.rpc.handlers.app import AppRPC
from superide.home.rpc.handlers.os import OSRPC
from superide.home.rpc.handlers.project import ProjectRPC
from superide.boards.cli import _get_boards
from superide.project.commands.init import project_init_cmd

# 创建一个 Flask 应用
# app = Flask(__name__)
# app.static_folder = './static/assets'
# app.template_folder='./static'
app = Flask(__name__, static_folder='static/assets', template_folder='static')
socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')
    
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
   
@socketio.on("load_state")
def handle_load_state():
    emit("load_state", AppRPC.load_state())

@socketio.on("save_state")
def handle_save_state(data):
    emit("save_state", AppRPC.save_state(data))

@socketio.on("init")
def handle_init(data):
    board, framework, programLanguage, env_image, example_code, project_dir = data.values()
    emit("init",ProjectRPC.init(board, framework, programLanguage,env_image,example_code,project_dir))

@socketio.on("clone")
def handle_clone(data):
    target_folder = data[1]
    repository_url = data[0]
    try:
        # 提取仓库名称（项目名称）
        repo_name = os.path.basename(repository_url)
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]  # 移除.git扩展名

        # 创建目标文件夹，以项目名称命名
        project_folder = os.path.join(target_folder, repo_name)
        os.makedirs(project_folder, exist_ok=True)

        # 使用GitPython库进行克隆操作
        repo = git.Repo.clone_from(repository_url, project_folder, bare=False)
        args = ["-d",project_folder]
        project_init_cmd(args=args,standalone_mode=False)
        emit("clone",project_folder)
        # return project_folder
    except Exception as e:
        # 如果发生错误，返回错误响应
        response_data = {'error': str(e)}
        emit("clone",response_data)
        # return response_data

@socketio.on("get_projects")
def handle_get_projects():
    emit("get_projects", ProjectRPC.get_projects())


@socketio.on("reveal_file")
def handle_reveal_file(data):
    emit("reveal_file", OSRPC.reveal_file(data))

@socketio.on("open_file")
def handle_open_file(data):
    # vscode.commands.executeCommand("vscode.openFolder", vscode.Uri.file(data))
    try:
        result = open_file_in_vscode_wsl(data)
        emit("open_file", result)
    except KeyError as e:
        print(f"KeyError: {e}")
        emit("open_file", {"success": False, "message": "KeyError: Missing key in data"})
    except Exception as e:
        print(f"Error handling open_file: {e}")
        emit("open_file", {"success": False, "message": f"Error handling open_file: {str(e)}"})
   

@socketio.on("is_file")
def handle_is_file(data):
    emit("is_file", OSRPC.is_file(data))

@socketio.on("boards_json")
def handle_boards_json():
    emit("boards_json",_get_boards())
   
def run_server(host, port, no_open, shutdown_timeout, home_url):
    socketio.run(app, host="0.0.0.0", port=8888, allow_unsafe_werkzeug=True)


def open_file_in_vscode_wsl(file_path):
    try:
        # 使用 wsl 命令以 VSCode 在 WSL 中打开文件
        result = subprocess.run(["which", "code"], capture_output=True, text=True)
        vscode_path = result.stdout.strip()
        # subprocess.run(["/mnt/d/Microsoft VS Code/bin/code", file_path])
        subprocess.run([vscode_path, file_path])
        return {"success": True, "message": "File opened successfully"}
    except Exception as e:
        return {"success": False, "message": f"Error opening file: {str(e)}"}


# if __name__ == '__main__':
#     socketio.run(debug=True)