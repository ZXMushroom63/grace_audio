@echo off
mkdir PLAYLIST
echo Launching...
echo THIS VARIANT IS EXTREMELY UNSTABLE
start %SystemRoot%\System32\conhost.exe cmd.exe /k "title GraceRuntimeAudioPatcher_P5 && .\python-rt-win64\python.exe .\lib\grace_audio_patcher_legacy.py"