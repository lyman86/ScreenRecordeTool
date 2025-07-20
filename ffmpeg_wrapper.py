#!/usr/bin/env python3
"""
FFmpeg包装器 - 解决macOS路径问题
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def find_ffmpeg():
    """查找FFmpeg二进制文件"""
    # 检查PATH
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    # 检查常见位置
    possible_paths = [
        '/usr/local/bin/ffmpeg',
        '/opt/homebrew/bin/ffmpeg',
        str(Path.home() / '.local' / 'bin' / 'ffmpeg'),
        '/usr/bin/ffmpeg'
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            return path
    
    return None

def run_ffmpeg(args):
    """运行FFmpeg命令"""
    ffmpeg_path = find_ffmpeg()
    if not ffmpeg_path:
        raise FileNotFoundError("FFmpeg not found")
    
    cmd = [ffmpeg_path] + args
    return subprocess.run(cmd, capture_output=True, text=True)

if __name__ == "__main__":
    try:
        result = run_ffmpeg(sys.argv[1:])
        sys.exit(result.returncode)
    except Exception as e:
        print(f"FFmpeg wrapper error: {e}", file=sys.stderr)
        sys.exit(1)
