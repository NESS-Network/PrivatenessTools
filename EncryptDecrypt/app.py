import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
import threading
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from NessKeys.KeyManager import KeyManager
from framework.Container import Container
from services.node import node as NodesUpdater
from NessKeys.JsonChecker.Checker import JsonChecker
from Crypto.Cipher import AES, Salsa20
from Crypto.Random import get_random_bytes

# Initialize Flask app
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY=os.environ.get('FLASK_SECRET', 'replace-with-secure-key'),
    DATA_DIR=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data'),
    UPLOAD_DIR=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
)

# Ensure necessary directories exist
os.makedirs(app.config['DATA_DIR'], exist_ok=True)
os.makedirs(app.config['UPLOAD_DIR'], exist_ok=True)

# Globals for background tasks
running_tasks = {}
tasks_lock = threading.Lock()

# Encryption utilities
def encrypt_data(data: bytes, algo: str, key: bytes) -> dict:
    if algo == 'salsa20':
        cipher = Salsa20.new(key=key)
        return {'nonce': cipher.nonce, 'ciphertext': cipher.encrypt(data)}
    elif algo == 'aes':
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        return {'iv': iv, 'ciphertext': cipher.encrypt(data)}
    else:
        raise ValueError('Unsupported algorithm')

def decrypt_data(enc: dict, algo: str, key: bytes) -> bytes:
    if algo == 'salsa20':
        cipher = Salsa20.new(key=key, nonce=enc['nonce'])
        return cipher.decrypt(enc['ciphertext'])
    elif algo == 'aes':
        cipher = AES.new(key, AES.MODE_CFB, iv=enc['iv'])
        return cipher.decrypt(enc['ciphertext'])
    else:
        raise ValueError('Unsupported algorithm')

# Home route
def get_data(filename):
    path = os.path.join(app.config['DATA_DIR'], filename)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

@app.route('/')
def index():
    return render_template('index.html')

# Encryption endpoint
@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_route():
    if request.method == 'POST':
        algo = request.form['algorithm']
        file = request.files['file']
        key = get_random_bytes(32)
        in_path = os.path.join(app.config['UPLOAD_DIR'], file.filename)
        file.save(in_path)
        data = open(in_path, 'rb').read()
        enc = encrypt_data(data, algo, key)
        out_path = in_path + '.enc'
        with open(out_path, 'wb') as f:
            f.write(enc['ciphertext'])
        metadata = {'algorithm': algo, 'key': key.hex()}
        # Include nonce/iv in metadata
        if 'nonce' in enc:
            metadata['nonce'] = enc['nonce'].hex()
        if 'iv' in enc:
            metadata['iv'] = enc['iv'].hex()
        return render_template('encrypt_result.html', filename=os.path.basename(out_path), metadata=metadata)
    return render_template('encrypt.html')

# Decryption endpoint
@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_route():
    if request.method == 'POST':
        algo = request.form['algorithm']
        key = bytes.fromhex(request.form['key'])
        file = request.files['file']
        in_path = os.path.join(app.config['UPLOAD_DIR'], file.filename)
        file.save(in_path)
        enc = {'ciphertext': open(in_path, 'rb').read()}
        if algo == 'salsa20':
            enc['nonce'] = bytes.fromhex(request.form['nonce'])
        elif algo == 'aes':
            enc['iv'] = bytes.fromhex(request.form['iv'])
        data = decrypt_data(enc, algo, key)
        out_path = in_path + '.dec'
        with open(out_path, 'wb') as f:
            f.write(data)
        return send_file(out_path, as_attachment=True)
    return render_template('decrypt.html')

# Generate user key
@app.route('/keygen', methods=['GET', 'POST'])
def keygen():
    if request.method == 'POST':
        username = request.form['username']
        entropy = int(request.form['entropy'])
        try:
            km = KeyManager()
            km.createUsersKey(username, entropy)
            flash(f'User key generated: {username}', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('keygen'))
    return render_template('keygen.html')

# Update nodes list
def update_nodes(rpc_args=None):
    updater = NodesUpdater()
    if rpc_args:
        updater.fetch_from_blockchain(*rpc_args)
    else:
        updater.fetch_from_public()
    updater.save(app.config['DATA_DIR'])

@app.route('/nodes', methods=['GET', 'POST'])
def nodes():
    if request.method == 'POST':
        mode = request.form['mode']
        rpc = None
        if mode == 'rpc':
            rpc = (
                request.form['rpc_host'],
                int(request.form['rpc_port']),
                request.form['rpc_user'],
                request.form['rpc_password']
            )
        try:
            update_nodes(rpc)
            flash('Nodes list updated', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('nodes'))
    data = get_data('nodes.json') or {'nodes': []}
    return render_template('nodes.html', nodes=data['nodes'])

# Select service node
@app.route('/nodes/select', methods=['POST'])
def select_node():
    node_url = request.form['node_url']
    try:
        km = KeyManager()
        km.selectNode(node_url)
        flash(f'Selected node: {node_url}', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('nodes'))

# Select current user
@app.route('/user', methods=['GET', 'POST'])
def user():
    km = KeyManager()
    users = list(km.listUsers())
    if request.method == 'POST':
        username = request.form['username']
        try:
            km.changeCurrentUser(username)
            flash(f'Current user set: {username}', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('user'))
    return render_template('user.html', users=users)

# Prepare NVS records
@app.route('/publish', methods=['POST'])
def publish():
    km = KeyManager()
    action = request.form['action']
    try:
        if action == 'user':
            km.prepareUserNVS()
        elif action == 'worm':
            km.prepareWormNVS()
        elif action == 'nodes':
            km.prepareNodesNVS()
        flash(f'{action.capitalize()} NVS prepared', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    return redirect(url_for('index'))

# Background task control
@app.route('/task/<task_id>/start', methods=['POST'])
def task_start(task_id):
    with tasks_lock:
        running_tasks[task_id] = {'status': 'running', 'progress': 0}
    return jsonify(running_tasks[task_id])

@app.route('/task/<task_id>/pause', methods=['POST'])
def task_pause(task_id):
    with tasks_lock:
        if task_id in running_tasks:
            running_tasks[task_id]['status'] = 'paused'
    return jsonify(running_tasks.get(task_id, {}))

@app.route('/task/<task_id>/resume', methods=['POST'])
def task_resume(task_id):
    with tasks_lock:
        if task_id in running_tasks:
            running_tasks[task_id]['status'] = 'running'
    return jsonify(running_tasks.get(task_id, {}))

@app.route('/task/<task_id>/progress', methods=['GET'])
def task_progress(task_id):
    return jsonify(running_tasks.get(task_id, {'status': 'unknown', 'progress': 0}))

if __name__ == '__main__':
   # app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
    app.run(host='0.0.0.0', port=5000, debug=True)