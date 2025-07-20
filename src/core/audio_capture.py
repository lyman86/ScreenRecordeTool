# macOS音频修复
"""
音频捕获模块
"""

import threading
import wave
import pyaudio
import numpy as np
from typing import Optional, List
from PyQt6.QtCore import QObject, pyqtSignal

class AudioCapture(QObject):
    """音频捕获类"""
    
    # 信号
    audio_data_ready = pyqtSignal(bytes)     # 音频数据就绪
    capture_started = pyqtSignal()           # 开始录制
    capture_stopped = pyqtSignal()           # 停止录制
    error_occurred = pyqtSignal(str)         # 发生错误
    
    def __init__(self):
        super().__init__()
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.record_thread = None
        
        # macOS音频修复 - 优化音频参数
        import platform
        if platform.system() == "Darwin":
            # macOS优化设置
            self.sample_rate = 44100
            self.channels = 1  # macOS上使用单声道更稳定
            self.chunk_size = 2048  # 增大缓冲区
            self.format = pyaudio.paInt16
        else:
            # 其他系统的设置
            self.sample_rate = 44100
            self.channels = 2
            self.chunk_size = 1024
            self.format = pyaudio.paInt16
        
        # 音频数据缓冲
        self.audio_buffer = []
        self.buffer_lock = threading.Lock()

        # 音量监控
        self.volume_level = 0.0
        
        print(f"音频参数: {self.sample_rate}Hz, {self.channels}声道, 缓冲区{self.chunk_size}")

    def __del__(self):
        """析构函数，确保资源清理"""
        try:
            self.stop_recording()
            if hasattr(self, 'audio') and self.audio:
                self.audio.terminate()
        except:
            pass

    def get_audio_devices(self) -> List[dict]:
        """获取音频设备列表"""
        devices = []
        try:
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:  # 只返回输入设备
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate'])
                    })
        except Exception as e:
            self.error_occurred.emit(f"获取音频设备失败: {str(e)}")
        
        return devices
    
    def set_audio_params(self, sample_rate: int = 44100, channels: int = 2, chunk_size: int = 1024):
        """设置音频参数"""
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """音频回调函数"""
        try:
            if self.is_recording and in_data:
                with self.buffer_lock:
                    self.audio_buffer.append(in_data)
                self.audio_data_ready.emit(in_data)
            return (None, pyaudio.paContinue)
        except Exception as e:
            print(f"音频回调错误: {e}")
            return (None, pyaudio.paAbort)
    
    def start_recording(self, device_index: Optional[int] = None):
        """开始录制音频"""
        if self.is_recording:
            return
        
        try:
            # 清空缓冲区
            with self.buffer_lock:
                self.audio_buffer.clear()
            
            # 创建音频流
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.stream.start_stream()
            self.capture_started.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"开始音频录制失败: {str(e)}")
    
    def stop_recording(self):
        """停止录制音频"""
        if not self.is_recording:
            return

        try:
            self.is_recording = False

            if self.stream:
                try:
                    if self.stream.is_active():
                        self.stream.stop_stream()
                except:
                    pass  # 忽略停止流时的错误

                try:
                    self.stream.close()
                except:
                    pass  # 忽略关闭流时的错误

                self.stream = None

            self.capture_stopped.emit()

        except Exception as e:
            self.error_occurred.emit(f"停止音频录制失败: {str(e)}")
    
    def get_audio_data(self) -> bytes:
        """获取录制的音频数据"""
        with self.buffer_lock:
            if self.audio_buffer:
                data = b''.join(self.audio_buffer)
                self.audio_buffer.clear()
                return data
        return b''
    
    def save_audio(self, filename: str):
        """保存音频到文件"""
        try:
            # 获取所有音频数据
            with self.buffer_lock:
                if not self.audio_buffer:
                    print("没有音频数据可保存")
                    return

                audio_data = b''.join(self.audio_buffer)
                print(f"保存音频数据: {len(audio_data)} 字节")

            if not audio_data:
                print("音频数据为空")
                return

            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_data)

            print(f"音频文件已保存: {filename}")

        except Exception as e:
            print(f"保存音频失败: {e}")
            self.error_occurred.emit(f"保存音频失败: {str(e)}")
    
    def get_volume_level(self) -> float:
        """获取当前音量级别（0.0-1.0）"""
        try:
            if not self.audio_buffer:
                return 0.0

            with self.buffer_lock:
                if self.audio_buffer:
                    # 获取最新的音频数据
                    latest_data = self.audio_buffer[-1]
                    if not latest_data:
                        return 0.0

                    # 转换为numpy数组并计算RMS
                    audio_array = np.frombuffer(latest_data, dtype=np.int16)
                    if len(audio_array) == 0:
                        return 0.0

                    # 计算均方根值，避免NaN
                    mean_square = np.mean(audio_array.astype(np.float64)**2)
                    if np.isnan(mean_square) or mean_square < 0:
                        return 0.0

                    rms = np.sqrt(mean_square)
                    if np.isnan(rms) or np.isinf(rms):
                        return 0.0

                    # 归一化到0-1范围
                    level = rms / 32768.0
                    return min(max(level, 0.0), 1.0)

        except Exception:
            pass

        return 0.0
    
    def __del__(self):
        """析构函数"""
        self.stop_recording()
        if hasattr(self, 'audio'):
            self.audio.terminate()
