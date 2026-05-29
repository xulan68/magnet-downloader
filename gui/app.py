import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import time
import os
import sys

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.downloader import MagnetDownloader


class MagnetDownloaderGUI:
    """磁力下载器GUI应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("磁力下载器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 下载器实例
        self.downloader = MagnetDownloader()
        self.update_thread = None
        self.is_running = True
        
        self.setup_ui()
        self.start_status_update()
        
    def setup_ui(self):
        """设置UI界面"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = ttk.Label(main_frame, text="磁力链接下载器", 
                                font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 磁力链接输入框
        ttk.Label(main_frame, text="磁力链接:").grid(row=1, column=0, sticky=tk.W)
        self.magnet_entry = ttk.Entry(main_frame, width=70)
        self.magnet_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 保存路径选择
        ttk.Label(main_frame, text="保存路径:").grid(row=2, column=0, sticky=tk.W)
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.path_label = ttk.Label(path_frame, text=self.downloader.get_save_path(), 
                                    foreground="blue")
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(path_frame, text="更改路径", 
                  command=self.change_path).pack(side=tk.RIGHT, padx=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        self.add_btn = ttk.Button(button_frame, text="添加下载", 
                                  command=self.add_download)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(button_frame, text="暂停", 
                                    command=self.pause_download, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.resume_btn = ttk.Button(button_frame, text="继续", 
                                     command=self.resume_download, state=tk.DISABLED)
        self.resume_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="停止", 
                                   command=self.stop_download, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        ttk.Label(main_frame, text="文件名:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.name_label = ttk.Label(main_frame, text="等待中...", foreground="gray")
        self.name_label.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Label(main_frame, text="进度:").grid(row=5, column=0, sticky=tk.W)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_label = ttk.Label(main_frame, text="0%")
        self.progress_label.grid(row=5, column=3, padx=5)
        
        # 详细信息框架
        info_frame = ttk.LabelFrame(main_frame, text="下载信息", padding="5")
        info_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       pady=10)
        
        # 信息标签
        ttk.Label(info_frame, text="已下载:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=3)
        self.downloaded_label = ttk.Label(info_frame, text="0 B", foreground="green")
        self.downloaded_label.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="总大小:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=3)
        self.total_label = ttk.Label(info_frame, text="0 B")
        self.total_label.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="下载速度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=3)
        self.speed_label = ttk.Label(info_frame, text="0 B/s", foreground="blue")
        self.speed_label.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="连接数:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=3)
        self.peers_label = ttk.Label(info_frame, text="0")
        self.peers_label.grid(row=1, column=3, sticky=tk.W, padx=5)
        
        ttk.Label(info_frame, text="状态:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=3)
        self.status_label = ttk.Label(info_frame, text="就绪", foreground="orange")
        self.status_label.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(1, weight=1)
        info_frame.columnconfigure(3, weight=1)
    
    def change_path(self):
        """更改保存路径"""
        new_path = filedialog.askdirectory(title="选择保存路径")
        if new_path:
            self.downloader.save_path = Path(new_path)
            self.path_label.config(text=new_path)
    
    def add_download(self):
        """添加下载"""
        magnet = self.magnet_entry.get().strip()
        
        if not magnet:
            messagebox.showwarning("警告", "请输入磁力链接")
            return
        
        if not magnet.startswith("magnet:"):
            messagebox.showerror("错误", "无效的磁力链接，应以 magnet: 开头")
            return
        
        if self.downloader.add_magnet(magnet):
            self.add_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.magnet_entry.config(state=tk.DISABLED)
            messagebox.showinfo("成功", "已添加下载任务")
        else:
            messagebox.showerror("错误", "添加下载失败，请检查磁力链接")
    
    def pause_download(self):
        """暂停下载"""
        self.downloader.pause()
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.NORMAL)
    
    def resume_download(self):
        """继续下载"""
        self.downloader.resume()
        self.pause_btn.config(state=tk.NORMAL)
        self.resume_btn.config(state=tk.DISABLED)
    
    def stop_download(self):
        """停止下载"""
        if messagebox.askyesno("确认", "确定要停止下载吗?"):
            self.downloader.stop()
            self.reset_ui()
    
    def reset_ui(self):
        """重置UI状态"""
        self.add_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        self.magnet_entry.config(state=tk.NORMAL)
        self.magnet_entry.delete(0, tk.END)
        
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.name_label.config(text="等待中...", foreground="gray")
        self.status_label.config(text="就绪", foreground="orange")
        self.downloaded_label.config(text="0 B")
        self.total_label.config(text="0 B")
        self.speed_label.config(text="0 B/s")
        self.peers_label.config(text="0")
    
    def format_bytes(self, bytes_val: int) -> str:
        """格式化字节大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_val < 1024.0:
                return f"{bytes_val:.2f} {unit}"
            bytes_val /= 1024.0
        return f"{bytes_val:.2f} PB"
    
    def update_status(self):
        """更新下载状态"""
        status = self.downloader.get_status()
        
        # 更新进度
        progress = status['progress']
        self.progress_var.set(progress)
        self.progress_label.config(text=f"{progress:.1f}%")
        
        # 更新文件名
        if status['name'] and status['name'] != self.name_label.cget("text"):
            self.name_label.config(text=status['name'], foreground="black")
        
        # 更新信息
        self.downloaded_label.config(text=self.format_bytes(status['downloaded']))
        self.total_label.config(text=self.format_bytes(status['total']))
        self.speed_label.config(text=self.format_bytes(status['speed']) + "/s")
        self.peers_label.config(text=str(status['peers']))
        
        # 更新状态
        if status['is_paused']:
            state_text = "已暂停"
            color = "red"
        elif status['is_seeding']:
            state_text = "做种中"
            color = "green"
        elif progress == 100:
            state_text = "已完成"
            color = "green"
        else:
            state_text = "下载中"
            color = "blue"
        
        self.status_label.config(text=state_text, foreground=color)
        
        # 下载完成
        if self.downloader.is_complete():
            messagebox.showinfo("完成", "下载已完成！")
            self.reset_ui()
    
    def start_status_update(self):
        """启动状态更新线程"""
        def update_loop():
            while self.is_running:
                try:
                    self.root.after(0, self.update_status)
                    time.sleep(0.5)
                except:
                    pass
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def on_closing(self):
        """窗口关闭事件处理"""
        if messagebox.askyesno("退出", "确定要退出吗?"):
            self.is_running = False
            if self.downloader.is_downloading:
                self.downloader.stop()
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MagnetDownloaderGUI(root)
    root.mainloop()
