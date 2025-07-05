#!/usr/bin/env python3
"""
A/B 테스트를 위한 두 가지 추천 엔진 버전 비교
- 엔진 A: 클래식 단순 매칭
- 엔진 B: 스마트 매칭 + 가중치 재조정
"""

from persona_recommendation_engine import PersonaRecommendationEngine
import json
from datetime import datetime

class ClassicRecommendationEngine(PersonaRecommendationEngine):
    """엔진 A: 클래식 단순 매칭 버전"""
    
    def __init__(self):
        super().__init__(debug_mode=False)
        self.engine_type = "classic"
    
    def _calculate_product_score(self, product_name: str, category: str, persona):
        """클래식 단순 매칭 로직"""
        scoring_details = {
            "product_name": product_name,
            "category": category,
            "base_score": 30,
            "trend_boost": 0,
            "interest_alignment": 0,
            "platform_match": 0,
            "budget_compatibility": 10,
            "final_score": 0,
            "scoring_breakdown": []
        }
        
        # Base score
        scoring_details["scoring_breakdown"].append("Base product score: +30")
        
        # Trend boost (기존 로직)
        trend_boost = 0
        category_lower = category.lower()
        for trend_keyword, trend_score in self.trend_data.items():
            if trend_keyword.lower() in category_lower or category_lower in trend_keyword.lower():
                trend_boost = min(25, int(trend_score * 0.25))
                scoring_details["scoring_breakdown"].append(f"Trend boost ({trend_keyword}): +{trend_boost}")
                break
        
        scoring_details["trend_boost"] = trend_boost
        
        # 단순 Interest alignment (키워드만 직접 매칭)
        interest_score = 0
        for interest_obj in persona.interests:
            keyword = interest_obj["keyword"].lower()
            if keyword in category_lower or category_lower in keyword:
                interest_score += 5
                scoring_details["scoring_breakdown"].append(f"Direct keyword match ({keyword}): +5")
        
        scoring_details["interest_alignment"] = min(20, interest_score)
        
        # Platform compatibility
        platform_score = 0
        if category_lower in ["beauty", "makeup", "skincare"] and "TikTok" in persona.social_platforms:
            platform_score += 8
        elif category_lower in ["fashion", "accessories"] and "Instagram" in persona.social_platforms:
            platform_score += 8
        
        if "Shopee" in persona.social_platforms or "Lazada" in persona.social_platforms:
            platform_score += 7
        
        platform_score = min(15, platform_score)
        scoring_details["platform_match"] = platform_score
        scoring_details["scoring_breakdown"].append(f"Platform compatibility: +{platform_score}")
        
        # Final score
        final_score = 30 + trend_boost + interest_score + platform_score + 10
        scoring_details["final_score"] = final_score
        
        return scoring_details

class SmartRecommendationEngine(PersonaRecommendationEngine):
    """엔진 B: 스마트 매칭 + 가중치 재조정 버전"""
    
    def __init__(self):
        super().__init__(debug_mode=False)
        self.engine_type = "smart"
    
    def _calculate_product_score(self, product_name: str, category: str, persona):
        """스마트 매칭 + 가중치 재조정 로직"""
        scoring_details = {
            "product_name": product_name,
            "category": category,
            "base_score": 30,
            "trend_boost": 0,
            "interest_alignment": 0,
            "platform_match": 0,
            "budget_compatibility": 10,
            "final_score": 0,
            "scoring_breakdown": []
        }
        
        # Base score
        scoring_details["scoring_breakdown"].append("Base product score: +30")
        
        # 가중치 재조정: 트렌드 최대 20점
        trend_boost = 0
        category_lower = category.lower()
        for trend_keyword, trend_score in self.trend_data.items():
            keyword_lower = trend_keyword.lower()
            if (keyword_lower in category_lower or 
                category_lower in keyword_lower or
                (category_lower == "패션" and keyword_lower == "fashion") or
                (category_lower == "fashion" and keyword_lower == "fashion")):
                boost = min(20, int(trend_score * 0.2))  # 최대 20점으로 조정
                trend_boost += boost
        
        trend_boost = min(20, trend_boost)
        scoring_details["trend_boost"] = trend_boost
        scoring_details["scoring_breakdown"].append(f"Enhanced trend boost: +{trend_boost}")
        
        # 가중치 재조정: 스마트 관심사 매칭 최대 30점
        interest_score = 0
        matched_interest_categories = set()
        search_text = f"{product_name.lower()} {category_lower}".strip()
        
        for interest_obj in persona.interests:
            keyword = interest_obj["keyword"]
            related_keywords = interest_obj["related"]
            
            if keyword in matched_interest_categories:
                continue
            
            match_found = False
            # 메인 키워드 확인
            keyword_lower = keyword.lower()
            if (keyword_lower in search_text or 
                any(part in search_text for part in keyword_lower.split()) or
                self._fuzzy_match(keyword_lower, search_text)):
                match_found = True
            
            # 관련 키워드 확인
            if not match_found:
                for related in related_keywords:
                    related_lower = related.lower()
                    if (related_lower in search_text or 
                        any(part in search_text for part in related_lower.split()) or
                        self._fuzzy_match(related_lower, search_text)):
                        match_found = True
                        break
            
            if match_found:
                interest_score += 10  # 가중치 재조정: 관심사당 10점
                matched_interest_categories.add(keyword)
        
        interest_score = min(30, interest_score)  # 최대 30점
        scoring_details["interest_alignment"] = interest_score
        scoring_details["scoring_breakdown"].append(f"Smart interest matching: +{interest_score}")
        
        # Platform compatibility
        platform_score = 0
        if category_lower in ["beauty", "makeup", "skincare"] and "TikTok" in persona.social_platforms:
            platform_score += 8
        elif category_lower in ["fashion", "accessories"] and "Instagram" in persona.social_platforms:
            platform_score += 8
        
        if "Shopee" in persona.social_platforms or "Lazada" in persona.social_platforms:
            platform_score += 7
        
        platform_score = min(15, platform_score)
        scoring_details["platform_match"] = platform_score
        scoring_details["scoring_breakdown"].append(f"Platform compatibility: +{platform_score}")
        
        # Final score
        final_score = 30 + trend_boost + interest_score + platform_score + 10
        scoring_details["final_score"] = final_score
        
        return scoring_details

def generate_user_facing_report(engine, persona_name="young_professional_fashionista"):
    """사용자용 리포트 생성 (점수 및 디버그 정보 제외)"""
    
    # 추천 생성
    recommendations = engine.generate_product_recommendations(persona_name)
    content_ideas = engine.generate_content_ideas(persona_name)
    
    # 페르소나 정보
    persona = engine.personas[persona_name]
    
    # 엔진별 맞춤 설명 생성
    insight_intro = ""
    if engine.engine_type == "classic":
        insight_intro = "Based on your professional lifestyle and direct style preferences, here are products that match your stated interests:"
    else:
        insight_intro = "Based on your professional lifestyle and deeper understanding of your needs, here are products that align perfectly with your work-life style:"
    
    # 리포트 작성
    report = f"""# 🎯 Your Personalized Style & Content Recommendations

## 👤 About Your Style Profile
**Name**: {persona.name}  
**Age Group**: {persona.age_group}  
**Budget Range**: ₱{persona.budget_range[0]:,}-{persona.budget_range[1]:,}  
**Style Focus**: {', '.join([interest["keyword"] for interest in persona.interests[:3]])}

---

## 🛍️ The Insight: Your Perfect Product Matches

{insight_intro}

"""
    
    # 제품 추천 (점수 기준 정렬)
    sorted_recommendations = sorted(recommendations, key=lambda x: x.trending_score, reverse=True)
    
    for i, rec in enumerate(sorted_recommendations, 1):
        # 엔진별 맞춤 추천 이유 생성
        if engine.engine_type == "classic":
            personalized_reason = f"직접적인 스타일 매치: {rec.why_recommended}"
        else:
            # 스마트 엔진용 더 상세한 설명
            if "토트백" in rec.product_name:
                personalized_reason = f"워크웨어 라이프스타일 완벽 매치: 토트백은 직장인의 필수 액세서리로, 노트북과 서류를 안전하게 보관하면서도 전문적인 이미지를 연출합니다. {rec.why_recommended}"
            elif "블레이저" in rec.product_name:
                personalized_reason = f"지속가능한 전문직 스타일: 친환경 소재로 제작된 블레이저는 지속가능한 패션에 관심이 많은 당신과 완벽하게 매치됩니다. {rec.why_recommended}"
            else:
                personalized_reason = rec.why_recommended
        
        report += f"""### {i}. {rec.product_name}
**Category**: {rec.category}  
**Price Range**: {rec.price_range}  
**Why Perfect for You**: {personalized_reason}  
**Where to Buy**: {', '.join(rec.where_to_buy)}  
**Content Angle**: {rec.content_angle}

"""
    
    report += """---

## 💡 Your Content Blueprint

Transform your style discoveries into engaging content with these personalized ideas:

"""
    
    # 콘텐츠 아이디어 (상위 3개만)
    for i, idea in enumerate(content_ideas[:3], 1):
        report += f"""### {i}. {idea.title}
**Format**: {idea.content_type}  
**Best Platform**: {idea.platform}  
**Hook**: "{idea.hook}"  
**Key Points**: 
{chr(10).join(f"- {point}" for point in idea.key_points)}  
**Call-to-Action**: {idea.call_to_action}

"""
    
    # 엔진별 맞춤 수익화 팁
    if engine.engine_type == "classic":
        monetization_section = f"""## 💰 Monetization Tip

Your {persona.age_group} demographic and {persona.income_level} income profile make you ideal for:
- **Brand Partnerships**: Focus on sustainable and professional fashion brands
- **Affiliate Marketing**: Office wear and accessories perform well with your audience  
- **Content Series**: "Professional Style on a Budget" resonates with similar professionals

**Next Steps**: Start with your most aligned interest area and create content around products that directly match your stated preferences."""
    else:
        monetization_section = f"""## 💰 Monetization Tip

Your {persona.age_group} demographic and {persona.income_level} income profile, combined with your work-life integration needs, make you ideal for:
- **Brand Partnerships**: Focus on sustainable fashion brands that understand the professional woman's lifestyle
- **Affiliate Marketing**: Work essentials like quality tote bags and versatile blazers have high conversion rates
- **Content Series**: "From Desk to Dinner" styling concepts resonate strongly with career-focused audiences
- **Lifestyle Integration**: Show how professional pieces work across multiple life scenarios

**Next Steps**: Create content showcasing how your recommended products solve real workplace challenges while maintaining style."""

    report += f"""---

{monetization_section}

---

*Report generated on {datetime.now().strftime('%B %d, %Y')}*
"""
    
    return report

def run_ab_test():
    """A/B 테스트 실행"""
    
    print("🔬 A/B 테스트 시작: 클래식 vs 스마트 추천 엔진")
    print("=" * 60)
    
    # 엔진 A: 클래식
    print("📊 엔진 A (클래식) 리포트 생성 중...")
    engine_a = ClassicRecommendationEngine()
    report_a = generate_user_facing_report(engine_a)
    
    with open('report_A_classic.md', 'w', encoding='utf-8') as f:
        f.write(report_a)
    
    print("✅ report_A_classic.md 생성 완료")
    
    # 엔진 B: 스마트
    print("📊 엔진 B (스마트) 리포트 생성 중...")
    engine_b = SmartRecommendationEngine()
    report_b = generate_user_facing_report(engine_b)
    
    with open('report_B_smart.md', 'w', encoding='utf-8') as f:
        f.write(report_b)
    
    print("✅ report_B_smart.md 생성 완료")
    
    print("\n🎉 A/B 테스트 리포트 생성 완료!")
    print("📁 파일 위치:")
    print("   - report_A_classic.md (클래식 엔진)")
    print("   - report_B_smart.md (스마트 엔진)")
    print("\n💡 이제 두 리포트를 블라인드 테스트에 사용할 수 있습니다.")

if __name__ == "__main__":
    run_ab_test()