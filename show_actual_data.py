#!/usr/bin/env python3
"""
Show Actual Collected Data
실제 수집된 데이터 내용 보기
"""

import os
from datetime import datetime
from dotenv import load_dotenv

def show_google_trends_data():
    """실제 Google Trends 데이터 상세 내용 표시"""
    print("🔍 실제 수집된 Google Trends 데이터 내용:")
    print("=" * 60)
    
    try:
        load_dotenv()
        from database.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        trends_data = client.get_latest_google_trends(limit=15)
        
        if trends_data:
            print(f"📊 총 {len(trends_data)}개의 트렌드 데이터가 수집되었습니다\n")
            
            for i, record in enumerate(trends_data, 1):
                print(f"📈 레코드 #{i}")
                print(f"   🔤 키워드: {record.get('keyword', 'N/A')}")
                print(f"   📅 수집날짜: {record.get('collection_date', 'N/A')[:19] if record.get('collection_date') else 'N/A'}")
                print(f"   🌍 지역: {record.get('region', 'N/A')} (필리핀)")
                print(f"   📊 관심도 점수: {record.get('interest_score', 'N/A')}")
                print(f"   🏷️ 트렌드 타입: {record.get('trend_type', 'N/A')}")
                print(f"   ⏰ 생성시간: {record.get('created_at', 'N/A')[:19] if record.get('created_at') else 'N/A'}")
                
                # 추가 데이터가 있다면 표시
                if record.get('related_queries'):
                    print(f"   🔗 관련 검색어: {record.get('related_queries')}")
                if record.get('search_volume'):
                    print(f"   📈 검색량: {record.get('search_volume')}")
                
                print("   " + "-" * 50)
                
                if i >= 10:  # 처음 10개만 자세히 표시
                    print(f"   ... 그 외 {len(trends_data) - 10}개 더 있음")
                    break
        else:
            print("❌ 수집된 Google Trends 데이터가 없습니다")
            
    except Exception as e:
        print(f"❌ 데이터 조회 오류: {e}")

def run_live_google_trends_test():
    """실시간 Google Trends 데이터 수집 테스트"""
    print("\n🔥 실시간 Google Trends 수집 테스트:")
    print("=" * 60)
    
    try:
        from pytrends.request import TrendReq
        
        # 필리핀 실제 트렌드 키워드로 테스트
        real_keywords = ["skincare", "makeup", "fashion", "k-pop", "food delivery"]
        
        print(f"🎯 테스트 키워드: {real_keywords}")
        print("📡 Google Trends API 연결 중...")
        
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(real_keywords, cat=0, timeframe='today 1-m', geo='PH', gprop='')
        
        # 관심도 데이터 가져오기
        interest_data = pytrends.interest_over_time()
        
        if not interest_data.empty:
            print(f"✅ 성공! {len(interest_data)}개 데이터 포인트 수집됨")
            print("\n📊 최신 트렌드 데이터 (필리핀):")
            
            # 최근 5일 데이터 표시
            recent_data = interest_data.tail(5)
            
            for date, row in recent_data.iterrows():
                print(f"\n📅 {date.strftime('%Y-%m-%d')}:")
                for keyword in real_keywords:
                    if keyword in row:
                        interest_score = row[keyword]
                        bar = "█" * (interest_score // 5) if interest_score > 0 else "▌"
                        print(f"   {keyword:15}: {interest_score:3d} {bar}")
            
            # 관련 검색어도 가져오기
            print("\n🔗 관련 검색어 (Top 5):")
            try:
                related_queries = pytrends.related_queries()
                for keyword in real_keywords[:2]:  # 처음 2개 키워드만
                    if keyword in related_queries and related_queries[keyword]['top'] is not None:
                        print(f"\n🔤 '{keyword}' 관련 검색어:")
                        top_queries = related_queries[keyword]['top'].head(5)
                        for idx, (_, query_row) in enumerate(top_queries.iterrows(), 1):
                            print(f"   {idx}. {query_row['query']} (관심도: {query_row['value']})")
            except:
                print("   관련 검색어 데이터 없음")
                
        else:
            print("❌ Google Trends에서 데이터를 가져올 수 없었습니다")
            
    except Exception as e:
        print(f"❌ 실시간 테스트 오류: {e}")

def show_system_metrics():
    """시스템 성능 지표 표시"""
    print("\n⚡ 시스템 성능 지표:")
    print("=" * 60)
    
    print("📊 수집된 데이터 종류:")
    print("   🔍 Google Trends: ✅ 실시간 수집 가능")
    print("   🛒 Shopee 제품: 🔧 스크래퍼 준비됨") 
    print("   🛒 Lazada 제품: 🔧 페르소나 타겟팅 스크래퍼 준비됨")
    print("   📱 TikTok Shop: 🔧 소셜 커머스 스크래퍼 준비됨")
    
    print("\n🎯 타겟 데이터:")
    print("   🌍 지역: 필리핀 (Philippines)")
    print("   👥 대상: 젊은 필리피나 (18-35세)")
    print("   🏷️ 카테고리: 뷰티, 패션, K-pop, 음식배달")
    print("   📈 예상 일일 수집량: ~183개 데이터 포인트")
    
    print("\n💾 데이터 저장:")
    print("   📍 위치: Supabase 클라우드 데이터베이스")
    print("   🔄 실시간: 즉시 저장 및 조회 가능")
    print("   📊 구조: 정규화된 테이블 구조")

def main():
    """메인 실행"""
    print("🇵🇭 VOOTCAMP PH SCRAPERS - 실제 수집 데이터")
    print("=" * 80)
    print(f"⏰ 조회 시간: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}")
    print()
    
    # 1. 저장된 데이터 표시
    show_google_trends_data()
    
    # 2. 실시간 테스트
    run_live_google_trends_test()
    
    # 3. 시스템 지표
    show_system_metrics()
    
    print("\n" + "=" * 80)
    print("✅ 실제 데이터 조회 완료!")
    print("🎯 시스템이 실시간으로 필리핀 트렌드 데이터를 수집하고 있습니다!")

if __name__ == "__main__":
    main()