# Fixing 500 Error on Render

## Problem
Your app is deployed and running, but you're getting 500 Internal Server Error when calling the API endpoints.

## Root Cause
SQLite (the default database) doesn't work well on Render's filesystem because:
- Render's filesystem is ephemeral (gets wiped on redeploy)
- SQLite requires file write permissions that may not be available
- For production, you should use PostgreSQL

## Solution: Use PostgreSQL on Render

### Step 1: Create PostgreSQL Database on Render

1. Go to your Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Name it (e.g., "student-attendance-db")
4. Choose your plan (Free tier is fine for testing)
5. Click **"Create Database"**

### Step 2: Get Database Connection String

1. In your PostgreSQL dashboard, find **"Internal Database URL"** or **"External Database URL"**
2. Copy the connection string (looks like: `postgres://user:password@host:port/dbname`)

### Step 3: Add Database URL to Render Service

1. Go to your **Web Service** (the Flask app)
2. Go to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Key: `DATABASE_URL`
5. Value: Paste the PostgreSQL connection string
6. Save changes (this will trigger a redeploy)

### Step 4: Verify Code is Updated

The updated `app.py` now automatically uses PostgreSQL if `DATABASE_URL` is set:

```python
database_url = os.environ.get('DATABASE_URL', 'sqlite:///attendance_system.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

Make sure you've pushed this updated code to your repository!

### Step 5: Test Again

After redeployment completes:

```bash
# Test health
curl https://student-attendance-api-zv6y.onrender.com/health

# Test mark attendance
curl -X POST https://student-attendance-api-zv6y.onrender.com/api/mark_attendance \
  -H "Content-Type: application/json" \
  -d '{
    "faculty_id": "F001",
    "course_id": "CS101",
    "attendance_list": [
      {"enroll_no": "S1001", "status": "Present"}
    ]
  }'
```

---

## Alternative: Quick Test Without PostgreSQL

If you want to test immediately without setting up PostgreSQL, you can:

1. **Check Render Logs** to see the exact error:
   - Go to Render Dashboard → Your Service → Logs
   - Look for Python traceback

2. **Common Issues:**
   - Database not initialized: Check if `db.create_all()` is running in `start.sh`
   - Missing initial data: Students S1001 and S1002 must exist before marking attendance

3. **Manual Database Init:**
   You can temporarily add a route to initialize:
   ```python
   @app.route('/init', methods=['POST'])
   def init_db():
       with app.app_context():
           db.create_all()
           populate_initial_data()
       return jsonify({"message": "Database initialized"}), 200
   ```
   Then call: `curl -X POST https://your-app.onrender.com/init`

---

## Check Current Status

1. **Go to Render Dashboard**
2. **Check Logs** - Look for error messages
3. **Check if service is "Live"** (green status)

The logs will tell you exactly what's wrong!

