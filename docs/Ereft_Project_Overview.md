# Ereft Platform Overview

_Last updated: {{TODAY}}_

## Mission & Product Goals
- Deliver a production-quality Ethiopian real estate marketplace with “Zillow-level” polish.
- Support property discovery, creation, and management for buyers, sellers, and agents across web and mobile.
- Ensure every listing is persistent, attributed to an authenticated user, and immediately searchable.
- Maintain fast initial load, responsive layouts, and consistent UX between desktop, mobile web, and native apps.

## High-Level Architecture
- **Frontend Web**: Next.js 16 (App Router) on Vercel with React 19.
- **Mobile App**: React Native + Expo (Android/iOS parity with the web experience).
- **Backend API**: Django 5 + Django REST Framework 3.14 on Render.
- **Database**: PostgreSQL in production (SQLite allowed locally).
- **Authentication**: DRF authtoken + Google OAuth + Twilio SMS endpoints ready.
- **Media Storage**: Cloudinary (secure URLs only, no secrets in code).
- **Maps & Geocoding**: Google Maps Platform (web + native).
- **Caching**: Django LocMemCache (list + detail endpoints cached for 60 s, flushed on mutations).
- **CI/CD**: Vercel auto-build for web, Render auto-deploy for backend, Expo EAS for native builds.

## Repository Layout
```
/Users/melaku/Documents/Projects/Ethioprojects/
├── Ereft/                # Backend + RN mobile + shared docs/assets
│   ├── listings/         # DRF app (models, serializers, viewsets, commands)
│   ├── ereft_mobile/     # React Native + Expo app
│   ├── docs/             # Project documentation
│   └── …
└── Ethioprojects/ereftwebsite/  # Next.js web frontend
```

## Environment Variables (Redacted)
Configure these in Render/Vercel/Expo. Never commit secrets.

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django cryptographic secret |
| `DATABASE_URL` | PostgreSQL connection string |
| `ALLOWED_HOSTS` | Include `ereft.com`, Render hostnames |
| `CLOUDINARY_URL` | Cloudinary credentials |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth web + mobile code exchange |
| `GOOGLE_REDIRECT_URI` | `https://ereft.onrender.com/oauth` |
| `FRONTEND_URL` | Web origin (`https://www.ereft.com`) |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_PHONE_NUMBER` | SMS verification |
| `GOOGLE_MAPS_API_KEY` | Maps/geocode for backend |
| `NEXT_PUBLIC_API_URL` | Web API base (`https://ereft.onrender.com`) |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Web maps key |
| `EXPO_PUBLIC_API_URL` | Mobile API base |
| `EXPO_PUBLIC_GOOGLE_MAPS_API_KEY` | Mobile maps key |

Maintain `.env.example` placeholders in each repo.

## Backend (Django / DRF)
- **PropertyViewSet**
  - `GET /api/listings/properties/` — filter by search, listing/property type, price, bedrooms, bathrooms, city.
  - `POST /api/listings/properties/` — accepts multipart uploads (web) *or* `images` array of Cloudinary URLs (mobile). Returns the full `PropertyDetailSerializer` payload, including UUID.
  - `GET /api/listings/properties/<uuid>/` — cached for 60 s.
  - `DELETE /api/listings/properties/<uuid>/` — owner-only, clears cache + dependent keys.
  - `GET /api/listings/properties/stats/` — `{ total, for_sale, for_rent, average_price }` (floats serialized for clients).
- **FavoritesViewSet**
  - `GET /api/listings/favorites/` — paginated list of saved properties for the current user.
  - `POST /api/listings/favorites/` body `{ "property": "<uuid>" }` — idempotent create; returns the created favorite with nested property snapshot.
  - `DELETE /api/listings/favorites/<uuid>/` — treats `<uuid>` as the property ID and removes the favorite for the authenticated user.
- **Contact & Reviews** — Property actions for inquiries (`POST /properties/<uuid>/contact/`) and reviews remain available.
- **Sample Data** — Migration `0007_populate_sample_properties` and management command `populate_sample_data` seed realistic Ethiopian listings (images, metadata, sample agent).
- **Caching** — Property list/detail, stats, and favorites responses respect LocMem cache. Create/Update/Delete clear relevant keys.

## Frontend Web (Next.js)
- **Global Data Access**: Shared `lib/api.ts` fetch helpers enforce tagging + caching, type-safe responses, and error propagation.
- **Homepage (`app/page.tsx`)**
  - Server-renders stats + featured listings. Fallback to skeleton UI on fetch failure (no fake data).
  - Stats cards match API shape; mobile nav includes Search / Map / Login + “Get Started” CTA.
- **Property List (`app/properties/page.tsx`)**
  - Server-streamed initial payload with Suspense fallback.
  - Client component handles filter state, URL sync, optimistic loading states, and favorite toggles.
  - Listing cards include agent contact summary (email/phone) and map quick links.
- **Property Detail (`app/properties/[id]/page.tsx`)**
  - Server component returns a friendly fallback when a property is missing (no 404 crash).
  - Client component renders galleries, price context, feature chips, contact info, map CTA, and owner-only delete with optimistic redirect.
- **Add Property (`app/add-property/page.tsx`)**
  - Requires auth; builds `FormData` and posts to Next API route (proxy to DRF). Images are optional; errors surfaced inline.
- **Static Pages**
  - `about`, `careers`, `blog`, `contact`, `faq`, `privacy`, `terms` eliminate footer/header dead links.
- **Navigation & Auth**
  - `AuthContext` stores token/user in `localStorage`; mobile header icons mirror React Native quick actions.

## Mobile App (React Native + Expo)
- **Context Providers**
  - `AuthContext` persists JWT in AsyncStorage, wraps API client.
  - `PropertyContext` handles listing fetch, favorites, Cloudinary uploads, stats, and local fallbacks.
- **Property Creation**
  - Users pick photos via Expo ImagePicker, upload to Cloudinary (with timeout + retry), then POST property payload (image URLs) to backend. Backend converts to `PropertyImage` records.
- **Property Detail**
  - Normalizes backend payload: gallery supports string/object URLs; owner contact displays email/phone when supplied.
  - “Contact Agent” opens dialer; map CTA navigates to `MapScreen` with the property selected.
- **Favorites**
  - Toggle integrates with DRF favorites API; deletes by property UUID to stay in sync with web.
- **Home Screen**
  - Market overview uses `/stats/` data; quick actions mirror web (Favorites, List Property, Map).
- **Offline Fallback**
  - Demo datasets still exist but are only used when API calls fail (logged for debugging).

## Data Flow Summary
1. **Authentication**: Users authenticate via credentials or Google OAuth → backend issues DRF token (web) or JWT (mobile) → clients persist tokens.
2. **Property Create**: Clients submit property payload (files or Cloudinary URLs) → backend uploads/validates → creates `Property` + `PropertyImage` → caches invalidated → detail/list endpoints reflect instantly.
3. **Favorites**: Clients POST/DELETE favorites via property UUID → backend maintains `Favorite` records and returns normalized property snapshots → both clients update local state.
4. **Stats**: Web + mobile call `/stats/`; backend computes from active/published properties and returns numeric metrics.
5. **Sample Data**: Run migration/command to ensure production DB never ships empty.

## Testing & QA
Run these before shipping:

### Backend
```bash
cd /Users/melaku/Documents/Projects/Ethioprojects/Ereft
# Activate virtualenv / conda environment first
python manage.py migrate          # Ensure schema is current
python manage.py test             # Optional: execute available unit tests
python manage.py populate_sample_data  # Load demo inventory (idempotent)
```

### Web Frontend
```bash
cd /Users/melaku/Documents/Projects/Ethioprojects/ereftwebsite
npm install
npm run lint
npm run build
```
Manual QA: login/logout, property create/delete, filter, favorites, map view, navigation links.

### Mobile
```bash
cd /Users/melaku/Documents/Projects/Ethioprojects/Ereft/ereft_mobile
npm install
npx expo start --tunnel
```
Device QA: auth flow, property list/detail, favorites, add property (with photo), map markers.

## Deployment Checklist

### Render (Backend)
1. Push latest changes to `main`.
2. Trigger Render deploy or click **Manual Deploy**.
3. SSH into Render shell (or use dashboard) and run:
   ```bash
   python manage.py migrate
   python manage.py populate_sample_data  # optional but recommended if DB empty
   ```
4. Confirm health check: `https://ereft.onrender.com/api/listings/properties/stats/`.

### Vercel (Web)
1. Push web repo changes to production branch.
2. Ensure `NEXT_PUBLIC_API_URL` and Google Maps env vars are set in Vercel.
3. Verify build succeeds (`npm run build`).
4. After deploy, smoke-test `/`, `/properties`, `/properties/<uuid>`, `/add-property`.

### Expo / EAS (Mobile)
```bash
cd ereft_mobile
eas login
expo doctor
# Configure app.json / eas.json with production env vars
EAS_NO_VCS=1 eas build --platform ios
EAS_NO_VCS=1 eas build --platform android
```
Upload resulting binaries to App Store Connect / Google Play Console. Ensure the OAuth redirect (`ereft://oauth`) is registered.

## Follow-Up & Enhancements
- Enable email notifications for inquiries (`ContactSerializer`) and integrate Twilio verify endpoints in the UI.
- Add pagination to web/mobile property lists when inventory grows.
- Extend caching layer with Redis/Memcache if traffic exceeds LocMem limits.
- Implement server-side analytics (views, favorites) reporting dashboards.
- Localize copy (Amharic) using i18n libraries on both web and mobile.

---

*This document reflects the current production-ready state of the Ereft platform. Update alongside future releases.*
*** End of File

