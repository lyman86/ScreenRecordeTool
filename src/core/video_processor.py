"""
视频处理和转换模块
"""

import os
import subprocess
import threading
from pathlib import Path
from typing import Optional, Dict, List, Callable
from PyQt6.QtCore import QObject, pyqtSignal

class VideoProcessor(QObject):
    """视频处理器"""
    
    # 信号
    processing_started = pyqtSignal(str)     # 开始处理
    processing_finished = pyqtSignal(str)    # 处理完成
    processing_failed = pyqtSignal(str, str) # 处理失败 (文件路径, 错误信息)
    progress_updated = pyqtSignal(str, int)  # 进度更新 (文件路径, 百分比)
    
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = self.find_ffmpeg()
        self.processing_queue = []
        self.is_processing = False
        
    def find_ffmpeg(self) -> Optional[str]:
        """查找FFmpeg可执行文件"""
        # 常见的FFmpeg路径
        possible_paths = [
            "ffmpeg",  # 系统PATH中
            "ffmpeg.exe",  # Windows
            "/usr/bin/ffmpeg",  # Linux
            "/usr/local/bin/ffmpeg",  # macOS Homebrew
            "./ffmpeg/bin/ffmpeg.exe",  # 本地目录
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-version"], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        return None
    
    def is_ffmpeg_available(self) -> bool:
        """检查FFmpeg是否可用"""
        return self.ffmpeg_path is not None
    
    def convert_video(self, input_path: str, output_path: str, 
                     format_type: str = "mp4", quality: str = "高质量",
                     custom_options: Dict = None) -> bool:
        """转换视频格式"""
        if not self.is_ffmpeg_available():
            self.processing_failed.emit(input_path, "FFmpeg不可用")
            return False
        
        # 构建FFmpeg命令
        cmd = [self.ffmpeg_path, "-i", input_path]
        
        # 添加质量设置
        quality_settings = self.get_quality_settings(quality)
        cmd.extend(quality_settings)
        
        # 添加格式特定设置
        format_settings = self.get_format_settings(format_type)
        cmd.extend(format_settings)
        
        # 添加自定义选项
        if custom_options:
            for key, value in custom_options.items():
                cmd.extend([f"-{key}", str(value)])
        
        # 输出文件
        cmd.extend(["-y", output_path])  # -y 覆盖输出文件
        
        # 在后台线程中执行转换
        thread = threading.Thread(
            target=self._run_conversion,
            args=(cmd, input_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return True
    
    def compress_video(self, input_path: str, output_path: str,
                      target_size_mb: Optional[int] = None,
                      compression_level: str = "medium") -> bool:
        """压缩视频"""
        if not self.is_ffmpeg_available():
            self.processing_failed.emit(input_path, "FFmpeg不可用")
            return False
        
        cmd = [self.ffmpeg_path, "-i", input_path]
        
        if target_size_mb:
            # 基于目标文件大小计算比特率
            duration = self.get_video_duration(input_path)
            if duration > 0:
                target_bitrate = int((target_size_mb * 8 * 1024) / duration)
                cmd.extend(["-b:v", f"{target_bitrate}k"])
        else:
            # 使用预设压缩级别
            compression_settings = {
                "low": ["-crf", "28", "-preset", "fast"],
                "medium": ["-crf", "23", "-preset", "medium"],
                "high": ["-crf", "18", "-preset", "slow"]
            }
            cmd.extend(compression_settings.get(compression_level, compression_settings["medium"]))
        
        cmd.extend(["-y", output_path])
        
        thread = threading.Thread(
            target=self._run_conversion,
            args=(cmd, input_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return True
    
    def extract_audio(self, input_path: str, output_path: str,
                     audio_format: str = "mp3") -> bool:
        """提取音频"""
        if not self.is_ffmpeg_available():
            self.processing_failed.emit(input_path, "FFmpeg不可用")
            return False
        
        cmd = [
            self.ffmpeg_path, "-i", input_path,
            "-vn",  # 不包含视频
            "-acodec", self.get_audio_codec(audio_format),
            "-y", output_path
        ]
        
        thread = threading.Thread(
            target=self._run_conversion,
            args=(cmd, input_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return True
    
    def trim_video(self, input_path: str, output_path: str,
                  start_time: str, duration: str) -> bool:
        """裁剪视频"""
        if not self.is_ffmpeg_available():
            self.processing_failed.emit(input_path, "FFmpeg不可用")
            return False
        
        cmd = [
            self.ffmpeg_path, "-i", input_path,
            "-ss", start_time,  # 开始时间
            "-t", duration,     # 持续时间
            "-c", "copy",       # 复制流，不重新编码
            "-y", output_path
        ]
        
        thread = threading.Thread(
            target=self._run_conversion,
            args=(cmd, input_path, output_path)
        )
        thread.daemon = True
        thread.start()
        
        return True
    
    def get_video_info(self, video_path: str) -> Dict:
        """获取视频信息"""
        if not self.is_ffmpeg_available():
            return {}
        
        cmd = [
            self.ffmpeg_path, "-i", video_path,
            "-hide_banner", "-f", "null", "-"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            # 解析FFmpeg输出获取视频信息
            info = self._parse_video_info(result.stderr)
            return info
        except Exception as e:
            print(f"获取视频信息失败: {str(e)}")
            return {}
    
    def get_video_duration(self, video_path: str) -> float:
        """获取视频时长（秒）"""
        info = self.get_video_info(video_path)
        return info.get("duration", 0.0)
    
    def get_quality_settings(self, quality: str) -> List[str]:
        """获取质量设置"""
        quality_map = {
            "低质量": ["-crf", "28", "-preset", "fast"],
            "中等质量": ["-crf", "23", "-preset", "medium"],
            "高质量": ["-crf", "18", "-preset", "slow"],
            "超高质量": ["-crf", "15", "-preset", "slower"]
        }
        return quality_map.get(quality, quality_map["高质量"])
    
    def get_format_settings(self, format_type: str) -> List[str]:
        """获取格式设置"""
        format_map = {
            "mp4": ["-c:v", "libx264", "-c:a", "aac"],
            "avi": ["-c:v", "libxvid", "-c:a", "mp3"],
            "mov": ["-c:v", "libx264", "-c:a", "aac"],
            "webm": ["-c:v", "libvpx-vp9", "-c:a", "libopus"],
            "mkv": ["-c:v", "libx264", "-c:a", "aac"]
        }
        return format_map.get(format_type.lower(), format_map["mp4"])
    
    def get_audio_codec(self, audio_format: str) -> str:
        """获取音频编解码器"""
        codec_map = {
            "mp3": "libmp3lame",
            "aac": "aac",
            "ogg": "libvorbis",
            "wav": "pcm_s16le"
        }
        return codec_map.get(audio_format.lower(), "libmp3lame")
    
    def _run_conversion(self, cmd: List[str], input_path: str, output_path: str):
        """运行转换命令"""
        self.processing_started.emit(input_path)
        
        try:
            # 启动FFmpeg进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )
            
            # 监控进度
            self._monitor_progress(process, input_path)
            
            # 等待完成
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.processing_finished.emit(output_path)
            else:
                error_msg = stderr or "转换失败"
                self.processing_failed.emit(input_path, error_msg)
                
        except Exception as e:
            self.processing_failed.emit(input_path, str(e))
    
    def _monitor_progress(self, process, input_path: str):
        """监控转换进度"""
        # 简化的进度监控实现
        # 实际实现需要解析FFmpeg的输出来获取准确进度
        try:
            while process.poll() is None:
                # 这里应该解析FFmpeg输出来获取实际进度
                # 由于篇幅限制，使用简化实现
                pass
        except Exception:
            pass
    
    def _parse_video_info(self, ffmpeg_output: str) -> Dict:
        """解析FFmpeg输出获取视频信息"""
        info = {}
        
        try:
            lines = ffmpeg_output.split('\n')
            for line in lines:
                if "Duration:" in line:
                    # 解析时长
                    duration_str = line.split("Duration:")[1].split(",")[0].strip()
                    info["duration"] = self._parse_duration(duration_str)
                elif "Video:" in line:
                    # 解析视频信息
                    parts = line.split(",")
                    for part in parts:
                        if "x" in part and part.strip().replace("x", "").replace(" ", "").isdigit():
                            # 解析分辨率
                            resolution = part.strip()
                            info["resolution"] = resolution
                        elif "fps" in part:
                            # 解析帧率
                            fps_str = part.replace("fps", "").strip()
                            try:
                                info["fps"] = float(fps_str)
                            except ValueError:
                                pass
        except Exception as e:
            print(f"解析视频信息失败: {str(e)}")
        
        return info
    
    def _parse_duration(self, duration_str: str) -> float:
        """解析时长字符串为秒数"""
        try:
            # 格式: HH:MM:SS.mmm
            parts = duration_str.split(":")
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except Exception:
            return 0.0
