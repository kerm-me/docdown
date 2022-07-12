from threading import activeCount
from playwright.sync_api import Playwright, sync_playwright
import os
from flask import Flask,send_from_directory,render_template
from flask_cors import CORS,cross_origin
from flask_socketio import SocketIO, emit
import tool

tasks_ = []

app = Flask(__name__)
app.jinja_env.variable_start_string = '{['
app.jinja_env.variable_end_string = ']}'
socketio = SocketIO(app)

@cross_origin(origins='*')
@app.route('/download/<string:filename>')
def download_image(filename):
    return send_from_directory(os.getcwd(), path=filename, as_attachment=True)

@cross_origin(origins='*')
@app.route('/')
def index():
    return render_template('index.html')

@cross_origin(origins='*')
@socketio.on('download')
def emit_init_balan(message):
    tasks_.append({'so':socketio,})
    socketio.emit('start')
    filename = tool.download_from_url(message['url'])
    socketio.emit('done',{'filename':filename})

if __name__ == '__main__':
    app.run(debug=True, port=8000, host="0.0.0.0")
