package uz.cyberguardian.android.sms

/**
 * On-device SMS scam heuristics (V2 foundation).
 *
 * Hard rules:
 * - Raw SMS body NEVER leaves the device
 * - Only optional anonymized risk events may sync later (consent-gated)
 * - No active probing / no auto-reply to senders
 */
data class SmsHeuristicHit(
    val code: String,
    val weight: Int,
    val family: String? = null,
)

data class SmsLocalVerdict(
    val score: Int,
    val verdict: String,
    val hits: List<SmsHeuristicHit>,
    val recommendedAction: String,
)

object OnDeviceSmsAnalyzer {
    private val payment = listOf("payme", "click", "uzum", "to'lov", "tolov", "karta pin", "cvv")
    private val gov = listOf("soliq", "iiv", "jarima", "subsidiya", "my.gov")
    private val urgency = listOf("zudlik", "blok", "hisobingiz", "darhol", "tezkor", "emergency")
    private val linkish = Regex("""https?://|\w+\.(tk|ml|ga|cf|gq|xyz)\b""", RegexOption.IGNORE_CASE)

    fun analyze(sender: String?, body: String): SmsLocalVerdict {
        val text = body.lowercase()
        val hits = mutableListOf<SmsHeuristicHit>()
        var score = 5

        if (payment.any { it in text }) {
            hits += SmsHeuristicHit("SMS_PAYMENT_LURE", 25, "payment_scam")
            score += 25
        }
        if (gov.any { it in text }) {
            hits += SmsHeuristicHit("SMS_GOV_IMPERSONATION", 30, "gov_impersonation")
            score += 30
        }
        if (urgency.any { it in text }) {
            hits += SmsHeuristicHit("SMS_URGENCY", 15, "emergency_scam")
            score += 15
        }
        if (linkish.containsMatchIn(body)) {
            hits += SmsHeuristicHit("SMS_SUSPICIOUS_LINK", 20, null)
            score += 20
        }
        val shortSender = sender?.filter { it.isDigit() || it == '+' }.orEmpty()
        if (shortSender.isNotEmpty() && shortSender.length <= 6) {
            hits += SmsHeuristicHit("SMS_SHORTCODE_SENDER", 10, null)
            score += 10
        }

        score = score.coerceIn(0, 100)
        val verdict = when {
            score >= 80 -> "malicious"
            score >= 40 -> "suspicious"
            else -> "clean"
        }
        val action = when (verdict) {
            "malicious" -> "block_and_warn"
            "suspicious" -> "warn_and_review"
            else -> "allow"
        }
        return SmsLocalVerdict(score, verdict, hits, action)
    }
}
