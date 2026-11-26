@echo off
ssh student@192.168.21.37 "rm -rf ~/.vscode-server"
if %errorlevel%==0 (
    echo VS Code servers removed.
) else (
    echo Something went wrong.
)
pause