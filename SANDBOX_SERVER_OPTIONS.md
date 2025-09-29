# Ereft Sandbox Server Options

## 🧪 **Recommended Sandbox URLs:**

### **Option 1: Railway Sandbox (Recommended)**
```
https://ereft-sandbox.up.railway.app
```
- **Use**: App Store testing, development
- **Data**: Separate test database
- **Benefits**: Isolated from production

### **Option 2: Render Sandbox**
```
https://ereft-sandbox.onrender.com
```
- **Use**: App Store testing, staging
- **Data**: Copy of production with test data
- **Benefits**: Same infrastructure as production

### **Option 3: Local Development (Current)**
```
http://192.168.12.129:8001
```
- **Use**: Local development only
- **Data**: Local SQLite database
- **Benefits**: Full control, fast iteration

### **Option 4: Use Production as Sandbox (Current Setup)**
```
https://ereft.onrender.com
```
- **Use**: App Store testing, quick testing
- **Data**: Same as production
- **Benefits**: No additional setup needed

## 📱 **For App Store Connect:**

### **What Apple Expects:**
- A **publicly accessible URL** that reviewers can reach
- **Test credentials** that work reliably
- **Consistent data** during the review period

### **Recommended for App Store Submission:**
```
Production URL: https://ereft.onrender.com
Test Account: demo@ereft.com / Demo123!
```

## 🔧 **Quick Configuration Update:**

If you want to use environment-based URLs, update `src/config/api.js`:

```javascript
import { ENV } from './env';

// Use environment-based URL selection
export const API_BASE_URL = __DEV__ 
  ? 'http://192.168.12.129:8001'  // Local development
  : 'https://ereft.onrender.com'; // Production/App Store

// Or use explicit sandbox for App Store testing
export const API_BASE_URL = process.env.NODE_ENV === 'production'
  ? 'https://ereft.onrender.com'          // Production
  : 'https://ereft-sandbox.onrender.com'; // Sandbox
```

## 🎯 **Current Recommendation:**

**For App Store submission, keep your current setup:**
- **Server URL**: `https://ereft.onrender.com`
- **Test Account**: Create `demo@ereft.com` with password `Demo123!`
- **Reason**: Simple, reliable, and already working

This gives Apple reviewers a consistent experience without additional infrastructure complexity.
