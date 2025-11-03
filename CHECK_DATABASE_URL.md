# 🔍 Check Your DATABASE_URL

## The Error

The SQLAlchemy engine creation is failing, which means there's an issue with your `DATABASE_URL` environment variable.

## How to Verify DATABASE_URL

### Step 1: Check if DATABASE_URL is Set

1. Go to your **Web Service** → **"Environment"** tab
2. Look for `DATABASE_URL` in the list
3. Verify it exists and has a value

### Step 2: Check the Format

Your `DATABASE_URL` should look like one of these:

**Internal Database URL (Recommended):**
```
postgres://user:password@dpg-d442gkadbo4c73b68dag-a.oregon-postgres.render.com:5432/student_attendance_db
```

**Connection Pooling URL:**
```
postgres://user:password@dpg-d442gkadbo4c73b68dag-a.oregon-postgres.render.com:5432/student_attendance_db?sslmode=require
```

### Step 3: Common Issues

❌ **Wrong URL type:**
- Using "External Database URL" instead of "Internal Database URL"
- Use **Internal Database URL** - it's faster and free

❌ **Missing parts:**
- Should include: `postgres://` + username + password + host + port + database name
- Check all parts are present

❌ **Special characters:**
- If password has special characters, they might need URL encoding
- Check if password contains: `@`, `#`, `$`, etc.

❌ **Wrong database name:**
- Database name in URL should match your actual database name
- Check your PostgreSQL dashboard for exact name

---

## How to Fix

### Option 1: Get Fresh Connection String

1. Go to your **PostgreSQL** dashboard (`student-attendance-db`)
2. Click **"Connect"** button
3. Copy **"Internal Database URL"** (not External)
4. Go to **Web Service** → **Environment** tab
5. **Delete** the old `DATABASE_URL` variable
6. **Add new** `DATABASE_URL` with fresh connection string
7. **Save** and wait for redeploy

### Option 2: Check Render Logs

1. Go to **Web Service** → **"Logs"** tab
2. Look for the full error message
3. It will tell you exactly what's wrong:
   - "connection refused" → Wrong host/port
   - "authentication failed" → Wrong password
   - "database does not exist" → Wrong database name
   - "no such file or directory" → psycopg2 not installed

---

## Quick Test

After fixing DATABASE_URL, the health check will show the error:

```bash
curl https://student-attendance-api-zv6y.onrender.com/health
```

If database connection fails, you'll see:
```json
{
  "status": "unhealthy",
  "message": "Database connection error - check DATABASE_URL environment variable",
  "error": "..."
}
```

---

## Most Common Fix

**90% of the time, the issue is:**
- Using External URL instead of Internal URL
- Or the connection string got corrupted

**Solution:** Delete and re-add the `DATABASE_URL` with a fresh "Internal Database URL" from your PostgreSQL dashboard.

