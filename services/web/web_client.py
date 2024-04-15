from flask import Flask, render_template
import subprocess

app = Flask(__name__, template_folder='../web')

@app.route('/')
def index():
    # Execute the 'node ls' command from Privatenys Tools
    result = subprocess.run(['python', '../../node.py', 'ls'], capture_output=True, text=True)
    if result.returncode == 0:
        # Split the output into a list of nodes
        nodes = result.stdout.strip().split('\n')
        return render_template('index.html', nodes=nodes)
    else:
        return "Error fetching node list"

if __name__ == '__main__':
    app.run(debug=True, threaded=True)