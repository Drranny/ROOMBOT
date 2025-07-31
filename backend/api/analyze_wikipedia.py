from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
try:
    from backend.services.sentence_similarity import SentenceSimilarityCalculator
except ImportError:
    from services.sentence_similarity import SentenceSimilarityCalculator
import logging
import pandas as pd
from datetime import datetime
import os

router = APIRouter()

class AnalyzeWikipediaRequest(BaseModel):
    query: str  # 기준 문장
    keywords: List[str]
    main_keyword: str  # wikipedia 검색용 대표 키워드
    top_k: int = 5
    save_excel: bool = True  # Excel 저장 여부

class WikipediaCandidate(BaseModel):
    sentence: str
    original_sentence: str = ""  # 원본 문장
    matched_keywords: List[str]
    url: str
    similarity: float
    nli_label: str
    nli_score: float
    final_score: float
    summary_method: str = ""  # 요약 방식 표시

@router.post("/analyze/wikipedia")
def analyze_wikipedia(req: AnalyzeWikipediaRequest):
    # 1. Wikipedia 후보군 수집
    try:
        wiki_resp = requests.post(
            "http://127.0.0.1:8000/wikipedia/search",
            json={
                "main_keyword": req.main_keyword,
                "keywords": req.keywords
            },
            timeout=60  # 10초 → 60초로 증가
        )
        if wiki_resp.status_code != 200:
            logging.error(f"Wikipedia API status: {wiki_resp.status_code}, body: {wiki_resp.text}")
            raise HTTPException(status_code=500, detail=f"Wikipedia API 호출 실패: {wiki_resp.status_code}, {wiki_resp.text}")
        wiki_data = wiki_resp.json()
        
        # 확장된 키워드 정보 추출 (Wikipedia API에서 반환된 경우)
        expanded_keywords = []
        original_keywords = req.keywords
        if isinstance(wiki_data, dict) and "candidates" in wiki_data:
            expanded_keywords = wiki_data.get("expanded_keywords", req.keywords)
            original_keywords = wiki_data.get("original_keywords", req.keywords)
            wiki_candidates = wiki_data["candidates"]
        else:
            # 확장된 키워드 정보가 없는 경우 원본 키워드 사용
            expanded_keywords = req.keywords
            wiki_candidates = wiki_data
            
    except Exception as e:
        logging.exception("Wikipedia API 호출 중 예외 발생")
        raise HTTPException(status_code=500, detail=f"Wikipedia API 호출 실패: {str(e)}")

    if not wiki_candidates:
        return []

    # 2. SBERT 유사도 계산 (모든 후보에 대해)
    sim_calc = SentenceSimilarityCalculator('paraphrase-multilingual-MiniLM-L12-v2')
    all_candidates_with_scores = []
    
    for c in wiki_candidates:
        sim = sim_calc.calculate_similarity(req.query, c["sentence"])
        similarity_score = sim.get("cosine_similarity", 0.0)
        c["similarity"] = similarity_score
        
        # Excel 저장용 데이터 추가
        all_candidates_with_scores.append({
            "sentence": c["sentence"],
            "original_sentence": c.get("original_sentence", ""),  # 원본 문장 추가
            "matched_keywords": ", ".join(c["matched_keywords"]),
            "url": c["url"],
            "similarity_score": similarity_score,
            "query_sentence": req.query,
            "search_keywords": ", ".join(req.keywords),
            "main_keyword": req.main_keyword
        })

    # 3. Excel 파일 저장 (모든 후보 문장)
    if req.save_excel and all_candidates_with_scores:
        try:
            # 저장 디렉토리 생성 (프로젝트 루트에 저장)
            import os
            current_dir = os.getcwd()
            if current_dir.endswith('backend'):
                # backend 디렉토리에서 실행 중이면 상위로 이동
                os.chdir('..')
            
            os.makedirs("wikipedia_analysis_results", exist_ok=True)
            
            # 타임스탬프를 포함한 파일명 생성
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wikipedia_analysis_results/wiki_analysis_{timestamp}.xlsx"
            
            # DataFrame 생성 및 Excel 저장
            df = pd.DataFrame(all_candidates_with_scores)
            
            # 유사도 점수로 정렬
            df = df.sort_values('similarity_score', ascending=False)
            
            # Excel 파일로 저장
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All_Candidates', index=False)
                
                # 요약 정보 시트 추가
                summary_data = {
                    "분석 정보": [
                        "기준 문장", req.query,
                        "검색 키워드", ", ".join(req.keywords),
                        "대표 키워드", req.main_keyword,
                        "총 후보 문장 수", len(all_candidates_with_scores),
                        "최고 유사도 점수", df['similarity_score'].max() if not df.empty else 0,
                        "평균 유사도 점수", df['similarity_score'].mean() if not df.empty else 0,
                        "분석 시간", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            logging.info(f"Excel 파일 저장 완료: {filename}")
            
        except Exception as e:
            logging.error(f"Excel 파일 저장 실패: {str(e)}")

    # 4. 상위 top_k 후보만 추림
    candidates = sorted(wiki_candidates, key=lambda x: x["similarity"], reverse=True)[:req.top_k]

    # 5. NLI 판별
    for c in candidates:
        nli_payload = {"premise": req.query, "hypothesis": c["sentence"]}
        try:
            nli_resp = requests.post("http://localhost:8004/nli", json=nli_payload, timeout=10)
            nli_data = nli_resp.json()
            c["nli_label"] = nli_data.get("label", "unknown")
            c["nli_score"] = nli_data.get("score", 0.0)
        except Exception:
            c["nli_label"] = "error"
            c["nli_score"] = 0.0

    # 6. 최종 점수 계산 (프론트엔드에서 계산하므로 여기서는 기본값 설정)
    for c in candidates:
        c["final_score"] = c["similarity"]  # 기본값으로 유사도 점수 사용
    
    # 7. 최종 정렬 및 반환
    candidates = sorted(candidates, key=lambda x: x["final_score"], reverse=True)
    
    # Wikipedia API에서 확장된 키워드 정보를 포함하여 반환
    response_data = {
        "candidates": [WikipediaCandidate(**c) for c in candidates],
        "expanded_keywords": expanded_keywords,
        "original_keywords": original_keywords
    }
    
    return response_data 