@echo off
REM 现代录屏工具构建脚本 (Windows)

echo ==================================
echo 现代录屏工具 - 构建脚本
echo ==================================

REM 获取项目根目录
set "PROJECT_ROOT=%~dp0.."
echo 项目根目录: %PROJECT_ROOT%

cd /d "%PROJECT_ROOT%"

REM 检查Python版本
echo 检查Python版本...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

REM 检查是否在虚拟环境中
if defined VIRTUAL_ENV (
    echo 检测到虚拟环境: %VIRTUAL_ENV%
) else (
    echo 警告: 未检测到虚拟环境，建议使用虚拟环境
)

REM 安装依赖
echo 安装Python依赖...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

REM 创建必要的目录
echo 创建必要的目录...
if not exist "resources" mkdir resources
if not exist "build" mkdir build
if not exist "dist" mkdir dist

REM 运行Windows构建脚本
echo 使用Windows构建脚本...
python build_scripts\build_windows.py
if %errorlevel% neq 0 (
    echo 错误: 构建失败
    pause
    exit /b 1
)

echo 构建完成!

REM 显示输出文件
if exist "dist" (
    echo 输出文件:
    dir /b dist\
)

pause
