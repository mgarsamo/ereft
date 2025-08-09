# Ereft API Deployment Guide

## Quick Deploy to Railway

1. **Create Railway Account**: Go to [railway.app](https://railway.app) and sign up

2. **Deploy from GitHub**:
   ```bash
   # Push your code to GitHub first
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/ereft-api.git
   git push -u origin main
   ```

3. **Connect to Railway**:
   - Click "New Project" on Railway
   - Select "Deploy from GitHub repo"
   - Choose your ereft-api repository
   - Railway will auto-detect Django and deploy

4. **Set Environment Variables** in Railway dashboard:
   ```
   DEBUG=False
   ALLOWED_HOSTS=your-app-name.up.railway.app,localhost,127.0.0.1
   CORS_ALLOWED_ORIGINS=https://your-app-name.up.railway.app
   CSRF_TRUSTED_ORIGINS=https://your-app-name.up.railway.app
   ```

5. **Add PostgreSQL Database**:
   - In Railway, click "New" → "Database" → "PostgreSQL"
   - Railway will automatically set DATABASE_URL

6. **Run Migrations**:
   - In Railway dashboard, go to your service
   - Click "Deploy" tab
   - Railway runs migrations automatically via `render.yaml`

7. **Create Superuser**:
   ```bash
   # In Railway console or locally with production DB
   python manage.py createsuperuser
   ```

## Alternative: Render Deploy

1. **Create render.yaml** (already created)
2. **Connect GitHub** to Render
3. **Deploy** - Render will follow the render.yaml configuration

## Update Mobile App

After deployment, update `ereft_mobile/src/config/api.js`:

```javascript
export const API_BASE_URL = 'https://your-actual-deployed-url.up.railway.app';
```

## Test Endpoints

After deployment, test these endpoints:

- `GET /api/` - Should return API info
- `POST /api/auth/login/` - Login endpoint
- `POST /api/auth/register/` - Registration endpoint  
- `GET /api/properties/` - Properties list

## OAuth Configuration

### Google OAuth:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 Client ID
5. Add authorized redirect URIs:
   - `https://auth.expo.io/@yourusername/ereft-mobile`
   - `ereft://auth/google`
6. Update `GoogleSignIn.js` with your client ID

### Facebook OAuth:
1. Go to [Facebook Developers](https://developers.facebook.com)
2. Create new app
3. Add Facebook Login product
4. Configure Valid OAuth Redirect URIs:
   - `https://auth.expo.io/@yourusername/ereft-mobile`
   - `ereft://auth/facebook`
5. Update `FacebookSignIn.js` with your App ID

## Production Checklist

- [ ] Backend deployed to public URL
- [ ] Mobile app updated with public API URL
- [ ] Google OAuth configured with valid client ID
- [ ] Facebook OAuth configured with valid app ID  
- [ ] CORS/CSRF settings allow mobile app domain
- [ ] Database migrations run
- [ ] Superuser created
- [ ] Test all auth methods on physical device
- [ ] SSL certificate active (automatic on Railway/Render)
