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
    interests: List[Dict[str, Any]]  # 새로운 구조: [{"keyword": "workwear", "related": ["blazer", "tote bag"]}]
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
    
    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.personas = self._define_personas()
        self.trend_data = self._get_current_trends()
        self.debug_log = []  # Store debug information
        
        if self.debug_mode:
            self._debug_print("🎯 PersonaRecommendationEngine initialized in debug mode")
            self._debug_print(f"📊 Loaded {len(self.personas)} personas")
            self._debug_print(f"📈 Loaded {len(self.trend_data)} trend data points")
    
    def _define_personas(self) -> Dict[str, PersonaProfile]:
        """타겟 페르소나 정의"""
        return {
            "young_filipina_beauty": PersonaProfile(
                name="마리아 (Young Filipina Beauty Enthusiast)",
                age_group="18-25",
                income_level="Lower-Middle",
                interests=[
                    {"keyword": "K-beauty", "related": ["korean skincare", "k-skincare", "korean makeup", "korean cosmetics", "korean brand"]},
                    {"keyword": "skincare", "related": ["serum", "moisturizer", "cleanser", "toner", "sunscreen", "face mask", "retinol", "vitamin c"]},
                    {"keyword": "makeup tutorials", "related": ["makeup", "tutorial", "cosmetics", "lip tint", "foundation", "concealer", "eyeshadow", "blush"]},
                    {"keyword": "affordable beauty", "related": ["budget", "cheap", "affordable", "drugstore", "dupe", "budget-friendly"]}
                ],
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
                interests=[
                    {"keyword": "sustainable fashion", "related": ["eco-friendly", "recycled", "organic cotton", "upcycled", "ethical fashion", "green fashion", "sustainable"]},
                    {"keyword": "workwear", "related": ["blazer", "tote bag", "slacks", "office look", "shirt", "blouse", "work outfit", "professional", "business casual", "office wear"]},
                    {"keyword": "Korean fashion", "related": ["k-fashion", "hongdae style", "wide pants", "seoul fashion", "korean style", "korean brand"]},
                    {"keyword": "accessories", "related": ["bag", "handbag", "jewelry", "watch", "scarf", "belt", "purse", "wallet", "tote", "crossbody"]}
                ],
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
                interests=[
                    {"keyword": "K-pop", "related": ["idol", "korean music", "k-music", "korean idol", "boy group", "girl group", "kpop", "korean pop"]},
                    {"keyword": "Korean skincare", "related": ["k-beauty", "korean cosmetics", "korean makeup", "korean brand", "skincare", "k-skincare"]},
                    {"keyword": "K-drama", "related": ["korean drama", "kdrama", "korean series", "korean actor", "korean actress", "korean show"]},
                    {"keyword": "Korean food", "related": ["korean cuisine", "k-food", "korean restaurant", "korean snack", "kimchi", "ramen", "korean cooking"]}
                ],
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
    
    def _debug_print(self, message: str):
        """Print debug message and store in log"""
        if self.debug_mode:
            print(f"🔍 {message}")
            self.debug_log.append(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def _fuzzy_match(self, keyword: str, text: str) -> bool:
        """Enhanced matching for better keyword detection"""
        # 특별한 매칭 규칙들
        special_matches = {
            "skincare": ["스킨케어", "세럼", "retinol", "레티놀"],
            "makeup": ["메이크업", "립밤", "lip", "틴트", "tint"],
            "tote bag": ["토트백", "토트 백", "bag"],
            "blazer": ["블레이저"],
            "sustainable": ["서스테이너블", "지속가능"],
            "korean": ["한국", "코리안", "k-"],
            "accessories": ["액세서리", "가방", "bag"]
        }
        
        # 특별 매칭 규칙 확인
        for match_keyword, variants in special_matches.items():
            if keyword in match_keyword or match_keyword in keyword:
                for variant in variants:
                    if variant in text:
                        return True
        
        return False
    
    def _calculate_product_score(self, product_name: str, category: str, persona: PersonaProfile) -> Dict[str, Any]:
        """Calculate detailed scoring for product recommendations"""
        scoring_details = {
            "product_name": product_name,
            "category": category,
            "base_score": 0,
            "trend_boost": 0,
            "persona_match": 0,
            "interest_alignment": 0,
            "platform_match": 0,
            "budget_compatibility": 0,
            "final_score": 0,
            "scoring_breakdown": []
        }
        
        # Base score (30 points max)
        base_score = 30
        scoring_details["base_score"] = base_score
        scoring_details["scoring_breakdown"].append(f"Base product score: +{base_score}")
        
        # Trend boost based on category (25 points max)
        trend_boost = 0
        category_lower = category.lower()
        matched_trends = []
        
        for trend_keyword, trend_score in self.trend_data.items():
            keyword_lower = trend_keyword.lower()
            # Check for category-trend matches
            if (keyword_lower in category_lower or 
                category_lower in keyword_lower or
                (category_lower == "메이크업" and keyword_lower == "makeup") or
                (category_lower == "makeup" and keyword_lower == "makeup") or
                (category_lower == "스킨케어" and keyword_lower == "skincare") or
                (category_lower == "skincare" and keyword_lower == "skincare") or
                (category_lower == "패션" and keyword_lower == "fashion") or
                (category_lower == "fashion" and keyword_lower == "fashion")):
                # Scale trend score to max 25 points (trend scores are typically 0-100)
                boost = min(25, int(trend_score * 0.25))
                trend_boost += boost
                matched_trends.append(f"{trend_keyword}({trend_score})")
        
        trend_boost = min(25, trend_boost)
        scoring_details["trend_boost"] = trend_boost
        
        if matched_trends:
            scoring_details["scoring_breakdown"].append(f"Trend boost ({', '.join(matched_trends)}): +{trend_boost}")
        else:
            scoring_details["scoring_breakdown"].append(f"Trend boost (no matches): +{trend_boost}")
        
        # Smart Interest Alignment (20 points max)
        interest_score = 0
        matching_interests = []
        matched_interest_categories = set()  # 중복 점수 방지
        
        # 상품명과 카테고리를 소문자로 변환하여 검색 대상 텍스트 준비
        search_text = f"{product_name.lower()} {category_lower}".strip()
        
        if self.debug_mode:
            self._debug_print(f"   🔎 Smart Interest Matching for: {product_name}")
            self._debug_print(f"      Search text: '{search_text}'")
        
        for interest_obj in persona.interests:
            keyword = interest_obj["keyword"]
            related_keywords = interest_obj["related"]
            
            # 해당 관심사 카테고리가 이미 매칭되었는지 확인
            if keyword in matched_interest_categories:
                continue
            
            match_found = False
            matched_keyword = None
            
            # 1. 메인 키워드 확인 (부분 문자열 매칭 포함)
            keyword_lower = keyword.lower()
            if (keyword_lower in search_text or 
                any(part in search_text for part in keyword_lower.split()) or
                self._fuzzy_match(keyword_lower, search_text)):
                match_found = True
                matched_keyword = keyword
                if self.debug_mode:
                    self._debug_print(f"      ✓ Main keyword match: '{keyword}'")
            
            # 2. 관련 키워드 확인 (향상된 매칭)
            if not match_found:
                for related in related_keywords:
                    related_lower = related.lower()
                    if (related_lower in search_text or 
                        any(part in search_text for part in related_lower.split()) or
                        self._fuzzy_match(related_lower, search_text)):
                        match_found = True
                        matched_keyword = related
                        if self.debug_mode:
                            self._debug_print(f"      ✓ Related keyword match: '{related}' for '{keyword}'")
                        break
            
            # 매칭이 발견되면 점수 부여 (관심사당 8점)
            if match_found:
                interest_score += 8
                matching_interests.append(f"{keyword} -> {matched_keyword}")
                matched_interest_categories.add(keyword)
                
                if self.debug_mode:
                    self._debug_print(f"      🎯 Interest match: {keyword} -> {matched_keyword} (+8 points)")
        
        interest_score = min(20, interest_score)
        scoring_details["interest_alignment"] = interest_score
        
        if matching_interests:
            scoring_details["scoring_breakdown"].append(f"Interest alignment ({', '.join(matching_interests)}): +{interest_score}")
            if self.debug_mode:
                self._debug_print(f"      📊 Total interest score: +{interest_score}")
        else:
            scoring_details["scoring_breakdown"].append(f"Interest alignment (no matches): +{interest_score}")
            if self.debug_mode:
                self._debug_print(f"      ❌ No interest matches found")
        
        # Platform compatibility (15 points max)
        platform_score = 0
        if category_lower in ["beauty", "makeup", "skincare"] and "TikTok" in persona.social_platforms:
            platform_score += 8
            scoring_details["scoring_breakdown"].append("Platform match (TikTok + Beauty): +8")
        elif category_lower in ["fashion", "accessories"] and "Instagram" in persona.social_platforms:
            platform_score += 8
            scoring_details["scoring_breakdown"].append("Platform match (Instagram + Fashion): +8")
        
        if "Shopee" in persona.social_platforms or "Lazada" in persona.social_platforms:
            platform_score += 7
            scoring_details["scoring_breakdown"].append("E-commerce platform familiarity: +7")
        
        platform_score = min(15, platform_score)
        scoring_details["platform_match"] = platform_score
        
        # Budget compatibility (10 points max)
        budget_score = 10  # Assume compatible unless we have specific price data
        scoring_details["budget_compatibility"] = budget_score
        scoring_details["scoring_breakdown"].append(f"Budget compatibility: +{budget_score}")
        
        # Calculate final score
        final_score = base_score + trend_boost + interest_score + platform_score + budget_score
        scoring_details["final_score"] = final_score
        
        if self.debug_mode:
            self._debug_print(f"📊 Product Scoring: {product_name}")
            self._debug_print(f"   Category: {category} | Persona: {persona.name}")
            for breakdown in scoring_details["scoring_breakdown"]:
                self._debug_print(f"   • {breakdown}")
            self._debug_print(f"   🎯 Final Score: {final_score}/100")
            self._debug_print("")
        
        return scoring_details
    
    def generate_product_recommendations(self, persona_name: str) -> List[ProductRecommendation]:
        """페르소나별 제품 추천 생성"""
        persona = self.personas.get(persona_name)
        if not persona:
            return []
        
        if self.debug_mode:
            self._debug_print(f"🎯 Generating product recommendations for: {persona.name}")
            self._debug_print(f"   Age Group: {persona.age_group}")
            self._debug_print(f"   Budget Range: ₱{persona.budget_range[0]}-{persona.budget_range[1]}")
            # 새로운 구조에 맞게 관심사 표시
            interest_keywords = [interest["keyword"] for interest in persona.interests[:3]]
            self._debug_print(f"   Key Interests: {', '.join(interest_keywords)}")
            self._debug_print("")
        
        recommendations = []
        
        if persona_name == "young_filipina_beauty":
            # Calculate scores for each product
            product_1_scoring = self._calculate_product_score("세트레티놀 나이트 세럼", "스킨케어", persona)
            product_2_scoring = self._calculate_product_score("콜로어팝 틴티드 립밤", "메이크업", persona)
            product_3_scoring = self._calculate_product_score("유니클로 에어리즘 UV 프로텍션 티셔츠", "패션", persona)
            
            recommendations.extend([
                ProductRecommendation(
                    product_name="세트레티놀 나이트 세럼",
                    category="스킨케어",
                    price_range="₱299-599",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('skincare', 25)}점. 저렴하면서도 효과적인 레티놀 제품으로 TikTok에서 화제",
                    where_to_buy=["Shopee", "Lazada", "Watsons"],
                    content_angle="30일 스킨케어 챌린지 - 레티놀 첫 사용 후기",
                    trending_score=product_1_scoring["final_score"]
                ),
                ProductRecommendation(
                    product_name="콜로어팝 틴티드 립밤",
                    category="메이크업",
                    price_range="₱450-650", 
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('makeup', 62)}점. 저렴한 K-beauty 듀프로 인기 급상승",
                    where_to_buy=["Beauty MNL", "Shopee", "Sephora PH"],
                    content_angle="비싼 립스틱 vs 저렴한 듀프 비교 리뷰",
                    trending_score=product_2_scoring["final_score"]
                ),
                ProductRecommendation(
                    product_name="유니클로 에어리즘 UV 프로텍션 티셔츠",
                    category="패션",
                    price_range="₱590-790",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('fashion', 86)}점. 필리핀 날씨에 완벽하고 합리적인 가격",
                    where_to_buy=["Uniqlo PH", "Zalora", "Shopee"],
                    content_angle="필리핀 더위 이기는 시원한 패션 아이템 5가지",
                    trending_score=product_3_scoring["final_score"]
                )
            ])
        
        elif persona_name == "young_professional_fashionista":
            # Calculate scores for each product
            product_1_scoring = self._calculate_product_score("망고 서스테이너블 블레이저", "패션", persona)
            product_2_scoring = self._calculate_product_score("COS 미니멀 토트백", "액세서리", persona)
            
            recommendations.extend([
                ProductRecommendation(
                    product_name="망고 서스테이너블 블레이저",
                    category="패션",
                    price_range="₱2,999-4,500",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('fashion', 86)}점. 지속가능한 패션이면서 직장에서 입기 좋음",
                    where_to_buy=["Mango PH", "Zalora", "Lazada"],
                    content_angle="직장인을 위한 지속가능한 패션 - 1주일 코디 아이디어",
                    trending_score=product_1_scoring["final_score"]
                ),
                ProductRecommendation(
                    product_name="COS 미니멀 토트백",
                    category="액세서리", 
                    price_range="₱3,500-5,500",
                    why_recommended="미니멀하면서도 실용적인 디자인으로 전문직 여성들에게 인기",
                    where_to_buy=["COS PH", "Zalora", "Rustan's"],
                    content_angle="투자 가치 있는 가방 - 10년 쓸 수 있는 백 추천",
                    trending_score=product_2_scoring["final_score"]
                )
            ])
        
        elif persona_name == "kpop_enthusiast":
            # Calculate scores for each product
            product_1_scoring = self._calculate_product_score("뉴진스 협업 한나 립 틴트", "메이크업", persona)
            product_2_scoring = self._calculate_product_score("아이유 아이유어 스킨케어 세트", "스킨케어", persona)
            
            recommendations.extend([
                ProductRecommendation(
                    product_name="뉴진스 협업 한나 립 틴트",
                    category="메이크업",
                    price_range="₱899-1,200",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('k-pop', 22)}점 + {self.trend_data.get('makeup', 62)}점. 아이돌 협업 제품으로 팬들에게 필수템",
                    where_to_buy=["Shopee", "Beauty MNL", "Olive Young PH"],
                    content_angle="뉴진스 멤버별 메이크업 따라하기 - 하니 스타일",
                    trending_score=product_1_scoring["final_score"]
                ),
                ProductRecommendation(
                    product_name="아이유 아이유어 스킨케어 세트",
                    category="스킨케어",
                    price_range="₱1,500-2,500",
                    why_recommended=f"K-pop 스타 아이유의 스킨케어 브랜드로 한국 뷰티 트렌드 반영",
                    where_to_buy=["Shopee", "Lazada", "BeautyMNL"],
                    content_angle="아이유처럼 글로우한 피부 만들기 - 30일 챌린지",
                    trending_score=product_2_scoring["final_score"]
                )
            ])
        
        return recommendations
    
    def generate_content_ideas(self, persona_name: str) -> List[ContentIdea]:
        """페르소나별 콘텐츠 아이디어 생성"""
        persona = self.personas.get(persona_name)
        recommendations = self.generate_product_recommendations(persona_name)
        
        if not persona:
            return []
        
        if self.debug_mode:
            self._debug_print(f"💡 Generating content ideas for: {persona.name}")
            self._debug_print(f"   Platform preferences: {', '.join(persona.social_platforms)}")
            self._debug_print(f"   Content types: {', '.join(persona.preferred_content)}")
            # 관심사 키워드 표시
            interest_keywords = [interest["keyword"] for interest in persona.interests]
            self._debug_print(f"   Interest keywords: {', '.join(interest_keywords)}")
            self._debug_print("")
        
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
        if self.debug_mode:
            self._debug_print("📋 Generating full recommendation report...")
            self._debug_print("")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "debug_mode": self.debug_mode,
            "trend_data": self.trend_data,
            "personas": {}
        }
        
        if self.debug_mode:
            report["debug_log"] = self.debug_log.copy()
        
        for persona_name in self.personas.keys():
            if self.debug_mode:
                print(f"\n{'='*60}")
                print(f"👤 PERSONA ANALYSIS: {self.personas[persona_name].name}")
                print(f"{'='*60}")
            
            persona = self.personas[persona_name]
            recommendations = self.generate_product_recommendations(persona_name)
            content_ideas = self.generate_content_ideas(persona_name)
            
            # Calculate persona statistics
            total_score = sum(rec.trending_score for rec in recommendations)
            avg_score = total_score / len(recommendations) if recommendations else 0
            high_score_products = [rec for rec in recommendations if rec.trending_score >= 70]
            
            if self.debug_mode:
                self._debug_print(f"📊 Persona Summary Statistics:")
                self._debug_print(f"   Total Products: {len(recommendations)}")
                self._debug_print(f"   Average Score: {avg_score:.1f}/100")
                self._debug_print(f"   High Score Products (≥70): {len(high_score_products)}")
                self._debug_print(f"   Content Ideas Generated: {len(content_ideas)}")
                self._debug_print("")
            
            report["personas"][persona_name] = {
                "profile": {
                    "name": persona.name,
                    "age_group": persona.age_group,
                    "income_level": persona.income_level,
                    "budget_range": f"₱{persona.budget_range[0]}-{persona.budget_range[1]}",
                    "main_interests": [interest["keyword"] for interest in persona.interests[:3]]
                },
                "statistics": {
                    "total_products": len(recommendations),
                    "average_score": round(avg_score, 1),
                    "high_score_products": len(high_score_products),
                    "content_ideas_count": len(content_ideas)
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
        
        if self.debug_mode:
            print(f"\n{'='*80}")
            print("🎯 TRANSPARENCY REPORT SUMMARY")
            print(f"{'='*80}")
            print(f"📊 Total Personas Analyzed: {len(self.personas)}")
            print(f"📈 Total Trend Keywords Used: {len(self.trend_data)}")
            
            total_products = sum(len(persona_data["product_recommendations"]) for persona_data in report["personas"].values())
            total_content = sum(len(persona_data["content_ideas"]) for persona_data in report["personas"].values())
            
            print(f"🛍️ Total Product Recommendations: {total_products}")
            print(f"💡 Total Content Ideas: {total_content}")
            print(f"🔍 Debug Log Entries: {len(self.debug_log)}")
            print(f"⏰ Report Generated: {report['generated_at']}")
            print(f"{'='*80}")
        
        return report

    def _map_user_interests_to_keywords(self, user_interests: List[str]) -> List[Dict[str, Any]]:
        """사용자 관심사를 내부 키워드 구조로 매핑"""
        # 관심사별 관련 키워드 매핑
        interest_mapping = {
            "vintage camera": {
                "keyword": "vintage photography",
                "related": ["camera", "vintage", "photography", "film", "analog", "retro camera", "vintage equipment"]
            },
            "specialty coffee": {
                "keyword": "specialty coffee", 
                "related": ["coffee", "cafe", "specialty", "brewing", "espresso", "latte", "coffee beans", "barista"]
            },
            "book reviews": {
                "keyword": "book reviews",
                "related": ["book", "review", "reading", "literature", "novel", "bestseller", "bookworm", "reading list"]
            },
            "slow living": {
                "keyword": "slow living",
                "related": ["minimalist", "slow", "mindful", "sustainable", "wellness", "simple living", "mindfulness"]
            },
            "sustainable fashion": {
                "keyword": "sustainable fashion",
                "related": ["eco-friendly", "recycled", "organic cotton", "upcycled", "ethical fashion", "green fashion", "sustainable"]
            },
            "workwear": {
                "keyword": "workwear",
                "related": ["blazer", "tote bag", "slacks", "office look", "shirt", "blouse", "work outfit", "professional", "business casual", "office wear"]
            },
            "korean fashion": {
                "keyword": "Korean fashion",
                "related": ["k-fashion", "hongdae style", "wide pants", "seoul fashion", "korean style", "korean brand"]
            },
            "accessories": {
                "keyword": "accessories",
                "related": ["bag", "handbag", "jewelry", "watch", "scarf", "belt", "purse", "wallet", "tote", "crossbody"]
            },
            "k-beauty": {
                "keyword": "K-beauty",
                "related": ["korean skincare", "k-skincare", "korean makeup", "korean cosmetics", "korean brand"]
            },
            "skincare": {
                "keyword": "skincare",
                "related": ["serum", "moisturizer", "cleanser", "toner", "sunscreen", "face mask", "retinol", "vitamin c"]
            },
            "makeup": {
                "keyword": "makeup tutorials",
                "related": ["makeup", "tutorial", "cosmetics", "lip tint", "foundation", "concealer", "eyeshadow", "blush"]
            },
            "k-pop": {
                "keyword": "K-pop",
                "related": ["idol", "korean music", "k-music", "korean idol", "boy group", "girl group", "kpop", "korean pop"]
            },
            "k-drama": {
                "keyword": "K-drama", 
                "related": ["korean drama", "kdrama", "korean series", "korean actor", "korean actress", "korean show"]
            },
            "korean food": {
                "keyword": "Korean food",
                "related": ["korean cuisine", "k-food", "korean restaurant", "korean snack", "kimchi", "ramen", "korean cooking"]
            }
        }
        
        mapped_interests = []
        for interest in user_interests:
            interest_lower = interest.lower()
            
            # 정확한 매치 찾기
            if interest_lower in interest_mapping:
                mapped_interests.append(interest_mapping[interest_lower])
            else:
                # 부분 매치 찾기
                found = False
                for key, value in interest_mapping.items():
                    if interest_lower in key or key in interest_lower:
                        mapped_interests.append(value)
                        found = True
                        break
                
                # 매치되지 않으면 일반적인 구조로 추가
                if not found:
                    mapped_interests.append({
                        "keyword": interest,
                        "related": [interest.lower(), interest.replace(" ", "")]
                    })
        
        return mapped_interests
    
    def _create_persona_from_dict(self, user_data: Dict[str, Any]) -> PersonaProfile:
        """사용자 데이터 딕셔너리에서 PersonaProfile 객체 생성"""
        # MBTI별 기본 특성 매핑
        mbti_traits = {
            "INFJ": {
                "shopping_behavior": {"quality_focused": True, "research_oriented": True, "values_authenticity": True},
                "preferred_content": ["in_depth_reviews", "tutorials", "brand_stories"],
                "personality_traits": ["introspective", "value-driven", "perfectionist"]
            },
            "ENFP": {
                "shopping_behavior": {"trend_follower": True, "influenced_by_reviews": True, "spontaneous": True},
                "preferred_content": ["trends", "lifestyle", "inspiration"],
                "personality_traits": ["enthusiastic", "creative", "social"]
            },
            "INTJ": {
                "shopping_behavior": {"efficiency_focused": True, "quality_over_quantity": True, "research_oriented": True},
                "preferred_content": ["detailed_analysis", "comparisons", "long_term_value"],
                "personality_traits": ["strategic", "independent", "quality-focused"]
            },
            "ESFP": {
                "shopping_behavior": {"trend_follower": True, "social_influenced": True, "spontaneous": True},
                "preferred_content": ["trends", "social_proof", "entertainment"],
                "personality_traits": ["spontaneous", "social", "fun-loving"]
            }
        }
        
        # 예산 레벨 매핑
        budget_mapping = {
            "low": (200, 1500),
            "medium": (1000, 5000), 
            "high": (3000, 15000)
        }
        
        # 채널 카테고리별 소셜 플랫폼 매핑
        platform_mapping = {
            "Tech": ["YouTube", "Instagram", "Twitter"],
            "Fashion": ["Instagram", "Pinterest", "TikTok"],
            "Food/Travel": ["Instagram", "YouTube", "TikTok"],
            "Beauty": ["TikTok", "Instagram", "YouTube"],
            "Lifestyle": ["Instagram", "Pinterest", "YouTube"]
        }
        
        mbti = user_data.get("mbti", "INFJ")
        channel_category = user_data.get("channel_category", "Lifestyle")
        budget_level = user_data.get("budget_level", "medium")
        user_interests = user_data.get("interests", [])
        
        # MBTI 특성 가져오기
        traits = mbti_traits.get(mbti, mbti_traits["INFJ"])
        
        # 관심사 매핑
        mapped_interests = self._map_user_interests_to_keywords(user_interests)
        
        # PersonaProfile 생성
        persona = PersonaProfile(
            name=f"Custom User ({mbti})",
            age_group="25-35",  # 기본값
            income_level="Middle",  # 예산 레벨에 따라 조정 가능
            interests=mapped_interests,
            shopping_behavior=traits["shopping_behavior"],
            social_platforms=platform_mapping.get(channel_category, ["Instagram", "YouTube"]),
            preferred_content=traits["preferred_content"],
            budget_range=budget_mapping.get(budget_level, (1000, 5000)),
            lifestyle=traits["personality_traits"] + [f"{channel_category.lower()}_focused"]
        )
        
        if self.debug_mode:
            self._debug_print(f"🎯 Custom persona created: {persona.name}")
            self._debug_print(f"   MBTI: {mbti} | Channel: {channel_category} | Budget: {budget_level}")
            self._debug_print(f"   Interests: {[i['keyword'] for i in mapped_interests]}")
            self._debug_print(f"   Platforms: {persona.social_platforms}")
            self._debug_print("")
        
        return persona

    def generate_custom_recommendation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 맞춤 추천 생성 (API용 메인 함수)"""
        if self.debug_mode:
            self._debug_print("🚀 Starting Custom Recommendation Generation")
            self._debug_print(f"   User Data: {user_data}")
        
        # 사용자 데이터에서 페르소나 생성
        custom_persona = self._create_persona_from_dict(user_data)
        
        # 맞춤 제품 추천 생성
        recommendations = self._generate_custom_product_recommendations(custom_persona)
        
        # 맞춤 콘텐츠 아이디어 생성
        content_ideas = self._generate_custom_content_ideas(custom_persona, recommendations)
        
        # 리포트 생성
        report = self._create_custom_report(custom_persona, recommendations, content_ideas, user_data)
        
        if self.debug_mode:
            self._debug_print(f"✅ Custom recommendation completed")
            self._debug_print(f"   Generated {len(recommendations)} products and {len(content_ideas)} content ideas")
        
        return report

    def _generate_custom_product_recommendations(self, persona: PersonaProfile) -> List[ProductRecommendation]:
        """맞춤 페르소나를 위한 제품 추천 생성"""
        if self.debug_mode:
            self._debug_print(f"🛍️ Generating custom product recommendations")
            self._debug_print(f"   Budget range: ₱{persona.budget_range[0]}-{persona.budget_range[1]}")
        
        recommendations = []
        
        # 관심사 기반 제품 매칭 
        interest_keywords = [interest["keyword"].lower() for interest in persona.interests]
        
        # 패션/액세서리 관련 제품들
        if any(keyword in interest for interest in interest_keywords for keyword in ["fashion", "workwear", "accessories", "sustainable"]):
            if persona.budget_range[1] >= 3000:  # 중상위 예산
                product_scoring = self._calculate_product_score("망고 서스테이너블 블레이저", "패션", persona)
                recommendations.append(ProductRecommendation(
                    product_name="망고 서스테이너블 블레이저",
                    category="패션",
                    price_range="₱2,999-4,500",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('fashion', 86)}점. 지속가능한 패션이면서 직장에서 입기 좋음",
                    where_to_buy=["Mango PH", "Zalora", "Lazada"],
                    content_angle="직장인을 위한 지속가능한 패션 - 1주일 코디 아이디어",
                    trending_score=product_scoring["final_score"]
                ))
                
                bag_scoring = self._calculate_product_score("COS 미니멀 토트백", "액세서리", persona)
                recommendations.append(ProductRecommendation(
                    product_name="COS 미니멀 토트백", 
                    category="액세서리",
                    price_range="₱3,500-5,500",
                    why_recommended="미니멀하면서도 실용적인 디자인으로 전문직 여성들에게 인기",
                    where_to_buy=["COS PH", "Zalora", "Rustan's"],
                    content_angle="투자 가치 있는 가방 - 10년 쓸 수 있는 백 추천",
                    trending_score=bag_scoring["final_score"]
                ))
            else:  # 저예산
                shirt_scoring = self._calculate_product_score("유니클로 에어리즘 UV 프로텍션 티셔츠", "패션", persona)
                recommendations.append(ProductRecommendation(
                    product_name="유니클로 에어리즘 UV 프로텍션 티셔츠",
                    category="패션", 
                    price_range="₱590-790",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('fashion', 86)}점. 필리핀 날씨에 완벽하고 합리적인 가격",
                    where_to_buy=["Uniqlo PH", "Zalora", "Shopee"],
                    content_angle="필리핀 더위 이기는 시원한 패션 아이템 5가지",
                    trending_score=shirt_scoring["final_score"]
                ))
        
        # 뷰티/스킨케어 관련 제품들
        if any(keyword in interest for interest in interest_keywords for keyword in ["beauty", "skincare", "makeup", "k-beauty"]):
            serum_scoring = self._calculate_product_score("세트레티놀 나이트 세럼", "스킨케어", persona)
            recommendations.append(ProductRecommendation(
                product_name="세트레티놀 나이트 세럼",
                category="스킨케어",
                price_range="₱299-599", 
                why_recommended=f"트렌드 스코어 {self.trend_data.get('skincare', 25)}점. 저렴하면서도 효과적인 레티놀 제품으로 TikTok에서 화제",
                where_to_buy=["Shopee", "Lazada", "Watsons"],
                content_angle="30일 스킨케어 챌린지 - 레티놀 첫 사용 후기",
                trending_score=serum_scoring["final_score"]
            ))
            
            if persona.budget_range[1] >= 800:
                lip_scoring = self._calculate_product_score("콜로어팝 틴티드 립밤", "메이크업", persona)
                recommendations.append(ProductRecommendation(
                    product_name="콜로어팝 틴티드 립밤",
                    category="메이크업",
                    price_range="₱450-650",
                    why_recommended=f"트렌드 스코어 {self.trend_data.get('makeup', 62)}점. 저렴한 K-beauty 듀프로 인기 급상승",
                    where_to_buy=["Beauty MNL", "Shopee", "Sephora PH"],
                    content_angle="비싼 립스틱 vs 저렴한 듀프 비교 리뷰",
                    trending_score=lip_scoring["final_score"]
                ))
        
        # K-pop/Korean culture 관련 제품들  
        if any(keyword in interest for interest in interest_keywords for keyword in ["k-pop", "korean", "k-drama"]):
            kpop_scoring = self._calculate_product_score("뉴진스 협업 한나 립 틴트", "메이크업", persona)
            recommendations.append(ProductRecommendation(
                product_name="뉴진스 협업 한나 립 틴트",
                category="메이크업",
                price_range="₱899-1,200",
                why_recommended=f"트렌드 스코어 {self.trend_data.get('k-pop', 22)}점 + {self.trend_data.get('makeup', 62)}점. 아이돌 협업 제품으로 팬들에게 필수템",
                where_to_buy=["Shopee", "Beauty MNL", "Olive Young PH"],
                content_angle="뉴진스 멤버별 메이크업 따라하기 - 하니 스타일",
                trending_score=kpop_scoring["final_score"]
            ))
        
        # 관심사가 없거나 특별한 취향인 경우 기본 추천
        if not recommendations:
            default_scoring = self._calculate_product_score("유니클로 에어리즘 UV 프로텍션 티셔츠", "패션", persona)  
            recommendations.append(ProductRecommendation(
                product_name="유니클로 에어리즘 UV 프로텍션 티셔츠",
                category="패션",
                price_range="₱590-790",
                why_recommended="필리핀 날씨에 적합한 기본 아이템",
                where_to_buy=["Uniqlo PH", "Zalora", "Shopee"],
                content_angle="필리핀 생활 필수템 - 실용적인 옷차림",
                trending_score=default_scoring["final_score"]
            ))
        
        if self.debug_mode:
            for rec in recommendations:
                self._debug_print(f"   📦 {rec.product_name} (Score: {rec.trending_score})")
        
        return recommendations

    def _generate_custom_content_ideas(self, persona: PersonaProfile, recommendations: List[ProductRecommendation]) -> List[ContentIdea]:
        """맞춤 페르소나를 위한 콘텐츠 아이디어 생성"""
        if self.debug_mode:
            self._debug_print(f"💡 Generating custom content ideas")
            self._debug_print(f"   Target platforms: {persona.social_platforms}")
        
        content_ideas = []
        
        # 제품 기반 콘텐츠 아이디어
        for rec in recommendations:
            primary_platform = persona.social_platforms[0] if persona.social_platforms else "Instagram"
            
            content_ideas.append(ContentIdea(
                title=rec.content_angle,
                content_type="Product Review",
                platform=primary_platform,
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
        
        # 관심사 기반 콘텐츠 아이디어
        interest_keywords = [interest["keyword"] for interest in persona.interests[:2]]
        for interest in interest_keywords:
            platform = persona.social_platforms[0] if persona.social_platforms else "Instagram"
            
            content_ideas.append(ContentIdea(
                title=f"{interest} 트렌드 분석 - 2025년 주목할 점",
                content_type="Trend Analysis",
                platform=platform,
                hook=f"{interest}에 관심 있다면 놓치면 안 될 이야기!",
                key_points=[
                    f"{interest} 최신 트렌드 소개",
                    "필리핀 시장에서의 인기도",
                    "실제 구매 가이드",
                    "예산별 추천템"
                ],
                call_to_action="여러분은 어떤 {interest} 아이템에 관심 있나요?",
                trend_connection=f"{interest} 관련 검색량 상승 중"
            ))
        
        return content_ideas

    def _create_custom_report(self, persona: PersonaProfile, recommendations: List[ProductRecommendation], 
                            content_ideas: List[ContentIdea], user_data: Dict[str, Any]) -> Dict[str, Any]:
        """맞춤 리포트 생성"""
        # 평균 점수 계산
        avg_score = sum(rec.trending_score for rec in recommendations) / len(recommendations) if recommendations else 0
        high_score_products = [rec for rec in recommendations if rec.trending_score >= 70]
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "user_profile": {
                "mbti": user_data.get("mbti"),
                "interests": user_data.get("interests"),
                "channel_category": user_data.get("channel_category"),
                "budget_level": user_data.get("budget_level"),
                "persona_name": persona.name
            },
            "statistics": {
                "total_products": len(recommendations),
                "average_score": round(avg_score, 1),
                "high_score_products": len(high_score_products),
                "content_ideas_count": len(content_ideas)
            },
            "product_recommendations": [
                {
                    "product": rec.product_name,
                    "category": rec.category,
                    "price": rec.price_range,
                    "reason": rec.why_recommended,
                    "trending_score": rec.trending_score,
                    "where_to_buy": rec.where_to_buy,
                    "content_angle": rec.content_angle
                } for rec in recommendations
            ],
            "content_ideas": [
                {
                    "title": idea.title,
                    "type": idea.content_type,
                    "platform": idea.platform,
                    "hook": idea.hook,
                    "key_points": idea.key_points,
                    "call_to_action": idea.call_to_action
                } for idea in content_ideas
            ],
            "debug_info": self.debug_log if self.debug_mode else None
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