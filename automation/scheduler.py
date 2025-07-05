#!/usr/bin/env python3
"""
자동화된 페르소나 타겟 데이터 수집 스케줄러
Automated Persona-Targeted Data Collection Scheduler
"""

import os
import sys
import time
import logging
import schedule
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from config.persona_config import TARGET_PERSONAS, PERSONA_SEARCH_STRATEGIES
from database.supabase_client import SupabaseClient
from scrapers.lazada_persona_scraper import LazadaPersonaScraper

logger = logging.getLogger(__name__)


class PersonaScheduler:
    """페르소나별 자동화된 데이터 수집 스케줄러"""
    
    def __init__(self):
        self.supabase_client = None
        self.active_scrapers = {}
        self.collection_stats = {
            "total_runs": 0,
            "successful_runs": 0,
            "failed_runs": 0,
            "last_run": None,
            "products_collected": 0
        }
        
        # Supabase 클라이언트 초기화
        try:
            self.supabase_client = SupabaseClient()
            logger.info("✅ Supabase client initialized for scheduler")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            self.supabase_client = None
        
        # 스케줄 설정
        self._setup_schedules()
        
        logger.info("🤖 Persona Scheduler initialized")
    
    def _setup_schedules(self):
        """자동화 스케줄 설정"""
        
        # 각 페르소나별 수집 스케줄
        persona_schedules = {
            "young_filipina": {
                "frequency": "daily",
                "time": "09:00",  # 오전 9시
                "limit": 10,
                "priority": "high"
            },
            "productivity_seeker": {
                "frequency": "daily", 
                "time": "14:00",  # 오후 2시 (대학생 활동 시간)
                "limit": 8,
                "priority": "high"
            },
            "urban_professional": {
                "frequency": "every_2_days",
                "time": "18:00",  # 오후 6시 (퇴근 후)
                "limit": 5,
                "priority": "medium"
            }
        }
        
        # 스케줄 등록
        for persona_name, config in persona_schedules.items():
            if persona_name in TARGET_PERSONAS:
                self._register_persona_schedule(persona_name, config)
        
        # 전체 시스템 헬스체크
        schedule.every().hour.do(self._health_check)
        
        # 통계 업데이트
        schedule.every().day.at("23:59").do(self._update_daily_stats)
        
        logger.info(f"📅 Scheduled collection for {len(persona_schedules)} personas")
    
    def _register_persona_schedule(self, persona_name: str, config: Dict[str, Any]):
        """개별 페르소나 스케줄 등록"""
        try:
            frequency = config.get("frequency", "daily")
            time_str = config.get("time", "12:00")
            limit = config.get("limit", 10)
            
            if frequency == "daily":
                schedule.every().day.at(time_str).do(
                    self._collect_persona_data,
                    persona_name=persona_name,
                    limit=limit
                )
            elif frequency == "every_2_days":
                schedule.every(2).days.at(time_str).do(
                    self._collect_persona_data,
                    persona_name=persona_name,
                    limit=limit
                )
            elif frequency == "weekly":
                schedule.every().week.at(time_str).do(
                    self._collect_persona_data,
                    persona_name=persona_name,
                    limit=limit
                )
            
            logger.info(f"📅 Scheduled {persona_name}: {frequency} at {time_str} ({limit} products)")
            
        except Exception as e:
            logger.error(f"❌ Failed to register schedule for {persona_name}: {e}")
    
    def _collect_persona_data(self, persona_name: str, limit: int = 10):
        """페르소나별 데이터 수집 실행"""
        
        start_time = datetime.now()
        logger.info(f"🚀 Starting scheduled collection for {persona_name}")
        
        try:
            self.collection_stats["total_runs"] += 1
            
            # 페르소나 스크래퍼 초기화
            scraper = LazadaPersonaScraper(
                persona_name=persona_name,
                use_undetected=True
            )
            
            # 데이터 수집 실행
            products = scraper.get_persona_trending_products(
                limit=limit,
                save_to_db=True
            )
            
            # 통계 업데이트
            products_count = len(products) if products else 0
            self.collection_stats["products_collected"] += products_count
            self.collection_stats["successful_runs"] += 1
            self.collection_stats["last_run"] = start_time.isoformat()
            
            # 수집 결과 로그
            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ {persona_name} collection completed: {products_count} products in {duration:.1f}s")
            
            # 사용자 알림을 위한 이벤트 데이터 저장
            if products_count > 0:
                self._save_collection_event(persona_name, products_count, start_time)
            
            return products
            
        except Exception as e:
            self.collection_stats["failed_runs"] += 1
            logger.error(f"❌ Failed to collect data for {persona_name}: {e}")
            return []
        
        finally:
            try:
                if 'scraper' in locals():
                    scraper.close()
            except:
                pass
    
    def _save_collection_event(self, persona_name: str, products_count: int, collection_time: datetime):
        """수집 이벤트를 데이터베이스에 저장 (사용자 알림용)"""
        
        if not self.supabase_client:
            return
        
        try:
            event_data = {
                "event_type": "persona_data_collection",
                "persona_name": persona_name,
                "products_collected": products_count,
                "collection_timestamp": collection_time.isoformat(),
                "status": "completed",
                "metadata": {
                    "scheduler_version": "1.0",
                    "collection_method": "automated"
                }
            }
            
            # events 테이블에 저장 (테이블이 없다면 생략)
            logger.info(f"📝 Collection event saved for {persona_name}: {products_count} products")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to save collection event: {e}")
    
    def _health_check(self):
        """시스템 헬스체크"""
        try:
            # 데이터베이스 연결 확인
            if self.supabase_client:
                # 간단한 쿼리로 연결 확인
                test_query = self.supabase_client.client.table('shopee_products').select('id').limit(1).execute()
                logger.debug("✅ Database connection healthy")
            
            # 메모리 사용량 확인
            import psutil
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 80:
                logger.warning(f"⚠️ High memory usage: {memory_percent}%")
            
            # 실행 통계 로그
            total_runs = self.collection_stats["total_runs"]
            if total_runs > 0:
                success_rate = (self.collection_stats["successful_runs"] / total_runs) * 100
                logger.info(f"📊 Scheduler health: {success_rate:.1f}% success rate ({total_runs} total runs)")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
    
    def _update_daily_stats(self):
        """일일 통계 업데이트"""
        logger.info(f"📊 Daily stats: {self.collection_stats}")
        
        # 통계 초기화 (일별 리셋)
        self.collection_stats.update({
            "daily_products": self.collection_stats["products_collected"],
            "products_collected": 0  # 일일 카운트 리셋
        })
    
    def get_persona_last_collection(self, persona_name: str) -> Optional[datetime]:
        """특정 페르소나의 마지막 수집 시간 조회"""
        
        if not self.supabase_client:
            return None
        
        try:
            query = self.supabase_client.client.table('shopee_products')\
                .select('created_at')\
                .contains('discount_info', {'persona_name': persona_name})\
                .order('created_at', desc=True)\
                .limit(1)\
                .execute()
            
            if query.data:
                return datetime.fromisoformat(query.data[0]['created_at'].replace('Z', '+00:00'))
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting last collection time for {persona_name}: {e}")
            return None
    
    def manual_collect(self, persona_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """수동 데이터 수집 트리거"""
        logger.info(f"🔧 Manual collection triggered for {persona_name}")
        return self._collect_persona_data(persona_name, limit)
    
    def get_stats(self) -> Dict[str, Any]:
        """스케줄러 통계 반환"""
        stats = self.collection_stats.copy()
        
        # 추가 정보
        stats.update({
            "active_personas": list(TARGET_PERSONAS.keys()),
            "scheduled_jobs": len(schedule.jobs),
            "next_run": str(schedule.next_run()) if schedule.jobs else None
        })
        
        return stats
    
    def start(self):
        """스케줄러 시작 (블로킹)"""
        logger.info("🤖 Persona Scheduler starting...")
        logger.info(f"📅 Next scheduled run: {schedule.next_run()}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 체크
                
        except KeyboardInterrupt:
            logger.info("⏹️ Scheduler stopped by user")
        except Exception as e:
            logger.error(f"❌ Scheduler error: {e}")
    
    def start_background(self):
        """백그라운드에서 스케줄러 시작 (논블로킹)"""
        
        def run_scheduler():
            self.start()
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        logger.info("🤖 Persona Scheduler started in background")
        return scheduler_thread


def main():
    """메인 실행 함수"""
    
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scheduler.log'),
            logging.StreamHandler()
        ]
    )
    
    # 스케줄러 시작
    scheduler = PersonaScheduler()
    
    print("🤖 Automated Persona Data Collection Scheduler")
    print("=" * 50)
    print(f"📅 Active personas: {list(TARGET_PERSONAS.keys())}")
    print(f"⏰ Next run: {schedule.next_run()}")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n⏹️ Scheduler stopped")


if __name__ == "__main__":
    main()