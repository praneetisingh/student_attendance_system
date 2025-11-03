# 🔧 Fix Deployment Failure

## Problem
Deployment failed with "Exited with status 1"

## Most Common Causes & Fixes

### ✅ Fix 1: Add DATABASE_URL Environment Variable (MOST IMPORTANT)

Since you've created the PostgreSQL database, you need to connect it:

1. **Get Database Connection String:**
   - In your PostgreSQL dashboard (`student-attendance-db`)
   - Click **"Connect"** button
   - Find **"Internal Database URL"** (or **"Connection Pooling"**)
   - Copy the connection string (starts with `postgres://`)

2. **Add to Web Service:**
   - Go to your **Web Service** (student-attendance-api-zv6y)
   - Click **"Environment"** tab
   - Click **"Add Environment Variable"**
   - **Key:** `DATABASE_URL`
   - **Value:** Paste the connection string you copied
   - **Save Changes**

3. **Redeploy:**
   - Render will automatically redeploy
   - Wait 2-5 minutes

---

### ✅ Fix 2: Check Build Command

In Render Web Service settings:

1. Go to **"Settings"** tab
2. Check **"Build Command"** should be:
   ```
   pip install -r requirements.txt
   ```
3. Check **"Start Command"** should be:
   ```
   bash start.sh
   ```
   OR
   ```
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```

---

### ✅ Fix 3: Check Render Logs

1. Go to your Web Service
2. Click **"Logs"** tab
3. Look for error messages like:
   - `ModuleNotFoundError` → Missing dependency
   - `Connection refused` → Database not connected
   - `No such file or directory` → Script issue
   - `Permission denied` → File permission issue

---

### ✅ Fix 4: Alternative Start Command (If start.sh fails)

If `bash start.sh` doesn't work, try direct gunicorn command:

1. Go to Web Service → **"Settings"**
2. Change **"Start Command"** to:
   ```
   python -c "from app import app, db, populate_initial_data; with app.app_context(): db.create_all(); populate_initial_data()" && gunicorn app:app --bind 0.0.0.0:$PORT
   ```

---

## 🔍 What to Check in Render Logs

After adding DATABASE_URL and redeploying, check logs for:

### ✅ Success Indicators:
- "Database initialized successfully"
- "Starting Gunicorn..."
- "Booting worker"
- "Listening at: http://0.0.0.0:XXXX"

### ❌ Error Indicators:
- "Database initialization error"
- "Connection refused"
- "ModuleNotFoundError"
- "gunicorn: command not found"

---

## 📝 Step-by-Step Fix

1. ✅ **You've already created PostgreSQL database** (I can see it in your screenshot)
2. ⏳ **Add DATABASE_URL to Web Service** (See Fix 1 above)
3. ⏳ **Wait for redeploy**
4. ⏳ **Check logs** to see if it works
5. ⏳ **Test endpoints** once "Live"

---

## 🚨 Quick Test

After fixing and redeploying:

```bash
# Should return 200 OK
curl https://student-attendance-api-zv6y.onrender.com/health
```

If this works, your deployment is fixed! 🎉

