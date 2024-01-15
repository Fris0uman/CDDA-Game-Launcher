﻿#define MyAppName "Kitten CDDA Launcher"
#define MyAppVersion FileRead(FileOpen("cddagl\VERSION"))
#define MyAppPublisher "Rémy Roy"
#define MyAppURL "https://github.com/remyroy/CDDA-Game-Launcher"
#define MyExecutable "Launcher.bat"
#define MyIcon "cddagl\resources\launcher.ico"


[Setup]
AppId={{9EDF6480-19FB-4DE1-B2AB-353DCC636079}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} v{#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

;;;; Installer Behavior
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
UsedUserAreasWarning=no
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SourceDir=.

;;;; Installer Documentation
LicenseFile=LICENSE
;InfoBeforeFile=README.md

;;;; Installer Icon, Filename & Path
UninstallDisplayIcon={uninstallexe}
SetupIconFile={#MyIcon}
OutputDir=dist\innosetup
OutputBaseFilename=cddagl_installer_v{#SetupSetting("AppVersion")}


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "armenian"; MessagesFile: "compiler:Languages\Armenian.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"
Name: "catalan"; MessagesFile: "compiler:Languages\Catalan.isl"
Name: "corsican"; MessagesFile: "compiler:Languages\Corsican.isl"
Name: "czech"; MessagesFile: "compiler:Languages\Czech.isl"
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "hebrew"; MessagesFile: "compiler:Languages\Hebrew.isl"
Name: "icelandic"; MessagesFile: "compiler:Languages\Icelandic.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "japanese"; MessagesFile: "compiler:Languages\Japanese.isl"
Name: "norwegian"; MessagesFile: "compiler:Languages\Norwegian.isl"
Name: "polish"; MessagesFile: "compiler:Languages\Polish.isl"
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "slovenian"; MessagesFile: "compiler:Languages\Slovenian.isl"
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "ukrainian"; MessagesFile: "compiler:Languages\Ukrainian.isl"


[Dirs]
Name: "{app}"; Flags: uninsalwaysuninstall;


[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}";


[Files]
Source: "build\archive\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs


[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyExecutable}"; IconFilename: "{app}\{#MyIcon}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyExecutable}"; IconFilename: "{app}\{#MyIcon}"; Tasks: desktopicon


[Run]
Filename: "{app}\{#MyExecutable}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


[Code]
//// NOTE: Code mostly "borrowed" from https://stackoverflow.com/a/2099805/236871

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


function IsInstalled(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;


function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  //// Return Values:
  //// 0 - successfully executed the UnInstallString
  //// 1 - UnInstallString is empty
  //// 2 - error executing the UnInstallString

  sUnInstallString := GetUninstallString();
  if sUnInstallString = '' then
    Result := 1
  else
  begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES', '', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 0
    else
      Result := 2;
  end;
end;


function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  iMsgBoxAnswer: Integer;
begin
  Result := '';

  if IsInstalled() then
  begin
    iMsgBoxAnswer := MsgBox('{#SetupSetting("AppName")} is already installed.' + #13#10
                            + 'Uninstall it before proceeding?',
                            mbInformation, MB_YESNO);
    if iMsgBoxAnswer = IDYES then
    begin
      if UnInstallOldVersion() <> 0 then
      begin
        iMsgBoxAnswer := MsgBox('Failed to uninstall existing installation!' + #13#10
                                + 'Try to reinstall anyways?' + #13#10
                                + '(This has a good chance to fix it.)',
                                mbInformation, MB_YESNO);
        if iMsgBoxAnswer = IDNO then
          Result := 'Failed to uninstall existing installation of {#SetupSetting("AppName")}!';
      end
    end
    else
      Result := 'Please, uninstall existing installation of {#SetupSetting("AppName")} before running this setup!';
  end;
end;
