# Actual package activation (AUMID), not launching the unpacked EXE directly.
function Initialize-AgroPackageActivation {
    if (-not ('AgroLines.PackageActivation' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace AgroLines {
 [ComImport, Guid("2E941141-7F97-4756-BA1D-9DECDE894A3D"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
 interface IActivation {
  [PreserveSig] int ActivateApplication([MarshalAs(UnmanagedType.LPWStr)] string app,
   [MarshalAs(UnmanagedType.LPWStr)] string args, uint options, out uint processId);
  [PreserveSig] int ActivateForFile(IntPtr app, IntPtr items, IntPtr verb, out uint processId);
  [PreserveSig] int ActivateForProtocol(IntPtr app, IntPtr items, out uint processId);
 }
 public static class PackageActivation {
  public static uint Launch(string app, string args) {
   var manager = (IActivation)Activator.CreateInstance(Type.GetTypeFromCLSID(
      new Guid("45BA127D-10A8-46EA-8AB7-56EA9078943C")));
   try { uint pid; int hr = manager.ActivateApplication(app,args,0,out pid);
    Marshal.ThrowExceptionForHR(hr); return pid;
   } finally { Marshal.ReleaseComObject(manager); }
  }
 }
}
'@
    }
}
function Invoke-AgroPackageProbe {
    param([string]$Report, [string]$ProjectDirectory)
    Initialize-AgroPackageActivation
    if (Test-Path $Report) { throw 'Relatorio ja existe; exigir evidencia nova.' }
    $reportPath = [IO.Path]::GetFullPath($Report)
    $projectPath = [IO.Path]::GetFullPath($ProjectDirectory)
    $arguments = '--smoke-report "' + $reportPath + '" --require-msix --offline-project-root "' + $projectPath + '"'
    $processId = [AgroLines.PackageActivation]::Launch('DelatorreCOrporation.AgroLines_pj9w8xnf5vxmg!AgroLines', $arguments)
    $process = [Diagnostics.Process]::GetProcessById($processId)
    try {
        if (-not $process.WaitForExit(120000)) { throw 'Aplicativo MSIX nao respondeu em 120s.' }
        if ($process.ExitCode -ne 0) { throw 'Aplicativo MSIX recusou verificacao; veja evidencia.' }
    } finally { $process.Dispose() }
    if (-not (Test-Path $reportPath)) { throw 'Aplicativo nao gravou evidencia externa.' }
    $result = Get-Content $reportPath -Raw | ConvertFrom-Json
    if (-not $result.frozen -or -not $result.checks_passed -or -not $result.msix_validation_passed -or
        -not $result.payload_integrity_verified -or -not $result.offline_projects.passed) {
        throw 'Identidade, componentes, subprocessos Qt ou persistencia MSIX nao comprovados.'
    }
    return $result
}
