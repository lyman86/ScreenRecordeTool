# ScreenRecorder PowerShell 构建脚本
# 为Windows用户提供便捷的构建和开发命令

param(
    [Parameter(Position=0)]
    [ValidateSet('help', 'install', 'dev', 'test', 'lint', 'format', 'build', 'clean', 'run', 'release', 'status')]
    [string]$Command = 'help',
    
    [Parameter()]
    [ValidateSet('patch', 'minor', 'major')]
    [string]$VersionType = 'patch',
    
    [Parameter()]
    [switch]$NoPush,
    
    [Parameter()]
    [switch]$Quick
)

# 颜色输出函数
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = 'White'
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" 'Green'
}

function Write-Info {
    param([string]$Message)
    Write-ColorOutput "ℹ️  $Message" 'Cyan'
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" 'Yellow'
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" 'Red'
}

# 检查Python是否安装
function Test-Python {
    try {
        $pythonVersion = python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Python版本: $pythonVersion"
            return $true
        }
    }
    catch {
        Write-Error "未找到Python，请先安装Python 3.9+"
        return $false
    }
    return $false
}

# 检查虚拟环境
function Test-VirtualEnv {
    if (Test-Path ".venv\Scripts\Activate.ps1") {
        Write-Info "发现虚拟环境"
        return $true
    }
    return $false
}

# 激活虚拟环境
function Invoke-VirtualEnv {
    if (Test-VirtualEnv) {
        Write-Info "激活虚拟环境..."
        & ".venv\Scripts\Activate.ps1"
    } else {
        Write-Warning "未找到虚拟环境，使用系统Python"
    }
}

# 执行命令并检查结果
function Invoke-CommandWithCheck {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Info $Description
    Write-Host "执行: $Command" -ForegroundColor Gray
    
    Invoke-Expression $Command
    if ($LASTEXITCODE -ne 0) {
        Write-Error "$Description 失败"
        exit 1
    }
}

# 显示帮助信息
function Show-Help {
    Write-ColorOutput "ScreenRecorder PowerShell 构建工具" 'Magenta'
    Write-Host ""
    Write-ColorOutput "用法: .\build.ps1 <命令> [选项]" 'White'
    Write-Host ""
    Write-ColorOutput "可用命令:" 'Yellow'
    Write-Host "  help        - 显示此帮助信息"
    Write-Host "  install     - 安装项目依赖"
    Write-Host "  dev         - 安装开发依赖"
    Write-Host "  test        - 运行测试"
    Write-Host "  lint        - 代码检查"
    Write-Host "  format      - 代码格式化"
    Write-Host "  build       - 构建应用程序"
    Write-Host "  clean       - 清理构建文件"
    Write-Host "  run         - 运行应用程序"
    Write-Host "  release     - 创建发布版本"
    Write-Host "  status      - 检查项目状态"
    Write-Host ""
    Write-ColorOutput "选项:" 'Yellow'
    Write-Host "  -VersionType <patch|minor|major>  - 版本升级类型 (默认: patch)"
    Write-Host "  -NoPush                           - 不推送到GitHub"
    Write-Host "  -Quick                            - 快速构建模式"
    Write-Host ""
    Write-ColorOutput "示例:" 'Yellow'
    Write-Host "  .\build.ps1 install               - 安装依赖"
    Write-Host "  .\build.ps1 build -Quick          - 快速构建"
    Write-Host "  .\build.ps1 release -VersionType minor  - 发布次要版本"
}

# 安装依赖
function Install-Dependencies {
    Write-Info "安装项目依赖..."
    
    Invoke-CommandWithCheck "python -m pip install --upgrade pip" "升级pip"
    
    if (Test-Path "requirements.txt") {
        Invoke-CommandWithCheck "pip install -r requirements.txt" "安装项目依赖"
    } else {
        Write-Warning "未找到requirements.txt文件"
    }
    
    Write-Success "依赖安装完成"
}

# 安装开发依赖
function Install-DevDependencies {
    Install-Dependencies
    
    Write-Info "安装开发依赖..."
    
    $devPackages = @(
        "pytest",
        "pytest-cov",
        "black",
        "isort",
        "flake8",
        "mypy",
        "bandit",
        "safety",
        "pyinstaller"
    )
    
    foreach ($package in $devPackages) {
        Invoke-CommandWithCheck "pip install $package" "安装 $package"
    }
    
    Write-Success "开发环境设置完成"
}

# 运行测试
function Invoke-Tests {
    Write-Info "运行测试..."
    
    if (Test-Path "tests") {
        Invoke-CommandWithCheck "python -m pytest tests/ -v --cov=src --cov-report=term-missing" "运行测试"
    } else {
        Write-Warning "未找到tests目录，跳过测试"
    }
}

# 代码检查
function Invoke-Lint {
    Write-Info "代码检查..."
    
    Write-Info "检查代码格式..."
    python -m black --check src/
    
    Write-Info "检查导入排序..."
    python -m isort --check-only src/
    
    Write-Info "运行flake8..."
    python -m flake8 src/
    
    Write-Info "类型检查..."
    python -m mypy src/ --ignore-missing-imports
    
    Write-Info "安全检查..."
    python -m bandit -r src/
    
    Write-Info "依赖安全检查..."
    python -m safety check
    
    Write-Success "代码检查完成"
}

# 代码格式化
function Invoke-Format {
    Write-Info "格式化代码..."
    
    Invoke-CommandWithCheck "python -m black src/" "格式化代码"
    Invoke-CommandWithCheck "python -m isort src/" "排序导入"
    
    Write-Success "代码格式化完成"
}

# 构建应用程序
function Invoke-Build {
    Write-Info "构建应用程序..."
    
    if (Test-Path "scripts\build_automation.py") {
        if ($Quick) {
            Invoke-CommandWithCheck "python scripts\build_automation.py --only-build" "快速构建"
        } else {
            Invoke-CommandWithCheck "python scripts\build_automation.py" "完整构建"
        }
    } elseif (Test-Path "build.py") {
        Invoke-CommandWithCheck "python build.py" "运行构建脚本"
    } else {
        Write-Info "使用默认PyInstaller构建..."
        Invoke-CommandWithCheck "python -m PyInstaller --onefile --windowed main.py" "PyInstaller构建"
    }
    
    Write-Success "构建完成"
    
    # 显示构建结果
    if (Test-Path "dist") {
        Write-Info "构建产物:"
        Get-ChildItem "dist" | ForEach-Object {
            $size = if ($_.PSIsContainer) { "目录" } else { "{0:N1} MB" -f ($_.Length / 1MB) }
            Write-Host "  $($_.Name) ($size)" -ForegroundColor Gray
        }
    }
}

# 清理构建文件
function Invoke-Clean {
    Write-Info "清理构建文件..."
    
    $cleanDirs = @("build", "dist")
    foreach ($dir in $cleanDirs) {
        if (Test-Path $dir) {
            Remove-Item $dir -Recurse -Force
            Write-Host "  删除: $dir" -ForegroundColor Gray
        }
    }
    
    # 清理 __pycache__ 目录
    Get-ChildItem -Path . -Recurse -Name "__pycache__" -Directory | ForEach-Object {
        $fullPath = Join-Path $PWD $_
        Remove-Item $fullPath -Recurse -Force
        Write-Host "  删除: $_" -ForegroundColor Gray
    }
    
    # 清理 .pyc 文件
    Get-ChildItem -Path . -Recurse -Name "*.pyc" | ForEach-Object {
        Remove-Item $_
    }
    
    Write-Success "清理完成"
}

# 运行应用程序
function Invoke-Run {
    Write-Info "启动应用程序..."
    
    if (Test-Path "main.py") {
        python main.py
    } else {
        Write-Error "未找到main.py文件"
    }
}

# 创建发布
function Invoke-Release {
    Write-Info "创建发布版本..."
    
    if (Test-Path "scripts\auto_release.py") {
        $releaseArgs = "--type $VersionType"
        if ($NoPush) {
            $releaseArgs += " --no-push"
        }
        
        Invoke-CommandWithCheck "python scripts\auto_release.py $releaseArgs" "创建发布"
    } else {
        Write-Error "未找到自动发布脚本"
    }
}

# 检查项目状态
function Show-Status {
    Write-Info "项目状态检查..."
    
    Write-ColorOutput "Git状态:" 'Yellow'
    git status --short
    
    Write-Host ""
    Write-ColorOutput "分支信息:" 'Yellow'
    git branch -v
    
    Write-Host ""
    Write-ColorOutput "最近提交:" 'Yellow'
    git log --oneline -5
    
    Write-Host ""
    Write-ColorOutput "构建文件:" 'Yellow'
    if (Test-Path "dist") {
        Get-ChildItem "dist" | ForEach-Object { Write-Host "  $($_.Name)" }
    } else {
        Write-Host "  无构建文件"
    }
    
    Write-Host ""
    Write-ColorOutput "Python环境:" 'Yellow'
    python --version
    pip --version
}

# 主函数
function Main {
    Write-ColorOutput "🚀 ScreenRecorder 构建工具" 'Magenta'
    Write-Host ""
    
    # 检查Python
    if (-not (Test-Python)) {
        exit 1
    }
    
    # 激活虚拟环境（如果存在）
    Invoke-VirtualEnv
    
    # 执行命令
    switch ($Command) {
        'help' { Show-Help }
        'install' { Install-Dependencies }
        'dev' { Install-DevDependencies }
        'test' { Invoke-Tests }
        'lint' { Invoke-Lint }
        'format' { Invoke-Format }
        'build' { Invoke-Build }
        'clean' { Invoke-Clean }
        'run' { Invoke-Run }
        'release' { Invoke-Release }
        'status' { Show-Status }
        default { 
            Write-Error "未知命令: $Command"
            Show-Help
            exit 1
        }
    }
}

# 错误处理
trap {
    Write-Error "脚本执行出错: $($_.Exception.Message)"
    exit 1
}

# 运行主函数
Main