import os
import sys
import json
import subprocess
import zipfile
import shutil
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GENERATORS_DIR = os.path.join(SCRIPT_DIR, "generators")
DATA_DIR = os.path.join(GENERATORS_DIR, "data")
GIT_EXE = os.path.join(SCRIPT_DIR, "git-portable", "bin", "git.exe")

def get_git_cmd():
    # Try system git first
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return "git"
    except:
        if os.path.exists(GIT_EXE):
            return GIT_EXE
    return None

def setup_from_git(repo_url):
    git_cmd = get_git_cmd()
    if not git_cmd:
        return False, "Git not found. Please install Git or use a ZIP file."
    
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    
    try:
        subprocess.run([git_cmd, "clone", repo_url, DATA_DIR], check=True)
        return True, "Successfully cloned repository."
    except Exception as e:
        return False, f"Git clone failed: {str(e)}"

def setup_from_zip(zip_path):
    if not os.path.exists(zip_path):
        return False, "ZIP file not found."
    
    if os.path.exists(DATA_DIR):
        shutil.rmtree(DATA_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check if there's a top-level folder in the zip
            top_level_folders = {os.path.split(n)[0] for n in zip_ref.namelist() if '/' in n}
            
            # Simple heuristic: if most files are inside a single folder, extract that folder's contents
            members = zip_ref.namelist()
            if members:
                first_part = members[0].split('/')[0]
                if all(m.startswith(first_part + '/') for m in members):
                    # Extract and move
                    temp_extract = os.path.join(GENERATORS_DIR, "temp_zip")
                    zip_ref.extractall(temp_extract)
                    src_path = os.path.join(temp_extract, first_part)
                    for item in os.listdir(src_path):
                        shutil.move(os.path.join(src_path, item), DATA_DIR)
                    shutil.rmtree(temp_extract)
                else:
                    zip_ref.extractall(DATA_DIR)
            
        return True, "Successfully extracted ZIP."
    except Exception as e:
        return False, f"ZIP extraction failed: {str(e)}"

def is_data_ready():
    # Check for critical paths
    # We expect generators/data/data/class and generators/data/data/spells
    class_dir = os.path.join(DATA_DIR, "data", "class")
    spells_dir = os.path.join(DATA_DIR, "data", "spells")
    return os.path.isdir(class_dir) and os.path.isdir(spells_dir)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TTRPG Card Generator - Setup</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; background: #f4f4f4; color: #111; }
        .panel { max-width: 600px; margin: auto; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.1); }
        h1 { margin-top: 0; color: #2d7aeb; }
        .form-group { margin-bottom: 1.5rem; }
        label { display: block; font-weight: bold; margin-bottom: 0.5rem; }
        input[type="text"], input[type="file"] { width: 100%; padding: 0.75rem; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; transition: background 0.2s; }
        .btn-primary { background: #2d7aeb; color: white; }
        .btn-primary:hover { background: #215ec8; }
        .status { margin-top: 1rem; padding: 1rem; border-radius: 6px; display: none; }
        .status-success { background: #e8f5e9; color: #2e7d32; display: block; }
        .status-error { background: #ffebee; color: #c62828; display: block; }
        .help-text { font-size: 0.85em; color: #666; margin-top: 0.25rem; }
    </style>
</head>
<body>
    <div class="panel">
        <h1>Welcome to TTRPG Card Generator</h1>
        <p>It looks like you haven't set up your data source yet. This tool requires a dataset following the 5etools structure (containing a <code>data/</code> folder with <code>class/</code>, <code>spells/</code>, etc.).</p>
        
        <div id="setup-form">
            <div class="form-group">
                <label>Option 1: Clone from Git Repository</label>
                <input type="text" id="repo-url" placeholder="https://github.com/your-repo-name-here">
                <p class="help-text">Enter the URL of a 5etools-compatible data repository.</p>
                <button class="btn btn-primary" onclick="setupGit()">Clone Repository</button>
            </div>
            
            <hr>
            
            <div class="form-group">
                <label>Option 2: Extract from Local ZIP</label>
                <input type="text" id="zip-path" placeholder="C:\\path\\to\\data.zip">
                <p class="help-text">Enter the full absolute path to a local ZIP file containing the data.</p>
                <button class="btn btn-primary" onclick="setupZip()">Extract ZIP</button>
            </div>
        </div>

        <div id="status" class="status"></div>
        
        <div id="launch-panel" style="display: __LAUNCH_DISPLAY__; margin-top: 2rem; border-top: 2px solid #eee; padding-top: 1rem;">
            <p style="color: #2e7d32; font-weight: bold;">Data is ready!</p>
            <button class="btn btn-primary" onclick="launchGenerator()">Launch Card Generator</button>
            <button class="btn" style="background: #eee;" onclick="toggleSetup()">Manage Data Source</button>
        </div>
    </div>

    <script>
        function setStatus(msg, isError) {
            const s = document.getElementById('status');
            s.textContent = msg;
            s.className = 'status ' + (isError ? 'status-error' : 'status-success');
        }

        async function setupGit() {
            const url = document.getElementById('repo-url').value;
            if (!url) return alert('Please enter a URL');
            setStatus('Cloning repository... this may take a minute.', false);
            const resp = await fetch('/setup?type=git&url=' + encodeURIComponent(url));
            const data = await resp.json();
            if (data.success) {
                location.reload();
            } else {
                setStatus(data.message, true);
            }
        }

        async function setupZip() {
            const path = document.getElementById('zip-path').value;
            if (!path) return alert('Please enter a path');
            setStatus('Extracting ZIP...', false);
            const resp = await fetch('/setup?type=zip&path=' + encodeURIComponent(path));
            const data = await resp.json();
            if (data.success) {
                location.reload();
            } else {
                setStatus(data.message, true);
            }
        }

        async function launchGenerator() {
            window.location.href = '/launch';
        }

        function toggleSetup() {
            const f = document.getElementById('setup-form');
            f.style.display = f.style.display === 'none' ? 'block' : 'none';
        }

        if (document.getElementById('launch-panel').style.display === 'block') {
            document.getElementById('setup-form').style.display = 'none';
        }
    </script>
</body>
</html>"""

class LauncherRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            ready = is_data_ready()
            html = HTML_TEMPLATE.replace('__LAUNCH_DISPLAY__', 'block' if ready else 'none')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            return
        
        elif parsed.path == '/setup':
            params = parse_qs(parsed.query)
            stype = params.get('type', [''])[0]
            success = False
            message = ""
            
            if stype == 'git':
                url = params.get('url', [''])[0]
                success, message = setup_from_git(url)
            elif stype == 'zip':
                path = params.get('path', [''])[0]
                success, message = setup_from_zip(path)
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success, "message": message}).encode('utf-8'))
            return

        elif parsed.path == '/launch':
            if is_data_ready():
                # Shutdown this server and start card_controller.py
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Launching...")
                
                # Start card_controller in a new process
                subprocess.Popen([sys.executable, "card_controller.py"])
                
                # Exit the launcher
                os._exit(0)
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Data not ready.")
                return

        super().do_GET()

def serve_launcher(port=8001):
    server_address = ('', port)
    httpd = HTTPServer(server_address, LauncherRequestHandler)
    url = f'http://localhost:{port}/'
    print(f'Starting Setup Launcher at {url}')
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    serve_launcher()
