# 🏠 Ereft - Ethiopian Real Estate App

A comprehensive Zillow-style real estate application designed specifically for the Ethiopian market, built with Django REST Framework and React Native.

## 🌟 Features

### 📱 Mobile App (React Native + Expo)
- **User Authentication**: Email/password login with OAuth support (Google, Facebook)
- **Property Browsing**: Browse properties by type, location, and price
- **Advanced Search**: Filter by bedrooms, bathrooms, area, and more
- **Interactive Maps**: Google Maps integration with property locations
- **Favorites System**: Save and manage favorite properties
- **User Profiles**: Personal dashboard with activity stats
- **Ethiopian Localization**: Addresses with sub-city, kebele, street names
- **Modern UI**: Zillow-inspired design with smooth navigation

### 🖥️ Backend API (Django REST Framework)
- **RESTful API**: Complete CRUD operations for properties
- **User Management**: Registration, authentication, profiles
- **Property Management**: Full property lifecycle management
- **Image Upload**: Property photo management
- **Admin Panel**: Django admin for content management
- **Ethiopian Address System**: City, sub-city, kebele, street structure
- **Metric Units**: Square meters instead of square feet

## 🏗️ Architecture

```
Ereft/
├── ereft_api/          # Django REST Framework Backend
│   ├── listings/       # Main app with models, views, serializers
│   ├── payments/       # Payment processing (Stripe integration)
│   ├── settings.py     # Django configuration
│   └── manage.py       # Django management commands
├── ereft_mobile/       # React Native Frontend
│   ├── src/
│   │   ├── screens/    # App screens (Home, Login, Profile, etc.)
│   │   ├── components/ # Reusable components
│   │   ├── context/    # React context for state management
│   │   └── config/     # API configuration
│   ├── app.json        # Expo configuration
│   └── package.json    # Dependencies
└── README.md
```

## 🚀 Quick Start

### Backend Setup
```bash
cd ereft_api
conda create -n ereft_env python=3.10
conda activate ereft_env
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8001
```

### Mobile App Setup
```bash
cd ereft_mobile
npm install
npx expo start --tunnel
```

## 📱 Screenshots & Demo

- **Login Screen**: Secure authentication with OAuth options
- **Home Screen**: Property listings with Ethiopian branding
- **Property Details**: Comprehensive property information
- **Search & Filters**: Advanced filtering capabilities
- **User Profile**: Activity dashboard and statistics

## 🛠️ Technology Stack

### Backend
- **Django 4.2.7**: Web framework
- **Django REST Framework**: API development
- **SQLite/PostgreSQL**: Database
- **Pillow**: Image processing
- **django-cors-headers**: CORS support
- **django-filter**: Advanced filtering

### Mobile
- **React Native**: Mobile framework
- **Expo SDK 53**: Development platform
- **React Navigation**: Navigation system
- **React Native Maps**: Google Maps integration
- **AsyncStorage**: Local data storage
- **Axios**: HTTP client

## 🌍 Ethiopian Localization

- **Address System**: Sub-city, kebele, street name fields
- **Metric Units**: All areas in square meters (m²)
- **Ethiopian Cities**: Pre-configured city list
- **Local Currency**: Ethiopian Birr (ETB) pricing
- **Cultural Adaptation**: UI/UX adapted for Ethiopian users

## 📊 Key Models

### Property Model
```python
- title, description
- property_type (house, apartment, condo, etc.)
- listing_type (sale, rent)
- price, price_per_sqm
- address, city, sub_city, kebele, street_name
- bedrooms, bathrooms, area_sqm
- latitude, longitude
- images, amenities
```

### User Features
- Custom user profiles
- Property favorites
- Activity statistics
- Admin management

## 🔐 Authentication

- **Token-based**: Django REST Framework tokens
- **OAuth Ready**: Google and Facebook integration
- **Session Management**: Persistent login across app restarts
- **Admin Access**: Django admin panel for management

## 🚀 Deployment

### Backend Deployment
- **Railway/Render**: One-click deployment
- **Environment Variables**: Production configuration
- **Static Files**: Whitenoise for static file serving
- **Database**: PostgreSQL for production

### Mobile App Deployment
- **Expo Build**: Production builds for app stores
- **iOS**: App Store Connect submission ready
- **Android**: Google Play Console submission ready
- **OTA Updates**: Expo over-the-air updates

## 📈 Current Status

✅ **Fully Functional**: All core features working
✅ **Production Ready**: Backend and frontend optimized
✅ **Store Ready**: Prepared for app store submission
✅ **Ethiopian Market**: Localized for Ethiopian real estate

## 👥 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

**Project**: Ereft Ethiopian Real Estate App
**Developer**: Melaku Garsamo
**Email**: melaku.garsamo@gmail.com

---

**🏠 Ereft - Making Ethiopian Real Estate Accessible** 🇪🇹