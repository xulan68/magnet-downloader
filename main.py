#!/usr/bin/env python3
"""
磁力下载器主程序入口
"""

import sys
from pathlib import Path
import tkinter as tk

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from gui.app import MagnetDownloaderGUI


def main():
    """启动应用"""
    root = tk.Tk()
    app = MagnetDownloaderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
