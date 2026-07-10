// Cyber Guardian AI — Windows scan window shell

namespace CyberGuardian.Windows.Ui;

public sealed class ScanWindowState
{
    public string Brand { get; } = "Cyber Guardian AI";
    public string Mode { get; set; } = "url"; // url | file
    public string Input { get; set; } = "";
    public bool Loading { get; set; }
    public int? Score { get; set; }
    public string? Verdict { get; set; }
    public string? RecommendedAction { get; set; }
    public string Status { get; set; } = "Tayyor";
}

public interface IScanWindowController
{
    Task SubmitAsync();
    Task PickFileAndHashAsync();
    void OpenEmergencySettings();
}

public sealed class ScanWindowController : IScanWindowController
{
    private readonly Func<string, Task<(int score, string verdict, string action)>> _scanUrl;
    private readonly Func<string, string?, Task<(int score, string verdict, string action)>> _scanFile;

    public ScanWindowState State { get; } = new();

    public ScanWindowController(
        Func<string, Task<(int score, string verdict, string action)>> scanUrl,
        Func<string, string?, Task<(int score, string verdict, string action)>> scanFile)
    {
        _scanUrl = scanUrl;
        _scanFile = scanFile;
    }

    public async Task SubmitAsync()
    {
        if (string.IsNullOrWhiteSpace(State.Input)) return;
        State.Loading = true;
        State.Status = "Tekshirilmoqda…";
        try
        {
            var (score, verdict, action) = State.Mode == "file"
                ? await _scanFile(State.Input, null)
                : await _scanUrl(State.Input);
            State.Score = score;
            State.Verdict = verdict;
            State.RecommendedAction = action;
            State.Status = "Tayyor";
        }
        catch
        {
            State.Status = "Xato";
        }
        finally
        {
            State.Loading = false;
        }
    }

    public Task PickFileAndHashAsync()
    {
        State.Mode = "file";
        State.Status = "Fayl hash kiritildi (UI shell)";
        return Task.CompletedTask;
    }

    public void OpenEmergencySettings() => State.Status = "Emergency settings (opt-in)";
}
