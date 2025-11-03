# Render Deployment Testing Commands

## Your Render URL
```
https://student-attendance-api-zv6y.onrender.com
```

## ⚠️ Important: Deploy Updated Code First

If you're getting 404 errors, you need to:
1. **Push the updated code to GitHub/GitLab** (if using Git)
2. **Redeploy on Render** (Render will auto-deploy if connected to Git, or manually trigger a deploy)

The updated code includes:
- ✅ `/health` endpoint
- ✅ `/` root endpoint (shows API info)
- ✅ All existing API endpoints

---

## Testing Commands (After Deployment)

### 1. Test Root Endpoint (API Info)
```bash
curl https://student-attendance-api-zv6y.onrender.com/
```

**Expected Response:**
```json
{
  "message": "Student Attendance System API",
  "endpoints": {
    "health": "/health",
    "mark_attendance": "/api/mark_attendance (POST)",
    "view_report": "/api/report/<enroll_no> (GET)"
  }
}
```

### 2. Test Health Check
```bash
curl https://student-attendance-api-zv6y.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Student Attendance System API is running",
  "database": "connected"
}
```

### 3. Test Mark Attendance
```bash
curl -X POST https://student-attendance-api-zv6y.onrender.com/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"},
      {"enroll_no": "S1002", "status": "Absent"}
    ]
  }'
```

### 4. Test View Report
```bash
curl https://student-attendance-api-zv6y.onrender.com/api/report/S1001
```

---

## 🔍 Troubleshooting 404 Errors

### Check Render Dashboard:

1. **Go to your Render dashboard**: https://dashboard.render.com
2. **Check your service status**:
   - ✅ Should show "Live" (green)
   - ❌ If "Building" or "Deploying" - wait for it to complete
   - ❌ If "Failed" - check the logs

3. **Check Logs**:
   - Click on your service → "Logs" tab
   - Look for errors like:
     - "ModuleNotFoundError"
     - "gunicorn: command not found"
     - "Address already in use"

4. **Check Build & Start Commands**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `bash start.sh` or `gunicorn app:app --bind 0.0.0.0:$PORT`

---

## ✅ Quick Test Script

Save this and run it after deployment:

```bash
#!/bin/bash
BASE_URL="https://student-attendance-api-zv6y.onrender.com"

echo "Testing Root Endpoint..."
curl -s "$BASE_URL/" | python -m json.tool
echo ""

echo "Testing Health Check..."
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

echo "Testing Mark Attendance..."
curl -s -X POST "$BASE_URL/api/mark_attendance" \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"}
    ]
  }' | python -m json.tool
echo ""

echo "Testing View Report..."
curl -s "$BASE_URL/api/report/S1001" | python -m json.tool
```

---

## 🚀 Deployment Checklist

- [ ] Code pushed to Git repository (if using Git)
- [ ] Render service connected to repository
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `bash start.sh` or `gunicorn app:app --bind 0.0.0.0:$PORT`
- [ ] Service shows "Live" status
- [ ] Root endpoint (`/`) works
- [ ] Health endpoint (`/health`) works
- [ ] API endpoints work

---

## 📝 Next Steps

1. **Push your code** (if using Git) or **manually redeploy** on Render
2. **Wait for deployment to complete** (check Render dashboard)
3. **Run the test commands above**
4. **Check logs** if still getting errors

