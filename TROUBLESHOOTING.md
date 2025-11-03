# Troubleshooting Common Errors

## Common Errors and Solutions

### Error 1: "gunicorn: command not found"
**Solution:**
```bash
# Activate virtual environment first
source venv/Scripts/activate
# Install gunicorn
pip install gunicorn
```

### Error 2: "python: command not found" or "python3: command not found"
**Solution:**
- Try `python3` instead of `python`
- Or `py` on Windows
- Or check your Python installation and PATH

### Error 3: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
# Activate virtual environment
source venv/Scripts/activate
# Install dependencies
pip install -r requirements.txt
```

### Error 4: "Address already in use" or "Port 5000 is already in use"
**Solution:**
```bash
# Windows (Git Bash)
netstat -ano | findstr :5000
# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or change port in start.sh to 5001
```

### Error 5: "Permission denied" when running start.sh
**Solution:**
```bash
# Make script executable
chmod +x start.sh
# Or run directly with bash
bash start.sh
```

### Error 6: "bash: ./start.sh: /bin/bash: bad interpreter"
**Solution (Windows Git Bash):**
- Use `bash start.sh` instead of `./start.sh`
- Or use the Windows batch file: `start.bat`

### Error 7: "ImportError" or "No module named 'app'"
**Solution:**
- Make sure you're in the correct directory: `cd student_attendance_system`
- Check that `app.py` exists in the current directory

---

## Quick Fixes

### For Windows Users (Git Bash):

1. **Activate virtual environment:**
```bash
source venv/Scripts/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run in development mode (easiest):**
```bash
python app.py
```

4. **Or use the batch file:**
```bash
start.bat
```

### For Production Testing (Gunicorn):

If gunicorn doesn't work on Windows, you can:
1. Use development mode: `python app.py`
2. Or test on Render directly (which supports gunicorn on Linux)

---

## Still Having Issues?

Please share:
1. The exact error message you're seeing
2. What command you ran
3. Whether virtual environment is activated
4. Your operating system

