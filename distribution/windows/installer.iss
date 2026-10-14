; Maintainer-only compiler input. Product execution never invokes Python/pip/PowerShell.
#ifndef Version
  #define Version "0.1.0.1"
#endif
#ifndef Manufacturer
  #define Manufacturer "AgroLines - identidade juridica pendente"
#endif
[Setup]
AppId={{A38AA663-25B7-4E10-9CFB-8358238BB271}
AppName=AgroLines Distribution PoC
AppVersion={#Version}
AppPublisher={#Manufacturer}
AppVerName=AgroLines Distribution PoC {#Version}
VersionInfoVersion={#Version}
VersionInfoCompany={#Manufacturer}
DefaultDirName={localappdata}\Programs\AgroLinesDistributionPoC
DefaultGroupName=AgroLines Distribution PoC
OutputDir=..\..\dist\installers
OutputBaseFilename=AgroLinesPoC-{#Version}-windows-x64
SetupIconFile=..\..\build\distribution\AgroLines.ico
UninstallDisplayIcon={app}\app\AgroLinesPoC.exe
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.22000
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
; SignTool configured only on a trusted signing builder; never use self-signed certificates.
#ifdef SigningTool
SignTool={#SigningTool}
SignedUninstaller=yes
#endif
[Files]
Source: "..\..\dist\AgroLinesPoC\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\AgroLines Distribution PoC"; Filename: "{app}\app\AgroLinesPoC.exe"
Name: "{autodesktop}\AgroLines Distribution PoC"; Filename: "{app}\app\AgroLinesPoC.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Criar atalho na área de trabalho"; Flags: unchecked
[Run]
Filename: "{app}\app\AgroLinesPoC.exe"; Description: "Abrir prova de distribuição"; Flags: nowait postinstall skipifsilent
