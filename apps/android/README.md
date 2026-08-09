# journal-android

Android client for journal — a thin WebView shell over the web app.

## What it is

The web app (`apps/web`) is a full client: login/register, entries, and
real-time sync over WebSocket. The Android app embeds it in a WebView, so the
phone gets the exact same product without maintaining a separate UI.

## Build

```bash
./gradlew assembleDebug
# APK at app/build/outputs/apk/debug/app-debug.apk
```

Requires Android SDK (compileSdk 35). Set `ANDROID_HOME` if needed.

## Configuration

The web app URL is baked in at build time via the `WEB_APP_URL` Gradle
property:

```bash
./gradlew assembleDebug -PWEB_APP_URL=https://klcombr.github.io/journal/apps/web/
```
