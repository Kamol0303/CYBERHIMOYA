package uz.cyberguardian.android.api

import java.net.HttpURLConnection
import java.net.URL

/**
 * Minimal JVM HTTP client stub (replace with Retrofit/Ktor in production module).
 * Defensive endpoints only.
 */
class HttpGuardianApi(
    private val baseUrl: String,
    private val tokenProvider: () -> String? = { null },
) : GuardianApi {
    override suspend fun scanUrl(url: String): ScanResponse {
        val body = """{"url":${jsonString(url)},"context":{"source":"manual","client_cache_hit":false}}"""
        val json = postJson("/v1/scan/url", body, auth = false)
        return ScanResponse(
            scanId = readString(json, "scan_id"),
            urlNormalized = readString(json, "url_normalized"),
            score = readInt(json, "score"),
            verdict = readString(json, "verdict"),
            recommendedAction = readString(json, "recommended_action"),
            mitreTags = emptyList(),
        )
    }

    override suspend fun scanQr(payloadText: String): QrScanResponse {
        val body = """{"payload_text":${jsonString(payloadText)}}"""
        val json = postJson("/v1/scan/qr", body, auth = false)
        return QrScanResponse(
            scanId = readString(json, "scan_id"),
            qrType = readString(json, "qr_type"),
            score = readInt(json, "score"),
            verdict = readString(json, "verdict"),
            recommendedAction = readString(json, "recommended_action"),
        )
    }

    override suspend fun scanFileHash(sha256: String, fileName: String?): FileScanResponse {
        val body =
            """{"sha256":${jsonString(sha256)},"file_name":${fileName?.let { jsonString(it) } ?: "null"},"run_yara":false}"""
        val json = postJson("/v1/scan/file", body, auth = false)
        return FileScanResponse(
            scanId = readString(json, "scan_id"),
            sha256 = readString(json, "sha256"),
            score = readInt(json, "score"),
            verdict = readString(json, "verdict"),
            recommendedAction = readString(json, "recommended_action"),
        )
    }

    override suspend fun syncThreatFeed(sinceVersion: String?): ThreatFeedSync {
        val path =
            if (sinceVersion.isNullOrBlank()) "/v1/threat-feed/sync"
            else "/v1/threat-feed/sync?since_version=$sinceVersion"
        val json = getJson(path)
        return ThreatFeedSync(
            version = readString(json, "version"),
            deltaUrl = readNullableString(json, "delta_url"),
            signature = readString(json, "signature"),
            algorithm = readString(json, "algorithm"),
        )
    }

    override suspend fun register(email: String, password: String, locale: String): TokenResponse {
        val body =
            """{"email":${jsonString(email)},"password":${jsonString(password)},"locale":${jsonString(locale)}}"""
        val json = postJson("/v1/auth/register", body, auth = false)
        return tokenFrom(json)
    }

    override suspend fun login(email: String, password: String): TokenResponse {
        val body = """{"email":${jsonString(email)},"password":${jsonString(password)}}"""
        val json = postJson("/v1/auth/token", body, auth = false)
        return tokenFrom(json)
    }

    override suspend fun listScans(): List<ScanHistoryItem> = emptyList()

    override suspend fun upsertConsent(type: String, granted: Boolean): ConsentRecord =
        ConsentRecord(type, granted)

    private fun tokenFrom(json: String) = TokenResponse(
        accessToken = readString(json, "access_token"),
        refreshToken = readString(json, "refresh_token"),
        expiresIn = readInt(json, "expires_in"),
    )

    private fun postJson(path: String, body: String, auth: Boolean): String {
        val conn = (URL(baseUrl.trimEnd('/') + path).openConnection() as HttpURLConnection)
        conn.requestMethod = "POST"
        conn.setRequestProperty("Content-Type", "application/json")
        conn.setRequestProperty("Accept", "application/json")
        if (auth) tokenProvider()?.let { conn.setRequestProperty("Authorization", "Bearer $it") }
        conn.doOutput = true
        conn.outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
        return conn.inputStream.bufferedReader().readText()
    }

    private fun getJson(path: String): String {
        val conn = (URL(baseUrl.trimEnd('/') + path).openConnection() as HttpURLConnection)
        conn.requestMethod = "GET"
        conn.setRequestProperty("Accept", "application/json")
        return conn.inputStream.bufferedReader().readText()
    }
}

private fun jsonString(value: String): String =
    "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\""

private fun readString(json: String, key: String): String {
    val re = Regex("\"$key\"\\s*:\\s*\"([^\"]*)\"")
    return re.find(json)?.groupValues?.get(1) ?: ""
}

private fun readNullableString(json: String, key: String): String? {
    val v = readString(json, key)
    return v.ifBlank { null }
}

private fun readInt(json: String, key: String): Int {
    val re = Regex("\"$key\"\\s*:\\s*(-?\\d+)")
    return re.find(json)?.groupValues?.get(1)?.toIntOrNull() ?: 0
}
