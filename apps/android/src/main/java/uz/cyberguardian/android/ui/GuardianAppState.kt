package uz.cyberguardian.android.ui

/**
 * Richer Compose screen model for production wiring.
 */
data class ScanResultUi(
    val title: String,
    val score: Int,
    val verdict: String,
    val action: String,
    val mitre: List<String> = emptyList(),
    val reasons: List<String> = emptyList(),
)

data class ConsentUiState(
    val analytics: Boolean = false,
    val smsOnDevice: Boolean = false,
    val emergencyLawEnforcement: Boolean = false,
)

data class GuardianAppUiState(
    val locale: String = "uz",
    val screen: String = "scan", // scan | dashboard | auth | emergency
    val scan: ScanUiState = ScanUiState(),
    val result: ScanResultUi? = null,
    val consents: ConsentUiState = ConsentUiState(),
    val signedInEmail: String? = null,
)

object EmergencyCopy {
    const val Title = "Favqulodda xabar"
    const val Body =
        "Faqat Critical + oldindan rozilik + ikki marta tasdiq. " +
            "AQ-039 allowlist bo‘lmaguncha faqat dry-run jurnal."
    const val OptIn = "IIV/UZCERT ga anonymized xabar (opt-in)"
}
