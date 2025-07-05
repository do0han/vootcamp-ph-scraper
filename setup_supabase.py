#!/usr/bin/env python3
"""
🚀 Supabase 자격증명 설정 스크립트

이 스크립트는 사용자가 Supabase 자격증명을 쉽게 설정할 수 있도록 도와줍니다.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """환영 배너 출력"""
    print("=" * 60)
    print("🚀 VOOTCAMP PH SCRAPER - SUPABASE 설정")
    print("=" * 60)
    print()

def validate_url(url):
    """URL 형식 검증"""
    return url.startswith('https://') and 'supabase.co' in url

def validate_key(key):
    """API 키 형식 검증"""
    return key.startswith('eyJ') and len(key) > 100

def setup_supabase_credentials():
    """Supabase 자격증명 설정"""
    
    print_banner()
    
    print("📋 설정 단계:")
    print("1. https://supabase.com 에서 새 프로젝트 생성")
    print("2. Settings → API 페이지로 이동")
    print("3. Project URL과 anon public key 복사")
    print("4. 아래에 입력")
    print()
    
    # URL 입력
    while True:
        print("🔗 Supabase Project URL을 입력하세요:")
        print("   예시: https://abcdefghijklmnop.supabase.co")
        url = input("URL: ").strip()
        
        if not url:
            print("❌ URL을 입력해주세요!")
            continue
            
        if url == "your_supabase_url_here":
            print("❌ 실제 URL을 입력해주세요!")
            continue
            
        if not validate_url(url):
            print("❌ 올바른 Supabase URL 형식이 아닙니다!")
            print("   https://프로젝트ID.supabase.co 형식이어야 합니다.")
            continue
            
        supabase_url = url
        break
    
    print("✅ URL이 설정되었습니다!")
    print()
    
    # API Key 입력
    while True:
        print("🔑 Supabase anon public key를 입력하세요:")
        print("   예시: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        key = input("Key: ").strip()
        
        if not key:
            print("❌ API 키를 입력해주세요!")
            continue
            
        if key == "your_supabase_anon_key_here":
            print("❌ 실제 API 키를 입력해주세요!")
            continue
            
        if not validate_key(key):
            print("❌ 올바른 API 키 형식이 아닙니다!")
            print("   'eyJ'로 시작하는 긴 문자열이어야 합니다.")
            continue
            
        supabase_key = key
        break
    
    print("✅ API 키가 설정되었습니다!")
    print()
    
    return supabase_url, supabase_key

def update_env_file(url, key):
    """환경 파일 업데이트"""
    print("💾 .env 파일을 업데이트하는 중...")
    
    env_path = Path('.env')
    
    # 현재 .env 파일 읽기
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
    else:
        print("❌ .env 파일을 찾을 수 없습니다!")
        return False
    
    # 자격증명 교체
    content = content.replace('SUPABASE_URL=your_supabase_url_here', f'SUPABASE_URL={url}')
    content = content.replace('SUPABASE_KEY=your_supabase_anon_key_here', f'SUPABASE_KEY={key}')
    
    # 파일 저장
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ .env 파일이 업데이트되었습니다!")
    return True

def test_connection():
    """연결 테스트"""
    print("\n🧪 데이터베이스 연결을 테스트하는 중...")
    
    try:
        # 환경변수 다시 로드
        from dotenv import load_dotenv
        load_dotenv()
        
        from database.supabase_client import SupabaseClient
        
        client = SupabaseClient()
        print("✅ Supabase 연결 성공!")
        
        # 테이블 확인
        print("\n📊 테이블 상태 확인:")
        tables = ['google_trends', 'shopee_products', 'tiktok_videos']
        
        for table in tables:
            try:
                result = client.client.table(table).select('*').limit(1).execute()
                print(f"  ✅ {table} 테이블 정상")
            except Exception as e:
                print(f"  ❌ {table} 테이블 오류: {e}")
                print(f"     → SUPABASE_SETUP_GUIDE.md의 2단계를 확인하세요!")
        
        return True
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("\n🔧 문제 해결:")
        print("1. URL과 API 키가 올바른지 확인")
        print("2. Supabase 프로젝트가 활성화되어 있는지 확인") 
        print("3. SUPABASE_SETUP_GUIDE.md의 스키마 생성 단계 확인")
        return False

def main():
    """메인 함수"""
    try:
        # 자격증명 설정
        url, key = setup_supabase_credentials()
        
        # 환경 파일 업데이트
        if not update_env_file(url, key):
            return False
        
        # 연결 테스트
        success = test_connection()
        
        if success:
            print("\n🎉 설정 완료!")
            print("\n📝 다음 단계:")
            print("1. python3 main.py 실행하여 전체 시스템 테스트")
            print("2. logs/ 폴더에서 수집된 데이터 확인")
            print("3. Supabase 대시보드에서 실시간 데이터 모니터링")
        else:
            print("\n⚠️  연결에 실패했습니다.")
            print("SUPABASE_SETUP_GUIDE.md를 참조하여 설정을 완료하세요.")
        
        return success
        
    except KeyboardInterrupt:
        print("\n\n👋 설정이 취소되었습니다.")
        return False
    except Exception as e:
        print(f"\n💥 오류 발생: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)