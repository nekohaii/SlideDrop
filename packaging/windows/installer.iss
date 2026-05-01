; Inno Setup script template for SlideDrop (fill paths before building).
; Requires Inno Setup: https://jrsoftware.org/isinfo.php

#define MyAppName "SlideDrop"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "SlideDrop"
#define MyAppExeName "SlideDrop.exe"

[Setup]
AppId={{F8F8F8F8-1111-2222-3333-444455556666}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\..\release\windows
OutputBaseFilename=SlideDrop-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\release\windows\SlideDrop-portable\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\release\windows\SlideDrop-portable\README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\release\windows\SlideDrop-portable\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\..\release\windows\SlideDrop-portable\NOTICE.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
