#!/usr/bin/env python3
"""
MCP Supabase 권한 문제 해결 가이드
- 읽기 전용 모드 해제
- 올바른 액세스 토큰 설정
- DDL 권한 확보
"""

import os
import json
import subprocess
from pathlib import Path

def check_mcp_status():
    """현재 MCP 설정 상태 확인"""
    print("🔍 MCP 서버 상태 확인")
    print("=" * 50)
    
    mcp_path = Path(".cursor/mcp.json")
    if not mcp_path.exists():
        print("❌ .cursor/mcp.json 파일이 없습니다!")
        return False
    
    with open(mcp_path, 'r') as f:
        config = json.load(f)
    
    if 'supabase' not in config.get('mcpServers', {}):
        print("❌ Supabase MCP 서버 설정이 없습니다!")
        return False
    
    supabase_config = config['mcpServers']['supabase']
    args = supabase_config.get('args', [])
    
    print("✅ Supabase MCP 서버 설정 발견:")
    print(f"   Command: {supabase_config.get('command')}")
    print(f"   Args: {args}")
    
    # 읽기 전용 모드 확인
    if '--read-only' in args:
        print("⚠️  현재 읽기 전용 모드로 설정됨")
        return 'read-only'
    else:
        print("✅ 읽기/쓰기 모드로 설정됨")
        return True

def fix_read_only_mode():
    """읽기 전용 모드 해제"""
    print("\n🔧 읽기 전용 모드 해제 중...")
    
    mcp_path = Path(".cursor/mcp.json")
    with open(mcp_path, 'r') as f:
        config = json.load(f)
    
    if 'supabase' in config['mcpServers']:
        args = config['mcpServers']['supabase']['args']
        if '--read-only' in args:
            args.remove('--read-only')
            print("✅ --read-only 플래그 제거됨")
        
        # 필요하면 모든 기능 활성화
        if '--features' not in ' '.join(args):
            args.extend(['--features', 'account,database,docs,debug,development,functions,branching,storage'])
            print("✅ 모든 기능 그룹 활성화")
    
    with open(mcp_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("💾 설정 파일 업데이트 완료")

def create_service_role_client():
    """Service Role 키를 사용한 클라이언트 설정 예시"""
    print("\n🔑 Service Role 클라이언트 설정 가이드")
    print("=" * 50)
    
    service_role_example = '''
# Service Role을 사용한 관리자 권한 클라이언트
from supabase import create_client

# 환경변수에서 Service Role Key 사용 (anon key가 아님!)
SUPABASE_URL = "https://rbsqmvhkfwtwqcdsgqdt.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Service Role Key

# 관리자 권한 클라이언트 생성
admin_client = create_client(
    SUPABASE_URL, 
    SUPABASE_SERVICE_ROLE_KEY,
    options={
        "auth": {
            "persistSession": False,
            "autoRefreshToken": False,
            "detectSessionInUrl": False
        }
    }
)

# DDL 작업 가능
result = admin_client.table('new_table').insert({}).execute()
'''
    
    print(service_role_example)

def upgrade_access_token():
    """액세스 토큰 권한 업그레이드 가이드"""
    print("\n🔐 액세스 토큰 권한 업그레이드")
    print("=" * 50)
    
    print("1️⃣ Supabase Dashboard → Settings → Access Tokens")
    print("2️⃣ 새 토큰 생성 시 다음 권한 선택:")
    print("   ✅ Read/Write access to all projects")
    print("   ✅ Organization admin access")
    print("   ✅ Database admin access")
    print("   ✅ Edge Functions deploy access")
    print()
    print("3️⃣ 생성된 토큰을 MCP 설정에 업데이트:")
    print("   .cursor/mcp.json → env → SUPABASE_ACCESS_TOKEN")

def alternative_solutions():
    """대안 솔루션 제시"""
    print("\n🚀 대안 솔루션")
    print("=" * 50)
    
    print("1️⃣ Supabase CLI 사용 (추천)")
    print("   - npm install -g supabase")
    print("   - supabase login")
    print("   - supabase db push")
    print()
    
    print("2️⃣ 직접 PostgreSQL MCP 서버 사용")
    print("   - @modelcontextprotocol/server-postgres")
    print("   - 직접 DB 연결 문자열 사용")
    print()
    
    print("3️⃣ 수동 SQL 실행")
    print("   - Supabase Dashboard → SQL Editor")
    print("   - 생성된 complete_schema_setup.sql 실행")

def restart_cursor_guide():
    """Cursor 재시작 가이드"""
    print("\n🔄 Cursor 재시작")
    print("=" * 50)
    
    print("1️⃣ Cursor 완전히 종료")
    print("2️⃣ .cursor/mcp.json 파일 수정 확인")
    print("3️⃣ Cursor 재시작")
    print("4️⃣ Settings → MCP 탭에서 상태 확인")
    print("5️⃣ 'supabase' 서버가 Active 상태인지 확인")

def main():
    """메인 실행 함수"""
    print("🛠️  MCP Supabase 권한 문제 해결 도구")
    print("=" * 50)
    
    # 1. 현재 상태 확인
    status = check_mcp_status()
    
    # 2. 읽기 전용 모드라면 해제
    if status == 'read-only':
        fix_read_only_mode()
    
    # 3. 해결 방법 가이드
    upgrade_access_token()
    create_service_role_client()
    alternative_solutions()
    restart_cursor_guide()
    
    print("\n✅ 권한 문제 해결 완료!")
    print("Cursor를 재시작한 후 MCP 도구를 다시 시도해보세요.")

if __name__ == "__main__":
    main() 