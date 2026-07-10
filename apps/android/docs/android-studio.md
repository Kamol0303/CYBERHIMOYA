# Android Studio import

1. Open `apps/android` in Android Studio (Giraffe+).
2. Sync Gradle; enable Compose BOM in `app/build.gradle.kts`.
3. Uncomment `@Composable` imports in `ui/Screens.kt`.
4. Convert `MainActivity` to `ComponentActivity` + `setContent` (see comments in file).
5. Point API base to `http://10.0.2.2:8000` on emulator (`CGA_API_BASE`).
6. SMS: raw body stays on-device via `OnDeviceSmsAnalyzer`.
7. `SEND_SMS` only after emergency consent + AQ-039 allowlist.
