import sys
import os
import threading
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import subprocess
# extend PYTHONPATH to project root
dir_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, dir_root)

# Import container for dependency injection
from framework.Container import Container
# Import key management and cryptors from NessKeys
from NessKeys.KeyManager import KeyManager
from services.node import node as NodesUpdater
from NessKeys.cryptors.Aes import Aes as AESCipher
from NessKeys.cryptors.Salsa20 import Salsa20 as Salsa20Cipher
from NessKeys.JsonChecker.Checker import JsonChecker

# Initialize Flask app
def create_app():
    app = Flask(__name__)
    # Configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('FLASK_SECRET', 'supersecret'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', os.path.join(dir_root, 'uploads')),
        NODES_JSON=os.environ.get('NODES_JSON', os.path.join(dir_root, 'nodes.json')),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB limit
    )

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Thread-safe storage for background tasks
    tasks_lock = threading.Lock()
    running_tasks = {}

    # Helpers
    def get_km():
        return Container.KeyManager()
    filemgr = Container.FileManager()

    # ----- Routes -----

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/keygen', methods=['GET', 'POST'])
    def keygen():
        if request.method == 'GET':
            return render_template('keygen.html')
        username = request.form['username']
        entropy = int(request.form.get('entropy', 256))
        try:
            km = get_km()
            km.createUsersKey(username, entropy)
            flash(f'User key generated: {username}', 'success')
        except Exception as e:
            flash(f'Error generating key: {e}', 'danger')
        return redirect(url_for('keygen'))

    @app.route('/nodes', methods=['GET', 'POST'])
    def nodes():
        km = get_km()
        if request.method == 'POST':
            mode = request.form['mode']
            try:
                if mode == 'public':
                    NodesUpdater.fetch_public_list()
                    flash('Public list fetched', 'success')
                else:
                    rpc = {
                        'host': request.form['rpc_host'],
                        'port': request.form['rpc_port'],
                        'user': request.form['rpc_user'],
                        'password': request.form['rpc_password']
                    }
                    NodesUpdater.update_blockchain(rpc, app.config['NODES_JSON'])
                    flash('Updated from RPC', 'success')
            except Exception as e:
                flash(f'Error managing nodes: {e}', 'danger')
            return redirect(url_for('nodes'))
        nodes = km.listNodes()
        return render_template('nodes.html', nodes=nodes)

    @app.route('/node', methods=['POST'])
    def select_node():
        """Mark a node as selected in the nodes.json file, creating it if missing."""
        node_url = request.form['node_url']
        nodes_file = app.config['NODES_JSON']
        try:
            # Load or initialize nodes JSON
            if not os.path.exists(nodes_file):
                data = {'nodes': [], 'selected_node': node_url}
            else:
                with open(nodes_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
                # Ensure dict
                if not isinstance(data, dict):
                    data = {'nodes': data}
                data['selected_node'] = node_url
            # Write back
            with open(nodes_file, 'w') as f:
                json.dump(data, f, indent=2)
            flash(f'Node selected: {node_url}', 'success')
        except Exception as e:
            flash(f'Error selecting node: {e}', 'danger')
        return redirect(url_for('nodes'))

    @app.route('/user', methods=['GET', 'POST'])
    def user():
        # POST: perform sel | nvs | worm via user.py
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            action   = request.form.get('action', '').strip()

            if not username:
                flash('Please select a user first.', 'warning')
                return redirect(url_for('user'))

            if action not in ('sel', 'nvs', 'worm'):
                flash('Invalid action.', 'danger')
                return redirect(url_for('user'))

            cli = os.path.join(dir_root, 'user.py')
            cmd = [sys.executable, cli, action, username]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=dir_root,
                    capture_output=True,
                    text=True,
                    check=True
                )
                # Use stdout if available, else fallback to a canned message
                out = result.stdout.strip() or f'User {action} completed for {username}.'
                flash(out, 'success')
            except subprocess.CalledProcessError as e:
                err = e.stderr.strip() or e.stdout.strip() or str(e)
                flash(f'Error ({action}): {err}', 'danger')

            return redirect(url_for('user'))

        # GET: fetch users via `user.py ls`
        users = []
        cli = os.path.join(dir_root, 'user.py')
        try:
            result = subprocess.run(
                [sys.executable, cli, 'ls'],
                cwd=dir_root,
                capture_output=True,
                text=True,
                check=True
            )
            for line in result.stdout.splitlines():
                line = line.strip()
                # Lines that start with '|' and contain real content
                if line.startswith('|') and not set(line.strip()).issubset({'|','-'}):
                    name = line.strip('|').strip()
                    # strip CLI arrows: ==> user <==
                    name = name.replace('==>', '').replace('<==', '').strip()
                    if name.lower() != 'username':
                        users.append(name)
        except subprocess.CalledProcessError as e:
            flash('Failed to fetch users. Please ensure user.py is working.', 'danger')

        return render_template('user.html', users=users)

    @app.route('/publish', methods=['GET', 'POST'])
    def publish():
        if request.method == 'GET':
            return render_template('publish.html')
        action = request.form['action']
        try:
            km = get_km()
            if action == 'user':
                km.prepareUserNVS()
            elif action == 'worm':
                km.prepareWormNVS()
            elif action == 'nodes':
                km.prepareNodesNVS()
            flash('Prepared NVS records', 'success')
        except Exception as e:
            flash(f'Error preparing NVS: {e}', 'danger')
        return redirect(url_for('publish'))

    # File system operations
    @app.route('/upload', methods=['POST'])
    def upload():
        file = request.files['file']
        dest = request.form.get('destination', '')
        try:
            filemgr.upload(file, dest)
            flash('Upload successful', 'success')
        except Exception as e:
            flash(f'Error uploading: {e}', 'danger')
        return redirect(url_for('index'))

    @app.route('/download')
    def download():
        path = request.args.get('path')
        try:
            return filemgr.download(path)
        except Exception as e:
            flash(f'Error downloading: {e}', 'danger')
            return redirect(url_for('index'))

    @app.route('/mkdir', methods=['POST'])
    def mkdir():
        path = request.form['path']
        try:
            filemgr.mkdir(path)
            flash('Directory created', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))

    @app.route('/rmdir', methods=['POST'])
    def rmdir():
        path = request.form['path']
        try:
            filemgr.rmdir(path)
            flash('Directory removed', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))

    @app.route('/ls')
    def ls():
        path = request.args.get('path', '')
        try:
            return jsonify(filemgr.ls(path))
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/move', methods=['POST'])
    def move():
        src = request.form['src']
        dst = request.form['dst']
        try:
            filemgr.move(src, dst)
            flash('Move successful', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))

    @app.route('/remove', methods=['POST'])
    def remove():
        path = request.form['path']
        try:
            filemgr.remove(path)
            flash('Removed', 'success')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        return redirect(url_for('index'))

    @app.route('/tree')
    def tree():
        root = request.args.get('root', '')
        try:
            return jsonify(filemgr.tree(root))
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/quota')
    def quota():
        try:
            return jsonify(filemgr.quota())
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/fileinfo')
    def fileinfo():
        path = request.args.get('path')
        try:
            return jsonify(filemgr.fileinfo(path))
        except Exception as e:
            return jsonify({'error': str(e)})

    # Encryption/Decryption
    @app.route('/encrypt', methods=['GET', 'POST'], endpoint='encrypt_route')
    def encrypt():
        if request.method == 'GET':
            return render_template('encrypt.html')
        algorithm = request.form['algorithm']
        file = request.files['file']
        km = get_km()
        key = km.getCurrentKey()  # uses selected user context
        cipher = AESCipher(key) if algorithm == 'aes' else Salsa20Cipher(key)
        infile = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(infile)
        outfile = cipher.encrypt_file(infile)
        metadata = cipher.get_metadata()
        return render_template('encrypt_result.html', filename=os.path.basename(outfile), metadata=metadata)

    @app.route('/decrypt', methods=['GET', 'POST'], endpoint='decrypt_route')
    def decrypt():
        if request.method == 'GET':
            return render_template('decrypt.html')
        algorithm = request.form['algorithm']
        key_hex = request.form['key']
        nonce = request.form.get('nonce')
        iv = request.form.get('iv')
        file = request.files['file']
        key = bytes.fromhex(key_hex)
        cipher = AESCipher(key, iv=bytes.fromhex(iv)) if algorithm == 'aes' else Salsa20Cipher(key, nonce=bytes.fromhex(nonce))
        infile = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(infile)
        outfile = cipher.decrypt_file(infile)
        return render_template('decrypt_result.html', filename=os.path.basename(outfile))

    # Background tasks
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
