# Render Start Script Setup - Automatic Sample Data Population

## 🚀 Automatic Sample Data Population

The `start.sh` script has been updated to automatically populate sample data when the database is empty.

## ✅ What Happens on Each Start

When your Render service starts, the `start.sh` script will:

1. **Run Migrations**: Ensures database schema is up to date
   ```bash
   python manage.py migrate --noinput
   ```

2. **Collect Static Files**: Prepares static assets
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Check Property Count**: Counts existing properties in database

4. **Populate Sample Data** (if needed): Only runs if database has less than 5 properties
   ```bash
   python manage.py populate_sample_data
   ```

5. **Start Gunicorn**: Launches the web server

## 🔧 Configure Render to Use start.sh

### Step 1: Set Start Command in Render

1. Go to your **Web Service** on Render
2. Navigate to **"Settings"** tab
3. Find **"Start Command"** field
4. Enter:
   ```bash
   bash start.sh
   ```
   Or if you prefer the full path:
   ```bash
   /bin/bash start.sh
   ```
5. Click **"Save Changes"**

### Step 2: Verify Build Command

Your **Build Command** should be:
```bash
pip install -r requirements.txt
```

**DO NOT** include migrations or populate commands in the build command - they're handled by `start.sh`.

## 📋 How It Works

The script checks the property count:
- **If < 5 properties**: Runs `populate_sample_data` to add sample listings
- **If ≥ 5 properties**: Skips population (assumes data already exists)

This ensures:
- ✅ Sample data is added when database is empty
- ✅ No duplicates are created (uses `get_or_create`)
- ✅ Existing data is preserved

## 🧪 Testing Welcome Email

The welcome email test is **commented out** in `start.sh` by default to avoid sending test emails on every restart.

To enable it, edit `start.sh` and uncomment this line:
```bash
python manage.py test_welcome_email
```

Or run it manually via Render Shell:
```bash
python manage.py test_welcome_email
```

## 🔍 Manual Execution

If you need to run commands manually:

```bash
# Via Render Shell
python manage.py migrate
python manage.py populate_sample_data
python manage.py test_welcome_email
```

## 🚨 Troubleshooting

### Issue: Sample data not populating

**Solution**: 
1. Check Render logs to see if script is running
2. Verify `start.sh` is being used as start command
3. Check property count - script only runs if < 5 properties
4. Run manually to see errors:
   ```bash
   python manage.py populate_sample_data
   ```

### Issue: "Permission denied" for start.sh

**Solution**: The script already has execute permissions. If issues persist:
```bash
chmod +x start.sh
```

### Issue: Script not running

**Solution**:
1. Verify "Start Command" is set to `bash start.sh` in Render
2. Check that `start.sh` is in your repository root
3. Check Render logs for errors

## ✅ Verification

After configuring, check Render logs to see:
```
📊 Running database migrations...
📦 Collecting static files...
🏠 Checking if sample data population is needed...
📝 Database has X properties. Populating sample data...
✅ Created property: [Property Name]
🚀 Starting Gunicorn server...
```

## 📝 Summary

- ✅ `start.sh` automatically populates sample data if database is empty
- ✅ No manual intervention needed after first setup
- ✅ Safe - won't create duplicates
- ✅ Smart - only runs when needed

Your service will now automatically maintain sample data on every start! 🎉

