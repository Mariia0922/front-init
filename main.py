import os
import json
import threading
import socket
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/message', methods=['GET', 'POST'])
def message():
    if request.method == 'POST':
        username = request.form['username']
        message = request.form['message']
        data = json.dumps({'username': username, 'message': message})
        send_to_socket(data.encode('utf-8'))
        return redirect(url_for('index'))
    return render_template('message.html')

@app.route('/static/<path:path>')
def static_file(path):
    return send_from_directory('static', path)

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html'), 404

def send_to_socket(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(data, ('localhost', 5000))

def run_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind(('localhost', 5000))
        while True:
            data, addr = server.recvfrom(1024)
            process_data(json.loads(data.decode()))

def process_data(data):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    filepath = os.path.join('storage', 'data.json')
    try:
        if not os.path.exists('storage'):
            os.makedirs('storage')
        if not os.path.isfile(filepath):
            with open(filepath, 'w') as f:
                json.dump({}, f)
        with open(filepath, 'r+') as file:
            storage = json.load(file)
            storage[timestamp] = data
            file.seek(0)
            json.dump(storage, file, indent=4)
    except Exception as e:
        print(f"Failed to write to file: {e}")

if __name__ == '__main__':
    t = threading.Thread(target=run_socket_server)
    t.start()
    app.run(port=3000, debug=True)
