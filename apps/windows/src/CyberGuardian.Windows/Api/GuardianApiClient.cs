// Cyber Guardian AI — Windows V1 API client
// Defensive only: scan + feed sync.

using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace CyberGuardian.Windows.Api;

public sealed class GuardianApiClient
{
    private readonly HttpClient _http;

    public GuardianApiClient(HttpClient http) => _http = http;

    public async Task<UrlScanResponse?> ScanUrlAsync(string url, CancellationToken ct = default)
    {
        using var res = await _http.PostAsJsonAsync(
            "/v1/scan/url",
            new { url, context = new { source = "manual", client_cache_hit = false } },
            ct);
        if (!res.IsSuccessStatusCode) return null;
        return await res.Content.ReadFromJsonAsync<UrlScanResponse>(cancellationToken: ct);
    }

    public async Task<ThreatFeedSync?> SyncFeedAsync(string? sinceVersion = null, CancellationToken ct = default)
    {
        var path = string.IsNullOrEmpty(sinceVersion)
            ? "/v1/threat-feed/sync"
            : $"/v1/threat-feed/sync?since_version={Uri.EscapeDataString(sinceVersion)}";
        return await _http.GetFromJsonAsync<ThreatFeedSync>(path, ct);
    }

    public async Task<EmergencyAllowlist?> GetEmergencyAllowlistAsync(CancellationToken ct = default) =>
        await _http.GetFromJsonAsync<EmergencyAllowlist>("/v1/emergency/allowlist", ct);
}

public sealed record UrlScanResponse(
    [property: JsonPropertyName("scan_id")] string ScanId,
    [property: JsonPropertyName("url_normalized")] string UrlNormalized,
    [property: JsonPropertyName("score")] int Score,
    [property: JsonPropertyName("verdict")] string Verdict,
    [property: JsonPropertyName("recommended_action")] string RecommendedAction
);

public sealed record ThreatFeedSync(
    [property: JsonPropertyName("version")] string Version,
    [property: JsonPropertyName("delta_url")] string? DeltaUrl,
    [property: JsonPropertyName("signature")] string Signature,
    [property: JsonPropertyName("algorithm")] string Algorithm
);

public sealed record EmergencyAllowlist(
    [property: JsonPropertyName("aq039_resolved")] bool Aq039Resolved,
    [property: JsonPropertyName("dry_run_forced")] bool DryRunForced,
    [property: JsonPropertyName("note")] string Note
);

/// <summary>
/// Verify ed25519 signed feed pack before applying IOCs (NFR-011).
/// Production: use NSec/BouncyCastle with embedded public key.
/// </summary>
public static class FeedVerifier
{
    public static bool LooksLikeSignedPack(string signedPayload, string signature, string publicKeyB64) =>
        !string.IsNullOrWhiteSpace(signedPayload)
        && !string.IsNullOrWhiteSpace(signature)
        && !string.IsNullOrWhiteSpace(publicKeyB64);
}
