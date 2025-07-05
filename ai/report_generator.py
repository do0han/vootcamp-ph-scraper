#!/usr/bin/env python3
"""
AI 기반 페르소나 맞춤형 리포트 생성 시스템
AI-Powered Persona-Targeted Report Generation System
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import re

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from config.persona_config import TARGET_PERSONAS, get_persona_filters
from database.supabase_client import SupabaseClient

logger = logging.getLogger(__name__)


class PersonaReportGenerator:
    """페르소나별 맞춤형 AI 리포트 생성기"""
    
    def __init__(self):
        self.supabase_client = None
        
        # Supabase 클라이언트 초기화
        try:
            self.supabase_client = SupabaseClient()
            logger.info("✅ Supabase client initialized for report generator")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
        
        # 시나리오별 템플릿
        self.scenario_templates = {
            "exam_period": {
                "personas": ["productivity_seeker"],
                "title": "시험 기간 집중력 향상 아이템",
                "focus": "productivity",
                "keywords": ["focus", "study", "concentration", "exam preparation"],
                "tone": "motivating"
            },
            "summer_skincare": {
                "personas": ["young_filipina"],
                "title": "여름철 피부 관리 필수템",
                "focus": "skincare",
                "keywords": ["summer", "sunscreen", "hydration", "oil control"],
                "tone": "friendly"
            },
            "work_from_home": {
                "personas": ["productivity_seeker", "urban_professional"],
                "title": "재택근무 효율성 극대화",
                "focus": "workspace",
                "keywords": ["remote work", "home office", "productivity", "ergonomic"],
                "tone": "professional"
            },
            "beauty_trends": {
                "personas": ["young_filipina", "urban_professional"],
                "title": "최신 뷰티 트렌드 & 추천템",
                "focus": "beauty",
                "keywords": ["trending", "viral", "popular", "k-beauty"],
                "tone": "trendy"
            }
        }
        
        logger.info("🤖 Persona Report Generator initialized")
    
    def get_persona_data(self, persona_name: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """특정 페르소나의 최근 수집 데이터 조회"""
        
        if not self.supabase_client:
            logger.warning("⚠️ No Supabase client available")
            return []
        
        try:
            # 최근 N일간의 페르소나 데이터 조회
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            
            query = self.supabase_client.client.table('shopee_products')\
                .select('*')\
                .contains('discount_info', {'persona_name': persona_name})\
                .gte('created_at', cutoff_date)\
                .order('created_at', desc=True)\
                .execute()
            
            products = query.data if query.data else []
            logger.info(f"📊 Retrieved {len(products)} products for {persona_name} (last {days_back} days)")
            
            return products
            
        except Exception as e:
            logger.error(f"❌ Error retrieving persona data: {e}")
            return []
    
    def analyze_products(self, products: List[Dict[str, Any]], persona_name: str) -> Dict[str, Any]:
        """제품 데이터 분석 및 인사이트 생성"""
        
        if not products:
            return {"status": "no_data", "insights": []}
        
        persona = TARGET_PERSONAS.get(persona_name)
        if not persona:
            return {"status": "invalid_persona", "insights": []}
        
        analysis = {
            "total_products": len(products),
            "avg_price": 0,
            "price_range": {"min": float('inf'), "max": 0},
            "avg_rating": 0,
            "avg_persona_score": 0,
            "top_categories": {},
            "brand_distribution": {},
            "insights": [],
            "recommendations": []
        }
        
        # 기본 통계 계산
        total_price = 0
        total_rating = 0
        total_persona_score = 0
        valid_prices = 0
        valid_ratings = 0
        valid_scores = 0
        
        for product in products:
            # 가격 분석
            price = product.get('price')
            if price and isinstance(price, (int, float)) and price > 0:
                total_price += price
                valid_prices += 1
                analysis["price_range"]["min"] = min(analysis["price_range"]["min"], price)
                analysis["price_range"]["max"] = max(analysis["price_range"]["max"], price)
            
            # 평점 분석
            rating = product.get('rating')
            if rating and isinstance(rating, (int, float)):
                total_rating += rating
                valid_ratings += 1
            
            # 페르소나 점수 분석
            discount_info = product.get('discount_info', {})
            persona_score = discount_info.get('persona_score', 0)
            if persona_score > 0:
                total_persona_score += persona_score
                valid_scores += 1
            
            # 카테고리 분포
            category = product.get('category', 'unknown')
            analysis["top_categories"][category] = analysis["top_categories"].get(category, 0) + 1
            
            # 브랜드 분포 (제품명에서 추출)
            product_name = product.get('product_name', '').lower()
            for brand in persona.preferred_brands:
                if brand.lower() in product_name:
                    analysis["brand_distribution"][brand] = analysis["brand_distribution"].get(brand, 0) + 1
                    break
        
        # 평균 계산
        if valid_prices > 0:
            analysis["avg_price"] = total_price / valid_prices
        if valid_ratings > 0:
            analysis["avg_rating"] = total_rating / valid_ratings
        if valid_scores > 0:
            analysis["avg_persona_score"] = total_persona_score / valid_scores
        
        # 가격 범위 보정
        if analysis["price_range"]["min"] == float('inf'):
            analysis["price_range"] = {"min": 0, "max": 0}
        
        # 인사이트 생성
        analysis["insights"] = self._generate_insights(analysis, persona_name)
        analysis["recommendations"] = self._generate_recommendations(analysis, persona_name)
        
        return analysis
    
    def _generate_insights(self, analysis: Dict[str, Any], persona_name: str) -> List[str]:
        """데이터 기반 인사이트 생성"""
        
        insights = []
        persona = TARGET_PERSONAS.get(persona_name)
        
        if not persona:
            return insights
        
        # 가격 인사이트
        avg_price = analysis.get("avg_price", 0)
        if avg_price > 0:
            persona_filters = get_persona_filters(persona_name)
            max_budget = persona_filters.get("max_price", 5000)
            
            if avg_price < max_budget * 0.5:
                insights.append(f"💰 평균 가격 ₱{avg_price:.0f}로 예산 친화적인 제품들이 많이 발견되었습니다.")
            elif avg_price > max_budget * 0.8:
                insights.append(f"💎 평균 가격 ₱{avg_price:.0f}로 프리미엄 제품들이 주로 수집되었습니다.")
            else:
                insights.append(f"💰 평균 가격 ₱{avg_price:.0f}로 적정 가격대의 제품들이 발견되었습니다.")
        
        # 품질 인사이트
        avg_rating = analysis.get("avg_rating", 0)
        if avg_rating >= 4.5:
            insights.append(f"⭐ 평균 평점 {avg_rating:.1f}로 매우 높은 품질의 제품들입니다.")
        elif avg_rating >= 4.0:
            insights.append(f"⭐ 평균 평점 {avg_rating:.1f}로 신뢰할 수 있는 품질의 제품들입니다.")
        
        # 페르소나 매칭 인사이트
        avg_score = analysis.get("avg_persona_score", 0)
        if avg_score >= 70:
            insights.append(f"🎯 페르소나 매칭도 {avg_score:.1f}%로 매우 적합한 제품들이 발견되었습니다.")
        elif avg_score >= 50:
            insights.append(f"🎯 페르소나 매칭도 {avg_score:.1f}%로 적합한 제품들이 수집되었습니다.")
        
        # 카테고리 인사이트
        top_categories = analysis.get("top_categories", {})
        if top_categories:
            most_popular = max(top_categories.items(), key=lambda x: x[1])
            insights.append(f"📂 '{most_popular[0]}' 카테고리에서 {most_popular[1]}개 제품이 발견되어 가장 인기가 높습니다.")
        
        # 브랜드 인사이트
        brand_dist = analysis.get("brand_distribution", {})
        if brand_dist:
            top_brand = max(brand_dist.items(), key=lambda x: x[1])
            insights.append(f"🏷️ '{top_brand[0]}' 브랜드 제품이 {top_brand[1]}개로 가장 많이 발견되었습니다.")
        
        return insights
    
    def _generate_recommendations(self, analysis: Dict[str, Any], persona_name: str) -> List[str]:
        """페르소나별 맞춤형 추천 생성"""
        
        recommendations = []
        persona = TARGET_PERSONAS.get(persona_name)
        
        if not persona:
            return recommendations
        
        # 페르소나별 맞춤 추천
        if persona_name == "young_filipina":
            recommendations.extend([
                "🌟 K-beauty 루틴에 맞는 제품들을 단계별로 사용해보세요.",
                "💡 학생 할인이나 번들 상품을 찾아보시면 더 경제적입니다.",
                "📱 TikTok에서 리뷰를 확인하고 구매하시는 것을 추천드려요."
            ])
        elif persona_name == "productivity_seeker":
            recommendations.extend([
                "📚 시험 기간에는 집중력 향상 아이템을 우선적으로 구매하세요.",
                "💻 인체공학적 제품에 투자하면 장기적으로 건강과 효율성에 도움됩니다.",
                "🔊 노이즈 캔슬링 헤드폰으로 집중 환경을 만들어보세요."
            ])
        elif persona_name == "urban_professional":
            recommendations.extend([
                "💼 업무 효율성을 높이는 프리미엄 제품에 투자해보세요.",
                "⏰ 시간 절약형 제품들로 워라밸을 개선할 수 있습니다.",
                "🏢 재택근무 환경 개선에 도움되는 아이템들을 고려해보세요."
            ])
        
        # 데이터 기반 추천
        avg_score = analysis.get("avg_persona_score", 0)
        if avg_score < 50:
            recommendations.append("🔍 더 적합한 제품을 찾기 위해 키워드를 조정해보는 것을 추천드립니다.")
        
        avg_price = analysis.get("avg_price", 0)
        persona_filters = get_persona_filters(persona_name)
        max_budget = persona_filters.get("max_price", 5000)
        
        if avg_price < max_budget * 0.3:
            recommendations.append("💰 예산에 여유가 있다면 더 높은 품질의 제품도 고려해보세요.")
        
        return recommendations
    
    def generate_scenario_report(self, scenario: str, persona_name: str) -> Dict[str, Any]:
        """시나리오별 맞춤형 리포트 생성"""
        
        if scenario not in self.scenario_templates:
            return {"error": f"Unknown scenario: {scenario}"}
        
        template = self.scenario_templates[scenario]
        
        if persona_name not in template["personas"]:
            return {"error": f"Persona {persona_name} not supported for scenario {scenario}"}
        
        # 데이터 수집
        products = self.get_persona_data(persona_name, days_back=7)
        analysis = self.analyze_products(products, persona_name)
        
        # 시나리오별 리포트 생성
        report = {
            "scenario": scenario,
            "persona": persona_name,
            "title": template["title"],
            "generated_at": datetime.now().isoformat(),
            "summary": self._generate_scenario_summary(template, analysis, persona_name),
            "analysis": analysis,
            "scenario_specific": self._generate_scenario_content(scenario, analysis, persona_name)
        }
        
        return report
    
    def _generate_scenario_summary(self, template: Dict[str, Any], analysis: Dict[str, Any], persona_name: str) -> str:
        """시나리오별 요약 생성"""
        
        total_products = analysis.get("total_products", 0)
        avg_score = analysis.get("avg_persona_score", 0)
        avg_price = analysis.get("avg_price", 0)
        
        focus = template.get("focus", "general")
        tone = template.get("tone", "friendly")
        
        if persona_name == "productivity_seeker" and focus == "productivity":
            return f"""
🎓 시험 기간을 앞둔 당신을 위한 특별한 추천!
최근 일주일간 수집된 {total_products}개의 생산성 향상 아이템들 중에서 
페르소나 매칭도 {avg_score:.1f}%의 최고 맞춤형 제품들을 선별했습니다.

평균 가격 ₱{avg_price:.0f}로 학생 예산에 적합한 아이템들이 많아
경제적 부담 없이 집중력 향상을 경험할 수 있습니다.
            """.strip()
        
        elif persona_name == "young_filipina" and focus == "beauty":
            return f"""
✨ K-beauty 트렌드를 놓치지 않는 당신을 위한 큐레이션!
최근 수집된 {total_products}개의 뷰티 아이템 중 
{avg_score:.1f}% 매칭도의 완벽한 제품들을 발견했어요.

평균 ₱{avg_price:.0f}의 합리적인 가격으로 
최신 트렌드를 따라갈 수 있는 기회입니다!
            """.strip()
        
        else:
            return f"""
{template['title']}을 위한 맞춤형 추천을 준비했습니다.
총 {total_products}개 제품을 분석하여 {avg_score:.1f}% 적합도의 
최고 품질 아이템들을 선별했습니다.
            """.strip()
    
    def _generate_scenario_content(self, scenario: str, analysis: Dict[str, Any], persona_name: str) -> Dict[str, Any]:
        """시나리오별 특화 콘텐츠 생성"""
        
        content = {}
        
        if scenario == "exam_period":
            content = {
                "focus_areas": [
                    "🧠 집중력 향상 도구",
                    "💺 인체공학적 학습 환경", 
                    "👁️ 눈 건강 보호",
                    "⏰ 시간 관리 도구"
                ],
                "study_tips": [
                    "포모도로 기법으로 25분 집중 + 5분 휴식 반복",
                    "블루라이트 차단 안경으로 눈의 피로 감소",
                    "인체공학적 의자로 장시간 학습 시 자세 유지",
                    "노이즈 캔슬링으로 최적의 집중 환경 조성"
                ],
                "urgent_items": [
                    "ergonomic chair", "blue light glasses", 
                    "study lamp", "noise cancelling headphones"
                ]
            }
        
        elif scenario == "summer_skincare":
            content = {
                "focus_areas": [
                    "☀️ UV 차단",
                    "💧 수분 공급",
                    "🧴 유분 조절",
                    "❄️ 쿨링 케어"
                ],
                "skincare_routine": [
                    "아침: 클렌징 → 토너 → 세럼 → 선크림",
                    "저녁: 더블클렌징 → 토너 → 에센스 → 모이스처라이저",
                    "주 2-3회: 수분 마스크팩으로 집중 케어",
                    "외출 후: 쿨링젤이나 알로에로 진정 케어"
                ],
                "must_have": [
                    "sunscreen", "hydrating serum",
                    "oil control toner", "cooling gel"
                ]
            }
        
        elif scenario == "work_from_home":
            content = {
                "focus_areas": [
                    "💻 워크스테이션 최적화",
                    "📞 화상회의 품질 향상",
                    "🏠 홈오피스 환경 구축",
                    "⚡ 생산성 도구"
                ],
                "productivity_tips": [
                    "듀얼 모니터로 멀티태스킹 효율성 증대",
                    "좋은 조명으로 화상회의 품질 개선",
                    "ergonomic 키보드/마우스로 손목 보호",
                    "식물이나 디퓨저로 쾌적한 업무 환경 조성"
                ],
                "essential_items": [
                    "monitor", "webcam", "ergonomic keyboard",
                    "desk lamp", "laptop stand"
                ]
            }
        
        return content
    
    def generate_daily_report(self, persona_name: str) -> Dict[str, Any]:
        """일일 페르소나 리포트 생성"""
        
        # 오늘 수집된 데이터
        today_products = self.get_persona_data(persona_name, days_back=1)
        
        # 주간 트렌드 비교
        week_products = self.get_persona_data(persona_name, days_back=7)
        
        today_analysis = self.analyze_products(today_products, persona_name)
        week_analysis = self.analyze_products(week_products, persona_name)
        
        report = {
            "type": "daily_report",
            "persona": persona_name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "today": {
                "products_found": len(today_products),
                "analysis": today_analysis
            },
            "weekly_comparison": {
                "total_products": len(week_products),
                "analysis": week_analysis,
                "trends": self._compare_trends(today_analysis, week_analysis)
            },
            "actionable_insights": self._generate_daily_insights(today_analysis, week_analysis, persona_name)
        }
        
        return report
    
    def _compare_trends(self, today: Dict[str, Any], week: Dict[str, Any]) -> Dict[str, Any]:
        """일일 vs 주간 트렌드 비교"""
        
        trends = {}
        
        # 가격 트렌드
        today_price = today.get("avg_price", 0)
        week_price = week.get("avg_price", 0)
        
        if week_price > 0:
            price_change = ((today_price - week_price) / week_price) * 100
            trends["price_trend"] = {
                "change_percent": price_change,
                "direction": "up" if price_change > 5 else "down" if price_change < -5 else "stable"
            }
        
        # 페르소나 점수 트렌드
        today_score = today.get("avg_persona_score", 0)
        week_score = week.get("avg_persona_score", 0)
        
        if week_score > 0:
            score_change = ((today_score - week_score) / week_score) * 100
            trends["relevance_trend"] = {
                "change_percent": score_change,
                "direction": "improving" if score_change > 10 else "declining" if score_change < -10 else "stable"
            }
        
        return trends
    
    def _generate_daily_insights(self, today: Dict[str, Any], week: Dict[str, Any], persona_name: str) -> List[str]:
        """일일 실행 가능한 인사이트 생성"""
        
        insights = []
        
        today_count = today.get("total_products", 0)
        week_count = week.get("total_products", 0)
        
        if today_count == 0:
            insights.append("😴 오늘은 새로운 제품이 발견되지 않았습니다. 키워드를 확장해보는 것을 고려해보세요.")
        elif today_count > week_count * 0.3:  # 30% 이상이면 활발
            insights.append(f"🔥 오늘 {today_count}개의 새로운 제품이 발견되어 활발한 하루였습니다!")
        
        # 시즌별 인사이트
        current_month = datetime.now().month
        if persona_name == "young_filipina":
            if current_month in [12, 1, 2]:  # 건기
                insights.append("☀️ 건기철이니 화이트닝과 자외선 차단 제품에 집중해보세요.")
            elif current_month in [6, 7, 8]:  # 우기
                insights.append("🌧️ 우기철이니 수분 공급과 실내 케어 제품을 찾아보세요.")
        
        elif persona_name == "productivity_seeker":
            if current_month in [3, 4, 5]:  # 봄 학기
                insights.append("📚 새 학기 시즌! 학습 환경 개선 아이템들을 점검해보세요.")
            elif current_month in [10, 11, 12]:  # 가을 학기/시험 기간
                insights.append("📖 시험 시즌 접근! 집중력 향상 도구들을 미리 준비하세요.")
        
        return insights


def main():
    """테스트 실행"""
    
    logging.basicConfig(level=logging.INFO)
    
    generator = PersonaReportGenerator()
    
    print("🤖 AI Report Generator Test")
    print("=" * 50)
    
    # Just Elias 시나리오 테스트
    print("🎓 Just Elias 시험 기간 리포트 생성...")
    exam_report = generator.generate_scenario_report("exam_period", "productivity_seeker")
    
    print(f"📊 리포트 제목: {exam_report.get('title', 'N/A')}")
    print(f"📅 생성 시간: {exam_report.get('generated_at', 'N/A')}")
    print(f"📝 요약:\n{exam_report.get('summary', 'N/A')}")
    
    # Young Filipina 일일 리포트 테스트
    print("\n" + "=" * 50)
    print("✨ Young Filipina 일일 리포트 생성...")
    daily_report = generator.generate_daily_report("young_filipina")
    
    print(f"📊 오늘 발견 제품: {daily_report['today']['products_found']}개")
    print(f"📈 주간 총 제품: {daily_report['weekly_comparison']['total_products']}개")
    
    insights = daily_report.get('actionable_insights', [])
    if insights:
        print("💡 오늘의 인사이트:")
        for insight in insights[:3]:
            print(f"  - {insight}")


if __name__ == "__main__":
    main()