; Maintainer-only compiler input. Product execution never invokes Python/pip/PowerShell.
#ifndef Version
  #define Version "0.1.0.1"
#endif
#ifndef Manufacturer
  #define Manufacturer "Delatorre Corporation"
#endif
#ifdef Standalone
  #ifndef Experimental
    #error Standalone commercial distribution is blocked pending signing and legal review.
  #endif
  #ifndef CandidateId
    #error CandidateId is required for isolated version directories.
  #endif
  #define ProductName "AgroLines Experimental"
  #define BinaryName "AgroLines"
  #define RuntimeDir "{app}\versions\" + Version + "-" + CandidateId
#else
  #define ProductName "AgroLines Distribution PoC"
  #define BinaryName "AgroLinesPoC"
  #define RuntimeDir "{app}\app"
#endif
[Setup]
#ifdef Standalone
; Separate identity: no Store/legacy PoC install is replaced.
AppId={{942C9844-703C-4B75-BE59-A66F3C3D9847}
DefaultDirName={autopf}\AgroLines Experimental
DefaultGroupName=AgroLines Experimental
OutputBaseFilename=AgroLines-Standalone-{#Version}-x64-{#CandidateId}-EXPERIMENTAL-UNSIGNED
PrivilegesRequired=admin
UninstallFilesDir={app}\uninstall
DisableProgramGroupPage=yes
RestartApplications=no
#else
AppId={{A38AA663-25B7-4E10-9CFB-8358238BB271}
DefaultDirName={localappdata}\Programs\AgroLinesDistributionPoC
DefaultGroupName=AgroLines Distribution PoC
OutputBaseFilename=AgroLinesPoC-{#Version}-windows-x64
PrivilegesRequired=lowest
#endif
AppName={#ProductName}
AppVersion={#Version}
AppPublisher={#Manufacturer}
AppVerName={#ProductName} {#Version}
VersionInfoVersion={#Version}
VersionInfoCompany={#Manufacturer}
OutputDir=..\..\dist\installers
SetupIconFile=..\..\build\distribution\AgroLines.ico
UninstallDisplayIcon={#RuntimeDir}\{#BinaryName}.exe
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.22000
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes
; No UninstallDelete/InstallDelete for user data, backups or replacement libraries.
; SignTool configured only on a trusted signing builder; never use self-signed certificates.
#ifdef SigningTool
SignTool={#SigningTool}
SignedUninstaller=yes
#endif
[Files]
#ifdef Standalone
Source: "..\..\dist\AgroLines\*"; DestDir: "{#RuntimeDir}"; Flags: ignoreversion recursesubdirs createallsubdirs
#else
Source: "..\..\dist\AgroLinesPoC\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif
[Icons]
Name: "{group}\{#ProductName}"; Filename: "{#RuntimeDir}\{#BinaryName}.exe"; WorkingDir: "{#RuntimeDir}"
Name: "{autodesktop}\{#ProductName}"; Filename: "{#RuntimeDir}\{#BinaryName}.exe"; WorkingDir: "{#RuntimeDir}"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Criar atalho na área de trabalho"; Flags: unchecked
[Run]
#ifndef Standalone
Filename: "{app}\app\AgroLinesPoC.exe"; Description: "Abrir prova de distribuição"; Flags: nowait postinstall skipifsilent
#endif
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
