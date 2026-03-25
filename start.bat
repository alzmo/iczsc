@echo off
cd /d %~dp0

echo ==============================
echo   ICZSC 本地站点启动中...
echo ==============================

hugo server -D

pause