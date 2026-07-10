package uz.cyberguardian.android.ui

import uz.cyberguardian.android.api.GuardianApi
import uz.cyberguardian.android.api.ScanResponse

/**
 * Production-oriented Compose screens.
 *
 * When opening in Android Studio, uncomment @Composable imports and annotations
 * after enabling Compose BOM in app/build.gradle.kts.
 *
 * import androidx.compose.foundation.layout.*
 * import androidx.compose.material3.*
 * import androidx.compose.runtime.*
 * import androidx.compose.ui.Modifier.*
 */

// @Composable
fun ScanScreen(
    state: ScanUiState,
    onMode: (String) -> Unit,
    onInput: (String) -> Unit,
    onSubmit: () -> Unit,
    result: ScanResultUi?,
) {
    // Scaffold / Column layout:
    // Brand (hero) → tagline → mode tabs → input → CTA → result
    ScanScreenCopy
    state
    onMode
    onInput
    onSubmit
    result
}

// @Composable
fun AuthScreen(
    email: String,
    password: String,
    onEmail: (String) -> Unit,
    onPassword: (String) -> Unit,
    onLogin: () -> Unit,
    onRegister: () -> Unit,
    error: String?,
) {
    email; password; onEmail; onPassword; onLogin; onRegister; error
}

// @Composable
fun DashboardScreen(
    email: String,
    consents: ConsentUiState,
    onConsent: (String, Boolean) -> Unit,
    history: List<ScanResultUi>,
) {
    email; consents; onConsent; history
}

/**
 * App root navigation shell.
 */
class GuardianAppViewModel(
    private val api: GuardianApi,
) {
    var ui: GuardianAppUiState = GuardianAppUiState()
        private set

    suspend fun submitScan() {
        ui = ui.copy(scan = ui.scan.copy(loading = true))
        try {
            when (ui.scan.mode) {
                "qr" -> {
                    val r = api.scanQr(ui.scan.input)
                    ui = ui.copy(
                        result = ScanResultUi(
                            title = r.qrType,
                            score = r.score,
                            verdict = r.verdict,
                            action = r.recommendedAction,
                        ),
                    )
                }
                else -> {
                    val r: ScanResponse = api.scanUrl(ui.scan.input)
                    ui = ui.copy(
                        result = ScanResultUi(
                            title = r.urlNormalized,
                            score = r.score,
                            verdict = r.verdict,
                            action = r.recommendedAction,
                            mitre = r.mitreTags,
                        ),
                    )
                }
            }
        } finally {
            ui = ui.copy(scan = ui.scan.copy(loading = false))
        }
    }

    fun setScreen(screen: String) {
        ui = ui.copy(screen = screen)
    }

    fun setMode(mode: String) {
        ui = ui.copy(scan = ui.scan.copy(mode = mode), result = null)
    }

    fun setInput(value: String) {
        ui = ui.copy(scan = ui.scan.copy(input = value))
    }
}
