@echo off
REM ScreenRecorder 批处理构建脚本
REM 为Windows用户提供简单的构建命令

setlocal enabledelayedexpansion

REM 设置颜色代码
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

REM 显示帮助信息
if "%1"=="" goto :help
if "%1"=="help" goto :help
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help

REM 检查Python
call :check_python
if errorlevel 1 exit /b 1

REM 执行命令
if "%1"=="install" goto :install
if "%1"=="dev" goto :dev
if "%1"=="test" goto :test
if "%1"=="lint" goto :lint
if "%1"=="format" goto :format
if "%1"=="build" goto :build
if "%1"=="clean" goto :clean
if "%1"=="run" goto :run
if "%1"=="release" goto :release
if "%1"=="status" goto :status

echo %RED%错误: 未知命令 "%1"%RESET%
goto :help

:help
echo %CYAN%ScreenRecorder 批处理构建工具%RESET%
echo.
echo 用法: build.bat ^<命令^>
echo.
echo %YELLOW%可用命令:%RESET%
echo   help        - 显示此帮助信息
echo   install     - 安装项目依赖
echo   dev         - 安装开发依赖
echo   test        - 运行测试
echo   lint        - 代码检查
echo   format      - 代码格式化
echo   build       - 构建应用程序
echo   clean       - 清理构建文件
echo   run         - 运行应用程序
echo   release     - 创建发布版本
echo   status      - 检查项目状态
echo.
echo %YELLOW%示例:%RESET%
echo   build.bat install     - 安装依赖
echo   build.bat build       - 构建应用
echo   build.bat run         - 运行应用
goto :eof

:check_python
echo %CYAN%检查Python环境...%RESET%
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: 未找到Python，请先安装Python 3.9+%RESET%
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo %GREEN%Python版本: !python_version!%RESET%

REM 检查虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo %CYAN%激活虚拟环境...%RESET%
    call .venv\Scripts\activate.bat
)
exit /b 0

:install
echo %CYAN%安装项目依赖...%RESET%
python -m pip install --upgrade pip
if errorlevel 1 goto :error

if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 goto :error
) else (
    echo %YELLOW%警告: 未找到requirements.txt文件%RESET%
)

echo %GREEN%依赖安装完成%RESET%
goto :eof

:dev
echo %CYAN%安装开发依赖...%RESET%
call :install

echo %CYAN%安装开发工具...%RESET%
pip install pytest pytest-cov black isort flake8 mypy bandit safety pyinstaller
if errorlevel 1 goto :error

echo %GREEN%开发环境设置完成%RESET%
goto :eof

:test
echo %CYAN%运行测试...%RESET%
if exist "tests" (
    python -m pytest tests/ -v --cov=src --cov-report=term-missing
    if errorlevel 1 goto :error
) else (
    echo %YELLOW%警告: 未找到tests目录，跳过测试%RESET%
)
echo %GREEN%测试完成%RESET%
goto :eof

:lint
echo %CYAN%代码检查...%RESET%

echo %CYAN%检查代码格式...%RESET%
python -m black --check src/
if errorlevel 1 echo %YELLOW%代码格式需要修复%RESET%

echo %CYAN%检查导入排序...%RESET%
python -m isort --check-only src/
if errorlevel 1 echo %YELLOW%导入排序需要修复%RESET%

echo %CYAN%运行flake8...%RESET%
python -m flake8 src/
if errorlevel 1 echo %YELLOW%发现代码问题%RESET%

echo %GREEN%代码检查完成%RESET%
goto :eof

:format
echo %CYAN%格式化代码...%RESET%
python -m black src/
if errorlevel 1 goto :error

python -m isort src/
if errorlevel 1 goto :error

echo %GREEN%代码格式化完成%RESET%
goto :eof

:build
echo %CYAN%构建应用程序...%RESET%

if exist "scripts\build_automation.py" (
    python scripts\build_automation.py
    if errorlevel 1 goto :error
) else if exist "build.py" (
    python build.py
    if errorlevel 1 goto :error
) else (
    echo %CYAN%使用默认PyInstaller构建...%RESET%
    python -m PyInstaller --onefile --windowed main.py
    if errorlevel 1 goto :error
)

echo %GREEN%构建完成%RESET%

REM 显示构建结果
if exist "dist" (
    echo %CYAN%构建产物:%RESET%
    dir /b dist
)
goto :eof

:clean
echo %CYAN%清理构建文件...%RESET%

if exist "build" (
    rmdir /s /q "build"
    echo   删除: build
)

if exist "dist" (
    rmdir /s /q "dist"
    echo   删除: dist
)

REM 清理 __pycache__ 目录
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
        echo   删除: %%d
    )
)

REM 清理 .pyc 文件
del /s /q *.pyc >nul 2>&1

echo %GREEN%清理完成%RESET%
goto :eof

:run
echo %CYAN%启动应用程序...%RESET%
if exist "main.py" (
    python main.py
) else (
    echo %RED%错误: 未找到main.py文件%RESET%
    exit /b 1
)
goto :eof

:release
echo %CYAN%创建发布版本...%RESET%
if exist "scripts\auto_release.py" (
    python scripts\auto_release.py --type patch
    if errorlevel 1 goto :error
) else (
    echo %RED%错误: 未找到自动发布脚本%RESET%
    exit /b 1
)
echo %GREEN%发布完成%RESET%
goto :eof

:status
echo %CYAN%项目状态检查...%RESET%

echo %YELLOW%Git状态:%RESET%
git status --short

echo.
echo %YELLOW%分支信息:%RESET%
git branch -v

echo.
echo %YELLOW%最近提交:%RESET%
git log --oneline -5

echo.
echo %YELLOW%构建文件:%RESET%
if exist "dist" (
    dir /b dist
) else (
    echo   无构建文件
)

echo.
echo %YELLOW%Python环境:%RESET%
python --version
pip --version
goto :eof

:error
echo %RED%操作失败%RESET%
exit /b 1

:eof