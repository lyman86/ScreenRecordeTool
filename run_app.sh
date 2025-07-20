#!/bin/bash

# 现代录屏工具启动脚本
# Modern Screen Recorder Startup Script

echo "🎬 启动现代录屏工具..."
echo "🎬 Starting Modern Screen Recorder..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行安装脚本"
    echo "❌ Virtual environment not found, please run setup first"
    exit 1
fi

# 激活虚拟环境并运行应用程序
source venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "✅ Virtual environment activated"

echo "🚀 启动应用程序..."
echo "🚀 Launching application..."

# 运行应用程序
python main.py

echo "👋 应用程序已退出"
echo "👋 Application exited"
