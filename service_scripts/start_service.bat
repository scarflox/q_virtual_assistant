@echo off
REM Launch Windows Terminal with PowerShell profile and run the PS script
wt.exe -p "PowerShell" powershell -NoExit -File "F:\q_virtual_assistant\service_scripts\run_assistant.ps1"


REM Have this file somewhere to run it, it will call the ps file and run the script to boot this program up.