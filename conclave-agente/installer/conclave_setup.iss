; CÓNCLAVE Agente — Inno Setup Installer Script
; © 2026 ceob68 / Vaultly. All rights reserved.
;
; Prerequisites:
;   1. Run PyInstaller first: pyinstaller conclave_agente.spec
;   2. Open this .iss file in Inno Setup Compiler
;   3. Click Build → Compile
;   Output: installer\output\CONCLAVE_Agente_Setup.exe

#define AppName "CONCLAVE Agente"
#define AppVersion "1.0.0"
#define AppPublisher "ceob68 / Vaultly"
#define AppURL "https://vaultly.ceob68.com"
#define AppExeName "CONCLAVE_Agente.exe"
#define AppBuildDir "..\dist\CONCLAVE_Agente"

[Setup]
AppId={{A7F2E4D8-3C1B-4F9A-8E6D-2B5C7A0F4E3D}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=no
LicenseFile=..\LICENSE.txt
InfoBeforeFile=..\README.txt
OutputDir=output
OutputBaseFilename=CONCLAVE_Agente_Setup
; SolidCompression reduces installer size significantly
SolidCompression=yes
WizardStyle=modern
; Require admin for Program Files installation
PrivilegesRequired=admin
; Minimum Windows version: Windows 10 (6.2 = Win8, 10.0 = Win10)
MinVersion=10.0
; Architecture
ArchitecturesInstallIn64BitMode=x64
; Uninstall support
Uninstallable=yes
UninstallDisplayName={#AppName}
; Window appearance
WizardImageFile=compiler:WizModernImage-IS.bmp
WizardSmallImageFile=compiler:WizModernSmallImage-IS.bmp

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el &Escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checked
Name: "quicklaunchicon"; Description: "Crear icono de acceso rápido en la &barra de tareas"; GroupDescription: "Iconos adicionales:"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; Main application directory (PyInstaller output)
Source: "{#AppBuildDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Additional docs
Source: "..\LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\README.txt"; DestDir: "{app}"; Flags: ignoreversion
; Manual (after generation)
; Source: "..\docs\CONCLAVE_Agente_Manual.pdf"; DestDir: "{app}"; Flags: ignoreversion
; Source: "..\docs\CONCLAVE_Agente_Guia_Rapida.pdf"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Start Menu
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
; Desktop shortcut (if task selected)
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Option to launch app after installation
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up user data directory on uninstall (optional — comment out to keep data)
; Type: filesandordirs; Name: "{userdocs}\CONCLAVE Agente"

[Messages]
; Spanish custom messages
WelcomeLabel1=Bienvenido al instalador de [name]
WelcomeLabel2=Este asistente instalará [name/ver] en su equipo.%n%nSe recomienda cerrar todas las demás aplicaciones antes de continuar.%n%nHaga clic en Siguiente para continuar.
FinishedHeadingLabel=Instalación de [name] completada
FinishedLabel=[name] ha sido instalado correctamente en su equipo.%n%nHaga clic en Finalizar para cerrar el instalador.
