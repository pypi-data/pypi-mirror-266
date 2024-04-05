
from flask import Flask, render_template # pip install Flask
import socketio # pip install python-socketio

# 创建一个 Flask 应用
app = Flask(__name__)

# 创建 Socket.IO 服务器实例
sio = socketio.Server()

# 将 Socket.IO 和 Flask 结合在一起
app.wsgi_app = socketio.WSGIApp(sio, app.wsgi_app)

# 定义路由和视图函数
@app.route('/')
def index():
    return render_template('index.html')

# 定义 Socket.IO 事件处理函数
@sio.on('message')
def handle_message(sid, data):
    print('Received message:', data)
    sio.emit('response', 'Got your message!')

if __name__ == '__main__':
    app.run()