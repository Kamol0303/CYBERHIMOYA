package uz.cyberguardian.android.wifi

/**
 * FR-061 Wi-Fi analyzer stub — on-device heuristics only.
 *
 * Hard rules:
 * - No credential capture
 * - No active probing / deauth / evil-twin tooling
 * - Warn user about open / suspiciously named networks
 */
data class WifiFinding(
    val ssidHint: String,
    val code: String,
    val severity: String,
    val recommendedAction: String,
)

object WifiAnalyzer {
    private val suspiciousTokens = listOf(
        "freewifi", "airport_free", "starbucks_free", "bank_wifi",
        "gov_wifi", "iiv", "soliq", "payme_free",
    )

    /**
     * @param ssid network name (may be empty if hidden)
     * @param isOpen true when network has no encryption
     */
    fun analyze(ssid: String?, isOpen: Boolean): List<WifiFinding> {
        val findings = mutableListOf<WifiFinding>()
        val name = ssid?.lowercase().orEmpty()

        if (isOpen) {
            findings += WifiFinding(
                ssidHint = redact(ssid),
                code = "WIFI_OPEN",
                severity = "warning",
                recommendedAction = "avoid_or_use_vpn",
            )
        }
        if (suspiciousTokens.any { it in name }) {
            findings += WifiFinding(
                ssidHint = redact(ssid),
                code = "WIFI_SUSPICIOUS_NAME",
                severity = "warning",
                recommendedAction = "warn_and_review",
            )
        }
        return findings
    }

    private fun redact(ssid: String?): String {
        if (ssid.isNullOrBlank()) return "(hidden)"
        return if (ssid.length <= 3) "***" else ssid.take(2) + "***"
    }
}
