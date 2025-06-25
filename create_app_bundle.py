#!/usr/bin/env python3
"""
创建macOS应用程序包
手动创建.app结构，不依赖PyInstaller
"""

import os
import shutil
import stat
from pathlib import Path

def create_app_bundle():
    """创建macOS应用程序包"""
    
    app_name = "StockNewsAnalyzer"
    app_dir = f"{app_name}.app"
    
    print(f"🍎 创建macOS应用包: {app_dir}")
    
    # 删除现有应用包
    if os.path.exists(app_dir):
        shutil.rmtree(app_dir)
        print("🗑️  删除现有应用包")
    
    # 创建应用包结构
    contents_dir = f"{app_dir}/Contents"
    macos_dir = f"{contents_dir}/MacOS"
    resources_dir = f"{contents_dir}/Resources"
    
    os.makedirs(macos_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)
    
    print("📁 创建应用包目录结构")
    
    # 创建Info.plist
    info_plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>{app_name}</string>
    <key>CFBundleIdentifier</key>
    <string>com.stocknews.analyzer</string>
    <key>CFBundleName</key>
    <string>Stock News Analyzer</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.15</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSUIElement</key>
    <false/>
</dict>
</plist>'''
    
    with open(f"{contents_dir}/Info.plist", "w") as f:
        f.write(info_plist_content)
    
    print("📄 创建Info.plist")
    
    # 创建启动脚本
    launcher_script = f'''#!/bin/bash

# 获取应用包路径
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RESOURCES_DIR="$APP_DIR/Resources"

# 切换到资源目录
cd "$RESOURCES_DIR"

# 设置Python路径
export PYTHONPATH="$RESOURCES_DIR:$PYTHONPATH"

# 启动Python应用
python3 run_app.py
'''
    
    launcher_path = f"{macos_dir}/{app_name}"
    with open(launcher_path, "w") as f:
        f.write(launcher_script)
    
    # 设置执行权限
    os.chmod(launcher_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print("🚀 创建启动脚本")
    
    # 复制应用文件到Resources目录
    files_to_copy = [
        'stock_news_analyzer.py',
        'gui_app.py',
        'run_app.py',
        'config.json',
        'lightweight_analyzer.py',
        'test_finbert.py'
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, resources_dir)
            print(f"📋 复制: {file}")
    
    # 复制数据库文件（如果存在）
    if os.path.exists('stock_news.db'):
        shutil.copy2('stock_news.db', resources_dir)
        print("📋 复制: stock_news.db")
    
    print(f"\n✅ 应用包创建完成: {app_dir}")
    print(f"📁 位置: {os.path.abspath(app_dir)}")
    print(f"\n🚀 使用方法:")
    print(f"1. 双击打开: open '{app_dir}'")
    print(f"2. 终端运行: open '{app_dir}'")
    print(f"\n💡 提示:")
    print("- 首次运行可能需要在系统偏好设置中允许")
    print("- 可以将应用拖拽到应用程序文件夹")

if __name__ == "__main__":
    create_app_bundle()