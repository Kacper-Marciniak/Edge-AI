@echo off
set "DIR=/home/student/EdgeAI"
set "KEEP=-not -name .venv -not -name qwen_local -not -name yolo26n.pt"

ssh -t student@192.168.21.37 "cd %DIR% || exit 1; echo '=== Current contents ==='; ls -lA; echo; echo '=== Will be DELETED ==='; find . -mindepth 1 -maxdepth 1 %KEEP% | sed 's|^\./||'; n=$(find . -mindepth 1 -maxdepth 1 %KEEP% | wc -l); echo; if [ $n -eq 0 ]; then echo 'Nothing to delete.'; exit 0; fi; read -p 'Delete these? (y/n): ' a; if [ x$a = xy ]; then find . -mindepth 1 -maxdepth 1 %KEEP% -exec rm -rf {} +; echo; echo '=== Left after cleanup ==='; ls -lA; else echo 'Cancelled, nothing deleted.'; fi"

pause