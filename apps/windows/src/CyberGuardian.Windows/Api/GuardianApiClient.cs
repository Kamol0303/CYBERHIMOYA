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
/// Verify signed feed pack before applying IOCs (NFR-011). Production: ed25519 public key.
/// </summary>
public static class FeedVerifier
{
    public static bool VerifyStub(string signedPayload, string signature, string secret)
    {
        using var sha = System.Security.Cryptography.SHA256.Create();
        var bytes = sha.ComputeHash(System.Text.Encoding.UTF8.GetBytes(secret + signedPayload));
        var expected = Convert.ToBase64String(bytes);
        return CryptographicEquals(expected, signature);
    }

    private static bool CryptographicEquals(string a, string b) =>
        System.Security.Cryptography.CryptographicOperations.FixedTimeEquals(
            System.Text.Encoding.UTF8.GetBytes(a),
            System.Text.Encoding.UTF8.GetBytes(b));
}
