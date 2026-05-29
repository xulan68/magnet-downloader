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
        
        # 应用基础优化配置
        self._apply_optimizations()
        
        self.handle = None
        self.info = None
        self.is_paused = False
        self.is_downloading = False
        self.torrent_name = ""
    
    def _apply_optimizations(self):
        """应用优化配置"""
        try:
            # 尝试使用 session 的 set_settings 方法
            settings = self.session.get_settings()
            
            # 连接优化
            settings['connections_limit'] = 500
            settings['half_open_limit'] = 100
            
            # 速率优化
            settings['upload_rate_limit'] = 0
            settings['download_rate_limit'] = 0
            
            # DHT优化
            settings['enable_dht'] = True
            
            # UPnP/NAT
            settings['enable_upnp'] = True
            settings['enable_natpmp'] = True
            
            # 缓存优化
            settings['cache_size'] = 2048
            
            self.session.set_settings(settings)
        except:
            # 如果设置失败，尝试直接配置
            try:
                # 启用DHT
                self.session.start_dht()
                
                # 添加DHT bootstrap节点
                self.session.add_dht_node(("router.bittorrent.com", 6881))
                self.session.add_dht_node(("dht.transmissionbt.com", 6881))
                self.session.add_dht_node(("router.utorrent.com", 6881))
                
                # 添加扩展
                self.session.add_extension("ut_pex")
                self.session.add_extension("ut_metadata")
            except:
                # 如果以上都失败，使用默认配置
                print("信息: 使用默认libtorrent配置")
                pass
    
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
            self.torrent_name = ""
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
            self.torrent_name = ""
    
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
            
            # 尝试获取种子名称
            name = self.torrent_name
            if not name:
                try:
                    info = self.handle.get_torrent_info()
                    if info:
                        name = info.name()
                        self.torrent_name = name
                except:
                    try:
                        name = self.handle.name()
                    except:
                        name = "下载中..."
            
            return {
                'state': str(status.state),
                'progress': status.progress * 100,
                'downloaded': status.total_done,
                'total': status.total_wanted,
                'speed': status.download_rate,
                'peers': status.num_peers,
                'name': name,
                'is_paused': self.is_paused,
                'is_seeding': status.is_seeding
            }
        except Exception as e:
            print(f"获取状态错误: {e}")
            try:
                status = self.handle.status()
                return {
                    'state': str(status.state),
                    'progress': status.progress * 100,
                    'downloaded': status.total_done,
                    'total': status.total_wanted,
                    'speed': status.download_rate,
                    'peers': status.num_peers,
                    'name': self.torrent_name or "下载中...",
                    'is_paused': self.is_paused,
                    'is_seeding': status.is_seeding
                }
            except:
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
