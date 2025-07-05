#!/usr/bin/env python3
"""
사용자 대시보드 API - 페르소나별 맞춤형 데이터 제공
User Dashboard API - Persona-Targeted Data Service
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

from config.persona_config import TARGET_PERSONAS, get_persona_filters
from database.supabase_client import SupabaseClient
from ai.report_generator import PersonaReportGenerator
from automation.scheduler import PersonaScheduler

logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="Vootcamp PH Dashboard API",
    description="페르소나 기반 맞춤형 상품 데이터 및 인사이트 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 서비스 인스턴스
supabase_client = None
report_generator = None
scheduler = None

# Pydantic 모델들
class UserRequest(BaseModel):
    user_id: str
    persona_name: Optional[str] = None

class PersonaFilter(BaseModel):
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rating_min: Optional[float] = None
    category: Optional[str] = None
    limit: Optional[int] = 20

class ProductResponse(BaseModel):
    id: int
    product_name: str
    price: Optional[float]
    rating: Optional[float]
    persona_score: Optional[float]
    category: str
    product_url: Optional[str]
    image_url: Optional[str]

class DashboardData(BaseModel):
    user_id: str
    persona: str
    total_products: int
    avg_persona_score: float
    recommended_products: List[ProductResponse]
    insights: List[str]
    last_updated: str


@app.on_event("startup")
async def startup_event():
    """API 시작 시 초기화"""
    global supabase_client, report_generator, scheduler
    
    try:
        # 서비스 초기화
        supabase_client = SupabaseClient()
        report_generator = PersonaReportGenerator()
        scheduler = PersonaScheduler()
        
        logger.info("✅ Dashboard API services initialized")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {e}")


@app.get("/")
async def root():
    """API 상태 확인"""
    return {
        "service": "Vootcamp PH Dashboard API",
        "status": "running",
        "version": "1.0.0",
        "available_personas": list(TARGET_PERSONAS.keys()),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/personas")
async def get_personas():
    """사용 가능한 페르소나 목록 조회"""
    personas = {}
    
    for name, persona in TARGET_PERSONAS.items():
        personas[name] = {
            "name": persona.name,
            "age_group": persona.age_group.value,
            "gender": persona.gender.value,
            "interests": persona.interests[:5],  # 상위 5개만
            "description": f"{persona.age_group.value} {persona.gender.value} interested in {', '.join(persona.interests[:3])}"
        }
    
    return {"personas": personas}


@app.get("/user/{user_id}/persona")
async def get_user_persona(user_id: str):
    """사용자의 페르소나 정보 조회"""
    
    # 실제로는 Supabase의 users 테이블에서 조회해야 함
    # 현재는 시뮬레이션
    
    user_personas = {
        "just_elias": "productivity_seeker",
        "maria_santos": "young_filipina", 
        "anna_cruz": "urban_professional"
    }
    
    persona_name = user_personas.get(user_id.lower())
    
    if not persona_name:
        raise HTTPException(status_code=404, detail="User not found")
    
    persona = TARGET_PERSONAS.get(persona_name)
    filters = get_persona_filters(persona_name)
    
    return {
        "user_id": user_id,
        "persona_name": persona_name,
        "persona_info": {
            "name": persona.name,
            "age_group": persona.age_group.value,
            "gender": persona.gender.value,
            "interests": persona.interests,
            "price_ranges": filters.get("price_ranges", []),
            "max_budget": filters.get("max_price", 5000)
        }
    }


@app.get("/user/{user_id}/dashboard")
async def get_user_dashboard(user_id: str):
    """사용자 맞춤형 대시보드 데이터"""
    
    try:
        # 사용자 페르소나 확인
        user_persona_response = await get_user_persona(user_id)
        persona_name = user_persona_response["persona_name"]
        
        # 최근 제품 데이터 조회
        products = await get_persona_products(persona_name, limit=20)
        
        # AI 리포트 생성
        if report_generator:
            daily_report = report_generator.generate_daily_report(persona_name)
            insights = daily_report.get("actionable_insights", [])
        else:
            insights = ["서비스 초기화 중입니다."]
        
        # 통계 계산
        total_products = len(products["products"])
        avg_score = sum(p.get("persona_score", 0) for p in products["products"]) / max(1, total_products)
        
        # 상위 추천 제품 (점수 기준)
        recommended = sorted(
            products["products"], 
            key=lambda x: x.get("persona_score", 0), 
            reverse=True
        )[:5]
        
        dashboard_data = {
            "user_id": user_id,
            "persona": persona_name,
            "total_products": total_products,
            "avg_persona_score": round(avg_score, 1),
            "recommended_products": recommended,
            "insights": insights[:3],  # 상위 3개만
            "last_updated": datetime.now().isoformat(),
            "persona_info": user_persona_response["persona_info"]
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error generating dashboard for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate dashboard")


@app.get("/persona/{persona_name}/products")
async def get_persona_products(
    persona_name: str,
    limit: int = Query(20, ge=1, le=100),
    days_back: int = Query(7, ge=1, le=30),
    min_score: Optional[float] = Query(None, ge=0, le=100)
):
    """페르소나별 제품 데이터 조회"""
    
    if persona_name not in TARGET_PERSONAS:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    if not supabase_client:
        raise HTTPException(status_code=503, detail="Database service unavailable")
    
    try:
        # 날짜 필터
        cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # 쿼리 빌드
        query = supabase_client.client.table('shopee_products')\
            .select('*')\
            .contains('discount_info', {'persona_name': persona_name})\
            .gte('created_at', cutoff_date)\
            .order('created_at', desc=True)
        
        if limit:
            query = query.limit(limit)
        
        result = query.execute()
        products = result.data if result.data else []
        
        # 페르소나 점수 필터링
        if min_score is not None:
            products = [
                p for p in products 
                if p.get('discount_info', {}).get('persona_score', 0) >= min_score
            ]
        
        # 응답 데이터 포맷팅
        formatted_products = []
        for product in products:
            discount_info = product.get('discount_info', {})
            formatted_products.append({
                "id": product.get('id'),
                "product_name": product.get('product_name', 'Unknown'),
                "price": product.get('price'),
                "rating": product.get('rating'),
                "persona_score": discount_info.get('persona_score', 0),
                "category": product.get('category', 'general'),
                "product_url": product.get('product_url'),
                "image_url": product.get('image_url'),
                "brand_bonus": discount_info.get('brand_bonus', False),
                "collection_date": product.get('created_at')
            })
        
        return {
            "persona": persona_name,
            "products": formatted_products,
            "total_count": len(formatted_products),
            "filters_applied": {
                "days_back": days_back,
                "min_score": min_score,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching products for {persona_name}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch products")


@app.get("/persona/{persona_name}/report/{scenario}")
async def get_scenario_report(persona_name: str, scenario: str):
    """시나리오별 맞춤형 리포트 생성"""
    
    if persona_name not in TARGET_PERSONAS:
        raise HTTPException(status_code=404, detail="Persona not found")
    
    if not report_generator:
        raise HTTPException(status_code=503, detail="Report service unavailable")
    
    try:
        report = report_generator.generate_scenario_report(scenario, persona_name)
        
        if "error" in report:
            raise HTTPException(status_code=400, detail=report["error"])
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating scenario report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")


@app.post("/user/{user_id}/collect")
async def trigger_manual_collection(user_id: str, limit: int = Query(10, ge=1, le=50)):
    """사용자를 위한 수동 데이터 수집 트리거"""
    
    try:
        # 사용자 페르소나 확인
        user_persona_response = await get_user_persona(user_id)
        persona_name = user_persona_response["persona_name"]
        
        if not scheduler:
            raise HTTPException(status_code=503, detail="Scheduler service unavailable")
        
        # 수동 수집 실행
        products = scheduler.manual_collect(persona_name, limit)
        
        return {
            "user_id": user_id,
            "persona": persona_name,
            "collection_triggered": True,
            "products_collected": len(products) if products else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error triggering manual collection for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger collection")


@app.get("/system/stats")
async def get_system_stats():
    """시스템 통계 및 상태"""
    
    stats = {
        "api_status": "running",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "available" if supabase_client else "unavailable",
            "report_generator": "available" if report_generator else "unavailable", 
            "scheduler": "available" if scheduler else "unavailable"
        }
    }
    
    # 스케줄러 통계
    if scheduler:
        scheduler_stats = scheduler.get_stats()
        stats["scheduler"] = scheduler_stats
    
    # 데이터베이스 통계 (간단히)
    if supabase_client:
        try:
            # 전체 제품 수
            total_query = supabase_client.client.table('shopee_products').select('id', count='exact').execute()
            stats["database"] = {
                "total_products": total_query.count if total_query.count else 0,
                "status": "connected"
            }
        except:
            stats["database"] = {"status": "error"}
    
    return stats


# Just Elias 시나리오 전용 엔드포인트
@app.get("/elias/dashboard")
async def get_elias_dashboard():
    """Just Elias 전용 대시보드 (시연용)"""
    return await get_user_dashboard("just_elias")


@app.get("/elias/exam-report")
async def get_elias_exam_report():
    """Just Elias 시험 기간 리포트 (시연용)"""
    return await get_scenario_report("productivity_seeker", "exam_period")


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """API 서버 실행"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"🚀 Starting Dashboard API on {host}:{port}")
    logger.info(f"📋 Available personas: {list(TARGET_PERSONAS.keys())}")
    logger.info(f"🔗 API docs: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()