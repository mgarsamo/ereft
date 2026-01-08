# Render Post-Deploy Script Setup

## 🚀 Automatic Post-Deploy Tasks

This guide shows you how to automatically run `populate_sample_data` and `test_welcome_email` after each deployment.

## ✅ Step 1: Post-Deploy Script Created

A post-deploy script (`render_post_deploy.sh`) has been created that will:
1. Run database migrations
2. Populate sample data (only if database has less than 5 properties)
3. Test welcome email functionality

## 🔧 Step 2: Configure Render to Use Post-Deploy Script

### Option A: Using Render Dashboard (Recommended)

1. Go to your **Web Service** on Render
2. Navigate to **"Settings"** tab
3. Scroll down to **"Post Deploy Command"** section
4. Enter:
   ```bash
   bash render_post_deploy.sh
   ```
5. Click **"Save Changes"**

### Option B: Using render.yaml (If you have one)

Add this to your `render.yaml`:

```yaml
services:
  - type: web
    name: ereft-api
    # ... other settings ...
    postDeployCommand: bash render_post_deploy.sh
```

## 📋 What the Script Does

The `render_post_deploy.sh` script:

1. **Runs Migrations**: Ensures database schema is up to date
   ```bash
   python manage.py migrate --noinput
   ```

2. **Checks Property Count**: Only populates if database has less than 5 properties
   ```bash
   # If properties < 5, run populate_sample_data
   python manage.py populate_sample_data
   ```

3. **Tests Welcome Email**: Verifies email functionality works
   ```bash
   python manage.py test_welcome_email
   ```

## ✅ Benefits

- **Automatic**: Runs after every deployment
- **Smart**: Only populates sample data if database is empty
- **Safe**: Won't duplicate existing properties (uses `get_or_create`)
- **Verification**: Tests email functionality to catch issues early

## 🔍 Manual Execution

If you need to run the script manually:

```bash
# Via Render Shell
bash render_post_deploy.sh

# Or run commands individually
python manage.py migrate
python manage.py populate_sample_data
python manage.py test_welcome_email
```

## 🚨 Troubleshooting

### Issue: Script not running

**Solution**: 
1. Verify "Post Deploy Command" is set in Render dashboard
2. Check that `render_post_deploy.sh` is in your repository root
3. Ensure script has execute permissions (already set with `chmod +x`)

### Issue: "Permission denied"

**Solution**: The script already has execute permissions. If issues persist, try:
```bash
chmod +x render_post_deploy.sh
```

### Issue: Sample data not populating

**Solution**: 
1. Check Render logs for errors
2. Verify database connection (`DATABASE_URL` is set)
3. Run manually to see specific errors:
   ```bash
   python manage.py populate_sample_data
   ```

### Issue: Welcome email test failing

**Solution**:
1. Check SendGrid credentials are set in environment variables
2. Verify `SENDGRID_EMAIL_HOST`, `SENDGRID_EMAIL_USER`, `SENDGRID_EMAIL_PASS` are configured
3. Check Render logs for specific error messages

## 📝 Summary

After configuring the post-deploy command in Render:

1. ✅ Every deployment will automatically run migrations
2. ✅ Sample data will be populated if database is empty
3. ✅ Welcome email will be tested to verify functionality
4. ✅ All tasks run automatically - no manual intervention needed

Your deployments will now automatically maintain sample data and verify email functionality! 🎉

