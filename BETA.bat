@echo off
mkdir PLAYLIST
echo Launching...
start %SystemRoot%\System32\conhost.exe cmd.exe /k "title GraceRuntimeAudioPatcher_P6_Beta && .\lib\gracepatcher.exe"