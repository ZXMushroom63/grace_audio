@echo off
mkdir PLAYLIST
echo Launching...
start %SystemRoot%\System32\conhost.exe cmd.exe /k "title GraceRuntimeAudioPatcher_P5 && .\python-rt-win32\python.exe .\lib\grace_audio_patcher.py"