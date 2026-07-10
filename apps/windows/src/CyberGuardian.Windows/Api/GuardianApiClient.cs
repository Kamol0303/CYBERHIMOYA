// Cyber Guardian AI — Windows V1 API client stub (.NET)
// Defensive only: scan + feed sync. No offensive tooling.

using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace CyberGuardian.Windows.Api;

public sealed class GuardianApiClient
{
    private readonly HttpClient _http;

    public GuardianApiClient(HttpClient http) => _http = http;

    public Task<UrlScanResponse?> ScanUrlAsync(string url, CancellationToken ct = default) =>
        _http.PostAsJsonAsync("/v1/scan/url", new { url, context = new { source = "manual" } }, ct)
            .ContinueWith(async t => await t.Result.Content.ReadFromJsonAsync<UrlScanResponse>(ct), ct)
            .Unwrap();

    public Task<ThreatFeedSync?> SyncFeedAsync(string? sinceVersion = null, CancellationToken ct = default)
    {
        var path = string.IsNullOrEmpty(sinceVersion)
            ? "/v1/threat-feed/sync"
            : $"/v1/threat-feed/sync?since_version={Uri.EscapeDataString(sinceVersion)}";
        return _http.GetFromJsonAsync<ThreatFeedSync>(path, ct);
    }
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

/// <summary>
/// Verify ed25519 signed feed pack before applying IOCs (NFR-011).
/// Production: use NSec or BouncyCastle Ed25519 with embedded public key.
/// </summary>
public static class FeedVerifier
{
    public static bool LooksLikeSignedPack(string signedPayload, string signature, string publicKeyB64) =>
        !string.IsNullOrWhiteSpace(signedPayload)
        && !string.IsNullOrWhiteSpace(signature)
        && !string.IsNullOrWhiteSpace(publicKeyB64);
}
