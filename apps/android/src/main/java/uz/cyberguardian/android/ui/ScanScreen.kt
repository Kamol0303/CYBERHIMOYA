package uz.cyberguardian.android.ui

/**
 * V1 Compose UI shell — defensive scan + consent only.
 * Wire into a real Android module with Jetpack Compose dependencies.
 */
object ScanScreenCopy {
    const val Brand = "Cyber Guardian AI"
    const val Tagline = "Mudofaa skaneri"
    const val UrlHint = "URL kiriting"
    const val QrHint = "QR matnini kiriting"
    const val FileHint = "Fayl tanlang (faqat SHA-256 yuboriladi)"
    const val ConsentSms = "SMS tekshiruvi faqat qurilmada (cloudga yuborilmaydi)"
}

data class ScanUiState(
    val mode: String = "url", // url | qr | file
    val input: String = "",
    val loading: Boolean = false,
    val score: Int? = null,
    val verdict: String? = null,
    val action: String? = null,
)

/**
 * Pseudo-Compose structure for the first screen.
 * Replace with @Composable fun ScanScreen(...) in the Android Studio project.
 */
class ScanScreenController(
    private val onScanUrl: suspend (String) -> Unit,
    private val onScanQr: suspend (String) -> Unit,
) {
    var state: ScanUiState = ScanUiState()
        private set

    suspend fun submit() {
        state = state.copy(loading = true)
        try {
            when (state.mode) {
                "qr" -> onScanQr(state.input)
                else -> onScanUrl(state.input)
            }
        } finally {
            state = state.copy(loading = false)
        }
    }
}
