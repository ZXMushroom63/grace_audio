@echo off
mkdir PLAYLIST
echo Rebuilding playlist cache...
rd /s /q playlist_cache
mkdir playlist_cache

attrib +h playlist_cache
 ::stop idiots from putting data directly into the cache folder

for %%f in ("PLAYLIST\*") do (
    echo Coverting: "%%~f"
    .\lib\ffmpeg\ffmpeg.exe -i "%%~f" -vn -acodec libvorbis -c:a libvorbis -ar 44100 "playlist_cache\%%~nf.ogg" >NUL 2>&1
)
echo Complete! You can now open RUN.bat
TIMEOUT 3