using System.Net.Http;
using System.Windows;
using CyberGuardian.Windows.Api;
using CyberGuardian.Windows.Ui;

namespace CyberGuardian.Windows;

public partial class MainWindow : Window
{
    private readonly GuardianApiClient _api;
    private readonly ScanWindowController _controller;

    public MainWindow()
    {
        InitializeComponent();
        var http = new HttpClient { BaseAddress = new Uri(EnvApiBase()) };
        _api = new GuardianApiClient(http);
        _controller = new ScanWindowController(
            async url =>
            {
                var r = await _api.ScanUrlAsync(url);
                if (r is null) return (0, "unknown", "allow");
                return (r.Score, r.Verdict, r.RecommendedAction);
            },
            async (hash, name) =>
            {
                await Task.CompletedTask;
                return (0, "unknown", "allow");
            });
    }

    private static string EnvApiBase() =>
        Environment.GetEnvironmentVariable("CGA_API_BASE") ?? "http://127.0.0.1:8000";

    private async void OnScanClick(object sender, RoutedEventArgs e)
    {
        _controller.State.Input = UrlBox.Text?.Trim() ?? "";
        _controller.State.Mode = "url";
        ScanButton.IsEnabled = false;
        try
        {
            await _controller.SubmitAsync();
            ResultTitle.Text = _controller.State.Verdict is null
                ? ""
                : $"{_controller.State.Verdict} · {_controller.State.Score}";
            ResultBody.Text = _controller.State.RecommendedAction ?? _controller.State.Status;
        }
        finally
        {
            ScanButton.IsEnabled = true;
        }
    }
}
