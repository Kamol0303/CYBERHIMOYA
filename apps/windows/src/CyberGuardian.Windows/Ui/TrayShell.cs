// Cyber Guardian AI — Windows tray UI shell (V1)
// Defensive scan entry points only.

namespace CyberGuardian.Windows.Ui;

public sealed class TrayAppState
{
    public string Brand { get; } = "Cyber Guardian AI";
    public string StatusText { get; set; } = "Himoya yoqilgan (mudofaa)";
    public bool FeedSyncOk { get; set; }
    public string? LastVerdict { get; set; }
}

public interface ITrayActions
{
    Task ScanUrlAsync(string url);
    Task ScanFileHashAsync(string sha256, string? fileName);
    Task SyncFeedAsync();
    void ShowConsentSettings();
}

/// <summary>
/// Placeholder for WinUI/WPF tray menu wiring.
/// </summary>
public sealed class TrayMenuBuilder
{
    public IReadOnlyList<string> DefaultItems { get; } =
    [
        "URL tekshirish",
        "Fayl hash tekshirish",
        "Threat feed sync",
        "Rozilik sozlamalari",
        "Chiqish",
    ];
}
