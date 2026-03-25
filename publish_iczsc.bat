@echo off
chcp 65001 >nul
title ICZSC 一键发布（自动版）

echo.
echo ==========================
echo   ICZSC 自动发布开始
echo ==========================
echo.

cd /d %~dp0

:: ===== 检查目录 =====
if not exist "hugo.toml" (
    echo [错误] 未找到 hugo.toml，请把BAT放在项目根目录
    pause
    exit /b 1
)

:: ===== 生成时间戳 =====
set datetime=%date% %time%

:: ===== Hugo 构建 =====
echo [1/4] 生成网站...
hugo
if errorlevel 1 (
    echo [错误] Hugo 构建失败
    pause
    exit /b 1
)

:: ===== Git add =====
echo.
echo [2/4] 添加变更...
git add .

:: ===== Git commit =====
echo.
echo [3/4] 提交变更...
git commit -m "update site %datetime%"

:: ===== Git push =====
echo.
echo [4/4] 推送到 GitHub...
git push
if errorlevel 1 (
    echo [错误] 推送失败（可能是网络问题）
    pause
    exit /b 1
)

echo.
echo ==========================
echo   发布成功！
echo ==========================
echo.

pause