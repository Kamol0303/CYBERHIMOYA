namespace CyberGuardian.Windows.Monitoring;

/// <summary>
/// FR-072 network monitoring stub — process↔egress correlation (detect/warn).
/// No packet injection, no MITM, no active scanning of third parties.
/// </summary>
public sealed class NetworkMonitor
{
    public sealed record Finding(
        string ProcessHint,
        string DomainHint,
        string ReasonCode,
        string Severity,
        string RecommendedAction);

    public Finding? EvaluateConnection(string processName, string remoteHost, bool tiHit)
    {
        var proc = processName ?? string.Empty;
        var host = (remoteHost ?? string.Empty).ToLowerInvariant();

        if (tiHit)
        {
            return new Finding(
                Redact(proc),
                Redact(host),
                "NET_TI_HIT",
                "critical",
                "warn_and_isolate_local");
        }

        if (host.EndsWith(".tk") || host.EndsWith(".ml") || host.EndsWith(".cf"))
        {
            return new Finding(
                Redact(proc),
                Redact(host),
                "NET_SUSPICIOUS_TLD",
                "warning",
                "warn_and_review");
        }

        return null;
    }

    private static string Redact(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return "***";
        return value.Length <= 3 ? "***" : value[..3] + "***";
    }
}
