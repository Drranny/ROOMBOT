from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import re
import urllib.parse
import logging
try:
    from services.text_summarizer import TextSummarizer
    from services.synonym_finder import SynonymFinder
except ImportError:
    from backend.services.text_summarizer import TextSummarizer
    from backend.services.synonym_finder import SynonymFinder

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_keyword_summary(text: str, keywords: List[str]) -> str:
    """
    키워드 기반 요약 함수
    키워드 주변의 문장을 추출하여 요약합니다.
    """
    if not keywords:
        return text[:80] + "..." if len(text) > 80 else text
    
    # 키워드 위치 찾기
    keyword_positions = []
    for keyword in keywords:
        pos = text.lower().find(keyword.lower())
        if pos != -1:
            keyword_positions.append((pos, keyword))
    
    if not keyword_positions:
        return text[:80] + "..." if len(text) > 80 else text
    
    # 가장 앞쪽 키워드 위치 기준으로 요약
    keyword_positions.sort(key=lambda x: x[0])
    start_pos = max(0, keyword_positions[0][0] - 30)
    end_pos = min(len(text), keyword_positions[0][0] + 50)
    
    summary = text[start_pos:end_pos].strip()
    
    # 문장 경계 조정
    if start_pos > 0:
        # 앞쪽에서 문장 시작점 찾기
        for i in range(start_pos, max(0, start_pos - 20), -1):
            if text[i] in '.!?':
                summary = text[i+1:end_pos].strip()
                break
    
    if end_pos < len(text):
        # 뒤쪽에서 문장 끝점 찾기
        for i in range(end_pos, min(len(text), end_pos + 20)):
            if text[i] in '.!?':
                summary = text[start_pos:i+1].strip()
                break
    
    return summary if len(summary) > 20 else text[:80] + "..."

router = APIRouter()

class WikipediaMultiRequest(BaseModel):
    main_keyword: str
    keywords: List[str]

class WikipediaFilteredResponse(BaseModel):
    sentence: str
    original_sentence: str = ""  # 원본 문장 저장
    url: str
    matched_keywords: List[str]
    summary_method: str = ""  # 요약 방식 표시 (GPT, 키워드, 원본)

@router.post("/wikipedia/search")
def search_wikipedia_multi(data: WikipediaMultiRequest):
    # 언어 자동 감지 (한글/영어) - 더 정확한 감지
    lang = "ko"
    # 영어 문자가 더 많으면 영어로 설정
    english_chars = len(re.findall(r'[a-zA-Z]', data.main_keyword))
    korean_chars = len(re.findall(r'[가-힣]', data.main_keyword))
    
    if english_chars > korean_chars or (english_chars > 0 and korean_chars == 0):
        lang = "en"
        logger.info(f"영어로 감지됨: {data.main_keyword} (영어: {english_chars}, 한글: {korean_chars})")
    else:
        logger.info(f"한국어로 감지됨: {data.main_keyword} (영어: {english_chars}, 한글: {korean_chars})")
    
    encoded_keyword = urllib.parse.quote(data.main_keyword)
    
    # MediaWiki API를 사용하여 전체 문서 내용 가져오기
    S = requests.Session()
    
    # 1. 페이지 ID 찾기
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "format": "json",
        "titles": data.main_keyword,
        "prop": "info"
    }
    
    response = S.get(search_url, params=search_params)
    logger.info(f"페이지 검색 URL: {response.url}")
    logger.info(f"페이지 검색 상태: {response.status_code}")
    
    if response.status_code != 200:
        raise HTTPException(status_code=404, detail="Wikipedia page not found")
    
    search_result = response.json()
    logger.info(f"페이지 검색 결과: {search_result}")
    
    pages = search_result.get("query", {}).get("pages", {})
    
    if not pages or "-1" in pages:
        raise HTTPException(status_code=404, detail="Wikipedia page not found")
    
    page_id = list(pages.keys())[0]
    logger.info(f"페이지 ID: {page_id}")
    
    # 2. 전체 문서 내용 가져오기
    content_params = {
        "action": "query",
        "format": "json",
        "pageids": page_id,
        "prop": "extracts",
        "exintro": "false",  # 소개 섹션만이 아닌 전체 내용
        "explaintext": "true",  # 텍스트 형식으로 반환
        "exsectionformat": "plain",
        "exlimit": "max"  # 최대한 많은 내용 가져오기
    }
    
    content_response = S.get(search_url, params=content_params)
    logger.info(f"내용 가져오기 URL: {content_response.url}")
    logger.info(f"내용 가져오기 상태: {content_response.status_code}")
    
    if content_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to get Wikipedia content")
    
    content_result = content_response.json()
    logger.info(f"내용 가져오기 결과: {content_result}")
    
    content_pages = content_result.get("query", {}).get("pages", {})
    
    if page_id not in content_pages:
        raise HTTPException(status_code=404, detail="Wikipedia content not found")
    
    full_content = content_pages[page_id].get("extract", "")
    logger.info(f"가져온 내용 길이: {len(full_content)}")
    logger.info(f"가져온 내용 일부: {full_content[:200]}...")
    
    # 만약 MediaWiki API에서 내용을 가져오지 못했다면 REST API 시도
    if len(full_content) == 0:
        logger.info("MediaWiki API에서 내용을 가져오지 못함. REST API 시도...")
        rest_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/html/{encoded_keyword}"
        rest_response = S.get(rest_url)
        if rest_response.status_code == 200:
            # HTML에서 텍스트 추출 (간단한 방법)
            html_content = rest_response.text
            # HTML 태그 제거
            text_content = re.sub(r'<[^>]+>', '', html_content)
            # 여러 공백을 하나로
            text_content = re.sub(r'\s+', ' ', text_content)
            full_content = text_content.strip()
            logger.info(f"REST API에서 가져온 내용 길이: {len(full_content)}")
        else:
            logger.error(f"REST API 호출 실패: {rest_response.status_code}")
    
    # 3. URL 정보 가져오기 (REST API 사용)
    rest_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{encoded_keyword}"
    rest_response = S.get(rest_url)
    url = ""
    if rest_response.status_code == 200:
        rest_result = rest_response.json()
        url = rest_result.get("content_urls", {}).get("desktop", {}).get("page", "")
    
    # 4. 유사어 찾기 및 확장된 키워드 생성
    logger.info(f"전체 문서 길이: {len(full_content)} 문자")
    logger.info(f"원본 검색 키워드: {data.keywords}")
    
    # 유사어 찾기
    synonym_finder = SynonymFinder()
    all_keywords = data.keywords.copy()
    
    for keyword in data.keywords:
        synonyms = synonym_finder.find_synonyms(keyword)
        # 유사어 중에서 원본 키워드와 다른 것만 추가
        for synonym in synonyms:
            if synonym != keyword and synonym not in all_keywords:
                all_keywords.append(synonym)
    
    logger.info(f"확장된 검색 키워드: {all_keywords}")
    
    # 5. 문장 분리 및 키워드 점수 계산 (검색 시점에서 중복 제거)
    sentences = re.split(r'[.!?\n]', full_content)
    logger.info(f"분리된 문장 수: {len(sentences)}")
    
    sentence_scores = []
    
    for i, sent in enumerate(sentences):
        sent = sent.strip()
        if len(sent) < 10:  # 너무 짧은 문장 제외
            continue
        
        # 키워드 매칭 및 점수 계산 (검색 시점에서 중복 제거)
        matched_keywords = []
        keyword_score = 0
        used_synonym_groups = set()  # 이미 사용된 유사어 그룹 추적
        
        for keyword in all_keywords:
            if keyword in sent:
                # 해당 키워드가 속한 유사어 그룹 확인
                synonym_group = synonym_finder._get_synonym_group(keyword)
                
                # 이미 해당 그룹의 키워드가 사용되었는지 확인
                if synonym_group not in used_synonym_groups:
                    matched_keywords.append(keyword)
                    used_synonym_groups.add(synonym_group)
                    
                    # 원본 키워드에 더 높은 점수 부여
                    if keyword in data.keywords:
                        keyword_score += 2
                    else:
                        keyword_score += 1
        
        if len(matched_keywords) >= 1:
            sentence_scores.append({
                'sentence': sent,
                'matched_keywords': matched_keywords,
                'keyword_score': keyword_score,
                'index': i
            })
    
    # 키워드 점수로 정렬 (높은 점수 우선)
    sentence_scores.sort(key=lambda x: x['keyword_score'], reverse=True)
    
    # 상위 문장들만 선택 (테스트용으로 10개로 제한)
    top_sentences = sentence_scores[:10]  # 상위 10개 문장
    
    filtered = []
    for item in top_sentences:
        logger.info(f"매칭된 문장 {item['index']}: {item['sentence'][:100]}... (키워드: {item['matched_keywords']}, 점수: {item['keyword_score']})")
        filtered.append(WikipediaFilteredResponse(
            sentence=item['sentence'], 
            original_sentence=item['sentence'],  # 원본 문장 저장
            url=url, 
            matched_keywords=item['matched_keywords']
        ))
    
    logger.info(f"최종 필터링된 문장 수: {len(filtered)}")
    
    # 5. 문장 요약 (GPT API 한도 고려하여 상위 10개만 요약)
    if filtered:
        try:
            logger.info("문장 요약 시작...")
            
            # GPT 요약 활성화 (테스트용으로 모든 10개 문장)
            for i, item in enumerate(filtered):
                original_sentence = item.sentence
                
                # 문장이 충분히 길면 GPT 요약 시도 (30단어 이상)
                if len(original_sentence.split()) > 30:
                    try:
                        # GPT-4o-mini 서비스 import
                        try:
                            from backend.services.gpt4_summarizer import summarize_with_gpt4
                        except ImportError:
                            from services.gpt4_summarizer import summarize_with_gpt4
                        
                        # GPT-4o-mini에게 요약 요청
                        summary = summarize_with_gpt4(original_sentence, item.matched_keywords)
                        
                        # 요약 결과가 너무 길면 자르기
                        if len(summary) > 80:
                            summary = summary[:80] + "..."
                        
                        item.sentence = summary
                        item.summary_method = "GPT-4o-mini"
                        logger.info(f"문장 {i+1} GPT-4o-mini 요약: {original_sentence[:50]}... -> {summary}")
                        
                    except Exception as e:
                        logger.error(f"GPT-4o-mini 요약 실패 (문장 {i+1}): {str(e)}")
                        # GPT 요약 실패시 키워드 기반 요약 사용
                        summary = extract_keyword_summary(original_sentence, item.matched_keywords)
                        if len(summary) > 80:
                            summary = summary[:80] + "..."
                        item.sentence = summary
                        item.summary_method = "키워드 요약"
                        logger.info(f"문장 {i+1} 키워드 요약 (GPT 실패): {original_sentence[:50]}... -> {summary}")
                else:
                    # 짧은 문장은 요약하지 않음 (30단어 이하)
                    item.summary_method = "원본 (짧음)"
                    logger.info(f"문장 {i+1} 너무 짧음 (30단어 이하): {len(original_sentence.split())}단어")
            

            

                
            logger.info(f"문장 요약 완료: {len(filtered)}개 문장")
            
        except Exception as e:
            logger.error(f"문장 요약 중 오류 발생: {str(e)}")
            pass
    
    # 확장된 키워드 정보와 함께 반환
    return {
        "candidates": filtered,
        "expanded_keywords": all_keywords,
        "original_keywords": data.keywords
    } 