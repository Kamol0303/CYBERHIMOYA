using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;

namespace CyberGuardian.Windows.Monitoring;

/// <summary>
/// FR-070 process monitoring stub — detection / alert only.
/// No remote exploitation, no process injection, no kill-by-default.
/// </summary>
public sealed class ProcessMonitor
{
    private static readonly HashSet<string> SuspiciousNames = new(StringComparer.OrdinalIgnoreCase)
    {
        "mimikatz", "procdump", "lazagne", "cobalt", "beacon"
    };

    public sealed record Finding(
        int Pid,
        string ProcessName,
        string ReasonCode,
        string Severity,
        string RecommendedAction);

    public IReadOnlyList<Finding> ScanOnce()
    {
        var findings = new List<Finding>();
        foreach (var proc in Process.GetProcesses())
        {
            try
            {
                var name = proc.ProcessName;
                if (SuspiciousNames.Any(s => name.Contains(s, StringComparison.OrdinalIgnoreCase)))
                {
                    findings.Add(new Finding(
                        proc.Id,
                        name,
                        "PROC_NAME_HEURISTIC",
                        "warning",
                        "warn_and_review"));
                }

                // Parent-child heuristic: short-lived console spawning network tools is out of scope
                // for V1 stub — reserved for Sigma pack integration.
            }
            catch
            {
                // Access denied on protected processes — skip silently.
            }
            finally
            {
                proc.Dispose();
            }
        }

        return findings;
    }
}
