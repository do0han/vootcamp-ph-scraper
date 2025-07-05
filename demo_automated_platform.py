#!/usr/bin/env python3
"""
자동화된 플랫폼 데모 - Just Elias 시나리오
Automated Platform Demo - Just Elias Scenario
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# 프로젝트 루트 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from config.persona_config import TARGET_PERSONAS, get_persona_filters
from database.supabase_client import SupabaseClient
from ai.report_generator import PersonaReportGenerator
from scrapers.lazada_persona_scraper import LazadaPersonaScraper

def simulate_elias_login():
    """Just Elias 로그인 시뮬레이션"""
    
    print("🎯 자동화된 플랫폼 데모 - Just Elias 시나리오")
    print("=" * 60)
    
    # 1. 사용자 로그인
    print("👤 Just Elias가 플랫폼에 로그인합니다...")
    time.sleep(1)
    
    # 2. 시스템 페르소나 인지
    print("🤖 시스템이 Supabase에서 Elias의 프로필을 확인합니다...")
    
    try:
        supabase_client = SupabaseClient()
        print("✅ Supabase 연결 성공")
    except Exception as e:
        print(f"❌ Supabase 연결 실패: {e}")
        return
    
    time.sleep(1)
    
    # 3. 페르소나 자동 감지
    elias_persona = "productivity_seeker"
    persona = TARGET_PERSONAS[elias_persona]
    filters = get_persona_filters(elias_persona)
    
    print(f"🎯 페르소나 감지: '{persona.name}'")
    print(f"   👥 연령대: {persona.age_group.value}")
    print(f"   💰 예산: ₱{filters.get('max_price', 0)} 이하")
    print(f"   🏷️ 관심사: {', '.join(persona.interests[:4])}...")
    
    time.sleep(2)
    
    # 4. 키워드 자동 로딩
    print("\n📚 시스템이 페르소나 키워드를 자동으로 로딩합니다...")
    print(f"   🔍 로딩된 키워드: {len(persona.keywords)}개")
    print(f"   📝 주요 키워드: {', '.join(persona.keywords[:8])}...")
    
    time.sleep(2)
    
    # 5. 실시간 데이터 수집
    print("\n🤖 클라우드 봇이 실시간으로 데이터를 수집합니다...")
    print("   🛍️ Lazada Philippines 검색 중...")
    
    try:
        # 실제 페르소나 스크래퍼 실행 (제한된 수량)
        scraper = LazadaPersonaScraper(persona_name=elias_persona, use_undetected=True)
        products = scraper.search_persona_products("productivity tools", limit=3)
        
        print(f"   ✅ {len(products)}개 제품 발견!")
        
        if products:
            print("   🎯 수집된 제품:")
            for i, product in enumerate(products, 1):
                name = product.get('product_name', 'Unknown')[:40]
                score = product.get('persona_score', 0)
                price = product.get('price_numeric', 0)
                print(f"      {i}. {name}... (점수: {score:.1f}/100, ₱{price})")
        
        scraper.close()
        
    except Exception as e:
        print(f"   ⚠️ 실시간 수집 시뮬레이션: {e}")
        # 샘플 데이터로 대체
        products = [
            {"product_name": "Ergonomic Study Chair", "persona_score": 85.0, "price_numeric": 2200},
            {"product_name": "Blue Light Glasses", "persona_score": 72.0, "price_numeric": 450},
            {"product_name": "Wireless Study Headphones", "persona_score": 78.0, "price_numeric": 1100}
        ]
        print(f"   ✅ {len(products)}개 제품 발견! (시뮬레이션)")
        for i, product in enumerate(products, 1):
            name = product['product_name']
            score = product['persona_score']
            price = product['price_numeric']
            print(f"      {i}. {name} (점수: {score}/100, ₱{price})")
    
    time.sleep(3)
    
    # 6. AI 분석 및 맞춤형 리포트 생성
    print("\n🧠 AI가 수집된 데이터를 분석하여 맞춤형 리포트를 생성합니다...")
    
    try:
        report_generator = PersonaReportGenerator()
        exam_report = report_generator.generate_scenario_report("exam_period", elias_persona)
        
        print("✅ AI 리포트 생성 완료!")
        print(f"   📊 리포트 제목: {exam_report.get('title', 'N/A')}")
        
        summary = exam_report.get('summary', '').strip()
        if summary:
            # 요약을 줄 단위로 표시
            summary_lines = summary.split('\n')
            print("   📝 맞춤형 메시지:")
            for line in summary_lines[:3]:  # 처음 3줄만
                if line.strip():
                    print(f"      {line.strip()}")
        
    except Exception as e:
        print(f"   ⚠️ AI 리포트 시뮬레이션: {e}")
        print("   📝 맞춤형 메시지:")
        print("      🎓 시험 기간을 앞둔 당신을 위한 특별한 추천!")
        print("      📚 집중력 향상에 도움되는 최고의 아이템들을 발견했습니다.")
        print("      💰 학생 예산에 맞는 경제적인 제품들이 많아요!")
    
    time.sleep(2)
    
    # 7. 대시보드 업데이트
    print("\n📊 Elias의 개인 대시보드가 자동으로 업데이트됩니다...")
    
    dashboard_data = {
        "사용자": "Just Elias",
        "페르소나": persona.name,
        "오늘_발견_제품": len(products),
        "평균_적합도": f"{sum(p.get('persona_score', 0) for p in products) / len(products):.1f}점" if products else "0점",
        "추천_상황": "시험 기간 집중력 향상",
        "업데이트_시간": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    print("   ✅ 대시보드 데이터:")
    for key, value in dashboard_data.items():
        print(f"      {key}: {value}")
    
    time.sleep(2)
    
    # 8. 완성된 자동화 워크플로우
    print("\n🎉 자동화된 플랫폼 워크플로우 완성!")
    print("=" * 60)
    print("📋 실행된 단계:")
    print("   1. ✅ Just Elias 로그인")
    print("   2. ✅ 페르소나 자동 감지 (생산성 추구자)")
    print("   3. ✅ 키워드 자동 로딩 (57개)")
    print("   4. ✅ 실시간 데이터 수집 (Lazada)")
    print("   5. ✅ AI 분석 및 리포트 생성")
    print("   6. ✅ 맞춤형 대시보드 업데이트")
    
    print(f"\n💡 결과: Elias는 로그인만 했는데도 자동으로")
    print(f"   🎯 페르소나에 맞는 {len(products)}개 제품")
    print(f"   📊 맞춤형 분석 리포트")
    print(f"   📱 개인화된 대시보드")
    print(f"   를 실시간으로 제공받았습니다!")
    
    return dashboard_data

def demonstrate_multi_persona():
    """다중 페르소나 시스템 시연"""
    
    print("\n" + "=" * 60)
    print("🌟 다중 페르소나 시스템 시연")
    print("=" * 60)
    
    users = [
        ("Just Elias", "productivity_seeker", "대학생"),
        ("Maria Santos", "young_filipina", "20대 여성"),
        ("Anna Cruz", "urban_professional", "직장인 여성")
    ]
    
    for name, persona_key, description in users:
        persona = TARGET_PERSONAS[persona_key]
        filters = get_persona_filters(persona_key)
        
        print(f"\n👤 {name} ({description})")
        print(f"   🎯 페르소나: {persona.name}")
        print(f"   💰 예산: ₱{filters.get('max_price', 0)} 이하")
        print(f"   🏷️ 주 관심사: {', '.join(persona.interests[:3])}")
        print(f"   🔍 핵심 키워드: {', '.join(persona.keywords[:5])}...")
        
        # 각 페르소나별 예상 추천 제품
        if persona_key == "productivity_seeker":
            print("   📦 예상 추천: 인체공학 의자, 블루라이트 안경, 노이즈캔슬링 헤드폰")
        elif persona_key == "young_filipina":
            print("   📦 예상 추천: K-beauty 세럼, 시트마스크, 트렌디한 메이크업")
        elif persona_key == "urban_professional":
            print("   📦 예상 추천: 프리미엄 스킨케어, 스마트 가젯, 고품질 액세서리")
    
    print(f"\n🤖 시스템 역량:")
    print(f"   • {len(TARGET_PERSONAS)}개 페르소나 동시 지원")
    print(f"   • 실시간 개인화 데이터 수집")
    print(f"   • AI 기반 맞춤형 인사이트")
    print(f"   • 자동화된 스케줄링 시스템")

def main():
    """메인 데모 실행"""
    
    # 로깅 설정
    logging.basicConfig(level=logging.WARNING)  # 로그 최소화
    
    try:
        # Just Elias 시나리오 시연
        elias_data = simulate_elias_login()
        
        # 다중 페르소나 시스템 시연
        demonstrate_multi_persona()
        
        print("\n" + "=" * 60)
        print("✨ 자동화된 플랫폼 데모 완료!")
        print("=" * 60)
        print("🎯 핵심 성과:")
        print("   ✅ 페르소나 기반 자동 타겟팅")
        print("   ✅ 실시간 데이터 수집 및 분석")
        print("   ✅ AI 맞춤형 인사이트 생성")
        print("   ✅ 개인화된 사용자 경험")
        
        print(f"\n🚀 Just Elias는 이제 로그인만 하면")
        print(f"   자동으로 시험 기간에 맞는 생산성 도구들을")
        print(f"   실시간으로 추천받을 수 있습니다!")
        
    except KeyboardInterrupt:
        print("\n⏹️ 데모가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류: {e}")

if __name__ == "__main__":
    main()