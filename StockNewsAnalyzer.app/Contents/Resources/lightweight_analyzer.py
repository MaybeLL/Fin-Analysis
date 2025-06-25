#!/usr/bin/env python3
"""
轻量级金融情感分析器
不依赖transformers，使用优化的关键词和规则进行金融文本分析
"""

import re
from typing import Tuple, List

class LightweightFinancialAnalyzer:
    """轻量级金融情感分析器"""
    
    def __init__(self):
        # 金融正面词汇
        self.positive_words = {
            'bullish', 'bull', 'rally', 'surge', 'soar', 'climb', 'rise', 'gain', 'up',
            'growth', 'profit', 'earnings', 'beat', 'exceed', 'outperform', 'strong',
            'robust', 'solid', 'healthy', 'positive', 'optimistic', 'confident',
            'breakthrough', 'success', 'expansion', 'milestone', 'record', 'high',
            'upgrade', 'buy', 'overweight', 'recommend', 'target', 'upside'
        }
        
        # 金融负面词汇
        self.negative_words = {
            'bearish', 'bear', 'crash', 'plunge', 'plummet', 'fall', 'drop', 'decline',
            'loss', 'losses', 'down', 'weak', 'poor', 'disappointing', 'miss', 'below',
            'underperform', 'concern', 'worry', 'fear', 'risk', 'threat', 'challenge',
            'pressure', 'struggle', 'difficulty', 'problem', 'issue', 'negative',
            'pessimistic', 'cautious', 'downgrade', 'sell', 'underweight', 'avoid'
        }
        
        # 中性但重要的金融词汇
        self.neutral_financial = {
            'revenue', 'sales', 'earnings', 'profit', 'margin', 'guidance', 'forecast',
            'quarter', 'quarterly', 'annual', 'report', 'announce', 'statement'
        }
        
        # 加权词汇（更重要的情感指标）
        self.high_weight_positive = {
            'surge', 'soar', 'skyrocket', 'breakthrough', 'record', 'beat', 'exceed'
        }
        
        self.high_weight_negative = {
            'crash', 'plunge', 'plummet', 'collapse', 'devastating', 'disaster'
        }
    
    def extract_financial_features(self, text: str) -> dict:
        """提取金融文本特征"""
        text_lower = text.lower()
        features = {
            'has_percentage': bool(re.search(r'\d+%', text)),
            'has_numbers': bool(re.search(r'\$\d+|\d+\.\d+[BMK]?', text)),
            'has_financial_terms': any(word in text_lower for word in self.neutral_financial),
            'sentence_length': len(text.split()),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?')
        }
        return features
    
    def calculate_sentiment_score(self, text: str) -> Tuple[float, str]:
        """计算情感分数"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        # 基础分数计算
        positive_score = 0
        negative_score = 0
        
        for word in words:
            if word in self.positive_words:
                weight = 2.0 if word in self.high_weight_positive else 1.0
                positive_score += weight
            elif word in self.negative_words:
                weight = 2.0 if word in self.high_weight_negative else 1.0
                negative_score += weight
        
        # 获取文本特征
        features = self.extract_financial_features(text)
        
        # 特征调整
        if features['has_percentage']:
            # 百分比通常表明重要信息
            if positive_score > negative_score:
                positive_score *= 1.3
            elif negative_score > positive_score:
                negative_score *= 1.3
        
        if features['has_numbers']:
            # 包含数字的新闻通常更具体
            positive_score *= 1.1
            negative_score *= 1.1
        
        # 处理否定词
        negation_patterns = [
            r'\bnot\s+(\w+)', r'\bno\s+(\w+)', r'\bnever\s+(\w+)',
            r'\bdoesn\'t\s+(\w+)', r'\bwon\'t\s+(\w+)', r'\bcan\'t\s+(\w+)'
        ]
        
        for pattern in negation_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match in self.positive_words:
                    positive_score -= 1.5
                    negative_score += 1.0
                elif match in self.negative_words:
                    negative_score -= 1.5
                    positive_score += 0.5
        
        # 计算最终极性分数 (-1 到 1)
        total_words = len(words) if words else 1
        normalized_positive = positive_score / total_words
        normalized_negative = negative_score / total_words
        
        polarity = (normalized_positive - normalized_negative) * 2
        polarity = max(-1.0, min(1.0, polarity))  # 限制在[-1, 1]范围内
        
        # 确定标签
        if polarity > 0.15:
            label = "positive"
        elif polarity < -0.15:
            label = "negative"
        else:
            label = "neutral"
        
        return polarity, label
    
    def analyze_sentiment(self, text: str) -> Tuple[float, str]:
        """主要情感分析方法"""
        if not text or not text.strip():
            return 0.0, "neutral"
        
        return self.calculate_sentiment_score(text)
    
    def get_sentiment_explanation(self, text: str) -> dict:
        """获取情感分析的详细解释"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        found_positive = [w for w in words if w in self.positive_words]
        found_negative = [w for w in words if w in self.negative_words]
        features = self.extract_financial_features(text)
        polarity, label = self.analyze_sentiment(text)
        
        return {
            'polarity': polarity,
            'label': label,
            'positive_words': found_positive,
            'negative_words': found_negative,
            'features': features,
            'word_count': len(words)
        }


def test_lightweight_analyzer():
    """测试轻量级分析器"""
    analyzer = LightweightFinancialAnalyzer()
    
    test_cases = [
        "Apple stock surges 15% after beating earnings expectations by 20%",
        "Tesla shares plummet 8% as investors worry about declining demand",
        "Microsoft reports solid revenue growth of $50B in cloud segment",
        "Amazon faces regulatory scrutiny but maintains strong market position",
        "Google announces breakthrough in AI technology, stock rises 3%",
        "Oil prices crash due to oversupply concerns",
        "Market volatility continues as investors await Fed decision",
        "Strong quarterly results exceed analyst expectations",
        "Company warns of potential losses amid economic uncertainty"
    ]
    
    print("=== 轻量级金融情感分析测试 ===\n")
    
    for i, text in enumerate(test_cases, 1):
        result = analyzer.get_sentiment_explanation(text)
        
        print(f"{i}. {text}")
        print(f"   情感: {result['label']} (分数: {result['polarity']:.3f})")
        print(f"   正面词: {result['positive_words']}")
        print(f"   负面词: {result['negative_words']}")
        print(f"   特征: 百分比={result['features']['has_percentage']}, "
              f"数字={result['features']['has_numbers']}")
        print()


if __name__ == "__main__":
    test_lightweight_analyzer()