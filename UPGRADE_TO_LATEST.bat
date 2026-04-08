@echo off
(
    :: load into memory
    echo Updating to latest grace_audio patch from github...
    curl -L "https://github.com/ZXMushroom63/grace_audio/archive/refs/heads/main.zip" -o "grace.zip"
    tar -xf "grace.zip"
    del "grace.zip"
    robocopy "grace_audio-main" . /E /IS /IT /R:3 /W:5
    rd /s /q "grace_audio-main"
    mkdir PLAYLIST
    echo Updated successfully!
    TIMEOUT 3
)