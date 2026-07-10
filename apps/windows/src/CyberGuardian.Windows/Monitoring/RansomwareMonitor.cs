namespace CyberGuardian.Windows.Monitoring;

/// <summary>
/// FR-074 ransomware monitoring stub — honeypot / mass-write heuristic.
/// Detection and user guidance only (backup reminder). No offensive response.
/// </summary>
public sealed class RansomwareMonitor
{
    public sealed record Finding(
        string PathHint,
        string ReasonCode,
        string Severity,
        string RecommendedAction);

    private int _rapidWrites;

    public Finding? ObserveWrite(string relativePath, int entropyHint0to100)
    {
        _rapidWrites++;
        if (_rapidWrites >= 20 && entropyHint0to100 >= 70)
        {
            _rapidWrites = 0;
            return new Finding(
                Redact(relativePath),
                "RANSOM_MASS_WRITE",
                "critical",
                "warn_backup_and_isolate_local");
        }

        if (relativePath.Contains("cga-honeypot", StringComparison.OrdinalIgnoreCase) &&
            entropyHint0to100 >= 50)
        {
            return new Finding(
                Redact(relativePath),
                "RANSOM_HONEYPOT",
                "critical",
                "warn_backup_and_isolate_local");
        }

        return null;
    }

    public void ResetWindow() => _rapidWrites = 0;

    private static string Redact(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) return "***";
        var name = System.IO.Path.GetFileName(path);
        return string.IsNullOrEmpty(name) ? "***" : name[..Math.Min(3, name.Length)] + "***";
    }
}
