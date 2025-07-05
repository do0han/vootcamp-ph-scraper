"""
Trend Analysis and Dynamic Keyword Generation
트렌드 분석 및 동적 키워드 생성 시스템
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.persona_config import (
    TARGET_PERSONAS,
    get_trending_keywords_for_persona,
    ACTIVE_PERSONA
)

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """트렌드 분석 및 페르소나 맞춤 키워드 생성"""
    
    def __init__(self, persona_name: str = ACTIVE_PERSONA):
        self.persona_name = persona_name
        self.persona = TARGET_PERSONAS.get(persona_name)
        
        if not self.persona:
            raise ValueError(f"Unknown persona: {persona_name}")
        
        # 트렌드 가중치 설정
        self.trend_weights = {
            "rising": 2.0,      # 급상승 트렌드
            "stable": 1.5,      # 안정적 트렌드  
            "declining": 0.8,   # 하락 트렌드
            "seasonal": 1.8,    # 계절성 트렌드
            "viral": 2.5        # 바이럴 트렌드
        }
        
        logger.info(f"🔍 Trend analyzer initialized for persona: {self.persona.name}")
    
    def analyze_google_trends_data(self, trends_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Google Trends 데이터 분석"""
        try:
            analyzed_trends = {
                "rising_keywords": [],
                "stable_keywords": [],
                "persona_relevant": [],
                "seasonal_patterns": [],
                "recommendation_scores": {}
            }
            
            for trend_item in trends_data:
                keyword = trend_item.get('keyword', '')
                search_volume = trend_item.get('search_volume', 0)
                trend_type = trend_item.get('trend_type', 'unknown')
                
                # 페르소나 관련성 분석
                relevance_score = self._calculate_persona_relevance(keyword)
                
                if relevance_score > 0.3:  # 30% 이상 관련성
                    trend_analysis = {
                        "keyword": keyword,
                        "search_volume": search_volume,
                        "trend_type": trend_type,
                        "persona_relevance": relevance_score,
                        "category": self._categorize_keyword(keyword),
                        "commercial_intent": self._assess_commercial_intent(keyword)
                    }
                    
                    analyzed_trends["persona_relevant"].append(trend_analysis)
                    
                    # 트렌드 유형별 분류
                    if search_volume > 1000:  # 높은 검색량
                        if trend_type == "rising":
                            analyzed_trends["rising_keywords"].append(trend_analysis)
                        else:
                            analyzed_trends["stable_keywords"].append(trend_analysis)
            
            # 권장 점수 계산
            for trend in analyzed_trends["persona_relevant"]:
                score = self._calculate_recommendation_score(trend)
                analyzed_trends["recommendation_scores"][trend["keyword"]] = score
            
            # 정렬 (권장 점수 기준)
            analyzed_trends["persona_relevant"].sort(
                key=lambda x: analyzed_trends["recommendation_scores"].get(x["keyword"], 0),
                reverse=True
            )
            
            logger.info(f"📊 Analyzed {len(trends_data)} trends, found {len(analyzed_trends['persona_relevant'])} persona-relevant")
            
            return analyzed_trends
            
        except Exception as e:
            logger.error(f"Error analyzing trends data: {e}")
            return {"rising_keywords": [], "stable_keywords": [], "persona_relevant": [], "seasonal_patterns": [], "recommendation_scores": {}}
    
    def _calculate_persona_relevance(self, keyword: str) -> float:
        """키워드의 페르소나 관련성 점수 계산 (0-1)"""
        try:
            keyword_lower = keyword.lower()
            relevance_score = 0.0
            
            # 페르소나 관심사와 매칭
            for interest in self.persona.interests:
                interest_lower = interest.lower()
                if interest_lower in keyword_lower or keyword_lower in interest_lower:
                    relevance_score += 0.4
            
            # 페르소나 키워드와 매칭
            for persona_keyword in self.persona.keywords:
                persona_kw_lower = persona_keyword.lower()
                if persona_kw_lower in keyword_lower or keyword_lower in persona_kw_lower:
                    relevance_score += 0.3
            
            # 브랜드 매칭
            for brand in self.persona.preferred_brands:
                brand_lower = brand.lower()
                if brand_lower in keyword_lower:
                    relevance_score += 0.5
            
            # 연령대/성별 키워드 매칭
            age_keywords = ["young", "teen", "millennial", "gen z", "20s", "30s"]
            gender_keywords = ["women", "woman", "female", "girl", "ladies"]
            
            if self.persona.gender.value == "female":
                for gkw in gender_keywords:
                    if gkw in keyword_lower:
                        relevance_score += 0.2
            
            if self.persona.age_group.value in ["20-29", "30-39"]:
                for akw in age_keywords:
                    if akw in keyword_lower:
                        relevance_score += 0.2
            
            return min(1.0, relevance_score)
            
        except Exception as e:
            logger.debug(f"Error calculating persona relevance for '{keyword}': {e}")
            return 0.0
    
    def _categorize_keyword(self, keyword: str) -> str:
        """키워드 카테고리 분류"""
        keyword_lower = keyword.lower()
        
        # 카테고리 키워드 매핑
        categories = {
            "beauty": ["beauty", "makeup", "cosmetics", "skincare", "skin care", "facial", "serum", "moisturizer"],
            "fashion": ["fashion", "clothing", "outfit", "style", "dress", "shirt", "pants", "shoes"],
            "lifestyle": ["lifestyle", "wellness", "self care", "health", "fitness", "home", "decor"],
            "tech": ["phone", "smartphone", "laptop", "computer", "gadget", "electronic", "tech"],
            "food": ["food", "recipe", "cooking", "restaurant", "cafe", "snack", "drink"],
            "shopping": ["sale", "discount", "promo", "deal", "shopping", "buy", "purchase", "price"]
        }
        
        for category, keywords in categories.items():
            if any(kw in keyword_lower for kw in keywords):
                return category
        
        return "general"
    
    def _assess_commercial_intent(self, keyword: str) -> float:
        """상업적 의도 점수 계산 (0-1)"""
        keyword_lower = keyword.lower()
        
        # 상업적 의도 키워드
        high_intent = ["buy", "purchase", "price", "cheap", "affordable", "sale", "discount", "deal", "shop", "store"]
        medium_intent = ["review", "best", "top", "compare", "vs", "brand", "quality"]
        low_intent = ["what", "how", "why", "tutorial", "guide", "tips"]
        
        if any(kw in keyword_lower for kw in high_intent):
            return 0.9
        elif any(kw in keyword_lower for kw in medium_intent):
            return 0.6
        elif any(kw in keyword_lower for kw in low_intent):
            return 0.3
        else:
            return 0.5  # 중성
    
    def _calculate_recommendation_score(self, trend: Dict[str, Any]) -> float:
        """트렌드 추천 점수 계산"""
        try:
            score = 0.0
            
            # 기본 점수 (페르소나 관련성)
            score += trend["persona_relevance"] * 40
            
            # 검색량 점수 (로그 스케일)
            search_volume = trend.get("search_volume", 0)
            if search_volume > 0:
                import math
                volume_score = min(20, math.log10(search_volume) * 4)
                score += volume_score
            
            # 상업적 의도 점수
            commercial_score = trend.get("commercial_intent", 0.5) * 25
            score += commercial_score
            
            # 트렌드 유형 보너스
            trend_type = trend.get("trend_type", "stable")
            trend_bonus = self.trend_weights.get(trend_type, 1.0) * 10
            score += trend_bonus
            
            # 카테고리 보너스 (페르소나 관심사와 매칭)
            category = trend.get("category", "general")
            if category in [interest.lower() for interest in self.persona.interests[:3]]:
                score += 15
            
            return min(100, score)
            
        except Exception as e:
            logger.debug(f"Error calculating recommendation score: {e}")
            return 0.0
    
    def generate_dynamic_keywords(self, trends_data: List[Dict[str, Any]], base_categories: List[str]) -> List[str]:
        """트렌드 기반 동적 키워드 생성"""
        try:
            analyzed_trends = self.analyze_google_trends_data(trends_data)
            dynamic_keywords = []
            
            # 고점수 트렌드 키워드 추출
            top_trends = analyzed_trends["persona_relevant"][:10]  # 상위 10개
            
            for trend in top_trends:
                keyword = trend["keyword"]
                category = trend["category"]
                
                # 기본 트렌드 키워드
                dynamic_keywords.append(keyword)
                
                # 페르소나 관심사와 결합
                for interest in self.persona.interests[:3]:
                    dynamic_keywords.extend([
                        f"{keyword} {interest}",
                        f"{interest} {keyword}",
                        f"trending {interest}"
                    ])
                
                # 베이스 카테고리와 결합
                for base_cat in base_categories:
                    dynamic_keywords.extend([
                        f"{keyword} {base_cat}",
                        f"{base_cat} {keyword}"
                    ])
                
                # 가격 의식적 수정어 추가 (young_filipina 페르소나 특성)
                if self.persona_name == "young_filipina":
                    dynamic_keywords.extend([
                        f"affordable {keyword}",
                        f"budget {keyword}",
                        f"{keyword} sale"
                    ])
            
            # 중복 제거 및 길이 제한
            unique_keywords = list(set(dynamic_keywords))
            
            # 길이별 필터링 (너무 긴 키워드 제거)
            filtered_keywords = [kw for kw in unique_keywords if len(kw.split()) <= 4 and len(kw) <= 50]
            
            logger.info(f"🎯 Generated {len(filtered_keywords)} dynamic keywords from {len(trends_data)} trends")
            
            return filtered_keywords[:50]  # 최대 50개
            
        except Exception as e:
            logger.error(f"Error generating dynamic keywords: {e}")
            return []
    
    def get_seasonal_adjustments(self, current_month: int) -> Dict[str, float]:
        """계절별 키워드 가중치 조정"""
        # 필리핀 기후 고려 (건기/우기)
        seasonal_weights = {
            # 건기 (11월-4월): 더위, 자외선 차단
            11: {"sunscreen": 1.5, "whitening": 1.3, "summer": 1.2},
            12: {"holiday": 1.8, "party": 1.5, "gift": 1.4, "new year": 1.6},
            1: {"new year": 1.7, "resolution": 1.3, "detox": 1.4},
            2: {"valentine": 1.8, "romantic": 1.5, "date": 1.3},
            3: {"spring": 1.2, "fresh": 1.3, "renewal": 1.2},
            4: {"summer": 1.5, "beach": 1.4, "swimwear": 1.3},
            
            # 우기 (5월-10월): 습도, 실내 활동
            5: {"rainy": 1.2, "indoor": 1.3, "moisture": 1.4},
            6: {"back to school": 1.5, "student": 1.3},
            7: {"mid year": 1.2, "summer break": 1.4},
            8: {"back to school": 1.6, "student deals": 1.4},
            9: {"autumn": 1.1, "transition": 1.2},
            10: {"halloween": 1.3, "costume": 1.4, "spooky": 1.2}
        }
        
        return seasonal_weights.get(current_month, {})
    
    def optimize_search_strategy(self, trends_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """트렌드 기반 검색 전략 최적화"""
        try:
            analyzed_trends = self.analyze_google_trends_data(trends_data)
            current_month = datetime.now().month
            seasonal_weights = self.get_seasonal_adjustments(current_month)
            
            strategy = {
                "priority_keywords": [],
                "secondary_keywords": [],
                "avoid_keywords": [],
                "price_modifiers": [],
                "trend_modifiers": [],
                "seasonal_boost": seasonal_weights
            }
            
            # 우선순위 키워드 (고점수 트렌드)
            top_trends = analyzed_trends["persona_relevant"][:5]
            strategy["priority_keywords"] = [t["keyword"] for t in top_trends]
            
            # 보조 키워드 (중간 점수)
            mid_trends = analyzed_trends["persona_relevant"][5:15]
            strategy["secondary_keywords"] = [t["keyword"] for t in mid_trends]
            
            # 페르소나별 수정어
            if self.persona_name == "young_filipina":
                strategy["price_modifiers"] = ["affordable", "budget", "cheap", "sale", "discount"]
                strategy["trend_modifiers"] = ["viral", "trending", "popular", "tiktok famous"]
            elif self.persona_name == "urban_professional":
                strategy["price_modifiers"] = ["premium", "quality", "professional", "investment"]
                strategy["trend_modifiers"] = ["best", "top rated", "recommended", "expert choice"]
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error optimizing search strategy: {e}")
            return {"priority_keywords": [], "secondary_keywords": [], "avoid_keywords": [], "price_modifiers": [], "trend_modifiers": [], "seasonal_boost": {}}


def analyze_trends_for_persona(trends_data: List[Dict[str, Any]], persona_name: str = ACTIVE_PERSONA) -> Dict[str, Any]:
    """편의 함수: 페르소나별 트렌드 분석"""
    analyzer = TrendAnalyzer(persona_name)
    return analyzer.analyze_google_trends_data(trends_data)


def generate_persona_keywords(trends_data: List[Dict[str, Any]], base_categories: List[str], persona_name: str = ACTIVE_PERSONA) -> List[str]:
    """편의 함수: 페르소나별 동적 키워드 생성"""
    analyzer = TrendAnalyzer(persona_name)
    return analyzer.generate_dynamic_keywords(trends_data, base_categories)