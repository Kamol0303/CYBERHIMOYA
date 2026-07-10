# Android Studio import

1. Open `apps/android` in Android Studio (Giraffe+).
2. Sync Gradle; add Compose BOM dependencies in `app/build.gradle.kts`.
3. Point API base to `http://10.0.2.2:8000` on emulator.
4. SMS: raw body stays on-device via `OnDeviceSmsAnalyzer`.
5. `SEND_SMS` only after emergency consent + AQ-039 allowlist.
