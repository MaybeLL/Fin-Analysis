#!/usr/bin/env python3
"""
股票新闻分析工具启动器
检测依赖并启动GUI应用
"""

import sys
import subprocess
import os
from pathlib import Path

def check_dependencies():
    """检查并安装依赖"""
    required_packages = ['requests', 'schedule']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安装")
    
    if missing_packages:
        print(f"\n📦 正在安装缺少的依赖: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ 依赖安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败，请手动安装:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def check_files():
    """检查必要文件"""
    required_files = [
        'stock_news_analyzer.py',
        'gui_app.py',
        'config.json'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少文件: {file}")
            return False
        print(f"✅ {file} - 存在")
    
    return True

def main():
    """主函数"""
    print("📈 股票新闻分析工具")
    print("==================")
    print()
    
    # 检查文件
    print("🔍 检查文件...")
    if not check_files():
        print("\n❌ 文件检查失败")
        input("按回车键退出...")
        return
    
    print("\n🔍 检查依赖...")
    if not check_dependencies():
        print("\n❌ 依赖检查失败")
        input("按回车键退出...")
        return
    
    print("\n🚀 启动应用...")
    try:
        # 导入并运行GUI应用
        from gui_app import StockNewsGUI
        app = StockNewsGUI()
        app.run()
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()