#!/usr/bin/env python3
"""
Enhanced PyInstaller hook for transformers library with complete metadata support
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files
import os
import sys

print("🔧 开始处理transformers库的依赖...")

# 收集所有transformers相关模块和数据
datas, binaries, hiddenimports = collect_all('transformers')

# 核心依赖包（必须按顺序处理）
core_dependencies = [
    'torch',           # 深度学习框架
    'numpy',           # 数值计算
    'transformers',    # 主库
    'tokenizers',      # 分词器
    'safetensors',     # 张量格式
    'huggingface_hub', # 模型中心
]

# 额外依赖包
extra_dependencies = [
    'tqdm',
    'requests', 
    'pyyaml',
    'regex',
    'filelock',
    'packaging',
    'sympy',
    'networkx',
    'fsspec',
]

# 处理核心依赖
for pkg in core_dependencies:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas.extend(pkg_datas)
        binaries.extend(pkg_binaries)
        hiddenimports.extend(pkg_hiddenimports)
        print(f"✓ 核心依赖 {pkg} 元数据收集完成")
    except Exception as e:
        print(f"❌ 核心依赖 {pkg} 收集失败: {e}")

# 处理额外依赖
for pkg in extra_dependencies:
    try:
        pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
        datas.extend(pkg_datas)
        binaries.extend(pkg_binaries)
        hiddenimports.extend(pkg_hiddenimports)
        print(f"✓ 额外依赖 {pkg} 元数据收集完成")
    except Exception as e:
        print(f"⚠ 额外依赖 {pkg} 跳过: {e}")

# 特别处理importlib.metadata相关
metadata_modules = [
    'importlib.metadata',
    'importlib_metadata',
    'pkg_resources',
]

for module in metadata_modules:
    if module not in hiddenimports:
        hiddenimports.append(module)
        print(f"✓ 添加元数据模块: {module}")

# 特别处理PyYAML包 - 包名和模块名不匹配
print("🔧 特别处理PyYAML包...")
try:
    # 直接收集yaml模块而不是pyyaml包名
    yaml_datas, yaml_binaries, yaml_hiddenimports = collect_all('yaml')
    datas.extend(yaml_datas)
    binaries.extend(yaml_binaries)
    hiddenimports.extend(yaml_hiddenimports)
    print("✓ PyYAML yaml模块收集成功")
    
    # 手动添加PyYAML的dist-info以便pkg_resources能找到版本信息
    import sys
    import os
    pyyaml_dist_info = None
    for path in sys.path:
        candidate = os.path.join(path, 'PyYAML-6.0.2.dist-info')
        if os.path.isdir(candidate):
            pyyaml_dist_info = candidate
            break
    
    if pyyaml_dist_info:
        # 收集整个dist-info目录
        datas.append((pyyaml_dist_info, 'PyYAML-6.0.2.dist-info'))
        print(f"✓ 手动收集PyYAML元数据: {pyyaml_dist_info}")
    else:
        print("⚠ 未找到PyYAML-6.0.2.dist-info目录")
except Exception as e:
    print(f"⚠ PyYAML包处理失败: {e}")

# 特别处理yaml模块
yaml_modules = ['yaml', '_yaml', 'yaml.loader', 'yaml.constructor', 'yaml.representer', 'yaml.resolver']
for module in yaml_modules:
    if module not in hiddenimports:
        hiddenimports.append(module)

print("✓ YAML模块处理完成")

# 收集所有transformers.models子模块
print("🔄 收集transformers.models子模块...")
model_submodules = collect_submodules('transformers.models')
hiddenimports.extend(model_submodules)
print(f"✓ 收集了 {len(model_submodules)} 个模型子模块")

# 包含关键的transformers模块
critical_modules = [
    # BERT相关
    'transformers.models.bert',
    'transformers.models.bert.modeling_bert',
    'transformers.models.bert.configuration_bert', 
    'transformers.models.bert.tokenization_bert',
    'transformers.models.bert.tokenization_bert_fast',
    
    # 核心工具
    'transformers.tokenization_utils',
    'transformers.tokenization_utils_base',
    'transformers.tokenization_utils_fast',
    'transformers.configuration_utils',
    'transformers.modeling_utils',
    'transformers.file_utils',
    
    # 实用工具
    'transformers.utils',
    'transformers.utils.hub',
    'transformers.utils.import_utils',
    'transformers.utils.logging',
    
    # tqdm相关
    'tqdm',
    'tqdm.std',
    'tqdm.auto',
    'tqdm.utils',
]

for module in critical_modules:
    if module not in hiddenimports:
        hiddenimports.append(module)

print(f"✓ 添加了 {len(critical_modules)} 个关键模块")

# 包含配置文件和元数据文件
print("📁 收集配置文件和数据...")
try:
    config_datas = collect_data_files('transformers', include_py_files=True)
    datas.extend(config_datas)
    print(f"✓ 收集了 {len(config_datas)} 个数据文件")
except Exception as e:
    print(f"⚠ 配置文件收集警告: {e}")

print(f"🎉 transformers hook完成! 总计:")
print(f"   - 数据文件: {len(datas)}")
print(f"   - 二进制文件: {len(binaries)}")  
print(f"   - 隐藏导入: {len(hiddenimports)}")
print("="*50)