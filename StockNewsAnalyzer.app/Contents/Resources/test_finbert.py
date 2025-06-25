#!/usr/bin/env python3
"""
测试FinBERT情感分析功能
"""

from stock_news_analyzer import NewsAnalyzer

def test_sentiment_analysis():
    """测试情感分析功能"""
    
    # 测试文本
    test_texts = [
        "Apple stock surges 5% after strong quarterly earnings beat expectations",
        "Tesla shares plummet as investors worry about declining demand",
        "Microsoft reports steady revenue growth in cloud computing segment",
        "Amazon faces regulatory scrutiny over market dominance",
        "Google parent Alphabet announces new AI breakthrough"
    ]
    
    print("=== 情感分析测试 ===\n")
    
    # 测试不使用FinBERT
    print("1. 使用备用情感分析方法:")
    analyzer_fallback = NewsAnalyzer(use_finbert=False)
    
    for i, text in enumerate(test_texts, 1):
        score, label = analyzer_fallback.analyze_sentiment(text)
        print(f"{i}. {text[:50]}...")
        print(f"   情感: {label} (分数: {score:.3f})\n")
    
    print("-" * 60)
    
    # 测试使用FinBERT
    print("2. 尝试使用FinBERT:")
    analyzer_finbert = NewsAnalyzer(use_finbert=True)
    
    for i, text in enumerate(test_texts, 1):
        score, label = analyzer_finbert.analyze_sentiment(text)
        print(f"{i}. {text[:50]}...")
        print(f"   情感: {label} (分数: {score:.3f})\n")

if __name__ == "__main__":
    test_sentiment_analysis()