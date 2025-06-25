# FinBERT集成指南

## 概述

FinBERT是专门为金融文本设计的BERT模型，在股票新闻情感分析方面表现更佳。本工具已集成FinBERT支持。

## 安装FinBERT依赖

```bash
pip install transformers torch
```

## 功能特性

### 1. 自动回退机制
- 优先使用FinBERT进行情感分析
- 如果FinBERT不可用，自动回退到备用方法
- 支持配置开关控制是否使用FinBERT

### 2. 智能缓存
- 首次使用会自动下载模型文件
- 模型文件缓存到本地目录 `./models`
- 后续使用直接从缓存加载

### 3. 增强的情感分析
- **FinBERT**: 专业金融文本分析，准确率更高
- **TextBlob**: 通用文本情感分析
- **关键词方法**: 基于金融词汇的简单分析

## 配置选项

在 `config.json` 中添加：

```json
{
  "analysis": {
    "use_finbert": true,
    "model_cache_dir": "./models"
  }
}
```

## 使用方法

### 启用FinBERT
```bash
# 确保配置文件中 use_finbert: true
python stock_news_analyzer.py --once
```

### 禁用FinBERT
修改配置文件:
```json
{
  "analysis": {
    "use_finbert": false
  }
}
```

## 性能对比

| 方法 | 准确率 | 速度 | 适用场景 |
|------|--------|------|----------|
| FinBERT | 高 | 慢 | 金融新闻分析 |
| TextBlob | 中 | 快 | 通用文本分析 |
| 关键词 | 低 | 快 | 简单快速分析 |

## 测试示例

运行测试脚本：
```bash
python test_finbert.py
```

测试结果显示不同方法的情感分析对比。

## 注意事项

1. **首次运行**: 会下载约400MB的模型文件
2. **内存需求**: 需要至少2GB内存运行FinBERT
3. **网络要求**: 首次需要联网下载模型
4. **兼容性**: 支持Python 3.7+

## 故障排除

### 模型下载失败
```bash
# 手动指定镜像源
export HF_ENDPOINT=https://hf-mirror.com
python stock_news_analyzer.py --once
```

### 内存不足
```bash
# 禁用FinBERT，使用轻量级方法
# 修改config.json中的use_finbert为false
```

### 依赖安装失败
```bash
# 使用conda安装
conda install pytorch transformers -c pytorch
```

## 效果展示

FinBERT能更准确识别金融新闻中的情感倾向：

- ✅ "股价飙升" → 正面情感
- ✅ "业绩超预期" → 正面情感  
- ✅ "监管担忧" → 负面情感
- ✅ "市场波动" → 中性情感