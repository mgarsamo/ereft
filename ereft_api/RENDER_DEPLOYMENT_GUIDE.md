# 🚀 Ereft Backend Deployment Guide - Render

## 📋 Pre-Deployment Checklist

✅ **Backend Configuration Complete**
- Django settings configured for production
- Requirements.txt includes all dependencies
- Procfile created for gunicorn startup
- render.yaml configured for Render deployment
- Static files collection tested
- Database migrations ready

## 🔧 Step-by-Step Render Deployment

### Step 1: Push Code to GitHub
```bash
# Make sure you're in the backend directory
cd /Users/melaku/Documents/Projects/Ethioprojects/Ereft/ereft_api

# Add all files
git add -A

# Commit changes
git commit -m "🚀 Backend ready for Render deployment

✅ Production-ready configuration:
- Updated settings.py for Render
- Added Procfile for gunicorn
- Updated render.yaml with correct environment variables
- Verified static files collection
- Tested Django configuration

🌐 Ready for production deployment!"

# Push to GitHub (replace with your actual backend repo)
git push origin main
```

### Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit https://render.com
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository: `mgarsamo/ereft`
   - Select the repository

3. **Configure Service**
   - **Name**: `ereft-api`
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users (e.g., Oregon)
   - **Branch**: `main`
   - **Root Directory**: `ereft_api` (if your Django app is in a subdirectory)

4. **Build & Deploy Settings**
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
     ```
   - **Start Command**: 
     ```
     gunicorn --bind 0.0.0.0:$PORT wsgi:application
     ```

5. **Environment Variables**
   Add these environment variables in Render dashboard:
   ```
   DEBUG = False
   SECRET_KEY = [Let Render generate this]
   ALLOWED_HOSTS = *.onrender.com,ereft-api.onrender.com,localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS = https://ereft-api.onrender.com,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8081
   CSRF_TRUSTED_ORIGINS = https://ereft-api.onrender.com,https://*.onrender.com
   DATABASE_URL = [Will be auto-set when you add PostgreSQL]
   ```

6. **Add PostgreSQL Database**
   - In your service dashboard, go to **"Environment"**
   - Click **"New Database"**
   - Choose **"PostgreSQL"**
   - Name: `ereft-db`
   - Plan: **Free**
   - This will automatically set the `DATABASE_URL` environment variable

7. **Deploy**
   - Click **"Create Web Service"**
   - Render will automatically build and deploy your app
   - Wait for deployment to complete (usually 5-10 minutes)

### Step 3: Verify Deployment

Once deployment is complete, you'll get a URL like: `https://ereft-api.onrender.com`

**Test these endpoints:**
1. **API Root**: `https://ereft-api.onrender.com/api/`
2. **Admin Panel**: `https://ereft-api.onrender.com/admin/`
3. **Properties**: `https://ereft-api.onrender.com/api/properties/`
4. **Authentication**: `https://ereft-api.onrender.com/api/auth/login/`

### Step 4: Create Superuser (Important!)
```bash
# In Render dashboard, go to your service
# Click "Shell" to access the server terminal
# Run this command to create admin user:
python manage.py createsuperuser
```

## 🔍 Testing Deployment

### Test API Endpoints
```bash
# Test API root
curl https://ereft-api.onrender.com/api/

# Test properties endpoint
curl https://ereft-api.onrender.com/api/properties/

# Test authentication
curl -X POST https://ereft-api.onrender.com/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### Expected Responses
- **API Root**: Should return DRF browsable API
- **Properties**: Should return `{"results": [], "count": 0}` (empty initially)
- **Admin**: Should show Django admin login page
- **Authentication**: Should return token or user data

## 🐛 Common Issues & Solutions

### Issue 1: Build Fails
**Error**: `ModuleNotFoundError`
**Solution**: Check `requirements.txt` has all dependencies

### Issue 2: Static Files Not Loading
**Error**: CSS/JS files not found
**Solution**: Verify `collectstatic` runs in build command

### Issue 3: Database Connection Error
**Error**: `django.db.utils.OperationalError`
**Solution**: Ensure PostgreSQL database is created and `DATABASE_URL` is set

### Issue 4: CORS Errors from Mobile App
**Error**: `CORS policy: No 'Access-Control-Allow-Origin'`
**Solution**: Add your mobile app's domain to `CORS_ALLOWED_ORIGINS`

## 📱 Next Steps: Update Mobile App

Once backend is deployed successfully, update your mobile app:

```javascript
// In ereft_mobile/src/config/api.js
export const API_BASE_URL = 'https://ereft-api.onrender.com';
```

## 🎉 Success Indicators

✅ **Deployment Successful When:**
- Build completes without errors
- Service shows "Live" status in Render dashboard
- API endpoints respond correctly
- Admin panel accessible
- Database migrations applied successfully
- Static files served correctly

## 📞 Support

If you encounter issues:
1. Check Render service logs in dashboard
2. Verify all environment variables are set
3. Ensure GitHub repository is updated
4. Check Django `settings.py` configuration

---

**🚀 Your Ereft backend will be live at: `https://ereft-api.onrender.com`**
