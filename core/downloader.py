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
        
        # 创建session并优化配置
        self.session = self._create_optimized_session()
        
        self.handle = None
        self.info = None
        self.is_paused = False
        self.is_downloading = False
        self.torrent_name = ""
    
    def _create_optimized_session(self):
        """创建优化的libtorrent session"""
        session = lt.session()
        
        # 设置监听端口范围
        session.listen_on(6881, 6891)
        
        # 优化设置
        settings = session.get_settings()
        
        # 1. 连接优化
        settings['connections_limit'] = 500  # 最大连接数
        settings['half_open_limit'] = 100    # 半开连接数
        settings['max_allowed_in_request_queue'] = 2000  # 请求队列
        
        # 2. 上传/下载优化
        settings['upload_rate_limit'] = 0    # 无上传限制（0表示无限制）
        settings['download_rate_limit'] = 0  # 无下载限制
        settings['max_out_request_queue'] = 500  # 最大出站请求队列
        
        # 3. DHT优化
        settings['enable_dht'] = True
        settings['dht_upload_rate_limit'] = 0
        
        # 4. UPnP/NAT穿透
        settings['upnp_ignore_nonrouters'] = True
        settings['enable_upnp'] = True
        settings['enable_natpmp'] = True
        
        # 5. 性能优化
        settings['aio_threads'] = 8  # 异步IO线程数
        settings['checking_mem_usage'] = 256  # 检查内存使用
        settings['disk_io_write_mode'] = 0  # 立即写入磁盘
        
        # 6. 缓存优化
        settings['cache_size'] = 2048  # 缓存大小（MB）
        settings['read_cache_line_size'] = 32
        
        session.set_settings(settings)
        
        # 启用DHT路由表
        session.start_dht()
        
        # 添加DHT bootstrap节点
        session.add_dht_node(("router.bittorrent.com", 6881))
        session.add_dht_node(("dht.transmissionbt.com", 6881))
        session.add_dht_node(("router.utorrent.com", 6881))
        
        # 添加tracker服务器
        session.add_extension("ut_pex")
        session.add_extension("ut_metadata")
        session.add_extension("lt_trackers")
        
        return session
    
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
            
            # 优化下载优先级
            self.handle = self.session.add_torrent(params)
            
            # 设置优先级为最高
            if self.handle:
                self.handle.set_priority(7)  # 最高优先级
            
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
            
            # 尝试获取种子名称（只有当元数据已加载时才有效）
            name = self.torrent_name
            if not name:
                try:
                    info = self.handle.get_torrent_info()
                    if info:
                        name = info.name()
                        self.torrent_name = name
                except:
                    # 元数据可能还没加载，使用hex name作为备选
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
            # 返回部分有效状态而不是完全默认
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
