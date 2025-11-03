# Testing Guide - Student Attendance System

This guide covers how to run the application locally, test with curl, and verify deployment status on Render.

---

## 📋 Table of Contents
1. [Running Locally](#running-locally)
2. [Testing with cURL](#testing-with-curl)
3. [Testing Render Deployment](#testing-render-deployment)

---

## 🚀 Running Locally

### Step 1: Activate Virtual Environment
```bash
cd student_attendance_system
source venv/Scripts/activate  # For Git Bash
```

### Step 2: Install Dependencies (if not already installed)
```bash
pip install -r requirements.txt
```

### Step 3: Run the Application

**Option A: Development Mode (Flask's built-in server)**
```bash
python app.py
```
The app will start on `http://127.0.0.1:5000` (default Flask port)

**Option B: Production Mode (using Gunicorn via start.sh)**
```bash
chmod +x start.sh  # Make script executable (Linux/Mac/Git Bash)
./start.sh
```
Or run the commands manually:
```bash
python -c "from app import app, db, populate_initial_data; with app.app_context(): db.create_all(); populate_initial_data()"
gunicorn app:app
```

---

## 🧪 Testing with cURL

All examples assume the app is running on `http://127.0.0.1:5000` (local) or your Render URL (production).

### 1. Health Check (Test if API is running)
```bash
curl http://127.0.0.1:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Student Attendance System API is running",
  "database": "connected"
}
```

### 2. Mark Attendance (POST Request)

**Request:**
```bash
curl -X POST http://127.0.0.1:5000/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {
        "enroll_no": "S1001",
        "status": "Present"
      },
      {
        "enroll_no": "S1002",
        "status": "Absent"
      }
    ]
  }'
```

**Expected Response:**
```json
{
  "message": "Attendance marked successfully for 2 students."
}
```

**Test Error Cases:**

**Unauthorized Faculty (403):**
```bash
curl -X POST http://127.0.0.1:5000/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F999",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"}
    ]
  }'
```

**Expected Response:**
```json
{
  "message": "Authorization failed. Faculty not assigned."
}
```

### 3. View Attendance Report (GET Request)

**Request:**
```bash
curl http://127.0.0.1:5000/api/report/S1001
```

**Expected Response:**
```json
{
  "student_name": "Alice Smith",
  "enroll_no": "S1001",
  "summary": {
    "total_classes": 1,
    "present_count": 1,
    "absent_count": 0,
    "percentage": "100.00%"
  },
  "detailed_history": [
    {
      "date": "2024-01-15",
      "course_id": "CS101",
      "status": "Present"
    }
  ]
}
```

**Test Student Not Found (404):**
```bash
curl http://127.0.0.1:5000/api/report/S9999
```

**Expected Response:**
```json
{
  "message": "Error: Student S9999 not found."
}
```

### 4. Complete Test Sequence

Run these commands in order to test the full workflow:

```bash
# 1. Check health
curl http://127.0.0.1:5000/health

# 2. Mark attendance for both students
curl -X POST http://127.0.0.1:5000/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"},
      {"enroll_no": "S1002", "status": "Present"}
    ]
  }'

# 3. View report for Student 1
curl http://127.0.0.1:5000/api/report/S1001

# 4. View report for Student 2
curl http://127.0.0.1:5000/api/report/S1002

# 4. Mark attendance again (should update existing records)
curl -X POST http://127.0.0.1:5000/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Absent"},
      {"enroll_no": "S1002", "status": "Present"}
    ]
  }'

# 5. Check updated reports
curl http://127.0.0.1:5000/api/report/S1001
curl http://127.0.0.1:5000/api/report/S1002
```

---

## 🌐 Testing Render Deployment

### Step 1: Deploy to Render

1. Push your code to GitHub/GitLab
2. Create a new **Web Service** on Render
3. Connect your repository
4. Configure build settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `bash start.sh` or `gunicorn app:app`
   - **Environment:** Python 3

### Step 2: Verify Deployment Status

After deployment, Render will provide a URL like: `https://your-app-name.onrender.com`

**Check Health Status:**
```bash
curl https://your-app-name.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Student Attendance System API is running",
  "database": "connected"
}
```

### Step 3: Test All Endpoints on Render

Replace `https://your-app-name.onrender.com` with your actual Render URL:

```bash
# Health check
curl https://your-app-name.onrender.com/health

# Mark attendance
curl -X POST https://your-app-name.onrender.com/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"},
      {"enroll_no": "S1002", "status": "Absent"}
    ]
  }'

# View report
curl https://your-app-name.onrender.com/api/report/S1001
```

### Step 4: Monitor Render Dashboard

1. Go to your Render dashboard
2. Check the **Logs** tab for any errors
3. Check the **Metrics** tab for:
   - Request count
   - Response times
   - Error rates
4. Verify the service status shows "Live" (green)

### Common Render Issues & Solutions

**Issue: Service shows "Build Failed"**
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure Python version is compatible

**Issue: Service shows "Deploying" but never completes**
- Check start command is correct (`gunicorn app:app` or `bash start.sh`)
- Verify `start.sh` is executable or use direct gunicorn command

**Issue: Health check returns 404**
- Ensure the `/health` endpoint is accessible
- Check if the app is binding to the correct port (Render uses `$PORT` environment variable)

**Issue: Database errors after deployment**
- Render may reset the database on each deploy
- Consider using a persistent database (PostgreSQL) instead of SQLite for production

---

## 📝 Notes for Render Deployment

### Recommended: Use PostgreSQL on Render

For production, consider switching to PostgreSQL:
1. Create a PostgreSQL database on Render
2. Get the connection string
3. Update `app.py` to use the PostgreSQL connection string in production:

```python
import os
database_url = os.environ.get('DATABASE_URL', 'sqlite:///attendance_system.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://')
```

### Port Configuration

Render automatically sets the `PORT` environment variable. If needed, update `start.sh`:
```bash
gunicorn app:app --bind 0.0.0.0:${PORT:-5000}
```

---

## ✅ Success Criteria

Your deployment is successful if:
- ✅ Health check returns 200 OK with "healthy" status
- ✅ Mark attendance endpoint accepts POST requests
- ✅ View report endpoint returns student data
- ✅ Render dashboard shows "Live" status
- ✅ All curl commands return expected JSON responses

---

## 🐛 Troubleshooting

### Local Testing Issues

**Port already in use:**
```bash
# Find and kill process on port 5000 (Linux/Mac)
lsof -ti:5000 | xargs kill -9

# Or change port in app.py
app.run(debug=True, port=5001)
```

**Database not created:**
- Ensure you run the app at least once so `db.create_all()` executes
- Check if `attendance_system.db` file exists in the `instance/` directory

### cURL Command Issues

**Windows PowerShell:**
- Use double quotes: `curl "http://127.0.0.1:5000/health"`
- For POST with JSON, escape quotes: `curl -X POST ... -d "{\"faculty_id\":\"F001\"}"`

**Git Bash:**
- Single quotes work fine as shown in examples above

---

For more help, check the Render documentation: https://render.com/docs

