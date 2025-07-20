"""
视频编码模块
"""

import cv2
import numpy as np
import threading
import time
import subprocess
import tempfile
from typing import Optional, Tuple
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

# 尝试导入ffmpeg-python
try:
    import ffmpeg
    FFMPEG_PYTHON_AVAILABLE = True
    print("✅ 使用ffmpeg-python库进行视频处理")
except ImportError:
    FFMPEG_PYTHON_AVAILABLE = False
    print("⚠️ ffmpeg-python未安装，将尝试使用系统FFmpeg命令")

class VideoEncoder(QObject):
    """视频编码器类"""
    
    # 信号
    encoding_started = pyqtSignal()          # 开始编码
    encoding_stopped = pyqtSignal()          # 停止编码
    frame_encoded = pyqtSignal(int)          # 帧已编码（帧数）
    error_occurred = pyqtSignal(str)         # 发生错误
    
    def __init__(self):
        super().__init__()
        self.writer = None
        self.is_encoding = False
        self.frame_count = 0
        self.fps = 30
        self.output_path = ""
        self.codec = "mp4v"
        self.quality = "高质量"
        
        # 编码参数
        self.fourcc_map = {
            "MP4": cv2.VideoWriter_fourcc(*'mp4v'),
            "AVI": cv2.VideoWriter_fourcc(*'XVID'),
            "MOV": cv2.VideoWriter_fourcc(*'mp4v'),
            "WebM": cv2.VideoWriter_fourcc(*'VP80')
        }
        
        # 质量设置
        self.quality_params = {
            "低质量": {"bitrate": 1000000, "quality": 50},
            "中等质量": {"bitrate": 2000000, "quality": 70},
            "高质量": {"bitrate": 4000000, "quality": 85},
            "超高质量": {"bitrate": 8000000, "quality": 95}
        }
    
    def set_output_params(self, output_path: str, fps: int, frame_size: Tuple[int, int], 
                         format_type: str = "MP4", quality: str = "高质量"):
        """设置输出参数"""
        self.output_path = output_path
        self.fps = fps
        self.frame_size = frame_size
        self.format_type = format_type
        self.quality = quality
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    def start_encoding(self) -> bool:
        """开始编码"""
        if self.is_encoding:
            return False

        try:
            # 验证参数
            if not self.output_path:
                self.error_occurred.emit("输出路径未设置")
                return False

            if not self.frame_size or len(self.frame_size) != 2:
                self.error_occurred.emit("帧大小未设置或无效")
                return False

            width, height = self.frame_size
            if width <= 0 or height <= 0:
                self.error_occurred.emit(f"帧大小无效: {width}x{height}")
                return False

            if self.fps <= 0:
                self.error_occurred.emit(f"帧率无效: {self.fps}")
                return False

            # 获取编码器
            fourcc = self.fourcc_map.get(self.format_type, cv2.VideoWriter_fourcc(*'mp4v'))

            print(f"创建视频写入器: {self.output_path}, {fourcc}, {self.fps}, {self.frame_size}")

            # 创建视频写入器
            self.writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.fps,
                self.frame_size
            )

            if not self.writer.isOpened():
                self.error_occurred.emit(f"无法创建视频写入器 - 路径: {self.output_path}, 大小: {self.frame_size}, FPS: {self.fps}")
                return False

            self.is_encoding = True
            self.frame_count = 0
            self.encoding_started.emit()
            return True

        except Exception as e:
            self.error_occurred.emit(f"开始编码失败: {str(e)}")
            return False
    
    def encode_frame(self, frame: np.ndarray) -> bool:
        """编码单帧"""
        if not self.is_encoding or self.writer is None:
            return False
        
        try:
            # 调整帧大小（如果需要）
            if frame.shape[:2][::-1] != self.frame_size:
                frame = cv2.resize(frame, self.frame_size)
            
            # 写入帧
            self.writer.write(frame)
            self.frame_count += 1
            self.frame_encoded.emit(self.frame_count)
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"编码帧失败: {str(e)}")
            return False
    
    def stop_encoding(self):
        """停止编码"""
        if not self.is_encoding:
            return
        
        try:
            self.is_encoding = False
            
            if self.writer:
                self.writer.release()
                self.writer = None
            
            self.encoding_stopped.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"停止编码失败: {str(e)}")
    
    def get_frame_count(self) -> int:
        """获取已编码的帧数"""
        return self.frame_count
    
    def get_duration(self) -> float:
        """获取视频时长（秒）"""
        if self.fps > 0:
            return self.frame_count / self.fps
        return 0.0

class ScreenRecorder(QObject):
    """屏幕录制器（整合屏幕捕获和视频编码）"""
    
    # 信号
    recording_started = pyqtSignal()         # 开始录制
    recording_stopped = pyqtSignal()         # 停止录制
    recording_paused = pyqtSignal()          # 暂停录制
    recording_resumed = pyqtSignal()         # 恢复录制
    progress_updated = pyqtSignal(int, float)  # 进度更新（帧数，时长）
    error_occurred = pyqtSignal(str)         # 发生错误
    
    def __init__(self):
        super().__init__()
        self.screen_capture = None
        self.video_encoder = None
        self.audio_capture = None
        
        self.is_recording = False
        self.is_paused = False
        self.start_time = 0
        self.pause_time = 0
        self.total_pause_duration = 0

        # 音频和视频文件路径
        self.video_temp_path = None
        self.audio_temp_path = None
        self.final_output_path = None
    
    def setup(self, screen_capture, video_encoder, audio_capture=None):
        """设置录制组件"""
        self.screen_capture = screen_capture
        self.video_encoder = video_encoder
        self.audio_capture = audio_capture

        # 连接信号
        if self.screen_capture:
            self.screen_capture.frame_captured.connect(self._on_frame_captured)
            self.screen_capture.error_occurred.connect(self.error_occurred)

        if self.video_encoder:
            self.video_encoder.frame_encoded.connect(self._on_frame_encoded)
            self.video_encoder.error_occurred.connect(self.error_occurred.emit)
            self.video_encoder.error_occurred.connect(self.error_occurred)
    
    def start_recording(self, output_path: str, fps: int = 30, quality: str = "高质量", format_type: str = "MP4"):
        """开始录制"""
        if self.is_recording:
            return False

        try:
            # 获取屏幕尺寸
            screen_size = self.screen_capture.get_screen_size()
            print(f"获取到的屏幕尺寸: {screen_size}")

            # 验证屏幕尺寸
            if not screen_size or len(screen_size) != 2 or screen_size[0] <= 0 or screen_size[1] <= 0:
                self.error_occurred.emit(f"无效的屏幕尺寸: {screen_size}")
                return False

            # 保存最终输出路径
            self.final_output_path = output_path

            # 如果有音频录制，创建临时文件
            if self.audio_capture:
                # 创建临时视频文件（无音频）
                temp_dir = tempfile.gettempdir()
                self.video_temp_path = str(Path(temp_dir) / f"temp_video_{int(time.time())}.mp4")
                self.audio_temp_path = str(Path(temp_dir) / f"temp_audio_{int(time.time())}.wav")

                # 设置视频编码器参数为临时文件
                self.video_encoder.set_output_params(self.video_temp_path, fps, screen_size, format_type, quality)
            else:
                # 没有音频，直接输出到最终文件
                self.video_encoder.set_output_params(output_path, fps, screen_size, format_type, quality)
            
            # 开始编码
            if not self.video_encoder.start_encoding():
                return False
            
            # 开始屏幕捕获
            self.screen_capture.set_fps(fps)
            self.screen_capture.start_capture()
            
            # 开始音频录制（如果启用）
            if self.audio_capture:
                self.audio_capture.start_recording()
            
            self.is_recording = True
            self.is_paused = False
            self.start_time = time.time()
            self.total_pause_duration = 0
            
            self.recording_started.emit()
            return True
            
        except Exception as e:
            self.error_occurred.emit(f"开始录制失败: {str(e)}")
            return False
    
    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return

        try:
            self.is_recording = False
            self.is_paused = False

            # 停止屏幕捕获
            if self.screen_capture:
                self.screen_capture.stop_capture()

            # 停止视频编码
            if self.video_encoder:
                self.video_encoder.stop_encoding()

            # 停止音频录制并保存音频文件
            if self.audio_capture and self.audio_temp_path:
                self.audio_capture.stop_recording()
                self.audio_capture.save_audio(self.audio_temp_path)

                # 合并音频和视频
                self._merge_audio_video()

            self.recording_stopped.emit()

        except Exception as e:
            self.error_occurred.emit(f"停止录制失败: {str(e)}")
    
    def pause_recording(self):
        """暂停录制"""
        if not self.is_recording or self.is_paused:
            return
        
        self.is_paused = True
        self.pause_time = time.time()
        
        if self.screen_capture:
            self.screen_capture.stop_capture()
        
        if self.audio_capture:
            self.audio_capture.stop_recording()
        
        self.recording_paused.emit()
    
    def resume_recording(self):
        """恢复录制"""
        if not self.is_recording or not self.is_paused:
            return
        
        self.total_pause_duration += time.time() - self.pause_time
        self.is_paused = False
        
        if self.screen_capture:
            self.screen_capture.start_capture()
        
        if self.audio_capture:
            self.audio_capture.start_recording()
        
        self.recording_resumed.emit()
    
    def _on_frame_captured(self, frame):
        """处理捕获的帧"""
        if self.is_recording and not self.is_paused and self.video_encoder:
            self.video_encoder.encode_frame(frame)
    
    def _on_frame_encoded(self, frame_count):
        """处理编码完成的帧"""
        duration = self.get_recording_duration()
        self.progress_updated.emit(frame_count, duration)
    
    def get_recording_duration(self) -> float:
        """获取录制时长"""
        if not self.is_recording:
            return 0.0

        current_time = time.time()
        if self.is_paused:
            return self.pause_time - self.start_time - self.total_pause_duration
        else:
            return current_time - self.start_time - self.total_pause_duration

    def _merge_audio_video(self):
        """合并音频和视频文件"""
        try:
            if not self.video_temp_path or not self.audio_temp_path or not self.final_output_path:
                return

            # 检查临时文件是否存在
            if not Path(self.video_temp_path).exists():
                self.error_occurred.emit("临时视频文件不存在")
                return

            if not Path(self.audio_temp_path).exists():
                # 如果音频文件不存在，只复制视频文件
                import shutil
                shutil.copy2(self.video_temp_path, self.final_output_path)
                self._cleanup_temp_files()
                return

            # 优先使用ffmpeg-python库
            if FFMPEG_PYTHON_AVAILABLE:
                try:
                    print("使用ffmpeg-python库合并音频视频...")

                    # macOS特殊处理：设置FFmpeg路径
                    import platform
                    if platform.system() == "Darwin":
                        self._setup_ffmpeg_path_macos()

                    # 使用ffmpeg-python合并
                    video_input = ffmpeg.input(self.video_temp_path)
                    audio_input = ffmpeg.input(self.audio_temp_path)

                    output = ffmpeg.output(
                        video_input, audio_input,
                        self.final_output_path,
                        vcodec='copy',  # 复制视频流
                        acodec='aac',   # 音频编码为AAC
                        strict='experimental'
                    )

                    # 执行合并，覆盖输出文件
                    ffmpeg.run(output, overwrite_output=True, quiet=True)
                    print("✅ 音频视频合并成功")
                    self._cleanup_temp_files()
                    return

                except Exception as e:
                    print(f"ffmpeg-python合并失败: {e}")
                    # 继续尝试系统FFmpeg命令

            # 使用系统FFmpeg命令作为备选方案
            cmd = [
                'ffmpeg', '-y',  # -y 覆盖输出文件
                '-i', self.video_temp_path,  # 输入视频
                '-i', self.audio_temp_path,  # 输入音频
                '-c:v', 'copy',  # 复制视频流
                '-c:a', 'aac',   # 音频编码为AAC
                '-strict', 'experimental',
                self.final_output_path
            ]

            print(f"执行系统FFmpeg命令: {' '.join(cmd)}")

            # 执行FFmpeg命令
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print("✅ 音频视频合并成功")
                self._cleanup_temp_files()
            else:
                print(f"❌ FFmpeg错误: {result.stderr}")
                # 如果合并失败，至少保存视频文件
                import shutil
                shutil.copy2(self.video_temp_path, self.final_output_path)
                self._cleanup_temp_files()
                self.error_occurred.emit(f"音频合并失败，已保存纯视频文件: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.error_occurred.emit("音频视频合并超时")
        except FileNotFoundError:
            # FFmpeg未安装，只保存视频文件
            import shutil
            shutil.copy2(self.video_temp_path, self.final_output_path)
            self._cleanup_temp_files()
            self.error_occurred.emit("FFmpeg未安装，已保存纯视频文件")
        except Exception as e:
            self.error_occurred.emit(f"合并音频视频失败: {str(e)}")

    def _setup_ffmpeg_path_macos(self):
        """设置macOS的FFmpeg路径"""
        try:
            import os
            import shutil

            # 检查当前PATH中是否有ffmpeg
            if shutil.which('ffmpeg'):
                return

            # 检查常见的macOS FFmpeg安装位置
            possible_paths = [
                '/usr/local/bin',
                '/opt/homebrew/bin',
                str(Path.home() / '.local' / 'bin'),
                '/usr/bin'
            ]

            for bin_path in possible_paths:
                ffmpeg_path = Path(bin_path) / 'ffmpeg'
                if ffmpeg_path.exists():
                    # 添加到PATH环境变量
                    current_path = os.environ.get('PATH', '')
                    if bin_path not in current_path:
                        os.environ['PATH'] = f"{bin_path}:{current_path}"
                        print(f"✅ 已添加FFmpeg路径到PATH: {bin_path}")
                    return

            print("⚠️ 未找到FFmpeg，可能需要安装")

        except Exception as e:
            print(f"设置FFmpeg路径失败: {e}")

    def _cleanup_temp_files(self):
        """清理临时文件"""
        try:
            if self.video_temp_path and Path(self.video_temp_path).exists():
                Path(self.video_temp_path).unlink()
            if self.audio_temp_path and Path(self.audio_temp_path).exists():
                Path(self.audio_temp_path).unlink()
        except Exception as e:
            print(f"清理临时文件失败: {e}")
        finally:
            self.video_temp_path = None
            self.audio_temp_path = None
            self.final_output_path = None
