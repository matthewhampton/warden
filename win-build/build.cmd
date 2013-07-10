@echo off
REM powershell Set-ExecutionPolicy RemoteSigned
powershell Set-ExecutionPolicy Bypass
powershell .\Build.ps1
