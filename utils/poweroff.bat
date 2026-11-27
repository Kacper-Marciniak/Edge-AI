@echo off
ssh student@192.168.21.37 "sudo poweroff"
if %errorlevel%==0 (
    echo Raspberry powered off.
) else (
    echo Something went wrong.
)
pause