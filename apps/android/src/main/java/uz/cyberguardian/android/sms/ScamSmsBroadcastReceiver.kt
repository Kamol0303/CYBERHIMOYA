package uz.cyberguardian.android.sms

/**
 * Platform BroadcastReceiver adapter.
 * Real module: extend android.content.BroadcastReceiver and call [ScamSmsReceiver].
 */
class ScamSmsBroadcastReceiver {
    private val analyzer = ScamSmsReceiver()

    fun handle(
        sender: String?,
        body: String,
        smsConsentGranted: Boolean,
    ): SmsLocalVerdict? = analyzer.onSmsReceived(sender, body, smsConsentGranted)
}
