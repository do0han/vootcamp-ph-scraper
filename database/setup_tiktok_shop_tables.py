#!/usr/bin/env python3
"""
TikTok Shop 데이터베이스 테이블 설정 스크립트
"""

import sys
import logging
from pathlib import Path

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from database.supabase_client import SupabaseClient

def setup_tiktok_shop_tables():
    """TikTok Shop 테이블 생성 및 설정"""
    
    print("🎬 TikTok Shop 데이터베이스 테이블 설정 시작")
    print("=" * 60)
    
    try:
        # Supabase 클라이언트 초기화
        supabase_client = SupabaseClient()
        print("✅ Supabase 연결 성공")
        
        # SQL 스키마 파일 읽기
        schema_file = Path(__file__).parent / "tiktok_shop_schema.sql"
        
        if not schema_file.exists():
            print("❌ 스키마 파일을 찾을 수 없습니다: tiktok_shop_schema.sql")
            return False
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        print("✅ 스키마 파일 읽기 완료")
        
        # SQL을 개별 명령어로 분할 (세미콜론 기준)
        sql_commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
        
        print(f"📝 총 {len(sql_commands)}개의 SQL 명령어 실행 예정")
        
        # 각 SQL 명령어 실행
        success_count = 0
        for i, command in enumerate(sql_commands, 1):
            try:
                if command.strip():
                    # 주석 제거
                    if command.strip().startswith('--'):
                        continue
                    
                    print(f"   {i}/{len(sql_commands)}: 실행 중...")
                    
                    # Supabase는 rpc 호출로 SQL 실행
                    result = supabase_client.client.rpc('exec_sql', {'query': command}).execute()
                    
                    success_count += 1
                    
            except Exception as e:
                # 일부 명령어는 이미 존재할 수 있으므로 경고로 처리
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ['already exists', 'duplicate', 'conflict']):
                    print(f"   ⚠️  {i}: 이미 존재함 (스킵)")
                    success_count += 1
                else:
                    print(f"   ❌ {i}: 실행 실패 - {e}")
        
        print(f"\n📊 실행 결과: {success_count}/{len(sql_commands)} 성공")
        
        # 테이블 생성 확인
        print("\n🔍 테이블 생성 확인 중...")
        
        tables_to_check = [
            'tiktok_shop_products',
            'tiktok_shop_creators', 
            'tiktok_product_creators'
        ]
        
        existing_tables = []
        for table in tables_to_check:
            try:
                # 테이블에서 1개 행만 조회해서 존재 여부 확인
                result = supabase_client.client.table(table).select('*').limit(1).execute()
                existing_tables.append(table)
                print(f"   ✅ {table}: 존재함")
            except Exception as e:
                print(f"   ❌ {table}: 없음 또는 접근 불가 - {e}")
        
        if len(existing_tables) == len(tables_to_check):
            print(f"\n🎉 모든 TikTok Shop 테이블이 성공적으로 생성되었습니다!")
            
            # 샘플 데이터 삽입 여부 확인
            user_input = input("\n📦 샘플 데이터를 삽입하시겠습니까? (y/n): ").lower()
            if user_input in ['y', 'yes']:
                insert_sample_data(supabase_client)
            
            return True
        else:
            print(f"\n⚠️  일부 테이블 생성 실패: {len(existing_tables)}/{len(tables_to_check)}")
            return False
            
    except Exception as e:
        print(f"❌ 데이터베이스 설정 실패: {e}")
        return False

def insert_sample_data(supabase_client):
    """샘플 데이터 삽입"""
    
    print("\n📦 TikTok Shop 샘플 데이터 삽입 중...")
    
    try:
        # 샘플 크리에이터 데이터
        sample_creators = [
            {
                'creator_id': 'tiktoker_beauty_ph',
                'creator_name': 'Maria Beauty PH',
                'creator_username': '@mariabeautyph',
                'follower_count': 250000,
                'category': 'beauty',
                'verification_status': 'verified',
                'is_affiliated': True
            },
            {
                'creator_id': 'tech_reviewer_manila',
                'creator_name': 'Tech Guy Manila', 
                'creator_username': '@techguymnl',
                'follower_count': 180000,
                'category': 'tech',
                'verification_status': 'verified',
                'is_affiliated': True
            },
            {
                'creator_id': 'lifestyle_influencer',
                'creator_name': 'Pinay Lifestyle',
                'creator_username': '@pinaylifestyle',
                'follower_count': 320000,
                'category': 'lifestyle', 
                'verification_status': 'business',
                'is_affiliated': True
            }
        ]
        
        # 크리에이터 삽입
        try:
            result = supabase_client.client.table('tiktok_shop_creators').upsert(sample_creators).execute()
            print(f"   ✅ 크리에이터 {len(sample_creators)}명 삽입 완료")
        except Exception as e:
            print(f"   ⚠️  크리에이터 삽입 실패: {e}")
        
        # 샘플 제품 데이터  
        sample_products = [
            # Young Filipina 타겟 제품들
            {
                'source_type': 'top_products',
                'product_name': 'COSRX Advanced Snail 96 Mucin Power Essence',
                'price': 899.00,
                'original_price': 1200.00,
                'discount_percentage': 25,
                'rating': 4.8,
                'review_count': 1580,
                'sales_count': 5200,
                'category': 'beauty',
                'brand': 'COSRX',
                'persona_target': 'young_filipina',
                'persona_score': 92.5,
                'is_viral': True,
                'tiktok_mentions': 1250,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/cosrx-snail-essence-001'
            },
            {
                'source_type': 'flash_sale',
                'product_name': 'The Ordinary Niacinamide 10% + Zinc 1%',
                'price': 450.00,
                'original_price': 650.00, 
                'discount_percentage': 31,
                'rating': 4.6,
                'review_count': 890,
                'sales_count': 3100,
                'category': 'beauty',
                'brand': 'The Ordinary',
                'persona_target': 'young_filipina',
                'persona_score': 88.3,
                'is_viral': True,
                'tiktok_mentions': 980,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/the-ordinary-niacinamide-002'
            },
            {
                'source_type': 'category_beauty',
                'product_name': 'Innisfree Green Tea Seed Serum',
                'price': 750.00,
                'original_price': 950.00,
                'discount_percentage': 21,
                'rating': 4.7,
                'review_count': 2100,
                'sales_count': 4500,
                'category': 'beauty',
                'brand': 'Innisfree',
                'persona_target': 'young_filipina',
                'persona_score': 85.2,
                'is_viral': False,
                'tiktok_mentions': 650,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/innisfree-green-tea-003'
            },
            
            # Productivity Seeker 타겟 제품들
            {
                'source_type': 'top_products',
                'product_name': 'Ergonomic Bluetooth Wireless Mouse',
                'price': 1250.00,
                'original_price': 1500.00,
                'discount_percentage': 17,
                'rating': 4.5,
                'review_count': 320,
                'sales_count': 1200,
                'category': 'tech',
                'brand': 'Logitech',
                'persona_target': 'productivity_seeker',
                'persona_score': 78.9,
                'is_viral': False,
                'tiktok_mentions': 180,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/logitech-mouse-004'
            },
            {
                'source_type': 'category_tech',
                'product_name': 'Blue Light Blocking Gaming Glasses',
                'price': 580.00,
                'original_price': 800.00,
                'discount_percentage': 28,
                'rating': 4.3,
                'review_count': 150,
                'sales_count': 800,
                'category': 'tech',
                'brand': 'Generic',
                'persona_target': 'productivity_seeker',
                'persona_score': 72.1,
                'is_viral': True,
                'tiktok_mentions': 420,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/blue-light-glasses-005'
            },
            {
                'source_type': 'flash_sale',
                'product_name': 'Laptop Stand Adjustable Aluminum',
                'price': 1850.00,
                'original_price': 2500.00,
                'discount_percentage': 26,
                'rating': 4.6,
                'review_count': 280,
                'sales_count': 950,
                'category': 'tech',
                'brand': 'UGREEN',
                'persona_target': 'productivity_seeker',
                'persona_score': 81.7,
                'is_viral': False,
                'tiktok_mentions': 95,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/ugreen-laptop-stand-006'
            },
            
            # Urban Professional 타겟 제품들
            {
                'source_type': 'top_products',
                'product_name': 'Premium Wireless Noise-Cancelling Headphones',
                'price': 3200.00,
                'original_price': 4000.00,
                'discount_percentage': 20,
                'rating': 4.8,
                'review_count': 450,
                'sales_count': 600,
                'category': 'tech',
                'brand': 'Sony',
                'persona_target': 'urban_professional',
                'persona_score': 89.3,
                'is_viral': False,
                'tiktok_mentions': 75,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/sony-headphones-007'
            },
            {
                'source_type': 'category_lifestyle',
                'product_name': 'Minimalist Leather Laptop Bag',
                'price': 2800.00,
                'original_price': 3500.00,
                'discount_percentage': 20,
                'rating': 4.7,
                'review_count': 180,
                'sales_count': 400,
                'category': 'lifestyle',
                'brand': 'Bellroy',
                'persona_target': 'urban_professional',
                'persona_score': 84.6,
                'is_viral': False,
                'tiktok_mentions': 45,
                'is_real_data': False,
                'product_url': 'https://www.tiktok.com/shop/ph/product/bellroy-laptop-bag-008'
            }
        ]
        
        # 제품 삽입 (upsert로 중복 방지)
        try:
            result = supabase_client.client.table('tiktok_shop_products').upsert(sample_products).execute()
            print(f"   ✅ 제품 {len(sample_products)}개 삽입 완료")
        except Exception as e:
            print(f"   ⚠️  제품 삽입 실패: {e}")
        
        print("\n🎉 샘플 데이터 삽입 완료!")
        
        # 삽입된 데이터 확인
        print("\n📊 삽입된 데이터 확인:")
        
        try:
            products_count = supabase_client.client.table('tiktok_shop_products').select('id', count='exact').execute()
            creators_count = supabase_client.client.table('tiktok_shop_creators').select('id', count='exact').execute()
            
            print(f"   📦 제품 테이블: {products_count.count}개")
            print(f"   👥 크리에이터 테이블: {creators_count.count}개")
            
        except Exception as e:
            print(f"   ⚠️  데이터 확인 실패: {e}")
        
    except Exception as e:
        print(f"❌ 샘플 데이터 삽입 실패: {e}")

def main():
    """메인 실행 함수"""
    
    logging.basicConfig(level=logging.WARNING)  # 로깅 최소화
    
    success = setup_tiktok_shop_tables()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TikTok Shop 데이터베이스 설정 완료!")
        print("🎯 다음 단계: 페르소나 타겟팅 로직 연동")
    else:
        print("\n" + "=" * 60)
        print("❌ TikTok Shop 데이터베이스 설정 실패")
        print("💡 Supabase 연결 및 권한을 확인해주세요")

if __name__ == "__main__":
    main()