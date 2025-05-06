import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(PROJECT_ROOT)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
PARENT_DIR = os.path.dirname(os.path.abspath(__file__))  # D:\PrivateNessTools
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)
print("sys.path:", sys.path)
import logging
from flask import Flask, request, jsonify, send_file, render_template, g, abort
from werkzeug.utils import secure_filename
from framework.Container import Container
from utils.db import get_db, init_db
from NessKeys.Cryptors.Aes import Aes
from NessKeys.Cryptors.Salsa20 import Salsa20
from NessKeys.Cryptors.BlockCryptor import BlockCryptor
from NessKeys.Cryptors.PasswordCryptor import PasswordCryptor
from NessKeys.Cryptors.TextCryptor import TextCryptor

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(PROJECT_ROOT, 'uploaded_files')
app.secret_key = os.environ.get('SECRET_KEY', 'a-very-secret-key')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Custom Exceptions ---
class EncryptionError(Exception): pass
class DirectoryError(Exception): pass

# --- FileManager Wrapper ---
class FileManager:
    def __init__(self):
        self.fm = Container.FileManager()

    def upload_file(self, file, algorithm, key) -> dict:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            enc_filename = filename + '.enc'
            enc_file_path = os.path.join(app.config['UPLOAD_FOLDER'], enc_filename)

            # Read file data
            with open(file_path, 'rb') as f:
                data = f.read()

            # Encrypt data
            if algorithm == 'AES':
                cryptor = Aes()
            elif algorithm == 'Salsa20':
                cryptor = Salsa20()
            else:
                raise EncryptionError(f"Unsupported algorithm: {algorithm}")

            encrypted_data = cryptor.encrypt(data, key)
            with open(enc_file_path, 'wb') as f:
                f.write(encrypted_data)

            # Register in DB
            db = get_db()
            db.execute(
                'INSERT INTO files (shadowname, filename, algorithm, key) VALUES (?, ?, ?, ?)',
                (enc_filename, filename, algorithm, key)
            )
            db.commit()
            # Remove original file for security
            os.remove(file_path)

            return {"shadowname": enc_filename, "filename": filename, "algorithm": algorithm}
        except Exception as e:
            logger.error(f"Error uploading/encrypting file: {str(e)}")
            raise

    def download_file(self, shadowname: str) -> str:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], shadowname)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {shadowname} not found.")
        return file_path

    def decrypt_file(self, shadowname: str, key: str) -> str:
        # Get file and algorithm from DB
        db = get_db()
        file_row = db.execute('SELECT * FROM files WHERE shadowname=?', (shadowname,)).fetchone()
        if not file_row:
            raise FileNotFoundError(f"File {shadowname} not found in DB.")
        algorithm = file_row['algorithm']
        orig_filename = file_row['filename']

        enc_file_path = os.path.join(app.config['UPLOAD_FOLDER'], shadowname)
        dec_filename = orig_filename + '.dec'
        dec_file_path = os.path.join(app.config['UPLOAD_FOLDER'], dec_filename)

        with open(enc_file_path, 'rb') as f:
            enc_data = f.read()

        if algorithm == 'AES':
            cryptor = Aes()
        elif algorithm == 'Salsa20':
            cryptor = Salsa20()
        else:
            raise EncryptionError(f"Unsupported algorithm: {algorithm}")

        try:
            dec_data = cryptor.decrypt(enc_data, key)
        except Exception as e:
            raise EncryptionError("Decryption failed. Wrong key or corrupted file.")

        with open(dec_file_path, 'wb') as f:
            f.write(dec_data)

        return dec_file_path

    def list_files(self) -> list:
        db = get_db()
        files = db.execute('SELECT * FROM files').fetchall()
        return [dict(f) for f in files]

    def file_info(self, shadowname: str) -> dict:
        db = get_db()
        file = db.execute('SELECT * FROM files WHERE shadowname=?', (shadowname,)).fetchone()
        if not file:
            raise FileNotFoundError(f"File {shadowname} not found.")
        return dict(file)

file_manager = FileManager()
operation_states = {}

@app.before_first_request
def setup():
    init_db()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"success": False, "error": "No file part in the request"}), 400
    file = request.files["file"]
    algorithm = request.form.get("algorithm")
    key = request.form.get("key")
    if not algorithm or not key:
        return jsonify({"success": False, "error": "Algorithm and key are required"}), 400
    try:
        result = file_manager.upload_file(file, algorithm, key)
        return jsonify({"success": True, "file": result})
    except Exception as e:
        logger.exception("Upload failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/download/<shadowname>", methods=["GET"])
def download_file(shadowname):
    try:
        file_path = file_manager.download_file(shadowname)
        return send_file(file_path, as_attachment=True)
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.exception("Download failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/decrypt/<shadowname>", methods=["POST"])
def decrypt_file(shadowname):
    key = request.form.get("key")
    if not key:
        return jsonify({"success": False, "error": "Key is required"}), 400
    try:
        dec_file_path = file_manager.decrypt_file(shadowname, key)
        return send_file(dec_file_path, as_attachment=True)
    except EncryptionError as e:
        logger.exception("Decryption failed")
        return jsonify({"success": False, "error": str(e)}), 400
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.exception("Decryption failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/files/list", methods=["GET"])
def list_files():
    try:
        files = file_manager.list_files()
        return jsonify({"success": True, "files": files})
    except Exception as e:
        logger.exception("List files failed")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/files/info/<shadowname>", methods=["GET"])
def file_info(shadowname):
    try:
        info = file_manager.file_info(shadowname)
        return jsonify({"success": True, "info": info})
    except FileNotFoundError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        logger.exception("File info failed")
        return jsonify({"success": False, "error": str(e)}), 500

# --- Pause/Resume/Start/Progress endpoints ---
@app.route("/operation/start", methods=["POST"])
def start_operation():
    op_id = request.json.get("op_id")
    operation_states[op_id] = {"paused": False, "progress": 0}
    return jsonify({"success": True, "status": "started"})

@app.route("/operation/pause", methods=["POST"])
def pause_operation():
    op_id = request.json.get("op_id")
    if op_id not in operation_states:
        return jsonify({"success": False, "error": "Invalid operation ID"}), 400
    operation_states[op_id]["paused"] = True
    return jsonify({"success": True, "status": "paused"})

@app.route("/operation/resume", methods=["POST"])
def resume_operation():
    op_id = request.json.get("op_id")
    if op_id not in operation_states:
        return jsonify({"success": False, "error": "Invalid operation ID"}), 400
    operation_states[op_id]["paused"] = False
    return jsonify({"success": True, "status": "resumed"})

@app.route("/operation/progress", methods=["GET"])
def operation_progress():
    op_id = request.args.get("op_id")
    state = operation_states.get(op_id)
    if not state:
        return jsonify({"success": False, "error": "Invalid operation ID"}), 400
    return jsonify({"success": True, "progress": state["progress"], "paused": state["paused"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
