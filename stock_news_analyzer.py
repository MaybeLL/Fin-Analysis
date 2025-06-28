#!/usr/bin/env python3
"""
股票新闻分析工具
定时拉取目标股票公司相关新闻，并进行情感分析
"""

import json
import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dataclasses import dataclass
import schedule
import re
import requests


@dataclass
class NewsItem:
    """新闻项目数据结构"""
    title: str
    content: str
    url: str
    publish_time: datetime
    source: str
    sentiment_score: float = 0.0
    sentiment_label: str = "neutral"


class NewsAnalyzer:
    """新闻分析器"""
    
    def __init__(self, use_finbert: bool = True, cache_dir: str = "./models"):
        self.finbert_model = None
        self.finbert_tokenizer = None
        self.use_finbert = use_finbert
        self.cache_dir = cache_dir
        self.analysis_method = "auto"  # auto, finbert, lightweight
        
        if self.use_finbert:
            self._init_finbert()
    
    def _init_finbert(self):
        """初始化FinBERT模型"""
        try:
            # 测试基本模块导入
            import torch
            print("✓ torch导入成功")
            
            import transformers
            print(f"✓ transformers导入成功，版本: {transformers.__version__}")
            
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            print("✓ 核心transformers类导入成功")
            
            # 测试所有必需的子模块
            test_modules = [
                'transformers.models',
                'transformers.models.bert',
                'transformers.models.bert.modeling_bert',
                'transformers.models.bert.configuration_bert',
                'transformers.models.bert.tokenization_bert'
            ]
            
            for module_name in test_modules:
                try:
                    __import__(module_name)
                    print(f"✓ {module_name} 可用")
                except ImportError as e:
                    print(f"⚠ {module_name} 不可用: {e}")
            
            import os
            
            # 创建缓存目录
            os.makedirs(self.cache_dir, exist_ok=True)
            
            model_name = "ProsusAI/finbert"
            print("正在加载FinBERT模型...")
            print("首次运行会下载模型文件，请耐心等待...")
            
            # 尝试加载模型，设置更宽松的参数
            self.finbert_tokenizer = AutoTokenizer.from_pretrained(
                model_name, 
                cache_dir=self.cache_dir,
                trust_remote_code=False,
                local_files_only=False
            )
            print("✓ FinBERT tokenizer加载成功")
            
            self.finbert_model = AutoModelForSequenceClassification.from_pretrained(
                model_name, 
                cache_dir=self.cache_dir,
                trust_remote_code=False,
                local_files_only=False,
                ignore_mismatched_sizes=True
            )
            print("✓ FinBERT模型加载成功")
            
            # 设置为评估模式
            self.finbert_model.eval()
            print("🎉 FinBERT完全初始化成功")
            
        except ImportError as e:
            print(f"❌ 模块导入失败: {e}")
            print("将使用备用情感分析方法")
            self.finbert_model = None
            self.finbert_tokenizer = None
        except Exception as e:
            print(f"❌ FinBERT模型加载失败: {e}")
            print("将使用备用情感分析方法")
            self.finbert_model = None
            self.finbert_tokenizer = None
    
    def _can_import(self, module_name):
        """检查是否可以导入模块"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def set_analysis_method(self, method: str):
        """设置分析方法"""
        if method in ["auto", "finbert", "lightweight"]:
            self.analysis_method = method
            print(f"分析方法已设置为: {method}")
        else:
            print(f"无效的分析方法: {method}")
    
    def get_analysis_method(self) -> str:
        """获取当前分析方法"""
        return self.analysis_method
    
    def analyze_sentiment_with_finbert(self, text: str) -> tuple[float, str]:
        """使用FinBERT进行情感分析"""
        try:
            import torch
            
            # 截取文本长度以适应模型输入限制
            max_length = 512
            if len(text) > max_length:
                text = text[:max_length]
            
            # 编码文本
            inputs = self.finbert_tokenizer(text, return_tensors="pt", 
                                          truncation=True, padding=True, max_length=max_length)
            
            # 预测
            with torch.no_grad():
                outputs = self.finbert_model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # FinBERT输出: [negative, neutral, positive]
            neg_score = predictions[0][0].item()
            neu_score = predictions[0][1].item()
            pos_score = predictions[0][2].item()
            
            # 计算极性分数 (-1 到 1)
            polarity = pos_score - neg_score
            
            # 确定标签
            if pos_score > max(neg_score, neu_score):
                label = "positive"
            elif neg_score > max(pos_score, neu_score):
                label = "negative"
            else:
                label = "neutral"
            
            return polarity, label
            
        except Exception as e:
            print(f"FinBERT分析失败: {e}")
            return self.analyze_sentiment_fallback(text)
    
    def analyze_sentiment_fallback(self, text: str) -> tuple[float, str]:
        """备用情感分析方法"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.1:
                label = "positive"
            elif polarity < -0.1:
                label = "negative"  
            else:
                label = "neutral"
                
            return polarity, label
            
        except ImportError:
            # 使用轻量级金融情感分析器
            return self._lightweight_financial_analysis(text)
    
    def _lightweight_financial_analysis(self, text: str) -> tuple[float, str]:
        """轻量级金融情感分析"""
        import re
        
        # 金融正面词汇
        positive_words = {
            'bullish', 'bull', 'rally', 'surge', 'soar', 'climb', 'rise', 'gain', 'up',
            'growth', 'profit', 'earnings', 'beat', 'exceed', 'outperform', 'strong',
            'robust', 'solid', 'healthy', 'positive', 'optimistic', 'confident',
            'breakthrough', 'success', 'expansion', 'milestone', 'record', 'high',
            'upgrade', 'buy', 'overweight', 'recommend', 'target', 'upside'
        }
        
        # 金融负面词汇
        negative_words = {
            'bearish', 'bear', 'crash', 'plunge', 'plummet', 'fall', 'drop', 'decline',
            'loss', 'losses', 'down', 'weak', 'poor', 'disappointing', 'miss', 'below',
            'underperform', 'concern', 'worry', 'fear', 'risk', 'threat', 'challenge',
            'pressure', 'struggle', 'difficulty', 'problem', 'issue', 'negative',
            'pessimistic', 'cautious', 'downgrade', 'sell', 'underweight', 'avoid'
        }
        
        # 高权重词汇
        high_weight_positive = {'surge', 'soar', 'skyrocket', 'breakthrough', 'record', 'beat', 'exceed'}
        high_weight_negative = {'crash', 'plunge', 'plummet', 'collapse', 'devastating', 'disaster'}
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 0.0, "neutral"
        
        # 计算情感分数
        positive_score = 0
        negative_score = 0
        
        for word in words:
            if word in positive_words:
                weight = 2.0 if word in high_weight_positive else 1.0
                positive_score += weight
            elif word in negative_words:
                weight = 2.0 if word in high_weight_negative else 1.0
                negative_score += weight
        
        # 百分比和数字加权
        if re.search(r'\d+%', text):
            if positive_score > negative_score:
                positive_score *= 1.3
            elif negative_score > positive_score:
                negative_score *= 1.3
        
        if re.search(r'\$\d+|\d+\.\d+[BMK]?', text):
            positive_score *= 1.1
            negative_score *= 1.1
        
        # 处理否定词
        negation_patterns = [r'\bnot\s+(\w+)', r'\bno\s+(\w+)', r'\bnever\s+(\w+)']
        for pattern in negation_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match in positive_words:
                    positive_score -= 1.5
                    negative_score += 1.0
        
        # 归一化分数
        total_words = len(words)
        normalized_positive = positive_score / total_words
        normalized_negative = negative_score / total_words
        
        polarity = (normalized_positive - normalized_negative) * 2
        polarity = max(-1.0, min(1.0, polarity))
        
        # 确定标签
        if polarity > 0.15:
            label = "positive"
        elif polarity < -0.15:
            label = "negative"
        else:
            label = "neutral"
        
        return polarity, label
    
    def analyze_sentiment(self, text: str) -> tuple[float, str]:
        """分析文本情感 - 支持算法选择"""
        method = self.analysis_method
        
        # 如果选择FinBERT但不可用，则使用备用方法
        if method == "finbert":
            if self.finbert_model is not None and self.finbert_tokenizer is not None:
                return self.analyze_sentiment_with_finbert(text)
            else:
                print("FinBERT不可用，使用轻量级分析")
                return self._lightweight_financial_analysis(text)
        
        # 如果选择轻量级，直接使用轻量级分析
        elif method == "lightweight":
            return self._lightweight_financial_analysis(text)
        
        # 自动模式：优先FinBERT，不可用则使用轻量级
        else:  # method == "auto"
            if self.finbert_model is not None and self.finbert_tokenizer is not None:
                return self.analyze_sentiment_with_finbert(text)
            else:
                return self._lightweight_financial_analysis(text)
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        try:
            from textblob import TextBlob
            blob = TextBlob(text)
            words = [word.lower() for word in blob.words if len(word) > 3]
            return list(set(words))
        except ImportError:
            # 简单的关键词提取回退方案
            import re
            words = re.findall(r'\b\w{4,}\b', text.lower())
            return list(set(words))


class NewsDatabase:
    """新闻数据库管理"""
    
    def __init__(self, db_path: str = "stock_news.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_symbol TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT,
                url TEXT UNIQUE,
                source TEXT,
                publish_time DATETIME,
                sentiment_score REAL,
                sentiment_label TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_news(self, stock_symbol: str, news: NewsItem):
        """保存新闻到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO news 
                (stock_symbol, title, content, url, source, publish_time, sentiment_score, sentiment_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (stock_symbol, news.title, news.content, news.url, news.source,
                  news.publish_time, news.sentiment_score, news.sentiment_label))
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
        finally:
            conn.close()
    
    def get_recent_news(self, stock_symbol: str, days: int = 7) -> List[Dict]:
        """获取最近几天的新闻"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days)
        cursor.execute('''
            SELECT * FROM news 
            WHERE stock_symbol = ? AND publish_time >= ?
            ORDER BY publish_time DESC
        ''', (stock_symbol, start_date))
        
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return results


class NewsCollector:
    """新闻收集器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # 根据配置初始化分析器
        use_finbert = self.config.get("analysis", {}).get("use_finbert", True)
        cache_dir = self.config.get("analysis", {}).get("model_cache_dir", "./models")
        
        self.analyzer = NewsAnalyzer(use_finbert=use_finbert, cache_dir=cache_dir)
        self.database = NewsDatabase()
    
    def fetch_alpha_vantage_news(self, symbol: str, api_key: str) -> List[NewsItem]:
        """从Alpha Vantage获取新闻"""
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'apikey': api_key,
            'limit': 50
        }
        
        news_items = []
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            if 'feed' in data:
                for item in data['feed']:
                    try:
                        publish_time = datetime.strptime(item.get('time_published', ''), '%Y%m%dT%H%M%S')
                    except:
                        publish_time = datetime.now()
                    
                    news_item = NewsItem(
                        title=item.get('title', ''),
                        content=item.get('summary', ''),
                        url=item.get('url', ''),
                        publish_time=publish_time,
                        source=item.get('source', 'Alpha Vantage')
                    )
                    
                    # 分析情感
                    sentiment_score, sentiment_label = self.analyzer.analyze_sentiment(
                        news_item.title + " " + news_item.content
                    )
                    news_item.sentiment_score = sentiment_score
                    news_item.sentiment_label = sentiment_label
                    
                    news_items.append(news_item)
                    
        except Exception as e:
            print(f"获取Alpha Vantage新闻失败: {e}")
        
        return news_items
    
    def fetch_finnhub_news(self, symbol: str, api_key: str) -> List[NewsItem]:
        """从Finnhub获取新闻"""
        url = "https://finnhub.io/api/v1/company-news"
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        to_date = datetime.now().strftime('%Y-%m-%d')
        
        params = {
            'symbol': symbol,
            'from': from_date,
            'to': to_date,
            'token': api_key
        }
        
        news_items = []
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            
            for item in data:
                news_item = NewsItem(
                    title=item.get('headline', ''),
                    content=item.get('summary', ''),
                    url=item.get('url', ''),
                    publish_time=datetime.fromtimestamp(item.get('datetime', 0)),
                    source=item.get('source', 'Finnhub')
                )
                
                # 分析情感
                sentiment_score, sentiment_label = self.analyzer.analyze_sentiment(
                    news_item.title + " " + news_item.content
                )
                news_item.sentiment_score = sentiment_score
                news_item.sentiment_label = sentiment_label
                
                news_items.append(news_item)
                
        except Exception as e:
            print(f"获取Finnhub新闻失败: {e}")
        
        return news_items


class StockNewsAnalyzer:
    """股票新闻分析主类"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config = self.load_config(config_file)
        self.collector = None
        self.running = False
        self.analyzer = NewsAnalyzer()  # 初始化分析器
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 创建默认配置
            default_config = {
                "stocks": ["AAPL", "GOOGL", "MSFT", "TSLA"],
                "api_keys": {
                    "alpha_vantage": "YOUR_ALPHA_VANTAGE_API_KEY",
                    "finnhub": "YOUR_FINNHUB_API_KEY"
                },
                "schedule": {
                    "interval_hours": 4,
                    "start_time": "09:00"
                },
                "analysis": {
                    "sentiment_threshold": 0.1,
                    "max_news_per_stock": 50
                }
            }
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            print(f"已创建默认配置文件: {config_file}")
            print("请编辑配置文件并添加您的API密钥")
            return default_config
    
    def set_analysis_method(self, method: str):
        """设置分析方法"""
        if hasattr(self, 'analyzer'):
            self.analyzer.set_analysis_method(method)
        else:
            print("分析器未初始化")
    
    def get_analysis_method(self) -> str:
        """获取当前分析方法"""
        if hasattr(self, 'analyzer'):
            return self.analyzer.get_analysis_method()
        return "auto"
    
    def collect_news_for_stock(self, symbol: str):
        """为单个股票收集新闻"""
        print(f"开始收集 {symbol} 的新闻...")
        
        # 确保collector存在
        if not self.collector:
            self.collector = NewsCollector(self.config)
        
        # 设置分析方法
        if hasattr(self, 'analyzer'):
            self.collector.analyzer.set_analysis_method(self.analyzer.get_analysis_method())
        
        all_news = []
        
        # 从Alpha Vantage收集
        if self.config["api_keys"]["alpha_vantage"] != "YOUR_ALPHA_VANTAGE_API_KEY":
            alpha_news = self.collector.fetch_alpha_vantage_news(
                symbol, self.config["api_keys"]["alpha_vantage"]
            )
            all_news.extend(alpha_news)
        
        # 从Finnhub收集
        if self.config["api_keys"]["finnhub"] != "YOUR_FINNHUB_API_KEY":
            finnhub_news = self.collector.fetch_finnhub_news(
                symbol, self.config["api_keys"]["finnhub"]
            )
            all_news.extend(finnhub_news)
        
        # 保存到数据库
        for news in all_news:
            self.collector.database.save_news(symbol, news)
        
        print(f"已为 {symbol} 收集并保存了 {len(all_news)} 条新闻")
        return all_news
    
    def run_collection_cycle(self):
        """运行一次完整的新闻收集周期"""
        self.collector = NewsCollector(self.config)
        # 设置分析方法
        if hasattr(self, 'analyzer'):
            self.collector.analyzer.set_analysis_method(self.analyzer.get_analysis_method())
        
        for symbol in self.config["stocks"]:
            self.collect_news_for_stock(symbol)
            time.sleep(1)  # 避免API限流
    
    def generate_analysis_report(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """生成分析报告"""
        database = NewsDatabase()
        recent_news = database.get_recent_news(symbol, days)
        
        if not recent_news:
            return {"error": f"没有找到 {symbol} 最近 {days} 天的新闻"}
        
        # 统计分析
        total_news = len(recent_news)
        positive_news = len([n for n in recent_news if n['sentiment_label'] == 'positive'])
        negative_news = len([n for n in recent_news if n['sentiment_label'] == 'negative'])
        neutral_news = total_news - positive_news - negative_news
        
        avg_sentiment = sum([n['sentiment_score'] for n in recent_news]) / total_news
        
        report = {
            "symbol": symbol,
            "period_days": days,
            "total_news": total_news,
            "sentiment_distribution": {
                "positive": positive_news,
                "negative": negative_news,
                "neutral": neutral_news
            },
            "average_sentiment_score": round(avg_sentiment, 3),
            "overall_sentiment": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
            "recent_headlines": [n['title'] for n in recent_news[:5]]
        }
        
        return report
    
    def start_scheduler(self):
        """启动定时任务"""
        interval_hours = self.config["schedule"]["interval_hours"]
        
        # 设置定时任务
        schedule.every(interval_hours).hours.do(self.run_collection_cycle)
        
        print(f"定时任务已启动，每 {interval_hours} 小时运行一次")
        print("按 Ctrl+C 停止程序")
        
        self.running = True
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n程序已停止")
            self.running = False
    
    def run_once(self):
        """运行一次新闻收集"""
        self.run_collection_cycle()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="股票新闻分析工具")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    parser.add_argument("--once", action="store_true", help="运行一次后退出")
    parser.add_argument("--report", type=str, help="生成指定股票代码的分析报告")
    parser.add_argument("--days", type=int, default=7, help="报告分析的天数")
    
    args = parser.parse_args()
    
    analyzer = StockNewsAnalyzer(args.config)
    
    if args.report:
        # 生成报告
        report = analyzer.generate_analysis_report(args.report, args.days)
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.once:
        # 运行一次
        analyzer.run_once()
    else:
        # 启动定时器
        analyzer.start_scheduler()


if __name__ == "__main__":
    main()