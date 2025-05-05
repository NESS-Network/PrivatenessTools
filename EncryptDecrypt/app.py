import sys
import os
PROJECT_ROOT = os.path.dirname (os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import logging
from flask import (
    Flask, request, jsonify, send_file, render_template, g
)
from werkzeug.utils import secure_filename
from framework.Container import Container
from utils.db import get_db, init_db
from typing import List, Dict

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_files'
app.secret_key = os.environ.get('SECRET_KEY', 'a-very-secret-key')

# --- Ensure upload folder exists ---
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Custom Exceptions ---
class EncryptionError(Exception): pass
class DirectoryError(Exception): pass

# --- FileManager Wrapper ---
class FileManager:
    def __init__(self):
        self.fm = Container.FileManager()

    def upload_file(self, file, encrypt: bool = False) -> Dict:
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Register in DB
            db = get_db()
            db.execute(
                'INSERT INTO files (shadowname, filename, algorithm) VALUES (?, ?, ?)',
                (filename, filename, request.form.get('algorithm', 'none'))
            )
            db.commit()
            return {"shadowname": filename, "filename": filename}
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise

    def download_file(self, shadowname: str) -> str:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], shadowname)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {shadowname} not found.")
        return file_path

    def list_files(self) -> List[Dict]:
        db = get_db()
        files = db.execute('SELECT * FROM files').fetchall()
        return [dict(f) for f in files]

    def file_info(self, shadowname: str) -> Dict:
        db = get_db()
        file = db.execute('SELECT * FROM files WHERE shadowname=?', (shadowname,)).fetchone()
        if not file:
            raise FileNotFoundError(f"File {shadowname} not found.")
        return dict(file)

file_manager = FileManager()

# --- Operation State (for Pause/Resume/Progress) ---
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
    try:
        result = file_manager.upload_file(file)
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