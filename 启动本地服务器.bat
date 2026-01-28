@echo off
chcp 65001 >nul
echo ========================================
echo   AI工程师训练营 - 本地开发服务器
echo ========================================
echo.
echo 启动中...
echo.
cd /d "i:\Study FastAPI"
D:\Anaconda\envs\pytorch_Gpu\python.exe -m uvicorn webapp.app:app --reload --port 8080
pause
