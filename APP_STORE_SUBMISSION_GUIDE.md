# 🍎 Ereft - Apple App Store Submission Guide

## 📱 App Overview
- **App Name**: Ereft - Ethiopian Real Estate
- **Bundle ID**: com.mgarsamo.ereft
- **Version**: 1.0.0
- **Platform**: iOS (iPhone & iPad)
- **Category**: Business / Real Estate
- **Target Audience**: 17+ (Real Estate transactions)

## 🔧 Pre-Submission Checklist

### ✅ 1. App Configuration
- [x] App name and bundle identifier set
- [x] App icon (1024x1024) ready
- [x] Splash screen configured
- [x] Production API connected (https://ereft.onrender.com)
- [x] All features working end-to-end

### ✅ 2. Required Assets
- [x] App Icon (1024x1024 PNG)
- [ ] Screenshots (6.7", 6.5", 5.5" devices)
- [ ] App Preview Videos (optional but recommended)
- [ ] Marketing materials

### ✅ 3. Technical Requirements
- [x] Built with Expo SDK 53
- [x] React Native 0.79.5
- [x] No development/debug code in production
- [x] Privacy policy URL
- [x] Terms of service URL

## 🚀 Step-by-Step Submission Process

### Step 1: Apple Developer Account Setup
1. **Create Apple Developer Account**: https://developer.apple.com/
   - Cost: $99/year
   - Required for App Store submission
   - Business account recommended for company apps

2. **Enable Two-Factor Authentication**
   - Required for all developer accounts
   - Set up in Apple ID settings

### Step 2: App Store Connect Setup
1. **Create App Record**:
   - Go to App Store Connect: https://appstoreconnect.apple.com/
   - Click "+" to create new app
   - Fill in app information:
     - **Name**: Ereft
     - **Bundle ID**: com.mgarsamo.ereft
     - **SKU**: ereft-ios-app
     - **Primary Language**: English

2. **App Information**:
   - **Category**: Business
   - **Content Rights**: You own or have licensed all rights
   - **Age Rating**: Complete questionnaire (likely 17+)

### Step 3: Build and Upload with EAS Build

1. **Install EAS CLI**:
   ```bash
   npm install -g @expo/eas-cli
   eas login
   ```

2. **Configure EAS Build**:
   ```bash
   eas build:configure
   ```

3. **Build for iOS**:
   ```bash
   # For App Store submission
   eas build --platform ios --profile production
   
   # For TestFlight testing (recommended first)
   eas build --platform ios --profile preview
   ```

4. **Submit to App Store**:
   ```bash
   eas submit --platform ios
   ```

### Step 4: App Store Connect Completion

1. **App Screenshots** (Required):
   - 6.7" Display (iPhone 14 Pro Max): 1290 x 2796 pixels
   - 6.5" Display (iPhone 11 Pro Max): 1242 x 2688 pixels
   - 5.5" Display (iPhone 8 Plus): 1242 x 2208 pixels
   - Take screenshots of:
     - Login screen
     - Home screen with property listings
     - Property detail page
     - Map view
     - Profile screen

2. **App Description**:
   ```
   Ereft - Find Your Perfect Home in Ethiopia
   
   Discover, buy, and rent properties across Ethiopia with Ereft, the leading real estate platform designed specifically for the Ethiopian market.
   
   🏠 KEY FEATURES:
   • Browse thousands of properties across major Ethiopian cities
   • Advanced search with filters for price, location, bedrooms, and more
   • Interactive maps showing property locations
   • High-quality photos and detailed property information
   • Direct contact with property owners and agents
   • Save favorite properties for later viewing
   • User-friendly interface in English
   
   🌍 COVERAGE:
   • Addis Ababa
   • Dire Dawa
   • Mekelle
   • Gondar
   • Adama
   • And many more cities across Ethiopia
   
   📱 PERFECT FOR:
   • Home buyers looking for their dream property
   • Renters seeking apartments and houses
   • Real estate investors
   • Property agents and brokers
   • Anyone relocating within Ethiopia
   
   Download Ereft today and find your perfect home in Ethiopia!
   ```

3. **Keywords**: ethiopian real estate, property, addis ababa, houses, apartments, rent, buy, ethiopia homes

4. **App Review Information**:
   - **Demo Account**: 
     - Username: demo@ereft.com
     - Password: demo123
   - **Review Notes**: Mention that this is a real estate app for Ethiopia

### Step 5: Privacy and Legal

1. **Privacy Policy** (Required):
   - Must be hosted on a public URL
   - Should cover data collection, usage, and sharing
   - Include contact information

2. **App Privacy Details**:
   - Data collection: Location, Contact Info, User Content
   - Data usage: App functionality, Analytics
   - Data sharing: None (or specify if applicable)

### Step 6: Pricing and Availability
- **Price**: Free (with potential in-app purchases later)
- **Availability**: All territories or specific countries
- **App Store Distribution**: Available to everyone

### Step 7: Submit for Review
1. **Final Review**:
   - All required fields completed
   - Screenshots uploaded
   - Build uploaded and processed
   - Privacy policy linked

2. **Submit for Review**:
   - Click "Submit for Review"
   - Review typically takes 24-48 hours
   - You'll receive email updates on status

## 📸 Screenshot Requirements

### Required Screenshots (minimum 3, maximum 10 per device):

1. **Login/Welcome Screen** - Show the beautiful Ereft branding
2. **Home Screen** - Display property listings and search
3. **Property Detail** - Show detailed property information
4. **Map View** - Highlight location features
5. **Search/Filter** - Demonstrate search capabilities

### Screenshot Tips:
- Use actual app content, not mockups
- Show the app's best features
- Include diverse property types
- Use high-quality, realistic data
- Avoid showing empty states

## 🎯 Common Rejection Reasons to Avoid

1. **Incomplete Information**: Ensure all metadata is complete
2. **Poor Screenshots**: Use high-quality, representative screenshots
3. **Crashes/Bugs**: Test thoroughly on multiple devices
4. **Placeholder Content**: Use real, meaningful content
5. **Missing Privacy Policy**: Required for all apps
6. **Inappropriate Content**: Follow App Store guidelines

## 📋 Testing Checklist Before Submission

- [ ] App launches successfully
- [ ] User can register/login
- [ ] Property listings load correctly
- [ ] Search functionality works
- [ ] Map integration functions properly
- [ ] Profile features work
- [ ] No crashes or major bugs
- [ ] Performance is smooth
- [ ] Works on different screen sizes

## 🔄 Post-Submission Process

1. **App Review** (24-48 hours)
2. **Possible Rejection** - Address feedback and resubmit
3. **Approval** - App goes live on App Store
4. **Monitor** - Watch for user feedback and ratings

## 📞 Support Information

- **Support URL**: https://ereft.onrender.com/support
- **Support Email**: support@ereft.com
- **Marketing URL**: https://ereft.onrender.com

## 🎉 Launch Strategy

1. **Soft Launch**: Start with Ethiopia/East Africa
2. **Marketing**: Social media, real estate partnerships
3. **User Feedback**: Monitor reviews and iterate
4. **Updates**: Regular feature updates and improvements

---

**Next Steps**: 
1. Set up Apple Developer Account ($99)
2. Create App Store Connect record
3. Take required screenshots
4. Build with EAS Build
5. Submit for review

**Estimated Timeline**: 1-2 weeks from start to App Store approval
