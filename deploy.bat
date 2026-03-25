@echo off
chcp 65001 >nul
title ICZSC Deploy

echo ==========================
echo ICZSC 一键发布开始
echo ==========================

cd /d %~dp0

echo.
echo [1/4] 生成网站...
hugo

if %errorlevel% neq 0 (
    echo Hugo 生成失败
    pause
    exit /b
)

echo.
echo [2/4] Git 提交本地修改...
git add .
git commit -m "update"

echo.
echo [3/4] 拉取远程更新...
git pull origin main --rebase

echo.
echo [4/4] 推送到 GitHub...
git push

if %errorlevel% neq 0 (
    echo Git 推送失败
    pause
    exit /b
)

echo.
echo ==========================
echo 发布完成
echo ==========================
pause