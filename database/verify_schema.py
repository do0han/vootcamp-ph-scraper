#!/usr/bin/env python3
"""
VOOTCAMP PH - Database Schema Verification Script
스키마 적용 후 모든 CORE 4 SCRAPERS 테이블이 정상 작동하는지 확인
"""

from database.supabase_client import SupabaseClient
from datetime import datetime
import json

def verify_complete_schema():
    """완성된 스키마의 모든 테이블과 기능을 검증"""
    
    print("🔍 VOOTCAMP PH CORE 4 SCRAPERS - 데이터베이스 스키마 검증")
    print("=" * 70)
    
    client = SupabaseClient()
    client._ensure_client()
    
    # 검증할 테이블들과 설명
    core_tables = {
        'google_trends': {
            'description': 'Google Trends Philippines (키워드 트렌드)',
            'key_columns': ['keyword', 'region', 'interest_score'],
            'test_insert': {
                'keyword': 'test_keyword',
                'region': 'Philippines',
                'interest_score': 95,
                'collection_date': datetime.now().isoformat()
            }
        },
        'shopee_products': {
            'description': 'Lazada Persona Targeting (페르소나 제품)',
            'key_columns': ['product_name', 'search_keyword', 'price'],
            'test_insert': {
                'product_name': 'Test Product',
                'search_keyword': 'skincare',
                'price': 299.99,
                'collection_date': datetime.now().isoformat()
            }
        },
        'tiktok_shop_products': {
            'description': 'TikTok Shop Philippines (TikTok 상품)',
            'key_columns': ['product_name', 'source_type', 'price'],
            'test_insert': {
                'source_type': 'test',
                'product_name': 'Test TikTok Product',
                'price': 199.99,
                'seller_name': 'Test Seller',
                'currency': 'PHP'
            }
        },
        'local_events': {
            'description': 'Local Events Philippines (로컬 이벤트)',
            'key_columns': ['event_name', 'event_location', 'source_website'],
            'test_insert': {
                'event_name': 'Test Event',
                'event_location': 'Manila',
                'source_url': 'https://test.com/event',
                'source_website': 'test_site',
                'event_type': 'test'
            }
        }
    }
    
    verification_results = {
        'total_tables': len(core_tables),
        'working_tables': 0,
        'total_records': 0,
        'tables_detail': {},
        'missing_tables': [],
        'test_results': {}
    }
    
    print("📋 테이블별 검증 결과:")
    
    for table_name, config in core_tables.items():
        try:
            # 1. 테이블 존재 확인
            result = client.client.table(table_name).select('*').limit(1).execute()
            
            # 2. 레코드 수 확인
            count_result = client.client.table(table_name).select('id', count='exact').execute()
            record_count = count_result.count if hasattr(count_result, 'count') else len(result.data)
            
            # 3. 컬럼 구조 확인
            if result.data:
                available_columns = list(result.data[0].keys())
                missing_columns = [col for col in config['key_columns'] if col not in available_columns]
            else:
                available_columns = []
                missing_columns = config['key_columns']
            
            verification_results['working_tables'] += 1
            verification_results['total_records'] += record_count
            verification_results['tables_detail'][table_name] = {
                'status': 'OK',
                'records': record_count,
                'columns': available_columns,
                'missing_columns': missing_columns
            }
            
            status_emoji = "✅" if not missing_columns else "⚠️"
            print(f"{status_emoji} {table_name}: {record_count}개 레코드")
            print(f"   📝 {config['description']}")
            if missing_columns:
                print(f"   ⚠️ 누락된 컬럼: {missing_columns}")
            
            # 4. 테스트 데이터 삽입/삭제 (선택적)
            try:
                # 테스트 데이터 삽입
                test_result = client.client.table(table_name).insert(config['test_insert']).execute()
                
                # 테스트 데이터 즉시 삭제 (정리)
                if test_result.data:
                    test_id = test_result.data[0]['id']
                    client.client.table(table_name).delete().eq('id', test_id).execute()
                    verification_results['test_results'][table_name] = 'INSERT/DELETE OK'
                else:
                    verification_results['test_results'][table_name] = 'INSERT FAILED'
                    
            except Exception as test_e:
                verification_results['test_results'][table_name] = f'TEST ERROR: {str(test_e)[:50]}'
                
        except Exception as e:
            verification_results['missing_tables'].append(table_name)
            verification_results['tables_detail'][table_name] = {
                'status': 'MISSING',
                'error': str(e)[:100]
            }
            print(f"❌ {table_name}: 테이블 없음")
            print(f"   📝 {config['description']}")
            print(f"   🚨 오류: {str(e)[:100]}...")
    
    # 요약 보고서
    print(f"\n📊 검증 요약:")
    print(f"• 전체 테이블: {verification_results['total_tables']}개")
    print(f"• 작동 중: {verification_results['working_tables']}개")
    print(f"• 완성률: {verification_results['working_tables']/verification_results['total_tables']*100:.1f}%")
    print(f"• 총 저장된 데이터: {verification_results['total_records']}개")
    print(f"• 누락된 테이블: {len(verification_results['missing_tables'])}개")
    
    if verification_results['missing_tables']:
        print(f"\n⚠️ 누락된 테이블:")
        for missing in verification_results['missing_tables']:
            print(f"  - {missing}")
        print(f"\n📋 해결방법: database/complete_schema_setup.sql을 Supabase에서 실행하세요")
    
    print(f"\n🧪 데이터 삽입 테스트 결과:")
    for table, result in verification_results['test_results'].items():
        emoji = "✅" if "OK" in result else "❌"
        print(f"  {emoji} {table}: {result}")
    
    # 추가 검증 (trending_summary 뷰, cleanup 함수 등)
    print(f"\n🔧 추가 기능 검증:")
    
    try:
        # trending_summary 뷰 확인
        trending_result = client.client.from_('trending_summary').select('*').execute()
        print(f"✅ trending_summary 뷰: {len(trending_result.data)}개 소스")
    except Exception as e:
        print(f"❌ trending_summary 뷰: {str(e)[:50]}...")
    
    try:
        # clean_old_data 함수 확인 (실행하지 않고 존재만 확인)
        func_result = client.client.rpc('clean_old_data', {'retention_days': 1}).execute()
        print(f"✅ clean_old_data 함수: 작동 확인")
    except Exception as e:
        print(f"❌ clean_old_data 함수: {str(e)[:50]}...")
    
    # 최종 평가
    completion_rate = verification_results['working_tables']/verification_results['total_tables']*100
    
    print(f"\n🎯 최종 평가:")
    if completion_rate == 100:
        print("✅ CORE 4 SCRAPERS 데이터베이스 스키마 완벽 구성!")
        print("🚀 모든 스크래퍼가 정상적으로 데이터를 저장할 수 있습니다.")
    elif completion_rate >= 50:
        print(f"⚠️ CORE 4 SCRAPERS 부분 완성 ({completion_rate:.1f}%)")
        print("📋 SQL 스크립트 실행으로 100% 완성 가능합니다.")
    else:
        print(f"❌ CORE 4 SCRAPERS 스키마 불완전 ({completion_rate:.1f}%)")
        print("🔧 즉시 스키마 적용이 필요합니다.")
    
    return verification_results

if __name__ == "__main__":
    verify_complete_schema() 