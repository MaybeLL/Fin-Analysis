# 股票新闻分析工具

一个用于定时拉取目标股票公司相关新闻并进行情感分析的Python工具。

## 功能特性

- 🔄 定时自动拉取股票新闻
- 📰 支持多个新闻数据源 (Alpha Vantage, Finnhub)
- 🧠 自动情感分析 (正面/负面/中性)
- 💾 SQLite数据库存储
- 📊 生成分析报告
- ⚙️ 灵活的配置选项

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置设置

1. 编辑 `config.json` 文件
2. 添加你的API密钥：
   - [Alpha Vantage API](https://www.alphavantage.co/support/#api-key)
   - [Finnhub API](https://finnhub.io/register)
3. 设置要监控的股票代码
4. 调整定时任务间隔

## 使用方法

### 启动定时任务
```bash
python stock_news_analyzer.py
```

### 运行一次收集
```bash
python stock_news_analyzer.py --once
```

### 生成分析报告
```bash
python stock_news_analyzer.py --report AAPL --days 7
```

### 自定义配置文件
```bash
python stock_news_analyzer.py --config my_config.json
```

## 配置文件说明

```json
{
  "stocks": ["AAPL", "GOOGL", "MSFT"],  // 监控的股票代码
  "api_keys": {
    "alpha_vantage": "YOUR_API_KEY",
    "finnhub": "YOUR_API_KEY"
  },
  "schedule": {
    "interval_hours": 4,  // 定时间隔(小时)
    "start_time": "09:00"
  },
  "analysis": {
    "sentiment_threshold": 0.1,
    "max_news_per_stock": 50
  }
}
```

## 数据库结构

工具使用SQLite数据库存储新闻数据，包含以下字段：
- 股票代码
- 新闻标题和内容
- 发布时间
- 情感分数和标签
- 数据源

## 分析报告示例

```json
{
  "symbol": "AAPL",
  "period_days": 7,
  "total_news": 25,
  "sentiment_distribution": {
    "positive": 12,
    "negative": 3,
    "neutral": 10
  },
  "average_sentiment_score": 0.156,
  "overall_sentiment": "positive",
  "recent_headlines": [...]
}
```

## 注意事项

- 需要注册并获取API密钥
- 注意API调用频率限制
- 定期备份数据库文件