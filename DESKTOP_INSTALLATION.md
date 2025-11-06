# Kairos Web UI - Desktop Installation Guide

## Your Files Are Located At:
- **GitHub Repository**: https://github.com/IamWheelze/Kairos
- **Branch**: claude/check-frd-status-011CUrcw9xEPUJapwgPRDxB4

## Desktop Installation Steps:

### Step 1: Open Command Prompt or PowerShell
Press `Win + R`, type `cmd` or `powershell`, press Enter

### Step 2: Navigate to Desktop
```cmd
cd Desktop
```

### Step 3: Clone Repository
```cmd
git clone https://github.com/IamWheelze/Kairos.git
cd Kairos
```

### Step 4: Switch to Web UI Branch
```cmd
git checkout claude/check-frd-status-011CUrcw9xEPUJapwgPRDxB4
```

### Step 5: Install Dependencies

**Option A: Quick Install (Recommended)**
```cmd
pip install -r requirements.txt
```

**Option B: Full Installation (Better for development)**
```cmd
pip install -e .
```

If pip is not recognized, try:
```cmd
python -m pip install -r requirements.txt
```

### Step 6: Launch Web UI

**Windows Users - Double-click:**
```
run_web_ui.bat
```

**Or use Command Prompt:**
```cmd
python run_web_ui.py
```

**Or if you did full installation:**
```cmd
kairos-web
```

### Step 7: Open Browser
Navigate to: http://localhost:8000

---

## Troubleshooting:

### "ModuleNotFoundError: No module named 'kairos'"
**Solution 1: Use the updated script (already fixed)**
The run_web_ui.py script now automatically adds src to the path.

**Solution 2: Install the package properly**
```cmd
pip install -e .
```

**Solution 3: Set PYTHONPATH manually**
```cmd
set PYTHONPATH=%CD%\src
python run_web_ui.py
```

### "git is not recognized"
Install Git from: https://git-scm.com/download/win

### "python is not recognized"
Install Python from: https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation

### "pip is not recognized"
Use: `python -m pip install -r requirements.txt`

### Port 8000 already in use
Try a different port: `python run_web_ui.py --port 3000`

### Dependencies installation fails
Try installing dependencies one by one or use a virtual environment:
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## File Structure After Installation:

```
Desktop/
└── Kairos/
    ├── run_web_ui.py              ← Run this to start
    ├── requirements.txt
    ├── src/kairos/web/
    │   ├── server.py
    │   ├── templates/index.html
    │   └── static/
    │       ├── css/main.css
    │       └── js/main.js
    └── docs/web_ui_guide.md
```

---

## Quick Start Commands:

```cmd
# Navigate to Desktop
cd Desktop

# Go to Kairos folder
cd Kairos

# Run Web UI
python run_web_ui.py

# Open browser to http://localhost:8000
```

---

## What You'll See:

1. Command window will show:
   ============================================================
   Kairos Voice-Activated Presentation Control - Web UI
   ============================================================

   Starting web server...
   Host: 0.0.0.0
   Port: 8000

   Open your browser and navigate to:
     http://localhost:8000

2. Browser will show beautiful web interface with:
   - Voice control panel
   - Transcription display
   - Presentation controls
   - Settings panel

---

## Need Help?

- Full guide: docs/web_ui_guide.md
- GitHub: https://github.com/IamWheelze/Kairos/tree/claude/check-frd-status-011CUrcw9xEPUJapwgPRDxB4

Press Ctrl+C in the command window to stop the server.
