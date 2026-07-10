namespace CyberGuardian.Windows.Monitoring;

/// <summary>
/// FR-073 USB protection stub — detect/warn only.
/// No mass wipe, no remote attack, no auto-exfil.
/// </summary>
public sealed class UsbMonitor
{
    public sealed record UsbFinding(
        string DeviceIdHint,
        string ReasonCode,
        string Severity,
        string RecommendedAction);

    /// <summary>
    /// Evaluate a newly attached removable device description.
    /// </summary>
    public UsbFinding? EvaluateAttachment(string deviceDescription, bool autorunAttempt)
    {
        var desc = deviceDescription ?? string.Empty;
        if (autorunAttempt)
        {
            return new UsbFinding(
                HashHint(desc),
                "USB_AUTORUN",
                "critical",
                "block_and_warn");
        }

        if (desc.Contains("unknown", StringComparison.OrdinalIgnoreCase) ||
            desc.Contains("generic", StringComparison.OrdinalIgnoreCase))
        {
            return new UsbFinding(
                HashHint(desc),
                "USB_UNKNOWN_DEVICE",
                "warning",
                "ask_user");
        }

        return null;
    }

    private static string HashHint(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return "usb:***";
        var take = Math.Min(4, value.Length);
        return "usb:" + value[..take] + "***";
    }
}
