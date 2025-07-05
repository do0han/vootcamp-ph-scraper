#!/usr/bin/env python3
"""
Persona-based Recommendation Engine
페르소나 기반 맞춤 추천 시스템
"""

import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
from dotenv import load_dotenv

@dataclass
class PersonaProfile:
    """페르소나 프로필 정의"""
    name: str
    age_group: str
    income_level: str
    interests: List[str]
    shopping_behavior: Dict[str, Any]
    social_platforms: List[str]
    preferred_content: List[str]
    budget_range: tuple
    lifestyle: List[str]

@dataclass
class ProductRecommendation:
    """제품 추천"""
    product_name: str
    category: str
    price_range: str
    why_recommended: str
    where_to_buy: List[str]
    content_angle: str
    trending_score: int

@dataclass
class ContentIdea:
    """콘텐츠 아이디어"""
    title: str
    content_type: str
    platform: str
    hook: str
    key_points: List[str]
    call_to_action: str
    trend_connection: str

class PersonaRecommendationEngine:
    """페르소나 맞춤 추천 엔진"""
    
    def __init__(self):
        self.personas = self._define_personas()
        self.trend_data = self._get_current_trends()
    
    def _define_personas(self) -> Dict[str, PersonaProfile]:
        """타겟 페르소나 정의"""
        return {
            "young_filipina_beauty": PersonaProfile(
                name="마리아 (Young Filipina Beauty Enthusiast)",
                age_group="18-25",
                income_level="Lower-Middle",
                interests=["K-beauty", "skincare", "makeup tutorials", "affordable beauty"],
                shopping_behavior={
                    "price_sensitive": True,
                    "influenced_by_reviews": True,
                    "shops_online": True,
                    "follows_influencers": True
                },
                social_platforms=["TikTok", "Instagram", "Shopee Live"],
                preferred_content=["tutorials", "reviews", "before_after", "dupes"],
                budget_range=(200, 1500),  # PHP
                lifestyle=["student", "working_class", "social_media_active"]
            ),
            
            "young_professional_fashionista": PersonaProfile(
                name="안나 (Young Professional Fashionista)",
                age_group="25-32",
                income_level="Middle",
                interests=["sustainable fashion", "workwear", "Korean fashion", "accessories"],
                shopping_behavior={
                    "quality_focused": True,
                    "brand_conscious": True,
                    "shops_online_offline": True,
                    "values_sustainability": True
                },
                social_platforms=["Instagram", "Pinterest", "Lazada"],
                preferred_content=["styling_tips", "outfit_ideas", "brand_stories", "sustainability"],
                budget_range=(1000, 5000),  # PHP
                lifestyle=["working_professional", "environmentally_conscious", "trendy"]
            ),
            
            "kpop_enthusiast": PersonaProfile(
                name="제시카 (K-pop & Korean Culture Fan)",
                age_group="16-28",
                income_level="Lower-Middle",
                interests=["K-pop", "Korean skincare", "K-drama", "Korean food"],
                shopping_behavior={
                    "trend_follower": True,
                    "idol_influenced": True,
                    "group_buying": True,
                    "collects_merchandise": True
                },
                social_platforms=["TikTok", "Twitter", "Shopee", "Instagram"],
                preferred_content=["idol_inspired", "k_drama_looks", "korean_trends", "merchandise"],
                budget_range=(300, 2000),  # PHP
                lifestyle=["fangirl", "social_media_native", "community_oriented"]
            )
        }
    
    def _get_current_trends(self) -> Dict[str, int]:
        """현재 트렌드 데이터 가져오기"""
        try:
            load_dotenv()
            from database.supabase_client import SupabaseClient
            
            client = SupabaseClient()
            trends_data = client.get_latest_google_trends(limit=20)
            
            # 트렌드 데이터를 점수로 변환
            trend_scores = {}
            for record in trends_data:
                keyword = record.get('keyword', '')
                # 최근 데이터일수록 높은 점수
                if keyword:
                    trend_scores[keyword] = trend_scores.get(keyword, 0) + 1
            
            # 실시간 트렌드도 추가
            trend_scores.update({
                "fashion": 86,
                "makeup": 62, 
                "skincare": 25,
                "k-pop": 22,
                "food delivery": 10
            })
            
            return trend_scores
            
        except Exception as e:
            print(f"트렌드 데이터 로드 실패: {e}")
            return {"fashion": 86, "makeup": 62, "skincare": 25, "k-pop": 22}
    
    def generate_product_recommendations(self, persona_name: str) -> List[ProductRecommendation]:
        """페르소나별 제품 추천 생성"""
        persona = self.personas.get(persona_name)
        if not persona:
            return []
        
        recommendations = []
        
        if persona_name == "young_filipina_beauty":
            recommendations.extend([
                ProductRecommendation(
                    product_name="세트레티놀 나이트 세럼",
                    category="스킨케어",
                    price_range="₱299-599",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('skincare', 25)}점. 저렴하면서도 효과적인 레티놀 제품으로 TikTok에서 화제",
                    where_to_buy=["Shopee", "Lazada", "Watsons"],
                    content_angle="30일 스킨케어 챌린지 - 레티놀 첫 사용 후기",
                    trending_score=self.trend_data.get('skincare', 25)
                ),
                ProductRecommendation(
                    product_name="콜로어팝 틴티드 립밤",
                    category="메이크업",
                    price_range="₱450-650", 
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('makeup', 62)}점. 저렴한 K-beauty 듀프로 인기 급상승",
                    where_to_buy=["Beauty MNL", "Shopee", "Sephora PH"],
                    content_angle="비싼 립스틱 vs 저렴한 듀프 비교 리뷰",
                    trending_score=self.trend_data.get('makeup', 62)
                ),
                ProductRecommendation(
                    product_name="유니클로 에어리즘 UV 프로텍션 티셔츠",
                    category="패션",
                    price_range="₱590-790",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('fashion', 86)}점. 필리핀 날씨에 완벽하고 합리적인 가격",
                    where_to_buy=["Uniqlo PH", "Zalora", "Shopee"],
                    content_angle="필리핀 더위 이기는 시원한 패션 아이템 5가지",
                    trending_score=self.trend_data.get('fashion', 86)
                )
            ])
        
        elif persona_name == "young_professional_fashionista":
            recommendations.extend([
                ProductRecommendation(
                    product_name="망고 서스테이너블 블레이저",
                    category="패션",
                    price_range="₱2,999-4,500",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('fashion', 86)}점. 지속가능한 패션이면서 직장에서 입기 좋음",
                    where_to_buy=["Mango PH", "Zalora", "Lazada"],
                    content_angle="직장인을 위한 지속가능한 패션 - 1주일 코디 아이디어",
                    trending_score=self.trend_data.get('fashion', 86)
                ),
                ProductRecommendation(
                    product_name="COS 미니멀 토트백",
                    category="액세서리", 
                    price_range="₱3,500-5,500",
                    why_recommended="미니멀하면서도 실용적인 디자인으로 전문직 여성들에게 인기",
                    where_to_buy=["COS PH", "Zalora", "Rustan's"],
                    content_angle="투자 가치 있는 가방 - 10년 쓸 수 있는 백 추천",
                    trending_score=75
                )
            ])
        
        elif persona_name == "kpop_enthusiast":
            recommendations.extend([
                ProductRecommendation(
                    product_name="뉴진스 협업 한나 립 틴트",
                    category="메이크업",
                    price_range="₱899-1,200",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('k-pop', 22)}점 + {self.trend_data.get('makeup', 62)}점. 아이돌 협업 제품으로 팬들에게 필수템",
                    where_to_buy=["Shopee", "Beauty MNL", "Olive Young PH"],
                    content_angle="뉴진스 멤버별 메이크업 따라하기 - 하니 스타일",
                    trending_score=self.trend_data.get('k-pop', 22) + self.trend_data.get('makeup', 62)
                ),
                ProductRecommendation(
                    product_name="아이유 아이유어 스킨케어 세트",
                    category="스킨케어",
                    price_range="₱1,500-2,500",
                    why_recommended=f"K-pop 스타 아이유의 스킨케어 브랜드로 한국 뷰티 트렌드 반영",
                    where_to_buy=["Shopee", "Lazada", "BeautyMNL"],
                    content_angle="아이유처럼 글로우한 피부 만들기 - 30일 챌린지",
                    trending_score=self.trend_data.get('k-pop', 22) + self.trend_data.get('skincare', 25)
                )
            ])
        
        return recommendations
    
    def generate_content_ideas(self, persona_name: str) -> List[ContentIdea]:
        """페르소나별 콘텐츠 아이디어 생성"""
        persona = self.personas.get(persona_name)
        recommendations = self.generate_product_recommendations(persona_name)
        
        if not persona:
            return []
        
        content_ideas = []
        
        # 제품 추천 기반 콘텐츠
        for rec in recommendations:
            content_ideas.append(ContentIdea(
                title=rec.content_angle,
                content_type="Product Review",
                platform="TikTok" if persona.age_group.startswith("16") or persona.age_group.startswith("18") else "Instagram",
                hook=f"필리핀에서 지금 핫한 {rec.category} 아이템이 뭔지 아세요?",
                key_points=[
                    f"가격: {rec.price_range}",
                    f"추천 이유: {rec.why_recommended}",
                    f"구매처: {', '.join(rec.where_to_buy[:2])}",
                    "실제 사용 후기 포함"
                ],
                call_to_action="댓글로 여러분의 후기도 들려주세요!",
                trend_connection=f"현재 트렌딩 점수: {rec.trending_score}점"
            ))
        
        # 페르소나별 추가 콘텐츠 아이디어
        if persona_name == "young_filipina_beauty":
            content_ideas.extend([
                ContentIdea(
                    title="₱500 이하로 완성하는 데일리 메이크업",
                    content_type="Tutorial",
                    platform="TikTok",
                    hook="학생도 부담 없는 가격으로 예쁘게!",
                    key_points=[
                        "총 비용 ₱450으로 풀메이크업",
                        "Shopee, Lazada에서 쉽게 구할 수 있는 제품만",
                        "5분 안에 완성하는 스피드 메이크업",
                        "필리핀 날씨에 지워지지 않는 팁"
                    ],
                    call_to_action="여러분의 저예산 꿀템도 공유해주세요!",
                    trend_connection=f"메이크업 트렌드 점수: {self.trend_data.get('makeup', 62)}점"
                ),
                ContentIdea(
                    title="K-뷰티 vs 로컬 브랜드 블라인드 테스트",
                    content_type="Challenge",
                    platform="Instagram Reels",
                    hook="비싼 게 정말 좋을까? 직접 테스트해봤어요!",
                    key_points=[
                        "동일한 카테고리 제품 5개씩 비교",
                        "가격 공개 전 품질 평가",
                        "필리핀 여성 10명 블라인드 테스트",
                        "가성비 킹 제품 발표"
                    ],
                    call_to_action="여러분이 궁금한 브랜드 대결 댓글로 신청!",
                    trend_connection="실시간 뷰티 트렌드 반영"
                )
            ])
        
        elif persona_name == "young_professional_fashionista":
            content_ideas.extend([
                ContentIdea(
                    title="직장인을 위한 1주일 미니멀 코디",
                    content_type="Style Guide",
                    platform="Instagram",
                    hook="5벌로 15가지 룩 완성하기",
                    key_points=[
                        "기본 아이템 5개로 다양한 조합",
                        "필리핀 오피스 복장 규정 고려",
                        "에어컨 환경과 야외 온도차 대비",
                        "브랜드별 가격대 상세 정보"
                    ],
                    call_to_action="여러분의 직장 코디 노하우도 공유해주세요!",
                    trend_connection=f"패션 트렌드 점수: {self.trend_data.get('fashion', 86)}점"
                ),
                ContentIdea(
                    title="지속가능한 패션, 이제 필리핀에서도!",
                    content_type="Educational",
                    platform="Instagram Stories + Feed",
                    hook="환경도 생각하고 스타일도 살리는 패션 팁",
                    key_points=[
                        "필리핀에서 구할 수 있는 친환경 브랜드",
                        "기존 옷장 활용한 새로운 스타일링",
                        "의류 재활용 및 업사이클링 방법",
                        "장기적으로 경제적인 쇼핑 전략"
                    ],
                    call_to_action="지속가능한 패션 실천 인증샷 해시태그와 함께!",
                    trend_connection="지속가능성 트렌드 급상승"
                )
            ])
        
        elif persona_name == "kpop_enthusiast":
            content_ideas.extend([
                ContentIdea(
                    title="2025년 K-pop 아이돌 메이크업 트렌드 총정리",
                    content_type="Trend Analysis",
                    platform="TikTok",
                    hook="올해 가장 핫한 아이돌 메이크업은 이거였어!",
                    key_points=[
                        "뉴진스, 아이브, 르세라핌 시그니처 룩",
                        "아이돌별 대표 메이크업 따라하기",
                        "필리핀에서 구할 수 있는 유사 제품",
                        "각 멤버별 퍼스널 컬러 분석"
                    ],
                    call_to_action="여러분이 따라하고 싶은 아이돌 메이크업 투표!",
                    trend_connection=f"K-pop 트렌드 점수: {self.trend_data.get('k-pop', 22)}점"
                ),
                ContentIdea(
                    title="K-drama 여주인공 룩북 - 필리핀 버전",
                    content_type="Lookbook",
                    platform="Instagram + TikTok",
                    hook="드라마 속 그 옷, 필리핀에서도 입을 수 있어요!",
                    key_points=[
                        "인기 K-drama 여주인공 스타일 분석",
                        "필리핀 날씨에 맞게 변형한 코디",
                        "로컬 쇼핑몰에서 구할 수 있는 유사템",
                        "총 비용과 구매 링크 제공"
                    ],
                    call_to_action="여러분이 따라하고 싶은 드라마 캐릭터 댓글로!",
                    trend_connection="한류 문화 트렌드 지속 상승"
                )
            ])
        
        return content_ideas
    
    def generate_full_recommendation_report(self) -> Dict[str, Any]:
        """전체 추천 리포트 생성"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "trend_data": self.trend_data,
            "personas": {}
        }
        
        for persona_name in self.personas.keys():
            persona = self.personas[persona_name]
            recommendations = self.generate_product_recommendations(persona_name)
            content_ideas = self.generate_content_ideas(persona_name)
            
            report["personas"][persona_name] = {
                "profile": {
                    "name": persona.name,
                    "age_group": persona.age_group,
                    "income_level": persona.income_level,
                    "budget_range": f"₱{persona.budget_range[0]}-{persona.budget_range[1]}",
                    "main_interests": persona.interests[:3]
                },
                "product_recommendations": [
                    {
                        "product": rec.product_name,
                        "category": rec.category,
                        "price": rec.price_range,
                        "reason": rec.why_recommended,
                        "trending_score": rec.trending_score
                    } for rec in recommendations
                ],
                "content_ideas": [
                    {
                        "title": idea.title,
                        "type": idea.content_type,
                        "platform": idea.platform,
                        "hook": idea.hook
                    } for idea in content_ideas
                ]
            }
        
        return report

def main():
    """메인 실행"""
    print("🎯 PERSONA-BASED RECOMMENDATION ENGINE")
    print("=" * 70)
    print(f"⏰ 생성 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
    print()
    
    engine = PersonaRecommendationEngine()
    
    for persona_name, persona in engine.personas.items():
        print(f"👤 페르소나: {persona.name}")
        print(f"💰 예산: ₱{persona.budget_range[0]}-{persona.budget_range[1]}")
        print()
        
        # 제품 추천
        recommendations = engine.generate_product_recommendations(persona_name)
        print("🛍️ 맞춤 제품 추천:")
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec.product_name}")
            print(f"      💰 가격: {rec.price_range}")
            print(f"      📊 트렌드 점수: {rec.trending_score}점")
            print(f"      ✨ 추천 이유: {rec.why_recommended}")
            print(f"      🛒 구매처: {', '.join(rec.where_to_buy)}")
            print()
        
        # 콘텐츠 아이디어
        content_ideas = engine.generate_content_ideas(persona_name)
        print("💡 맞춤 콘텐츠 아이디어:")
        for i, idea in enumerate(content_ideas[:3], 1):  # 상위 3개만
            print(f"   {i}. {idea.title}")
            print(f"      📱 플랫폼: {idea.platform}")
            print(f"      🎣 훅: {idea.hook}")
            print(f"      📢 CTA: {idea.call_to_action}")
            print()
        
        print("=" * 70)
        print()
    
    # 전체 리포트 저장
    report = engine.generate_full_recommendation_report()
    
    with open('persona_recommendations.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print("✅ 페르소나별 맞춤 추천 리포트 생성 완료!")
    print("📁 상세 리포트: persona_recommendations.json")

if __name__ == "__main__":
    main()