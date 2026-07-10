package uz.cyberguardian.android.sms

/**
 * SMS BroadcastReceiver shell (V2).
 *
 * - Analyzes on-device only via [OnDeviceSmsAnalyzer]
 * - Never uploads raw SMS body
 * - Optional anonymized alert callback (consent-gated) can be wired later
 */
class ScamSmsReceiver {
    fun onSmsReceived(sender: String?, body: String, smsConsentGranted: Boolean): SmsLocalVerdict? {
        if (!smsConsentGranted) return null
        return OnDeviceSmsAnalyzer.analyze(sender, body)
    }

    fun shouldRequestSendSmsPermission(emergencyConsentGranted: Boolean): Boolean =
        emergencyConsentGranted
}
