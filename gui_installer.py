import os
import sys
import json
import subprocess
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXE = sys.executable
ICON_FILE = os.path.join(SCRIPT_DIR, "icons", "favicon.ico")

def create_shortcuts(desktop=False):
    try:
        launch_bat = os.path.join(SCRIPT_DIR, "launch.bat")
        install_bat = os.path.join(SCRIPT_DIR, "install.bat")
        
        # 1. Project Folder Shortcut: Launch TTRPG Generator
        # 2. Project Folder Shortcut: Setup & Repair
        # 3. Desktop Shortcut (Optional): TTRPG Generator
        
        ps_script = f"""
$sh = New-Object -ComObject WScript.Shell;

# Helper to create shortcut
function New-BrandedShortcut {{
    param($Path, $Target, $WorkingDir, $Icon)
    $s = $sh.CreateShortcut($Path)
    $s.TargetPath = $Target
    $s.WorkingDirectory = $WorkingDir
    $s.IconLocation = $Icon
    $s.Save()
}}

# Root Shortcuts
New-BrandedShortcut -Path "{os.path.join(SCRIPT_DIR, 'Launch TTRPG Generator.lnk')}" -Target "{launch_bat}" -WorkingDir "{SCRIPT_DIR}" -Icon "{ICON_FILE}"
New-BrandedShortcut -Path "{os.path.join(SCRIPT_DIR, 'Setup & Repair.lnk')}" -Target "{install_bat}" -WorkingDir "{SCRIPT_DIR}" -Icon "{ICON_FILE}"
"""
        
        if desktop:
            ps_script += f"""
# Desktop Shortcut
$desktopPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'TTRPG Generator.lnk'
New-BrandedShortcut -Path $desktopPath -Target "{launch_bat}" -WorkingDir "{SCRIPT_DIR}" -Icon "{ICON_FILE}"
"""
            
        subprocess.run(["powershell", "-Command", ps_script], check=True)
        return True, "Shortcuts created successfully."
    except Exception as e:
        return False, f"Failed to create shortcuts: {str(e)}"

def install_dependencies():
    try:
        req_file = os.path.join(SCRIPT_DIR, "requirements.txt")
        if os.path.exists(req_file):
            subprocess.run([PYTHON_EXE, "-m", "pip", "install", "-r", req_file], check=True)
        return True, "Dependencies installed."
    except Exception as e:
        return False, f"Dependency installation failed: {str(e)}"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>TTRPG Card Generator - Installation</title>
    <link rel="icon" type="image/svg+xml" href="/icons/favicon.svg">
    <style>
        body { font-family: Arial, sans-serif; margin: 2rem; background: #f4f4f4; color: #111; }
        .panel { max-width: 600px; margin: auto; padding: 2rem; background: white; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,.1); }
        h1 { margin-top: 0; color: #2d7aeb; display: flex; align-items: center; gap: 15px; }
        .step { margin-bottom: 1rem; padding: 1rem; border-radius: 8px; background: #fafafa; border: 1px solid #eee; }
        .step-active { border-color: #2d7aeb; background: #f0f7ff; }
        .step-done { border-color: #2e7d32; background: #f1f8e9; }
        .btn { display: inline-block; padding: 0.75rem 1.5rem; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; text-decoration: none; transition: background 0.2s; }
        .btn-primary { background: #2d7aeb; color: white; }
        .btn-primary:hover { background: #215ec8; }
        .status { margin-top: 1rem; padding: 1rem; border-radius: 6px; }
        .status-success { background: #e8f5e9; color: #2e7d32; }
        .status-error { background: #ffebee; color: #c62828; }
        .checkbox-group { margin: 1.5rem 0; display: flex; align-items: center; gap: 10px; font-weight: bold; cursor: pointer; }
        input[type="checkbox"] { width: 20px; height: 20px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="panel">
        <h1>
            <img src="/icons/favicon.svg" width="40" height="40">
            Installation Complete
        </h1>
        
        <p>The TTRPG Card Generator has been successfully set up on your system.</p>
        
        <div class="step step-done">
            <strong>✓ Environment Ready</strong>
            <p style="font-size: 0.9em; color: #666; margin: 5px 0 0 0;">Python and Git are configured.</p>
        </div>

        <div id="status" class="status" style="display:none;"></div>

        <label class="checkbox-group">
            <input type="checkbox" id="create-shortcut" checked>
            Create Desktop Shortcut
        </label>
        
        <button class="btn btn-primary" onclick="finishSetup()">Finish Setup & Launch</button>
    </div>

    <script>
        async function finishSetup() {
            const createShortcut = document.getElementById('create-shortcut').checked;
            const status = document.getElementById('status');
            
            status.style.display = 'block';
            status.className = 'status';
            status.textContent = 'Finalizing shortcuts and environment...';
            
            try {
                const resp = await fetch(`/finish?shortcut=${createShortcut}`);
                const data = await resp.json();
                
                if (data.success) {
                    status.className = 'status status-success';
                    status.textContent = 'Setup complete! Launching generator and closing this tab...';
                    
                    // Close tab after a short delay
                    setTimeout(() => {
                        window.close();
                        // Fallback
                        document.body.innerHTML = '<div class="panel"><h1>Done</h1><p>You can close this tab now. Branded shortcuts have been added to your folder.</p></div>';
                    }, 1500);
                } else {
                    status.className = 'status status-error';
                    status.textContent = data.message;
                }
            } catch (e) {
                status.className = 'status status-error';
                status.textContent = 'An error occurred: ' + e;
            }
        }
    </script>
</body>
</html>"""

class InstallerRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
            return
            
        elif parsed.path == '/finish':
            params = parse_qs(parsed.query)
            do_shortcut = params.get('shortcut', ['false'])[0].lower() == 'true'
            
            # Always create folder shortcuts, conditionally create desktop shortcut
            success, message = create_shortcuts(desktop=do_shortcut)
            
            if success:
                # Write a lock file if not present
                with open(os.path.join(SCRIPT_DIR, "install.lock"), "w") as f:
                    f.write("Setup complete")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                
                # Small delay to ensure the browser receives the response before we shut down
                import threading
                import time
                def delayed_launch():
                    time.sleep(1)
                    subprocess.Popen(["cmd", "/c", "launch.bat"], shell=True)
                    os._exit(0)
                threading.Thread(target=delayed_launch).start()
            else:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "message": message}).encode('utf-8'))
            return

        elif parsed.path.startswith('/icons/'):
            return super().do_GET()

        super().do_GET()

def serve_installer(port=8002):
    server_address = ('', port)
    httpd = HTTPServer(server_address, InstallerRequestHandler)
    url = f'http://localhost:{port}/'
    print(f'Installation complete. Please finish setup at {url}')
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()

if __name__ == '__main__':
    # Run the technical parts first (silent)
    install_dependencies()
    serve_installer()
