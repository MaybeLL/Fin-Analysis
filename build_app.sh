#!/bin/bash

# macOS应用构建脚本
# 自动安装依赖并打包应用

echo "📦 构建股票新闻分析工具 - macOS版本"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "✅ Python环境检查通过"

# 安装依赖
echo "📥 安装依赖包..."
pip install -r requirements_gui.txt

if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi

echo "✅ 依赖安装完成"

# 检查必要文件
if [ ! -f "gui_app.py" ]; then
    echo "❌ 错误: 未找到gui_app.py"
    exit 1
fi

if [ ! -f "stock_news_analyzer.py" ]; then
    echo "❌ 错误: 未找到stock_news_analyzer.py"
    exit 1
fi

if [ ! -f "config.json" ]; then
    echo "⚠️  警告: 未找到config.json，将使用默认配置"
fi

echo "✅ 文件检查完成"

# 运行PyInstaller
echo "🔨 开始打包应用..."

pyinstaller \
    --name="StockNewsAnalyzer" \
    --windowed \
    --onefile \
    --clean \
    --noconfirm \
    --add-data="config.json:." \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --hidden-import=sqlite3 \
    --hidden-import=requests \
    --hidden-import=schedule \
    --target-arch=universal2 \
    --osx-bundle-identifier=com.stocknews.analyzer \
    gui_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 构建成功！"
    echo "📁 应用程序位置: ./dist/StockNewsAnalyzer"
    echo ""
    echo "🚀 运行方法:"
    echo "1. 双击打开: open ./dist/StockNewsAnalyzer"
    echo "2. 终端运行: ./dist/StockNewsAnalyzer"
    echo ""
    echo "📝 注意事项:"
    echo "- 首次运行可能需要在系统偏好设置中允许运行"
    echo "- 如需分发，请考虑代码签名"
    echo ""
else
    echo "❌ 构建失败"
    exit 1
fi