
@REM powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

@echo off 
@REM Change to the directory where the other batch file is located 
@REM cd /d "D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e" 
@REM REM Call the other batch file 
@REM call "ff_speedup_audio_select.bat" 
@REM REM Change back to the original directory if needed 
@REM cd /d "D:\mideoToGPhoto"

set PYTHONUTF8=1
cd /d "src"
uv run main_convert.py
uv run main_upload.py