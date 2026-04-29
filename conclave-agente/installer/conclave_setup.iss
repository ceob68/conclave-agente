#define AppName "CONCLAVE Agente"
#define AppVersion "1.0.0"
#define AppExeName "CONCLAVE_Agente.exe"
#define AppBuildDir "..\dist\CONCLAVE_Agente"

[Setup]
AppId={{A7F2E4D8-3C1B-4F9A-8E6D-2B5C7A0F4E3D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=ceob68 / Vaultly
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
OutputDir=output
OutputBaseFilename=CONCLAVE_Agente_Setup
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
MinVersion=10.0
LicenseFile=..\LICENSE.txt

[Files]
Source: "{#AppBuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar ahora"; Flags: nowait postinstall skipifsilent
