#!/usr/bin/env python3
"""
Single-file runner for Flask-React Template
This script automatically:
1. Checks Python version
2. Creates/activates virtual environment
3. Installs Python dependencies
4. Installs Node.js dependencies (if Node.js is available)
5. Initializes database
6. Starts Flask backend server (port 5000)
7. Starts React frontend server (port 3000)
8. Shows real-time output from both servers
"""

import os
import sys
import subprocess
import platform
import venv
import threading
import queue
import time
from pathlib import Path
import socket

# Fix encoding for Windows
if platform.system() == 'Windows':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# Colors for output (Windows compatible)
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.GREEN):
    """Print colored message (works on Windows 10+)"""
    if platform.system() == 'Windows':
        # Enable ANSI colors on Windows
        try:
            subprocess.run(['powershell', '-Command', '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8'], 
                          capture_output=True, check=False)
        except:
            pass
    print(f"{color}{message}{Colors.END}")

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print_colored("Error: Python 3.7 or higher is required", Colors.RED)
        sys.exit(1)
    print_colored(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected", Colors.GREEN)

def get_venv_path():
    """Get the path to the virtual environment"""
    backend_dir = Path(__file__).parent / "backend"
    return backend_dir / "venv"

def get_python_executable():
    """Get a working Python executable (prefer venv if valid)."""
    venv_path = get_venv_path()
    if _is_venv_valid(venv_path):
        if platform.system() == 'Windows':
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        return str(python_exe)
    return sys.executable

def _is_venv_valid(venv_path: Path) -> bool:
    """Validate that the venv was created on this system and is usable."""
    # Check python executable exists
    if platform.system() == 'Windows':
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"
    if not python_exe.exists():
        return False
    # Check pyvenv.cfg home points to an existing directory
    cfg_file = venv_path / 'pyvenv.cfg'
    if not cfg_file.exists():
        return False
    try:
        for line in cfg_file.read_text(errors='ignore').splitlines():
            if line.lower().startswith('home ='):
                home_path = line.split('=', 1)[1].strip()
                return Path(home_path).exists()
    except Exception:
        return False
    return False

def create_venv_if_needed():
    """Create virtual environment if it doesn't exist or is invalid"""
    venv_path = get_venv_path()
    
    if venv_path.exists():
        if _is_venv_valid(venv_path):
            print_colored(f"✓ Virtual environment found at {venv_path}", Colors.GREEN)
            return
        else:
            print_colored("⚠ Existing virtual environment is invalid. Recreating...", Colors.YELLOW)
            try:
                if platform.system() == 'Windows':
                    subprocess.run(['powershell', '-NoProfile', '-Command', f"Remove-Item -Recurse -Force '{str(venv_path)}'"], check=False)
                else:
                    subprocess.run(['rm', '-rf', str(venv_path)], check=False)
            except Exception:
                pass
    
    print_colored("Creating virtual environment...", Colors.YELLOW)
    try:
        venv.create(venv_path, with_pip=True)
        print_colored("✓ Virtual environment created", Colors.GREEN)
    except Exception as e:
        print_colored(f"Error creating virtual environment: {e}", Colors.RED)
        sys.exit(1)

def install_dependencies():
    """Install Python dependencies from requirements.txt"""
    backend_dir = Path(__file__).parent / "backend"
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print_colored(f"Warning: {requirements_file} not found", Colors.YELLOW)
        return
    
    python_exe = get_python_executable()
    print_colored("Installing Python dependencies...", Colors.YELLOW)
    
    # Try to upgrade pip, but don't fail if it doesn't work
    try:
        subprocess.run(
            [python_exe, "-m", "pip", "install", "--upgrade", "pip", "--quiet"],
            check=False,
            capture_output=True,
            timeout=60
        )
    except (subprocess.TimeoutExpired, Exception):
        pass  # Continue even if pip upgrade fails
    
    # Install dependencies
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", str(requirements_file), "--quiet"],
            check=False,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_colored("✓ Python dependencies installed", Colors.GREEN)
        else:
            # Check if packages are already installed
            if "already satisfied" in result.stdout.lower() or "requirement already satisfied" in result.stdout.lower():
                print_colored("✓ Python dependencies already installed", Colors.GREEN)
            else:
                print_colored(f"Warning: Some dependencies may not have installed correctly", Colors.YELLOW)
                print_colored("Continuing anyway...", Colors.YELLOW)
    except Exception as e:
        print_colored(f"Warning: Error installing dependencies: {e}", Colors.YELLOW)
        print_colored("Continuing anyway...", Colors.YELLOW)

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        print_colored(f"✓ Node.js {version} detected", Colors.GREEN)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("⚠ Node.js not found - Frontend will not be started", Colors.YELLOW)
        return False

def install_node_dependencies():
    """Install Node.js dependencies for frontend"""
    frontend_dir = Path(__file__).parent / "frontend"
    package_json = frontend_dir / "package.json"
    
    if not package_json.exists():
        print_colored(f"Warning: {package_json} not found", Colors.YELLOW)
        return False
    
    if not check_node_installed():
        return False
    
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists() and (node_modules / "react").exists():
        print_colored("✓ Frontend dependencies already installed", Colors.GREEN)
        return True
    
    print_colored("Installing frontend dependencies (this may take a while)...", Colors.YELLOW)
    try:
        original_dir = os.getcwd()
        os.chdir(frontend_dir)
        subprocess.run(['npm', 'install'], check=True, capture_output=False)
        print_colored("✓ Frontend dependencies installed", Colors.GREEN)
        return True
    except subprocess.CalledProcessError as e:
        print_colored(f"Error installing frontend dependencies: {e}", Colors.RED)
        return False
    finally:
        os.chdir(original_dir)

def initialize_database():
    """Initialize the database by running the Flask app initialization"""
    print_colored("Initializing database...", Colors.YELLOW)
    # Database will be created automatically when Flask app starts
    # The app.py already has db.create_all() in create_app()
    print_colored("✓ Database will be initialized on first run", Colors.GREEN)

def read_output(pipe, prefix, color, output_queue):
    """Read output from a subprocess pipe and add to queue"""
    try:
        for line in iter(pipe.readline, ''):
            if line:
                output_queue.put((prefix, color, line.rstrip()))
        pipe.close()
    except Exception as e:
        output_queue.put((prefix, color, f"Error reading output: {e}"))

def run_flask_app(output_queue):
    """Run the Flask application in a separate process"""
    backend_dir = Path(__file__).parent / "backend"
    app_file = backend_dir / "app.py"
    
    if not app_file.exists():
        print_colored(f"Error: {app_file} not found", Colors.RED)
        return None
    
    python_exe = get_python_executable()
    
    try:
        process = subprocess.Popen(
            [python_exe, str(app_file)],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start thread to read output
        thread = threading.Thread(
            target=read_output,
            args=(process.stdout, "[BACKEND]", Colors.CYAN, output_queue),
            daemon=True
        )
        thread.start()
        
        return process
    except Exception as e:
        output_queue.put(("[BACKEND]", Colors.RED, f"Error starting Flask: {e}"))
        return None

def _is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0

def _find_free_port(start_port: int) -> int:
    """Return the first available port >= start_port."""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(("", port))
                return port
            except OSError:
                port += 1

def run_frontend_app(output_queue):
    """Run the React frontend application in a separate process"""
    frontend_dir = Path(__file__).parent / "frontend"
    
    if not (frontend_dir / "package.json").exists():
        return None
    
    try:
        # Set environment variable to prevent browser auto-open
        env = os.environ.copy()
        env['BROWSER'] = 'none'
        # Choose an available port (default 3000, fallback to 3001+ if busy)
        chosen_port = 3000 if not _is_port_in_use(3000) else _find_free_port(3001)
        env['PORT'] = str(chosen_port)
        
        process = subprocess.Popen(
            ['npm', 'start'],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env,
            shell=(platform.system() == 'Windows')
        )
        
        # Start thread to read output
        thread = threading.Thread(
            target=read_output,
            args=(process.stdout, "[FRONTEND]", Colors.MAGENTA, output_queue),
            daemon=True
        )
        thread.start()
        
        # Inform about chosen port
        output_queue.put(("[FRONTEND]", Colors.GREEN, f"React server starting on http://localhost:{chosen_port}"))
        return process, chosen_port
    except Exception as e:
        output_queue.put(("[FRONTEND]", Colors.RED, f"Error starting React: {e}"))
        return None, None

def print_output(output_queue):
    """Print output from the queue"""
    while True:
        try:
            prefix, color, line = output_queue.get(timeout=0.1)
            print_colored(f"{prefix} {line}", color)
        except queue.Empty:
            continue

def run_servers(has_frontend):
    """Run both backend and optionally frontend, showing output"""
    print_colored("\n" + "="*70, Colors.BLUE)
    print_colored("Starting Application Servers", Colors.BOLD + Colors.BLUE)
    print_colored("="*70, Colors.BLUE)
    print_colored("Backend API:  http://localhost:5000", Colors.GREEN)
    frontend_port = 3000
    if has_frontend:
        print_colored("Frontend App: http://localhost:3000", Colors.GREEN)
    print_colored("\nAPI Endpoints:", Colors.GREEN)
    print_colored("  - GET    /api/tasks", Colors.GREEN)
    print_colored("  - POST   /api/tasks", Colors.GREEN)
    print_colored("  - PUT    /api/tasks/<id>", Colors.GREEN)
    print_colored("  - DELETE /api/tasks/<id>", Colors.GREEN)
    print_colored("  - GET    /api/tasks/<id>/comments", Colors.GREEN)
    print_colored("  - POST   /api/tasks/<id>/comments", Colors.GREEN)
    print_colored("  - PUT    /api/comments/<id>", Colors.GREEN)
    print_colored("  - DELETE /api/comments/<id>", Colors.GREEN)
    print_colored("="*70, Colors.BLUE)
    print_colored("\nPress Ctrl+C to stop all servers\n", Colors.YELLOW)
    
    # Create output queue for server logs
    output_queue = queue.Queue()
    
    # Start Flask backend
    flask_process = run_flask_app(output_queue)
    if not flask_process:
        print_colored("Failed to start Flask backend", Colors.RED)
        return
    
    # Give Flask a moment to start
    time.sleep(2)
    
    # Start React frontend if available
    frontend_process = None
    if has_frontend:
        frontend_process, frontend_port = run_frontend_app(output_queue)
        if frontend_process:
            print_colored(f"Frontend server starting on port {frontend_port}...", Colors.YELLOW)
        time.sleep(3)
    
    # Print output from both servers
    try:
        while True:
            # Check if processes are still alive
            if flask_process.poll() is not None:
                print_colored("\n[BACKEND] Flask server stopped unexpectedly", Colors.RED)
                break
            
            if frontend_process and frontend_process.poll() is not None:
                print_colored("\n[FRONTEND] React server stopped unexpectedly", Colors.RED)
                break
            
            # Print any queued output
            print_output(output_queue)
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print_colored("\n\n" + "="*70, Colors.YELLOW)
        print_colored("Shutting down servers...", Colors.YELLOW)
        print_colored("="*70, Colors.YELLOW)
        
        # Terminate processes
        if flask_process:
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                flask_process.kill()
        
        if frontend_process:
            frontend_process.terminate()
            try:
                frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frontend_process.kill()
        
        print_colored("All servers stopped. Goodbye!", Colors.GREEN)
        sys.exit(0)

def main():
    """Main function to orchestrate the setup and run process"""
    print_colored("\n" + "="*70, Colors.BOLD + Colors.BLUE)
    print_colored("Flask-React Template - Auto Setup & Run", Colors.BOLD + Colors.BLUE)
    print_colored("="*70 + "\n", Colors.BLUE)
    
    # Step 1: Check Python version
    check_python_version()
    
    # Step 2: Create virtual environment
    create_venv_if_needed()
    
    # Step 3: Install Python dependencies
    install_dependencies()
    
    # Step 4: Check Node.js and install frontend dependencies
    has_frontend = install_node_dependencies()
    
    # Step 5: Initialize database (will be done automatically)
    initialize_database()
    
    # Step 6: Run both servers with output
    run_servers(has_frontend)

if __name__ == "__main__":
    main()
