# 磁力下载器 (Magnet Downloader)

一个简洁、纯净的Python 3磁力链接下载器，无广告，支持暂停/继续下载。

## 功能特性

✅ **磁力链接解析** - 支持标准magnet:?xt=urn:btih:格式  
✅ **图形化界面** - 简洁易用的GUI，基于tkinter  
✅ **暂停/继续** - 随时暂停和恢复下载  
✅ **实时统计** - 显示下载进度、速度、连接数等信息  
✅ **自定义路径** - 灵活选择文件保存位置  
✅ **纯净无广告** - 开源项目，完全免费  

## 系统要求

- Python 3.7+
- Linux / macOS / Windows

## 安装

### 1. 克隆项目

```bash
git clone https://github.com/xulan68/magnet-downloader.git
cd magnet-downloader
```

### 2. 安装依赖

#### Ubuntu/Debian:
```bash
sudo apt-get install python3-libtorrent
pip3 install -r requirements.txt
```

#### macOS (使用Homebrew):
```bash
brew install libtorrent-rasterbar
pip3 install -r requirements.txt
```

#### Windows:
```bash
pip3 install -r requirements.txt
```

## 使用

### 启动应用

```bash
python3 main.py
```

### 基本操作

1. **粘贴磁力链接** - 在输入框中粘贴磁力链接（以`magnet:`开头）
2. **选择保存路径** - 点击"更改路径"选择文件保存位置
3. **开始下载** - 点击"添加下载"按钮
4. **暂停/继续** - 使用"暂停"和"继续"按钮控制下载
5. **停止下载** - 点击"停止"按钮停止当前任务

## 项目结构

```
magnet-downloader/
├── main.py                 # 主程序入口
├── requirements.txt        # 项目依赖
├── README.md              # 项目说明
├── core/
│   └── downloader.py      # 核心下载引擎
├── gui/
│   └── app.py             # GUI应用界面
└── downloads/             # 默认下载文件夹
```

## API 说明

### MagnetDownloader 类

#### 初始化
```python
from core.downloader import MagnetDownloader

downloader = MagnetDownloader(save_path="./downloads")
```

#### 添加磁力链接
```python
success = downloader.add_magnet("magnet:?xt=urn:btih:...")
```

#### 控制下载
```python
downloader.pause()      # 暂停
downloader.resume()     # 继续
downloader.stop()       # 停止
```

#### 获取状态
```python
status = downloader.get_status()
# 返回: {
#   'state': 'downloading',
#   'progress': 50.5,
#   'downloaded': 512000,
#   'total': 1024000,
#   'speed': 102400,
#   'peers': 10,
#   'name': 'filename',
#   'is_paused': False,
#   'is_seeding': False
# }
```

## 常见问题

### Q: 如何添加多个下载任务？
A: 目前支持单个下载任务。完成或停止当前任务后可以添加新任务。

### Q: 支持哪些文件类型？
A: 支持所有BitTorrent格式的文件，包括单文件和多文件种子。

### Q: 下载速度很慢怎么办？
A: 这取决于：
1. 磁力链接的种子数（Peers数量）
2. 网络连接质量
3. 系统资源

### Q: 在哪里找到已下载的文件？
A: 文件保存在你设置的保存路径中，默认为项目目录下的 `downloads` 文件夹。

## 免责声明

此项目仅供学习和合法用途使用。使用者应遵守当地法律，不应用于下载受著作权保护的内容。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 作者

xulan68
