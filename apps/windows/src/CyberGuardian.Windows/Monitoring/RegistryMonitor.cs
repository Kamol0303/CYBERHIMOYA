namespace CyberGuardian.Windows.Monitoring;

/// <summary>
/// FR-071 registry monitoring stub — detect/warn only.
/// Watches policy-listed keys conceptually; no exploit tooling.
/// </summary>
public sealed class RegistryMonitor
{
    public sealed record Finding(
        string KeyHint,
        string ReasonCode,
        string Severity,
        string RecommendedAction);

    private static readonly string[] WatchedSuffixes =
    {
        @"\Run",
        @"\RunOnce",
        @"\Image File Execution Options",
    };

    public Finding? EvaluateChange(string keyPath, string valueName)
    {
        var path = keyPath ?? string.Empty;
        foreach (var suffix in WatchedSuffixes)
        {
            if (path.EndsWith(suffix, StringComparison.OrdinalIgnoreCase))
            {
                return new Finding(
                    Redact(path),
                    "REG_AUTOSTART",
                    "warning",
                    "warn_and_review");
            }
        }

        if (!string.IsNullOrEmpty(valueName) &&
            valueName.Contains("debugger", StringComparison.OrdinalIgnoreCase))
        {
            return new Finding(
                Redact(path),
                "REG_IFEO_DEBUGGER",
                "critical",
                "block_and_warn");
        }

        return null;
    }

    private static string Redact(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) return "***";
        var leaf = path.Split('\\')[^1];
        return leaf.Length <= 3 ? "***" : leaf[..3] + "***";
    }
}
