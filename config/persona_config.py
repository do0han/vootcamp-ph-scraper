"""
Persona-based targeting configuration for Vootcamp PH Data Scraper
페르소나 기반 타겟팅 설정
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class AgeGroup(Enum):
    """연령대 분류"""
    TEEN = "13-19"
    YOUNG_ADULT = "20-29" 
    ADULT = "30-39"
    MIDDLE_AGED = "40-49"
    SENIOR = "50+"

class Gender(Enum):
    """성별 분류"""
    FEMALE = "female"
    MALE = "male"
    UNISEX = "unisex"

class PriceRange(Enum):
    """가격대 분류"""
    BUDGET = (50, 500)      # ₱50-500
    MID_LOW = (500, 1000)   # ₱500-1,000  
    MID = (1000, 2500)      # ₱1,000-2,500
    MID_HIGH = (2500, 5000) # ₱2,500-5,000
    PREMIUM = (5000, 15000) # ₱5,000-15,000

@dataclass
class PersonaProfile:
    """페르소나 프로필 정의"""
    name: str
    age_group: AgeGroup
    gender: Gender
    price_ranges: List[PriceRange]
    interests: List[str]
    keywords: List[str]
    preferred_brands: List[str]
    shopping_behaviors: List[str]
    social_media_platforms: List[str]
    min_rating: float = 4.0
    min_review_count: int = 50

# 🎯 주요 타겟 페르소나 정의
TARGET_PERSONAS = {
    "young_filipina": PersonaProfile(
        name="Young Filipina Beauty Enthusiast",
        age_group=AgeGroup.YOUNG_ADULT,
        gender=Gender.FEMALE,
        price_ranges=[PriceRange.BUDGET, PriceRange.MID_LOW, PriceRange.MID],
        interests=[
            "K-beauty",
            "Korean skincare", 
            "makeup tutorials",
            "beauty trends",
            "self-care",
            "affordable fashion",
            "lifestyle products",
            "wellness"
        ],
        keywords=[
            # K-beauty 관련
            "korean skincare", "k-beauty", "glass skin", "korean cosmetics",
            "snail cream", "essence", "sheet mask", "korean makeup",
            
            # 트렌드 기반
            "viral skincare", "tiktok famous", "influencer recommended", 
            "trending makeup", "popular skincare", "viral beauty",
            
            # 가격 의식적
            "affordable skincare", "budget beauty", "cheap makeup",
            "student friendly", "sale beauty", "discount skincare",
            
            # 기능별
            "acne treatment", "whitening", "anti-aging", "moisturizer",
            "sunscreen", "serum", "cleanser", "toner",
            
            # 패션 관련
            "korean fashion", "cute clothes", "trendy outfit", 
            "affordable fashion", "casual wear", "street style"
        ],
        preferred_brands=[
            # Korean beauty brands
            "COSRX", "The Ordinary", "CeraVe", "Innisfree", "Etude House",
            "Laneige", "IOPE", "Klairs", "Benton", "Purito",
            
            # Accessible international brands  
            "Cetaphil", "Neutrogena", "Olay", "Dove", "Nivea",
            
            # Popular local/Asian brands
            "Human Nature", "Pond's", "Maybelline", "L'Oreal"
        ],
        shopping_behaviors=[
            "price comparison",
            "reviews reading", 
            "social media influenced",
            "trend following",
            "bundle purchasing",
            "seasonal shopping"
        ],
        social_media_platforms=[
            "TikTok", "Instagram", "Facebook", "YouTube", "Pinterest"
        ],
        min_rating=4.0,
        min_review_count=30  # Lower for accessibility
    ),
    
    "urban_professional": PersonaProfile(
        name="Urban Professional Filipina",
        age_group=AgeGroup.ADULT,
        gender=Gender.FEMALE,
        price_ranges=[PriceRange.MID, PriceRange.MID_HIGH],
        interests=[
            "premium skincare",
            "work-life balance",
            "quality fashion",
            "tech gadgets",
            "home improvement",
            "fitness",
            "professional development"
        ],
        keywords=[
            # Professional beauty
            "office makeup", "professional skincare", "anti-aging",
            "premium beauty", "dermatologist recommended", "clinical skincare",
            
            # Quality focused
            "high quality", "long lasting", "investment pieces",
            "premium brands", "luxury skincare", "professional grade",
            
            # Convenience
            "quick skincare", "busy lifestyle", "time saving",
            "multi-purpose", "travel size", "portable",
            
            # Technology  
            "laptop", "smartphone", "fitness tracker", "smart home",
            "productivity tools", "work from home"
        ],
        preferred_brands=[
            "SK-II", "Estee Lauder", "Clinique", "MAC", "Sephora",
            "Apple", "Samsung", "Nike", "Adidas", "Uniqlo"
        ],
        shopping_behaviors=[
            "quality over quantity",
            "brand loyalty", 
            "convenience shopping",
            "bulk purchasing",
            "subscription services"
        ],
        social_media_platforms=[
            "LinkedIn", "Instagram", "Facebook", "YouTube"
        ],
        min_rating=4.3,
        min_review_count=100
    ),
    
    "productivity_seeker": PersonaProfile(
        name="Productivity Seeker (College Student)",
        age_group=AgeGroup.YOUNG_ADULT,
        gender=Gender.UNISEX,
        price_ranges=[PriceRange.BUDGET, PriceRange.MID_LOW, PriceRange.MID],
        interests=[
            "productivity tools",
            "study accessories",
            "ergonomic furniture",
            "tech gadgets",
            "organization",
            "focus enhancement",
            "time management",
            "workspace optimization"
        ],
        keywords=[
            # Study & Productivity
            "ergonomic chair", "study desk", "laptop stand", "blue light glasses",
            "study lamp", "desk organizer", "planner", "notebook",
            "productivity apps", "time tracker", "focus timer", "study schedule",
            
            # Tech & Gadgets
            "wireless headphones", "bluetooth speaker", "power bank", "charging station",
            "tablet", "smartphone accessories", "keyboard", "mouse",
            "monitor", "webcam", "microphone", "laptop bag",
            
            # Health & Wellness
            "posture corrector", "wrist rest", "eye drops", "back support",
            "standing desk", "foot rest", "stress ball", "aromatherapy",
            
            # Organization
            "file organizer", "storage box", "cable management", "drawer divider",
            "wall shelf", "book stand", "pen holder", "sticky notes",
            
            # Budget-conscious
            "affordable", "student discount", "budget-friendly", "cheap",
            "sale", "clearance", "wholesale", "bulk buy"
        ],
        preferred_brands=[
            # Tech brands
            "Logitech", "HP", "Dell", "Asus", "Acer", "Lenovo",
            "Anker", "Xiaomi", "Huawei", "Samsung",
            
            # Furniture/Office
            "IKEA", "Steelcase", "Herman Miller", "Uplift",
            
            # Stationery
            "Moleskine", "Pilot", "Muji", "Zebra", "Stabilo"
        ],
        shopping_behaviors=[
            "price comparison",
            "reviews reading",
            "bulk purchasing", 
            "seasonal sales shopping",
            "student discount hunting",
            "functionality focused",
            "durability conscious"
        ],
        social_media_platforms=[
            "YouTube", "Reddit", "Discord", "Instagram", "TikTok"
        ],
        min_rating=4.0,
        min_review_count=20  # Lower threshold for student budget
    )
}

# 🔍 페르소나별 검색 전략
PERSONA_SEARCH_STRATEGIES = {
    "young_filipina": {
        "primary_categories": ["beauty", "skincare", "makeup", "fashion"],
        "trending_modifiers": ["viral", "trending", "popular", "tiktok famous"],
        "price_modifiers": ["affordable", "budget", "cheap", "sale", "discount"],
        "quality_filters": {
            "min_rating": 3.8,
            "min_reviews": 20,
            "max_price": 2000
        }
    },
    
    "urban_professional": {
        "primary_categories": ["premium skincare", "anti-aging", "professional", "tech"],
        "trending_modifiers": ["best", "top rated", "premium", "professional"],
        "price_modifiers": ["investment", "quality", "luxury", "professional grade"],
        "quality_filters": {
            "min_rating": 4.2,
            "min_reviews": 80,
            "max_price": 8000
        }
    },
    
    "productivity_seeker": {
        "primary_categories": ["productivity tools", "study accessories", "ergonomic furniture", "tech gadgets"],
        "trending_modifiers": ["best", "top rated", "student favorite", "highly recommended"],
        "price_modifiers": ["affordable", "student discount", "budget-friendly", "sale", "clearance"],
        "quality_filters": {
            "min_rating": 4.0,
            "min_reviews": 15,
            "max_price": 3000  # Student budget consideration
        }
    }
}

def get_persona_keywords(persona_name: str, category: str = None) -> List[str]:
    """페르소나별 맞춤 키워드 생성"""
    if persona_name not in TARGET_PERSONAS:
        return []
    
    persona = TARGET_PERSONAS[persona_name]
    strategy = PERSONA_SEARCH_STRATEGIES.get(persona_name, {})
    
    keywords = []
    
    # 기본 관심사 키워드
    keywords.extend(persona.keywords)
    
    # 카테고리별 특화 키워드
    if category:
        category_keywords = [
            f"{category} {modifier}" for modifier in strategy.get("trending_modifiers", [])
        ] + [
            f"{modifier} {category}" for modifier in strategy.get("price_modifiers", [])
        ]
        keywords.extend(category_keywords)
    
    return list(set(keywords))  # 중복 제거

def get_persona_filters(persona_name: str) -> Dict[str, Any]:
    """페르소나별 필터링 조건 반환"""
    if persona_name not in TARGET_PERSONAS:
        return {}
    
    persona = TARGET_PERSONAS[persona_name]
    strategy = PERSONA_SEARCH_STRATEGIES.get(persona_name, {})
    
    return {
        "min_rating": strategy.get("quality_filters", {}).get("min_rating", persona.min_rating),
        "min_reviews": strategy.get("quality_filters", {}).get("min_review_count", persona.min_review_count),
        "max_price": strategy.get("quality_filters", {}).get("max_price", 5000),
        "preferred_brands": persona.preferred_brands,
        "price_ranges": [(pr.value[0], pr.value[1]) for pr in persona.price_ranges]
    }

def get_trending_keywords_for_persona(persona_name: str, base_trends: List[str]) -> List[str]:
    """트렌드와 페르소나를 결합한 키워드 생성"""
    if persona_name not in TARGET_PERSONAS:
        return base_trends
    
    persona = TARGET_PERSONAS[persona_name]
    combined_keywords = []
    
    for trend in base_trends:
        # 페르소나 관심사와 트렌드 결합
        for interest in persona.interests[:3]:  # 상위 3개 관심사만
            combined_keywords.extend([
                f"{trend} {interest}",
                f"{interest} {trend}",
                f"trending {interest}"
            ])
    
    return list(set(combined_keywords))

# 🎯 현재 활성 페르소나 (설정 가능)
ACTIVE_PERSONA = "young_filipina"

def get_current_persona() -> PersonaProfile:
    """현재 활성화된 페르소나 반환"""
    return TARGET_PERSONAS[ACTIVE_PERSONA]

def set_active_persona(persona_name: str) -> bool:
    """활성 페르소나 변경"""
    global ACTIVE_PERSONA
    if persona_name in TARGET_PERSONAS:
        ACTIVE_PERSONA = persona_name
        return True
    return False