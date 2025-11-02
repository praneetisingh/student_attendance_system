# Virtual Environment Guide for Windows (Git Bash)

## Quick Reference

### Option 1: Activate Existing Virtual Environment (Git Bash)
```bash
cd student_attendance_system
source venv/Scripts/activate
```

### Option 2: Activate Existing Virtual Environment (Windows CMD)
```cmd
cd student_attendance_system
venv\Scripts\activate
```

### Option 3: Activate Existing Virtual Environment (PowerShell)
```powershell
cd student_attendance_system
venv\Scripts\Activate.ps1
```

---

## Creating a New Virtual Environment

If you need to create a fresh virtual environment:

### Step 1: Navigate to Project Directory
```bash
cd student_attendance_system
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
```

**OR** if you have multiple Python versions:
```bash
python3 -m venv venv
# OR specify Python version
py -3.10 -m venv venv
```

### Step 3: Activate the Virtual Environment

**For Git Bash (what you're using):**
```bash
source venv/Scripts/activate
```

**For Windows CMD:**
```cmd
venv\Scripts\activate.bat
```

**For PowerShell:**
```powershell
venv\Scripts\Activate.ps1
```

**Note:** If PowerShell gives an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Verify Activation

After activation, you should see `(venv)` at the beginning of your command prompt:
```
(venv) user@computer MINGW64 /c/Users/prane/OneDrive/Desktop/SE/student_attendance_system$
```

You can also verify by checking Python location:
```bash
which python
# Should show: .../student_attendance_system/venv/Scripts/python
```

---

## Common Issues & Solutions

### Issue 1: "source: command not found" or activation script doesn't work
**Solution:** Make sure you're using forward slashes and the correct path:
```bash
source venv/Scripts/activate
```
If this doesn't work, try:
```bash
. venv/Scripts/activate
```

### Issue 2: "No such file or directory"
**Solution:** Check you're in the correct directory:
```bash
pwd  # Should show you're in the student_attendance_system folder
ls venv/Scripts/  # Should show activate, activate.bat, etc.
```

### Issue 3: Python not found
**Solution:** Install Python or add it to PATH. Check Python installation:
```bash
python --version
python3 --version
py --version
```

### Issue 4: Permission denied
**Solution:** Run Git Bash as Administrator, or check file permissions:
```bash
ls -la venv/Scripts/activate
```

---

## Deactivate Virtual Environment

To deactivate (works in all shells):
```bash
deactivate
```

---

## Installing Packages

Once activated, install packages:
```bash
pip install package_name
```

To install from requirements file:
```bash
pip install -r requirements.txt
```

---

## Best Practices

1. **Always activate** before installing packages or running Python scripts
2. **Add venv to .gitignore** (so virtual environment isn't committed to Git)
3. **Create requirements.txt** after installing packages:
   ```bash
   pip freeze > requirements.txt
   ```






