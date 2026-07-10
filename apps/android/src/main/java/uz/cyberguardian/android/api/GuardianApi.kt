package uz.cyberguardian.android.api

/**
 * V1 defensive API client stub (Kotlin).
 * Wire with Retrofit/Ktor — no offensive capabilities.
 */
interface GuardianApi {
    suspend fun scanUrl(url: String): ScanResponse
    suspend fun scanQr(payloadText: String): QrScanResponse
    suspend fun scanFileHash(sha256: String, fileName: String?): FileScanResponse
    suspend fun syncThreatFeed(sinceVersion: String?): ThreatFeedSync
    suspend fun register(email: String, password: String, locale: String): TokenResponse
    suspend fun login(email: String, password: String): TokenResponse
    suspend fun listScans(): List<ScanHistoryItem>
    suspend fun upsertConsent(type: String, granted: Boolean): ConsentRecord
}

data class ScanResponse(
    val scanId: String,
    val urlNormalized: String,
    val score: Int,
    val verdict: String,
    val recommendedAction: String,
    val mitreTags: List<String>,
)

data class QrScanResponse(
    val scanId: String,
    val qrType: String,
    val score: Int,
    val verdict: String,
    val recommendedAction: String,
)

data class FileScanResponse(
    val scanId: String,
    val sha256: String,
    val score: Int,
    val verdict: String,
    val recommendedAction: String,
)

data class ThreatFeedSync(
    val version: String,
    val deltaUrl: String?,
    val signature: String,
    val algorithm: String,
)

data class TokenResponse(
    val accessToken: String,
    val refreshToken: String,
    val expiresIn: Int,
)

data class ScanHistoryItem(
    val scanId: String,
    val scanType: String,
    val score: Int,
    val verdict: String,
)

data class ConsentRecord(
    val consentType: String,
    val granted: Boolean,
)

/**
 * Clients MUST verify feed signature with ed25519 public key before applying IOC deltas (NFR-011).
 */
object FeedVerifier {
    fun isValid(
        signedPayload: String,
        signatureB64: String,
        publicKeyB64: String,
    ): Boolean {
        // Production: use Tink or BouncyCastle Ed25519 verify.
        // This stub documents the contract; wire crypto in the Android module.
        return signedPayload.isNotBlank() && signatureB64.isNotBlank() && publicKeyB64.isNotBlank()
    }
}
