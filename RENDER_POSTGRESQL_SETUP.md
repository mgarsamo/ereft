# PostgreSQL Setup for Render - CRITICAL for Data Persistence

## ⚠️ IMPORTANT: User-Created Properties Will Be Lost Without PostgreSQL

If `POSTGRE_DATABASE_URL` is not set correctly in Render, the application will fall back to SQLite, and **all user-created properties will be lost on every redeployment**.

## Step 1: Verify PostgreSQL Database is Created

1. Go to your Render dashboard
2. Click on "New" → "PostgreSQL"
3. Create a new PostgreSQL database (if you haven't already)
4. Note the **Internal Database URL** (it should look like: `postgresql://user:password@host:port/database`)

## Step 2: Set Environment Variable in Render

1. Go to your **Web Service** (Django backend) on Render
2. Click on "Environment" tab
3. Add or verify the following environment variable:

   **Variable Name:** `POSTGRE_DATABASE_URL`
   
   **Value:** `postgresql://ereft_postgre_user:RbgiySE3RUL9QhYyA7u5UsoM9cOrJuyQ@dpg-d5fq3n4hg0os73dtjhg0-a/ereft_postgre`

   ⚠️ **IMPORTANT:** 
   - Use the exact variable name: `POSTGRE_DATABASE_URL` (not `DATABASE_URL` unless Render auto-sets it)
   - The value should start with `postgresql://` or `postgres://`
   - Do NOT include quotes around the value

4. Click "Save Changes"

## Step 3: Link Database to Web Service (Optional but Recommended)

1. In your Web Service settings, go to "Environment" tab
2. Scroll down to "Add Environment Variable from Service"
3. If your PostgreSQL database is listed, you can link it
4. This will automatically set `DATABASE_URL` (which also works)

## Step 4: Verify Configuration After Deployment

After redeploying, check the Render logs. You should see:

```
✅ PostgreSQL database confirmed - data WILL persist across deployments
📊 Database Engine: django.db.backends.postgresql
📊 Database Name: ereft_postgre
✅ Database connection: OK
```

If you see:
```
❌ WARNING: NOT using PostgreSQL! Data will NOT persist!
```

Then the environment variable is not set correctly.

## Step 5: Run Verification Script (Optional)

You can run the verification script on Render:

```bash
python verify_postgresql.py
```

This will confirm:
- ✅ PostgreSQL is configured
- ✅ Database connection works
- ✅ Existing data is preserved

## Troubleshooting

### Issue: Properties are still being lost

**Check 1:** Verify environment variable name
- Must be exactly: `POSTGRE_DATABASE_URL` or `DATABASE_URL`
- Case-sensitive!

**Check 2:** Verify the value format
- Must start with `postgresql://` or `postgres://`
- Should NOT have quotes: `"postgresql://..."` ❌
- Should be: `postgresql://...` ✅

**Check 3:** Check Render logs
- Look for: `✅ PostgreSQL database confirmed`
- If you see: `⚠️ WARNING: No DATABASE_URL or POSTGRE_DATABASE_URL found` → Variable not set
- If you see: `❌ ERROR: Database engine is not PostgreSQL` → Wrong database URL format

**Check 4:** Verify database is running
- Go to your PostgreSQL service on Render
- Ensure it's "Available" (green status)
- Check the "Info" tab for the connection string

### Issue: Environment variable not persisting

1. Make sure you click "Save Changes" after adding the variable
2. Redeploy the service after adding the variable
3. Check that the variable appears in the "Environment" tab

## Current Configuration

Based on your provided database URL:
- **Database:** `ereft_postgre`
- **User:** `ereft_postgre_user`
- **Host:** `dpg-d5fq3n4hg0os73dtjhg0-a`
- **Connection String:** `postgresql://ereft_postgre_user:RbgiySE3RUL9QhYyA7u5UsoM9cOrJuyQ@dpg-d5fq3n4hg0os73dtjhg0-a/ereft_postgre`

## Verification Checklist

After setting up, verify:

- [ ] `POSTGRE_DATABASE_URL` is set in Render environment variables
- [ ] Value starts with `postgresql://`
- [ ] Web service has been redeployed after setting the variable
- [ ] Render logs show: `✅ PostgreSQL database confirmed`
- [ ] Render logs show: `📊 Database Engine: django.db.backends.postgresql`
- [ ] Existing properties are still visible after redeployment

## Why This Matters

- **With PostgreSQL:** Data persists across deployments ✅
- **Without PostgreSQL (SQLite):** Data is lost on every redeployment ❌

The application code now includes automatic verification that will warn you if PostgreSQL is not configured correctly.

