# Render Environment Variable Setup - PostgreSQL Database

## ✅ PostgreSQL Database Connection

You have created a PostgreSQL database on Render. Now you need to configure your web service to use it.

## 🔧 Step-by-Step Setup

### Step 1: Add Database URL to Web Service Environment Variables

1. Go to your **Web Service** on Render (not the database service)
2. Navigate to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Add the following:

   **Variable Name**: `DATABASE_URL` (or `POSTGRE_DATABASE_URL`)
   
   **Value**: `postgresql://ereft_postgre_user:RbgiySE3RUL9QhYyA7u5UsoM9cOrJuyQ@dpg-d5fq3n4hg0os73dtjhg0-a/ereft_postgre`

   ⚠️ **Important**: Make sure to use the **Internal Database URL** from your PostgreSQL service, not the external one.

### Step 2: Verify Database Connection String Format

Your connection string should look like:
```
postgresql://username:password@host:port/database
```

If your connection string is missing the port, Render's `dj-database-url` library will use the default PostgreSQL port (5432).

### Step 3: Link Database to Web Service (Optional but Recommended)

1. In your **Web Service** settings
2. Go to **"Connections"** or **"Linked Services"**
3. Link your PostgreSQL database service
4. This automatically adds `DATABASE_URL` environment variable

### Step 4: Verify Build and Start Commands

**Build Command** (should be):
```bash
pip install -r requirements.txt && python manage.py migrate --noinput
```

**Start Command** (should be):
```bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT
```

⚠️ **DO NOT** include any of these in your commands:
- ❌ `python manage.py flush` - DELETES ALL DATA
- ❌ `python manage.py reset_db` - DELETES ALL DATA
- ❌ `dropdb` or `createdb` - DELETES ALL DATA

### Step 5: Redeploy Your Service

1. After adding the environment variable, click **"Manual Deploy"** → **"Deploy latest commit"**
2. Or push a new commit to trigger auto-deploy
3. Watch the logs to ensure migrations run successfully

### Step 6: Verify Data Persistence

After deployment, verify your data is still there:

1. Go to Render Shell (or SSH into your service)
2. Run:
   ```bash
   python manage.py shell
   ```
3. Check data:
   ```python
   from listings.models import Property
   from django.contrib.auth.models import User
   
   print(f"Properties: {Property.objects.count()}")
   print(f"Users: {User.objects.count()}")
   ```

## 🔍 Troubleshooting

### Issue: "No such table" errors

**Solution**: Run migrations:
```bash
python manage.py migrate
```

### Issue: Connection refused

**Solution**: 
1. Verify `DATABASE_URL` is set correctly
2. Check that you're using the **Internal Database URL** (not external)
3. Ensure database service is running

### Issue: Data still being deleted

**Solution**:
1. Verify `DATABASE_URL` is set in environment variables
2. Check build/start commands don't include destructive operations
3. Ensure you're using the managed PostgreSQL service (not SQLite)

### Issue: Can't connect to database

**Solution**:
1. Check database service is running
2. Verify connection string format
3. Try using the **Internal Database URL** from Render dashboard

## ✅ Verification Checklist

Before considering setup complete:

- [ ] PostgreSQL database service created on Render
- [ ] `DATABASE_URL` environment variable added to web service
- [ ] Build command does NOT include `flush`, `reset_db`, etc.
- [ ] Start command does NOT include database operations
- [ ] Service redeployed after adding `DATABASE_URL`
- [ ] Migrations run successfully
- [ ] Existing data persists after deployment
- [ ] New data can be created and persists

## 📝 Important Notes

1. **Database is Separate**: Your PostgreSQL database is a separate service from your web service. Deployments to your web service will NOT affect the database.

2. **Data Persists**: As long as `DATABASE_URL` points to your managed PostgreSQL service, all data (users, properties, favorites, etc.) will persist across deployments.

3. **Migrations are Safe**: Running `python manage.py migrate` only updates the database schema - it does NOT delete data.

4. **Backups**: Render provides automatic backups for PostgreSQL databases on paid plans. Consider upgrading if you need automatic backups.

## 🎯 Summary

Your database connection string:
```
postgresql://ereft_postgre_user:RbgiySE3RUL9QhYyA7u5UsoM9cOrJuyQ@dpg-d5fq3n4hg0os73dtjhg0-a/ereft_postgre
```

**Action Required**: Add this as `DATABASE_URL` environment variable in your Render web service, then redeploy.

Once configured, all data will persist across deployments! 🎉

