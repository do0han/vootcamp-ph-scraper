'AI 리포트 생성기' 구현 계획 (v1.0)
목표: Supabase에 저장된 '분석 완료된 데이터'와 '사용자 프로필'을 입력받아, OpenAI GPT-4o API를 통해 개인화된 '콘텐츠 전략 리포트' 텍스트를 자동으로 생성하는 Python 모듈을 구현한다.

1단계: 데이터 입력 및 준비 (AI를 위한 '재료' 준비)
구현 위치: ai/report_generator.py 파일 안에 새로운 클래스 AIReportGenerator를 만듭니다.
핵심 로직:
데이터베이스 연결: supabase_client를 사용하여 Supabase에 연결합니다.
데이터 가져오기:
사용자 프로필: 특정 user_id를 기반으로 users 테이블에서 페르소나, MBTI, 관심 키워드 등을 가져옵니다.
분석된 이벤트 데이터: analyzed_events 테이블에서 '기회 점수'가 높은 상위 1~2개의 최신 이벤트를 가져옵니다.
분석된 상품 데이터: analyzed_products 테이블(미래에 만들) 또는 현재의 lazada_products, tiktok_shop_products 테이블에서 사용자의 페르소나와 관련된 상위 1~2개의 트렌드 상품을 가져옵니다.
데이터 정제: 가져온 모든 데이터를 AI가 이해하기 쉬운 깔끔한 텍스트나 JSON 형식으로 가공합니다.
Cursor에게 내릴 명령 예시:
"Python으로 ai/report_generator.py 파일 안에 AIReportGenerator 클래스를 만들어 줘. 이 클래스는 user_id를 입력받아서, supabase_client를 통해 users, analyzed_events, lazada_products 테이블에서 해당 사용자와 관련된 최신 데이터를 가져오는 메소드를 포함해야 해."

2단계: '마스터 프롬프트' 설계 및 API 호출 (AI에게 '요리법' 지시)
구현 위치: AIReportGenerator 클래스 내에, 리포트를 생성하는 핵심 메소드(예: generate_report)를 만듭니다.
핵심 로직:
마스터 프롬프트 정의: 이것이 가장 중요합니다. 우리는 이전에 함께 설계했던 '마스터 프롬프트'를 이 메소드 안에 함수나 변수 형태로 정의합니다. 이 프롬프트는 AI에게 '역할', '목표', '출력 형식', '가이드라인'을 명확하게 지시합니다.
동적 데이터 삽입: 1단계에서 준비한 '사용자 프로필'과 '최신 트렌드 데이터'를 이 마스터 프롬프트 템플릿의 지정된 위치에 동적으로 삽입합니다.
OpenAI API 호출: 완성된 최종 프롬프트를 가지고, openai Python 라이브러리를 사용하여 GPT-4o 모델에 요청을 보냅니다.
결과 수신: AI가 생성한 '콘텐츠 전략 리포트' 텍스트를 응답으로 받습니다.
Cursor에게 내릴 명령 예시:
"이전에 우리가 설계했던 '마스터 프롬프트'를 Python 함수로 만들어 줘. 이 함수는 user_profile과 trend_data를 인자로 받아서, 포맷된 최종 프롬프트 문자열을 반환해야 해. 그 다음, openai 라이브러리를 사용해서 이 프롬프트를 GPT-4o 모델에 보내고, 생성된 텍스트 응답을 받아오는 코드를 작성해 줘."

3단계: 결과 저장 및 후처리 (완성된 '요리' 플레이팅)
구현 위치: generate_report 메소드의 마지막 부분.
핵심 로직:
리포트 저장: AI가 생성한 최종 리포트 텍스트를 Supabase의 content_reports 테이블에 해당 user_id와 함께 저장합니다.
포맷팅 (선택사항): 생성된 텍스트를 나중에 웹 대시보드에서 더 예쁘게 보여주기 위해, Markdown 형식이나 HTML 형식으로 변환할 수 있습니다.
알림 (선택사항): 리포트 생성이 완료되면, 슬랙(Slack)이나 이메일을 통해 "Zaila Mae를 위한 리포트 생성이 완료되었습니다. 검수 후 발송해주세요." 와 같은 알림을 관리자(당신)에게 보냅니다.
Cursor에게 내릴 명령 예시:
"GPT-4o API로부터 받은 텍스트 응답을 content_reports 테이블에 저장하는 Supabase 연동 코드를 추가해 줘. 저장할 때는 user_id, report_title, report_body 컬럼을 사용해야 해."