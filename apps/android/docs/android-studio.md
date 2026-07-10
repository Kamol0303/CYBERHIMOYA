# Android Studio import

1. Open `apps/android` in Android Studio (Giraffe+).
2. Sync Gradle (`compose = true` and Compose BOM version are already set).
3. In `app/build.gradle.kts`, **uncomment** the Compose dependency lines (`implementation(composeBom)`, ui, material3, activity-compose).
4. Uncomment `@Composable` imports / bodies in `ui/Screens.kt`.
5. Convert `MainActivity` to `ComponentActivity` + `setContent` (see comments in file).
6. Point API base to `http://10.0.2.2:8000` on emulator (`CGA_API_BASE`). `HttpGuardianApi` implements `GuardianApi`.
7. SMS: raw body stays on-device via `OnDeviceSmsAnalyzer`.
8. `SEND_SMS` only after emergency consent + AQ-039 allowlist.
