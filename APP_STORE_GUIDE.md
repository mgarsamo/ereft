# 📱 Ereft App Store Submission Guide

## 🍎 iOS App Store Submission

### Prerequisites
1. **Apple Developer Account** ($99/year)
   - Sign up at: https://developer.apple.com
   - Complete enrollment process

2. **App Store Connect Access**
   - Create app listing
   - Configure app information

### Step 1: Prepare App for iOS
```bash
cd ereft_mobile
npx expo install --fix
npx expo build:ios
```

### Step 2: App Store Connect Setup
1. **Create New App**
   - App Name: "Ereft - Ethiopian Real Estate"
   - Bundle ID: `com.ereft.realestate`
   - SKU: `ereft-real-estate-ethiopia`
   - Language: English (add Amharic later)

2. **App Information**
   - **Category**: Business
   - **Subcategory**: Real Estate
   - **Content Rights**: No, it does not use third-party content
   - **Age Rating**: 4+ (No objectionable content)

3. **Pricing & Availability**
   - Price: Free
   - Availability: Ethiopia, United States (expand later)

### Step 3: App Metadata

#### App Store Description
```
🏠 Ereft - Ethiopia's Premier Real Estate Platform

Find your dream property in Ethiopia with Ereft, the comprehensive real estate app designed specifically for the Ethiopian market.

✨ KEY FEATURES:
• Browse thousands of properties across Ethiopia
• Advanced search with Ethiopian address system (sub-city, kebele)
• Interactive maps with property locations
• Save favorite properties for later
• User-friendly Ethiopian Birr (ETB) pricing
• Secure user authentication
• Professional property photos and details

🏘️ PROPERTY TYPES:
• Houses and villas
• Apartments and condos
• Commercial properties
• Land for sale or rent
• Townhouses

🌍 ETHIOPIAN LOCALIZATION:
• Ethiopian address system (city, sub-city, kebele, street)
• Metric measurements (square meters)
• Ethiopian Birr currency
• Major Ethiopian cities supported

📱 MODERN EXPERIENCE:
• Clean, intuitive interface
• Fast property search and filtering
• High-quality property images
• Detailed property information
• Contact property owners directly

Whether you're buying, selling, or renting in Addis Ababa, Dire Dawa, or any Ethiopian city, Ereft makes real estate simple and accessible.

Download Ereft today and find your perfect property in Ethiopia! 🇪🇹
```

#### Keywords
```
real estate, Ethiopia, property, house, apartment, rent, buy, Addis Ababa, Ethiopian, homes, land, commercial, residential
```

#### App Preview Screenshots (Required: 6.5", 5.5", iPad Pro)
- Login screen with Ethiopian branding
- Home screen with property listings  
- Property detail screen
- Search and filters screen
- Map view with properties
- User profile screen

### Step 4: Technical Requirements

#### App Icons (Required Sizes)
```
1024x1024 - App Store
180x180 - iPhone app icon
167x167 - iPad Pro app icon
152x152 - iPad app icon
120x120 - iPhone app icon (60pt @2x)
87x87 - iPhone app icon (29pt @3x)
80x80 - iPhone app icon (40pt @2x)
76x76 - iPad app icon
58x58 - iPhone app icon (29pt @2x)
40x40 - iPhone app icon (20pt @2x)
29x29 - iPhone app icon
```

#### Privacy Policy (Required)
Create at: `https://www.privacypolicytemplate.net`

#### Support URL
Set up: `https://ereft.com/support` (or GitHub issues page)

### Step 5: Build Submission
```bash
# Create production build
npx expo build:ios --type archive

# Upload to App Store Connect
# Use Xcode or Application Loader
```

---

## 🤖 Google Play Store Submission

### Prerequisites
1. **Google Play Console Account** ($25 one-time fee)
   - Sign up at: https://play.google.com/console
   - Complete registration

### Step 1: Prepare App for Android
```bash
cd ereft_mobile
npx expo build:android --type app-bundle
```

### Step 2: Play Console Setup
1. **Create New App**
   - App Name: "Ereft - Ethiopian Real Estate"
   - Default Language: English
   - App or Game: App
   - Free or Paid: Free

2. **Store Listing**
   - **Short Description** (80 chars):
     ```
     Ethiopia's premier real estate app. Find houses, apartments & land easily.
     ```
   
   - **Full Description** (4000 chars):
     ```
     🏠 Ereft - Ethiopia's Premier Real Estate Platform
     
     Discover your perfect property in Ethiopia with Ereft, the most comprehensive real estate app designed specifically for the Ethiopian market.
     
     ✨ KEY FEATURES:
     • Browse thousands of properties across Ethiopia
     • Advanced search with Ethiopian address system
     • Interactive Google Maps integration
     • Save and manage favorite properties
     • Ethiopian Birr (ETB) pricing
     • Secure user authentication
     • High-quality property photos
     
     🏘️ FIND ANY PROPERTY TYPE:
     • Residential houses and villas
     • Modern apartments and condos  
     • Commercial office spaces
     • Land for development
     • Rental properties
     
     🌍 BUILT FOR ETHIOPIA:
     • Ethiopian address system (sub-city, kebele, street)
     • Square meter measurements
     • Ethiopian Birr currency
     • All major Ethiopian cities
     • Localized user experience
     
     📱 MODERN & EASY TO USE:
     • Clean, professional interface
     • Lightning-fast search
     • Advanced filtering options
     • Detailed property information
     • Direct contact with property owners
     
     Whether you're in Addis Ababa, Dire Dawa, Mekelle, or anywhere in Ethiopia, Ereft connects you with the best properties in your area.
     
     Perfect for:
     • First-time home buyers
     • Property investors
     • Renters looking for apartments
     • Real estate professionals
     • Anyone seeking Ethiopian properties
     
     Download Ereft today and experience the future of Ethiopian real estate! 🇪🇹
     ```

3. **Graphics Requirements**
   - **App Icon**: 512x512 PNG
   - **Feature Graphic**: 1024x500 PNG
   - **Screenshots**: 
     - Phone: 16:9 or 9:16 ratio, min 320px
     - 7-inch tablet: min 600px
     - 10-inch tablet: min 800px

### Step 3: Content Rating
- **Target Age Group**: Everyone
- **Content**: No violent, sexual, or inappropriate content
- **Interactive Elements**: Users can interact (chat, share info)

### Step 4: App Content
- **Privacy Policy**: Required (same as iOS)
- **Target Audience**: Everyone
- **Content Guidelines**: Family-friendly real estate app

### Step 5: Release Management
1. **Production Track**
2. **Upload AAB file** (from Expo build)
3. **Release Notes**:
   ```
   🎉 Welcome to Ereft v1.0!
   
   • Browse Ethiopian properties easily
   • Advanced search and filters
   • Interactive maps
   • User profiles and favorites
   • Secure authentication
   • Ethiopian address system
   
   Find your dream property in Ethiopia today!
   ```

---

## 📊 Launch Checklist

### Pre-Launch
- [ ] Backend deployed to production server
- [ ] API endpoints tested and working
- [ ] User authentication functional
- [ ] Property data populated
- [ ] Maps integration working
- [ ] App icons created (all sizes)
- [ ] Screenshots captured (all devices)
- [ ] Privacy policy published
- [ ] Support page created

### App Store Submission
- [ ] iOS build uploaded to App Store Connect
- [ ] Android build uploaded to Play Console  
- [ ] App metadata completed
- [ ] Pricing set to free
- [ ] Target countries selected
- [ ] Age rating completed
- [ ] Content rating completed

### Post-Launch
- [ ] Monitor app reviews
- [ ] Track download metrics
- [ ] Gather user feedback
- [ ] Plan feature updates
- [ ] Marketing and promotion

---

## 🚀 Expected Timeline

- **iOS Review**: 1-7 days
- **Android Review**: 1-3 days
- **Total Launch Time**: 1-2 weeks

## 📈 Success Metrics

- **Downloads**: Target 1,000+ in first month
- **User Retention**: 30%+ weekly retention
- **Reviews**: Maintain 4.0+ rating
- **Growth**: 20% month-over-month growth

---

**🏠 Ready to launch Ereft and revolutionize Ethiopian real estate! 🇪🇹**
