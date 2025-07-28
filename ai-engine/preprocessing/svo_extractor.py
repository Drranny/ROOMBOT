from .keyword_extractor import extract_keywords

def analyze_svo(text: str, lang: str, api_key: str = None, method: str = "okt"):
    """
    언어별 키워드 추출 통합 함수 (기존 SVO 추출기 대체)
    
    Args:
        text: 분석할 텍스트
        lang: 언어 ("ko" 또는 "en")
        api_key: 사용하지 않음 (하위 호환성을 위해 유지)
        method: 한국어 태거 방법 ("okt", "komoran", "hannanum")
    
    Returns:
        키워드 추출 결과
    """
    return extract_keywords(text, lang, method)
