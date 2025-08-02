; Inno Setup Script for YouTube MP3 İndirici v2.2.0

#define MyAppName "YouTube MP3 İndirici"
#define MyAppVersion "2.2.0"
#define MyAppPublisher "Mehmet Yerli"
#define MyAppURL "https://github.com/mytsx/YtbMp3Indir"
#define MyAppExeName "Youtube Mp3 İndir.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{A3B7C9D8-5E4F-6A2B-8C9D-0E1F2A3B4C5D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE.txt
OutputDir=installer_output
OutputBaseFilename=YouTube_MP3_Indirici_v{#MyAppVersion}_Setup
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=YouTube videolarını MP3 formatında indirin ve dosyaları dönüştürün
VersionInfoCopyright=Copyright (c) 2025 {#MyAppPublisher}
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}

[Languages]
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\Youtube Mp3 İndir\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Youtube Mp3 İndir\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[CustomMessages]
turkish.CreateDesktopIcon=Masaüstü kısayolu oluştur
turkish.AdditionalIcons=Ek simgeler:
turkish.LaunchProgram=%1 uygulamasını başlat
english.CreateDesktopIcon=Create a desktop shortcut
english.AdditionalIcons=Additional icons:
english.LaunchProgram=Launch %1

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Kurulum sonrası yapılacak işlemler
  end;
end;