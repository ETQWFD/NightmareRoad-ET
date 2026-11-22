Unicode true
SetCompressor /SOLID lzma
RequestExecutionLevel admin
Name "Nightmare Road-ET Server"
OutFile "..\NightmareRoad-ET-Server-1.8.0-win64-setup.exe"
InstallDir "$PROGRAMFILES64\Nightmare Road-ET Server"
InstallDirRegKey HKLM "Software\NightmareRoadETServer" "InstallPath"
ShowInstDetails show
ShowUninstDetails show
VIProductVersion "1.8.0.0"
VIAddVersionKey "ProductName" "Nightmare Road-ET Server"
VIAddVersionKey "CompanyName" "ET"
VIAddVersionKey "FileDescription" "Nightmare Road-ET Server 1.8.0 Installer"
VIAddVersionKey "FileVersion" "1.8.0.0"
VIAddVersionKey "LegalCopyright" "Copyright (C) 2026 ET"
Icon "server.ico"
UninstallIcon "server.ico"

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "server.ico"
!define MUI_UNICON "server.ico"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"

Function .onInit
  SetRegView 64
  ${IfNot} ${RunningX64}
    MessageBox MB_ICONSTOP "此安装包仅支持 64 位 Windows。"
    Abort
  ${EndIf}
FunctionEnd

Section "Nightmare Road-ET Server（必需）" SEC01
  SectionIn RO
  SetOutPath "$INSTDIR"
  SetOverwrite on
  File /r "..\pkg-win\NightmareRoad-ET-Server-1.8.0-win64\*.*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"

  CreateDirectory "$SMPROGRAMS\Nightmare Road-ET Server"
  CreateShortCut "$SMPROGRAMS\Nightmare Road-ET Server\启动服务（管理员）.lnk" "$INSTDIR\Start-Server-Admin.bat" "" "$INSTDIR\etserver.exe" 0 SW_SHOWNORMAL
  CreateShortCut "$SMPROGRAMS\Nightmare Road-ET Server\停止服务.lnk" "$INSTDIR\Stop-Server-Admin.bat" "" "$INSTDIR\etserver.exe" 0 SW_SHOWNORMAL
  CreateShortCut "$SMPROGRAMS\Nightmare Road-ET Server\使用说明.lnk" "$INSTDIR\README.txt"
  CreateShortCut "$SMPROGRAMS\Nightmare Road-ET Server\卸载.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortCut "$DESKTOP\Nightmare Road-ET Server.lnk" "$INSTDIR\Start-Server-Admin.bat" "" "$INSTDIR\etserver.exe" 0 SW_SHOWNORMAL

  WriteRegStr HKLM "Software\NightmareRoadETServer" "InstallPath" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "DisplayName" "Nightmare Road-ET Server"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "DisplayVersion" "1.8.0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "Publisher" "ET"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "DisplayIcon" "$INSTDIR\etserver.exe,0"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer" "NoRepair" 1

  ; 让首次运行不被 Windows 防火墙拦截；失败不影响安装。
  nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="Nightmare Road-ET Server" >nul 2>&1'
  nsExec::ExecToLog 'netsh advfirewall firewall add rule name="Nightmare Road-ET Server" dir=in action=allow program="$INSTDIR\etserver.exe" enable=yes profile=any'
  Pop $0
SectionEnd

Section "Uninstall"
  Delete "$DESKTOP\Nightmare Road-ET Server.lnk"
  RMDir /r "$SMPROGRAMS\Nightmare Road-ET Server"
  RMDir /r "$INSTDIR"
  DeleteRegKey HKLM "Software\NightmareRoadETServer"
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\NightmareRoadETServer"
  nsExec::ExecToLog 'netsh advfirewall firewall delete rule name="Nightmare Road-ET Server" >nul 2>&1'
  Pop $0
SectionEnd

Function .onInstSuccess
  MessageBox MB_YESNO|MB_ICONQUESTION "安装完成。是否立即启动管理端？$\r$\n（会请求管理员权限）" IDNO +2
  ExecShell "open" "$INSTDIR\Start-Server-Admin.bat"
FunctionEnd
