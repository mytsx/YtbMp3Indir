[Setup]
AppName=Youtube Mp3 İndir
AppVersion=2.2.0
AppId={{8B5F9C2D-4F3E-4A1C-9E8D-7A6B5C4D3E2F}}
AppPublisher=Mehmet Yerli
AppPublisherURL=https://mehmetyerli.com
AppSupportURL=https://github.com/mytsx/YtbMp3Indir/issues
AppUpdatesURL=https://github.com/mytsx/YtbMp3Indir/releases
AppContact=iletisim@mehmetyerli.com
DefaultDirName={autopf}\Youtube Mp3 İndir
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer_output
OutputBaseFilename=Youtube_Mp3_Indir_Setup_v2.2.0_by_MehmetYerli
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE.txt
InfoBeforeFile=README.md

; Branding
WizardImageFile=
WizardImageAlphaFormat=defined
WizardImageStretch=no
WizardSmallImageFile=

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "dist\Youtube Mp3 İndir\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Youtube Mp3 İndir"; Filename: "{app}\Youtube Mp3 İndir.exe"; Comment: "YouTube'dan MP3 indirme aracı - Mehmet Yerli"
Name: "{autodesktop}\Youtube Mp3 İndir"; Filename: "{app}\Youtube Mp3 İndir.exe"; Tasks: desktopicon; Comment: "YouTube'dan MP3 indirme aracı - Mehmet Yerli"
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Youtube Mp3 İndir"; Filename: "{app}\Youtube Mp3 İndir.exe"; Tasks: quicklaunchicon

; Additional shortcuts
Name: "{autoprograms}\Youtube Mp3 İndir\Mehmet Yerli - Website"; Filename: "https://mehmetyerli.com"
Name: "{autoprograms}\Youtube Mp3 İndir\GitHub Repository"; Filename: "https://github.com/mytsx/YtbMp3Indir"
Name: "{autoprograms}\Youtube Mp3 İndir\İletişim"; Filename: "mailto:iletisim@mehmetyerli.com"

[Run]
Filename: "{app}\Youtube Mp3 İndir.exe"; Description: "{cm:LaunchProgram,Youtube Mp3 İndir}"; Flags: nowait postinstall skipifsilent
Filename: "https://mehmetyerli.com"; Description: "Geliştirici web sitesini ziyaret et (mehmetyerli.com)"; Flags: postinstall skipifsilent shellexec
Filename: "https://github.com/mytsx/YtbMp3Indir"; Description: "GitHub'da projeyi incele"; Flags: postinstall skipifsilent shellexec

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Messages]
turkish.WelcomeLabel2=Bu sihirbaz [name] uygulamasını bilgisayarınıza kuracaktır.%n%nGeliştirici: Mehmet Yerli%nWeb: mehmetyerli.com%nE-posta: iletisim@mehmetyerli.com%n%nDevam etmeden önce diğer tüm uygulamaları kapatmanız önerilir.
english.WelcomeLabel2=This will install [name] on your computer.%n%nDeveloper: Mehmet Yerli%nWebsite: mehmetyerli.com%nEmail: iletisim@mehmetyerli.com%n%nIt is recommended that you close all other applications before continuing.

[Code]
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (IsUpgrade()) then
    begin
      UnInstallOldVersion();
    end;
  end;
end;
