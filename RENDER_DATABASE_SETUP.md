# Render Database Setup - Ensuring Data Persistence

## 🚨 CRITICAL: Data Persistence Configuration

This document ensures that **ALL user data, properties, and listings are retained across Render deployments**. Data should NEVER be deleted during deployments.

## ✅ Required Setup: Managed PostgreSQL Database

### Step 1: Create a Separate PostgreSQL Database Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `ereft-database` (or your preferred name)
   - **Database**: `ereft_db` (or your preferred name)
   - **User**: `ereft_user` (or your preferred name)
   - **Region**: Same region as your web service
   - **Plan**: Choose a plan that fits your needs (Starter is fine for now)
4. Click **"Create Database"**

### Step 2: Get the Database Connection String

1. After creating the database, go to the database service page
2. Find the **"Internal Database URL"** or **"Connection String"**
3. It should look like: `postgresql://ereft_user:password@dpg-xxxxx-a.oregon-postgres.render.com/ereft_db`

### Step 3: Configure Your Web Service to Use the Database

1. Go to your **Web Service** on Render
2. Navigate to **"Environment"** tab
3. Add/Update the `DATABASE_URL` environment variable:
   ```
   DATABASE_URL=postgresql://ereft_user:password@dpg-xxxxx-a.oregon-postgres.render.com/ereft_db
   ```
   (Use the actual connection string from Step 2)

### Step 4: Verify Database Configuration

Your `settings.py` should already be configured to use `DATABASE_URL`:

```python
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Production: Use DATABASE_URL from Render
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Development: Fallback to SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

## ✅ Build Command Configuration

### IMPORTANT: Build Command Should NOT Clear Data

Your Render build command should be:

```bash
pip install -r requirements.txt && python manage.py migrate --noinput
```

**DO NOT** include any of these destructive commands:
- ❌ `python manage.py flush` - DELETES ALL DATA
- ❌ `python manage.py reset_db` - DELETES ALL DATA
- ❌ `python manage.py clear_db` - DELETES ALL DATA
- ❌ `dropdb` or `createdb` commands - DELETES ALL DATA

### Recommended Build Command

```bash
pip install -r requirements.txt && python manage.py migrate --noinput
```

This will:
- ✅ Install dependencies
- ✅ Run migrations (creates/updates tables without deleting data)
- ✅ Preserve all existing data

## ✅ Start Command Configuration

Your Render start command should be:

```bash
gunicorn wsgi:application --bind 0.0.0.0:$PORT
```

**DO NOT** include database operations in the start command.

## ✅ Post-Deploy Script (Optional but Recommended)

If you want to populate sample data ONLY when the database is empty, you can add a post-deploy script:

1. Create a file: `render_post_deploy.sh`
2. Add this content:

```bash
#!/bin/bash
# Only populate if database is empty (no properties exist)
python manage.py shell << EOF
from listings.models import Property
if Property.objects.count() == 0:
    print("Database is empty, populating sample data...")
    import subprocess
    subprocess.run(['python', 'manage.py', 'populate_sample_data'])
else:
    print(f"Database has {Property.objects.count()} properties. Skipping population.")
EOF
```

3. In Render, set **"Post Deploy Command"** to: `bash render_post_deploy.sh`

## ✅ Verify Data Persistence

After each deployment:

1. Check that properties still exist:
   ```bash
   python manage.py shell
   >>> from listings.models import Property
   >>> Property.objects.count()
   ```

2. Check that users still exist:
   ```bash
   >>> from django.contrib.auth.models import User
   >>> User.objects.count()
   ```

3. Verify specific data:
   ```bash
   >>> Property.objects.first()
   >>> User.objects.first()
   ```

## 🚨 Common Issues and Solutions

### Issue: Data is being deleted on each deployment

**Cause**: Using SQLite instead of PostgreSQL, or DATABASE_URL not configured

**Solution**:
1. Create a managed PostgreSQL database on Render (see Step 1)
2. Set DATABASE_URL environment variable (see Step 3)
3. Redeploy your web service

### Issue: Build command is clearing data

**Cause**: Build command includes `flush` or similar destructive commands

**Solution**: Remove any destructive commands from build command (see Build Command Configuration above)

### Issue: Database is resetting

**Cause**: Using ephemeral database or database service is being recreated

**Solution**: Ensure you're using a **managed PostgreSQL service** (not ephemeral), and it's a **separate service** from your web service

## ✅ Best Practices

1. **Always use a separate managed PostgreSQL service** - Never use SQLite in production
2. **Never include destructive database commands in build/start scripts**
3. **Use migrations for schema changes** - They preserve data
4. **Backup your database regularly** - Render provides automatic backups for paid plans
5. **Test migrations locally** before deploying
6. **Monitor database size** - Ensure you have adequate storage

## 📊 Database Backup

Render provides automatic backups for PostgreSQL databases:
- **Free tier**: Manual backups only
- **Paid tiers**: Automatic daily backups

To create a manual backup:
1. Go to your PostgreSQL service on Render
2. Click **"Backups"** tab
3. Click **"Create Backup"**

## 🔍 Verification Checklist

Before going to production, verify:

- [ ] Separate PostgreSQL database service created on Render
- [ ] `DATABASE_URL` environment variable set in web service
- [ ] Build command does NOT include `flush`, `reset_db`, or similar
- [ ] Start command does NOT include database operations
- [ ] Migrations run successfully without data loss
- [ ] Existing data persists after deployment
- [ ] New data can be created and persists
- [ ] Database backups are configured (if using paid plan)

## 📝 Summary

**Key Points**:
1. ✅ Use **managed PostgreSQL** (separate service)
2. ✅ Set **DATABASE_URL** environment variable
3. ✅ **Never** include destructive commands in build/start scripts
4. ✅ Use **migrations** for schema changes
5. ✅ **Test** data persistence after each deployment

Your data will persist across deployments as long as:
- You're using a managed PostgreSQL database (separate service)
- DATABASE_URL is properly configured
- No destructive commands are in your build/start scripts

