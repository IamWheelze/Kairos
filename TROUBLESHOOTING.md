# Kairos Web UI - Troubleshooting Guide

## 🚨 Localhost Not Working? Follow These Steps:

### Step 1: Run the Development Script

**Windows - Use this script for detailed error checking:**
```cmd
run_dev.bat
```

This will:
- ✅ Check Python installation
- ✅ Check you're in the right directory
- ✅ Check dependencies are installed
- ✅ Check if port is available
- ✅ Start the server with detailed errors

---

### Step 2: Manual Debugging

If `run_dev.bat` doesn't work, try these steps manually:

#### A. Check Python Version
```cmd
python --version
```

**Expected:** Python 3.7.x or higher

**If not working:**
- Download Python from: https://www.python.org/downloads/
- During install, check "Add Python to PATH"
- Restart Command Prompt

#### B. Check You're in the Right Directory
```cmd
cd C:\Users\HP\OneDrive\Desktop\kaiross\Kairos
dir
```

**You should see:**
- run_web_ui.py
- run_web_ui.bat
- run_dev.bat
- requirements-webui.txt

#### C. Install Dependencies
```cmd
pip install -r requirements-webui.txt
```

**If this fails:**
```cmd
python -m pip install -r requirements-webui.txt
```

#### D. Run the Server Manually
```cmd
python run_web_ui.py
```

**Watch the output!** You should see:
```
============================================================
Kairos Voice-Activated Presentation Control - Web UI
============================================================

Starting web server...
Host: 0.0.0.0
Port: 8000

Open your browser and navigate to:
  http://localhost:8000
```

---

### Step 3: Common Issues & Solutions

#### Issue 1: "python is not recognized"

**Solution:**
1. Install Python from https://www.python.org/downloads/
2. **IMPORTANT:** Check "Add Python to PATH" during installation
3. Restart Command Prompt
4. Try again

#### Issue 2: "No module named 'fastapi'"

**Solution:**
```cmd
pip install -r requirements-webui.txt
```

Or install manually:
```cmd
pip install fastapi uvicorn jinja2 python-multipart websockets
```

#### Issue 3: "Address already in use" or Port 8000 taken

**Solution - Use a different port:**
```cmd
python run_web_ui.py --port 3000
```

Then open: http://localhost:3000

#### Issue 4: Server starts but browser shows "Can't reach this page"

**Possible causes:**

**A. Firewall blocking:**
- Windows Defender might block Python
- Click "Allow access" when prompted

**B. Wrong URL:**
- Try: http://127.0.0.1:8000
- Try: http://localhost:8000
- Try: http://0.0.0.0:8000

**C. Server crashed:**
- Look at the Command Prompt for error messages
- Copy any error messages and check below

#### Issue 5: Server crashes immediately

**Check the error message!**

Common errors:

**"ModuleNotFoundError"**
```cmd
pip install -r requirements-webui.txt
```

**"SyntaxError" or "TypeError"**
- You might have Python 2.x
- Upgrade to Python 3.7+

**"Permission denied"**
- Run Command Prompt as Administrator
- Right-click → "Run as administrator"

---

### Step 4: Test Installation

Run this diagnostic script:

```cmd
python -c "import sys; print(f'Python {sys.version}'); import fastapi; print('FastAPI OK'); import uvicorn; print('Uvicorn OK'); print('All dependencies installed!')"
```

**Expected output:**
```
Python 3.7.x ...
FastAPI OK
Uvicorn OK
All dependencies installed!
```

---

### Step 5: Still Not Working?

#### Check What's Running:

**See if something is listening on port 8000:**
```cmd
netstat -ano | findstr :8000
```

**Kill the process if needed:**
```cmd
taskkill /PID <process_id> /F
```

#### Try Completely Fresh Install:

```cmd
# 1. Delete and re-clone
cd Desktop
rmdir /s Kairos
git clone https://github.com/IamWheelze/Kairos.git
cd Kairos
git checkout claude/check-frd-status-011CUrcw9xEPUJapwgPRDxB4

# 2. Fresh install
pip install -r requirements-webui.txt

# 3. Run
python run_web_ui.py
```

---

## 🎯 Quick Diagnostic Checklist

Run these commands and note what fails:

```cmd
# 1. Python installed?
python --version

# 2. In right directory?
dir run_web_ui.py

# 3. Dependencies installed?
pip list | findstr fastapi

# 4. Can import modules?
python -c "import fastapi"

# 5. Port available?
netstat -ano | findstr :8000

# 6. Run server
python run_web_ui.py
```

---

## 📝 Collecting Error Information

If you need to ask for help, provide:

1. **Python version:**
   ```cmd
   python --version
   ```

2. **Installed packages:**
   ```cmd
   pip list
   ```

3. **Full error message** (copy everything from the Command Prompt)

4. **What command you ran** that caused the error

---

## 🔧 Alternative: Run with Python Directly

If the scripts don't work, try running the server module directly:

```cmd
cd C:\Users\HP\OneDrive\Desktop\kaiross\Kairos
set PYTHONPATH=%CD%\src
python -m uvicorn kairos.web.server:app --host 0.0.0.0 --port 8000
```

---

## ✅ Success Indicators

When everything works, you should see:

**In Command Prompt:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**In Browser (http://localhost:8000):**
- Beautiful dark gradient interface
- "Kairos" logo and header
- Three panels: Voice Control, Transcription, Presentation Control
- "Start System" button

---

## 🆘 Emergency: Just Want to See It Work?

Run this minimal test server:

```cmd
python -c "from http.server import HTTPServer, SimpleHTTPRequestHandler; HTTPServer(('', 8000), SimpleHTTPRequestHandler).serve_forever()"
```

Then open: http://localhost:8000

If THIS works, your network is fine and the issue is with the Kairos code.
If THIS doesn't work, you have a network/firewall issue.
