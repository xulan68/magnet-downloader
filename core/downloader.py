import libtorrent as lt
import os
import time
from pathlib import Path
from typing import Optional, Callable


class MagnetDownloader:
    """磁力链接下载器核心引擎"""
    
    def __init__(self, save_path: str = "./downloads"):
        """
        初始化下载器
        
        Args:
            save_path: 文件保存路径
        """
        self.save_path = Path(save_path)
        self.save_path.mkdir(parents=True, exist_ok=True)
        
        # 创建session
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        
        self.handle = None
        self.info = None
        self.is_paused = False
        self.is_downloading = False
        
    def add_magnet(self, magnet_uri: str) -> bool:
        """
        添加磁力链接
        
        Args:
            magnet_uri: 磁力链接 (magnet:?xt=urn:btih:...)
            
        Returns:
            成功返回True
        """
        try:
            params = lt.parse_magnet_uri(magnet_uri)
            params.save_path = str(self.save_path)
            self.handle = self.session.add_torrent(params)
            self.is_downloading = True
            return True
        except Exception as e:
            print(f"添加磁力链接失败: {e}")
            return False
    
    def pause(self):
        """暂停下载"""
        if self.handle and not self.is_paused:
            self.handle.pause()
            self.is_paused = True
    
    def resume(self):
        """继续下载"""
        if self.handle and self.is_paused:
            self.handle.resume()
            self.is_paused = False
    
    def stop(self):
        """停止下载"""
        if self.handle:
            self.session.remove_torrent(self.handle)
            self.handle = None
            self.is_downloading = False
            self.is_paused = False
    
    def get_status(self) -> dict:
        """
        获取下载状态
        
        Returns:
            包含下载信息的字典
        """
        # 默认状态
        default_status = {
            'state': 'idle',
            'progress': 0,
            'downloaded': 0,
            'total': 0,
            'speed': 0,
            'peers': 0,
            'name': '',
            'is_paused': False,
            'is_seeding': False
        }
        
        if not self.handle:
            return default_status
        
        try:
            status = self.handle.status()
            info = self.handle.get_torrent_info()
            
            return {
                'state': str(status.state),
                'progress': status.progress * 100,
                'downloaded': status.total_done,
                'total': status.total_wanted,
                'speed': status.download_rate,
                'peers': status.num_peers,
                'name': info.name(),
                'is_paused': self.is_paused,
                'is_seeding': status.is_seeding
            }
        except Exception as e:
            print(f"获取状态错误: {e}")
            return default_status
    
    def is_complete(self) -> bool:
        """检查下载是否完成"""
        if not self.handle:
            return False
        try:
            status = self.handle.status()
            return status.is_seeding or status.progress == 1.0
        except:
            return False
    
    def get_save_path(self) -> str:
        """获取保存路径"""
        return str(self.save_path)
