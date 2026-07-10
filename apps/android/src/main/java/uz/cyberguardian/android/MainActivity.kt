package uz.cyberguardian.android

import uz.cyberguardian.android.api.HttpGuardianApi
import uz.cyberguardian.android.ui.GuardianAppViewModel

/**
 * MainActivity production shell.
 *
 * Real wiring (Android Studio):
 * ```
 * class MainActivity : ComponentActivity() {
 *   override fun onCreate(savedInstanceState: Bundle?) {
 *     super.onCreate(savedInstanceState)
 *     val vm = GuardianAppViewModel(HttpGuardianApi(BuildConfig.API_BASE))
 *     setContent {
 *       when (vm.ui.screen) {
 *         "auth" -> AuthScreen(...)
 *         "dashboard" -> DashboardScreen(...)
 *         else -> ScanScreen(...)
 *       }
 *     }
 *   }
 * }
 * ```
 */
class MainActivity {
    private val apiBase: String = System.getenv("CGA_API_BASE") ?: "http://10.0.2.2:8000"
    private val vm = GuardianAppViewModel(HttpGuardianApi(apiBase))

    fun onCreate() {
        // setContent { ... } — enable after Compose dependencies
        vm.setScreen("scan")
    }
}
