#!/usr/bin/env python3
"""
PyInstaller打包脚本
将GUI应用打包成macOS可执行应用
"""

import PyInstaller.__main__
import os
import sys

def build_app():
    """构建macOS应用程序"""
    
    # PyInstaller参数
    args = [
        'gui_app.py',
        '--name=StockNewsAnalyzer',
        '--windowed',  # 无控制台窗口
        '--onefile',   # 单文件模式
        '--clean',     # 清理临时文件
        '--noconfirm', # 不询问覆盖
        
        # 包含数据文件
        '--add-data=config.json:.',
        '--add-data=stock_news.db:.',
        
        # 隐藏导入模块
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=sqlite3',
        '--hidden-import=requests',
        '--hidden-import=schedule',
        
        # macOS特定设置
        '--target-arch=universal2',  # 支持Intel和Apple Silicon
        '--osx-bundle-identifier=com.stocknews.analyzer',
        
        # 图标设置（如果有的话）
        # '--icon=icon.icns',
        
        # 输出目录
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
    ]
    
    print("🚀 开始构建macOS应用程序...")
    print(f"参数: {' '.join(args)}")
    
    # 运行PyInstaller
    PyInstaller.__main__.run(args)
    
    print("✅ 构建完成！")
    print("📁 应用程序位置: dist/StockNewsAnalyzer")
    print("💡 双击运行或在终端中执行: ./dist/StockNewsAnalyzer")

if __name__ == "__main__":
    build_app()