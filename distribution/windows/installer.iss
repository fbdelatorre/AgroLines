; Maintainer-only compiler input. Product execution never invokes Python/pip/PowerShell.
#ifndef Version
  #define Version "0.1.0.1"
#endif
#ifndef Manufacturer
  #define Manufacturer "Delatorre Corporation"
#endif
#ifdef Standalone
  #ifndef Experimental
    #ifndef SigningTool
      #error Standalone commercial distribution is blocked pending signing and legal review.
    #endif
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
#ifdef FunctionalTest
  #ifndef Standalone
    #error FunctionalTest requires Standalone.
  #endif
  #ifndef Experimental
    #error FunctionalTest is never a production release.
  #endif
  #undef ProductName
  #define ProductName "AgroLines TESTE"
#endif
[Setup]
#ifdef Standalone
; Separate identity: no Store/legacy PoC install is replaced.
#ifdef FunctionalTest
AppId={{77EA2840-FDA9-4634-88DA-FC049E901050}
DefaultDirName={autopf}\AgroLines TESTE
DefaultGroupName=AgroLines TESTE
OutputBaseFilename=AgroLines-Setup-{#Version}-TESTE-x64
DisableDirPage=no
#else
AppId={{942C9844-703C-4B75-BE59-A66F3C3D9847}
DefaultDirName={autopf}\AgroLines Experimental
DefaultGroupName=AgroLines Experimental
#ifdef Experimental
OutputBaseFilename=AgroLines-Standalone-{#Version}-x64-{#CandidateId}-EXPERIMENTAL-UNSIGNED
#else
OutputBaseFilename=AgroLines-Standalone-{#Version}-x64-{#CandidateId}-HOMOLOGACAO-ASSINADO-SAC-PENDENTE
#endif
#endif
PrivilegesRequired=admin
UninstallFilesDir={app}\uninstall
; Draft information only: this is not an accepted commercial EULA or consent.
InfoBeforeFile=..\..\dist\AgroLines\legal\LEIA-ME.txt
DisableProgramGroupPage=yes
RestartApplications=no
AppMutex=Global\AgroLinesStandalone-942C9844-703C-4B75-BE59-A66F3C3D9847
SetupMutex=Global\AgroLinesStandaloneInstall-942C9844
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
#ifdef Standalone
UninstallDisplayIcon={app}\AgroLines.exe
#else
UninstallDisplayIcon={#RuntimeDir}\{#BinaryName}.exe
#endif
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
; Stable entrypoint; pointer is installed last, after the complete version tree.
Source: "..\..\build\distribution\AgroLinesLauncher.exe"; DestDir: "{app}"; DestName: "AgroLines.exe"; Flags: ignoreversion
Source: "..\..\build\distribution\AgroLines.current.txt"; DestDir: "{app}"; Flags: ignoreversion
#ifdef FunctionalTest
Source: "standalone\functional-test.marker"; DestDir: "{app}"; DestName: "AgroLines.test-channel"; Flags: ignoreversion
#endif
#else
Source: "..\..\dist\AgroLinesPoC\*"; DestDir: "{app}\app"; Flags: ignoreversion recursesubdirs createallsubdirs
#endif
[Icons]
#ifdef Standalone
Name: "{group}\{#ProductName}"; Filename: "{app}\AgroLines.exe"; WorkingDir: "{app}"; AppUserModelID: "Delatorre.AgroLines.Standalone"
Name: "{group}\Avisos e documentos jurídicos"; Filename: "{#RuntimeDir}\legal\THIRD_PARTY_NOTICES.txt"; WorkingDir: "{#RuntimeDir}\legal"
Name: "{group}\Fontes de componentes de terceiros"; Filename: "{#RuntimeDir}\third-party-sources\AgroLines-Third-Party-Sources.zip"; WorkingDir: "{#RuntimeDir}\third-party-sources"
#ifdef FunctionalTest
Name: "{group}\Versões\AgroLines TESTE {#Version}"; Filename: "{#RuntimeDir}\AgroLines.exe"; WorkingDir: "{#RuntimeDir}"; AppUserModelID: "Delatorre.AgroLines.Test.{#Version}"
#endif
Name: "{autodesktop}\{#ProductName}"; Filename: "{app}\AgroLines.exe"; WorkingDir: "{app}"; AppUserModelID: "Delatorre.AgroLines.Standalone"; Tasks: desktopicon
#else
Name: "{group}\{#ProductName}"; Filename: "{#RuntimeDir}\{#BinaryName}.exe"; WorkingDir: "{#RuntimeDir}"
Name: "{autodesktop}\{#ProductName}"; Filename: "{#RuntimeDir}\{#BinaryName}.exe"; WorkingDir: "{#RuntimeDir}"; Tasks: desktopicon
#endif
[Tasks]
Name: desktopicon; Description: "Criar atalho na área de trabalho"; Flags: unchecked
[Run]
#ifndef Standalone
Filename: "{app}\app\AgroLinesPoC.exe"; Description: "Abrir prova de distribuição"; Flags: nowait postinstall skipifsilent
#endif
[Languages]
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

#ifdef FunctionalTest
[Code]
function PrepareToInstall(var NeedsRestart: Boolean): String;
var ExistingMarker: AnsiString;
begin
  Result := '';
  if FileExists(ExpandConstant('{app}\AgroLines.exe')) or
     FileExists(ExpandConstant('{app}\AgroLines.test-channel')) then begin
    if not LoadStringFromFile(ExpandConstant('{app}\AgroLines.test-channel'), ExistingMarker) or
       (Trim(String(ExistingMarker)) <> 'AgroLines-functional-test-v1') then begin
      Result := 'Esta pasta pertence a outra instalação. Escolha uma pasta exclusiva para AgroLines TESTE.';
      Exit;
    end;
    if not WizardSilent then
      if MsgBox('Atualizar esta instalação AgroLines TESTE? Os runtimes anteriores e os projetos serão preservados.',
                mbConfirmation, MB_YESNO or MB_DEFBUTTON2) <> IDYES then
        Result := 'Atualização cancelada. Nenhuma instalação anterior foi substituída.';
  end;
end;
#endif
