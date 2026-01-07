# Ereft Deployment Guide

This guide captures the exact steps required to ship the Ereft platform (backend on Render, web on Vercel, mobile via Expo EAS). It assumes code is up to date with the production-ready changes described in `docs/Ereft_Project_Overview.md`.

---

## 1. Prerequisites
- Render account with PostgreSQL instance (production DB).
- Vercel project connected to `ereftwebsite` repository.
- Expo account with EAS credits for iOS/Android builds.
- Cloudinary, Google OAuth, Twilio credentials stored as environment variables (see overview doc).

---

## 2. Backend (Render)
1. **Push latest code** to `main` (or deployment branch).
2. **Trigger deploy** in Render dashboard.
3. **Run migrations + seed data**:
   ```bash
   # Render shell or deploy hook
   python manage.py migrate
   python manage.py populate_sample_data  # optional but recommended for empty DBs
   ```
4. **Smoke test API**:
   - `GET https://<render-app>/api/listings/properties/stats/`
   - `POST https://<render-app>/api/listings/properties/` with sample payload (multipart or image URLs).

---

## 3. Web Frontend (Vercel)
1. Ensure the following env vars are set in Vercel:
   - `NEXT_PUBLIC_API_URL=https://<render-app>`
   - `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`
2. Run locally before pushing:
   ```bash
   npm install
   npm run lint
   npm run build
   ```
3. Push changes; Vercel will auto-build.
4. Validate production URLs:
   - `/` (stats + featured load instantly)
   - `/properties` (filters + favorites toggles)
   - `/properties/<uuid>` (detail renders, contact info present)
   - `/add-property` (auth required, submit form)

---

## 4. Mobile (Expo / EAS)
1. Confirm `EXPO_PUBLIC_API_URL`, `EXPO_PUBLIC_GOOGLE_MAPS_API_KEY`, and Cloudinary env values in `app.json`/`eas.json`.
2. Build binaries:
   ```bash
   cd ereft_mobile
   npm install
   expo doctor
   EAS_NO_VCS=1 eas build --platform ios
   EAS_NO_VCS=1 eas build --platform android
   ```
3. Upload artifacts to App Store Connect and Google Play Console.
4. Smoke test using Expo Go or TestFlight: login, add property (upload image), toggle favorites, view map markers.

---

## 5. Final Checks
- **Monitoring**: Verify Render logs show cache hits/misses; set up uptime checks.
- **Search Console**: Confirm the Google verification file exists (`public/google24e517a3fba6dd1d.html`).
- **Analytics**: Optional — hook up to GA4 or Segment after launch.
- **Support**: Ensure `support@ereft.com` mailbox is monitored.

---

Keep this guide updated alongside production releases. For deeper architectural details, reference `docs/Ereft_Project_Overview.md`.
