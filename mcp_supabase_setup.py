#!/usr/bin/env python3
"""
MCP 통합 Supabase 설정 도구
사용자가 쉽게 Supabase 테이블을 생성할 수 있도록 도와주는 스크립트
"""

import os
import sys
import webbrowser
from pathlib import Path

def open_supabase_sql_editor():
    """Supabase SQL Editor를 자동으로 열어줍니다"""
    
    print('🚀 MCP 통합 Supabase 설정 도구')
    print('=' * 50)
    print()
    
    # Supabase URL 확인
    supabase_url = os.getenv('SUPABASE_URL', 'https://rbsqmvhkfwtwqcdsgqdt.supabase.co')
    project_id = supabase_url.split('//')[1].split('.')[0]
    
    sql_editor_url = f"https://supabase.com/dashboard/project/{project_id}/sql/new"
    
    print(f'📋 프로젝트 정보:')
    print(f'   Supabase URL: {supabase_url}')
    print(f'   프로젝트 ID: {project_id}')
    print()
    
    # SQL 스키마 내용 표시
    schema_path = Path('database/schema.sql')
    if schema_path.exists():
        print('📄 실행할 SQL 스키마:')
        print('=' * 50)
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_content = f.read()
        
        # 스키마 내용 미리보기 (처음 몇 줄)
        lines = schema_content.split('\n')
        preview_lines = [line for line in lines[:20] if line.strip() and not line.strip().startswith('--')]
        
        for line in preview_lines[:10]:
            print(line)
        
        print('...')
        print(f'(총 {len(lines)} 줄)')
        print('=' * 50)
        print()
        
        # 복사할 수 있도록 전체 스키마를 파일로 저장
        clipboard_file = Path('supabase_schema_for_copy.sql')
        with open(clipboard_file, 'w', encoding='utf-8') as f:
            f.write(schema_content)
        
        print(f'📋 복사용 스키마 파일 생성: {clipboard_file}')
        print()
    
    print('🎯 다음 단계:')
    print()
    print('1️⃣ Supabase SQL Editor 열기')
    print(f'   URL: {sql_editor_url}')
    print()
    print('2️⃣ SQL 스키마 복사 및 실행')
    print('   - 아래 명령어로 스키마를 복사하세요:')
    print(f'   cat database/schema.sql | pbcopy  # Mac')
    print(f'   cat database/schema.sql | xclip -selection clipboard  # Linux')
    print()
    print('3️⃣ SQL Editor에서 붙여넣기 후 실행')
    print()
    print('4️⃣ 완료 확인')
    print('   - 테이블이 생성되면 다음 명령어로 확인:')
    print('   python3 test_connection.py')
    print()
    
    # 자동으로 브라우저 열기 여부 묻기
    try:
        response = input('🌐 Supabase SQL Editor를 자동으로 열까요? (y/n): ').lower().strip()
        if response in ['y', 'yes', '예', 'ㅇ']:
            print('🔗 브라우저에서 Supabase SQL Editor를 엽니다...')
            webbrowser.open(sql_editor_url)
            print('✅ 브라우저가 열렸습니다!')
        else:
            print('💡 수동으로 접속하세요:', sql_editor_url)
    except KeyboardInterrupt:
        print('\n👋 설정이 취소되었습니다.')
        return False
    
    print()
    print('🎉 설정이 완료되면 다음 명령어로 테스트하세요:')
    print('python3 main.py')
    
    return True

def verify_mcp_setup():
    """MCP 설정 확인"""
    print('🔧 MCP 설정 확인:')
    
    # MCP 서버 목록 확인
    try:
        import subprocess
        result = subprocess.run(['claude', 'mcp', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print('✅ MCP 서버 설정 확인됨:')
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f'   - {line}')
        else:
            print('⚠️ MCP 서버 설정을 확인할 수 없습니다')
    except Exception as e:
        print(f'⚠️ MCP 확인 중 오류: {e}')
    
    print()

def create_mcp_config():
    """프로젝트용 MCP 설정 파일 생성"""
    print('📝 프로젝트 MCP 설정 파일 생성 중...')
    
    mcp_config = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "/Users/DoohanIT/VOOTCAMPPHV1/vootcamp_ph_scraper"]
            },
            "web": {
                "command": "npx", 
                "args": ["@modelcontextprotocol/server-web"]
            }
        }
    }
    
    # .mcp.json 파일 생성
    import json
    with open('.mcp.json', 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    print('✅ .mcp.json 파일이 생성되었습니다')
    print()

if __name__ == "__main__":
    print('🔧 MCP 통합 Supabase 설정을 시작합니다...')
    print()
    
    # MCP 설정 확인
    verify_mcp_setup()
    
    # 프로젝트 MCP 설정 생성
    create_mcp_config()
    
    # Supabase 설정 안내
    success = open_supabase_sql_editor()
    
    sys.exit(0 if success else 1)