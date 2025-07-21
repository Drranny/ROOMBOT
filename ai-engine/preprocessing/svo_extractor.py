from .svo_extractor_en import analyze_svo_en
from .svo_extractor_ko import analyze_svo_ko
from .svo_extractor_konlpy import analyze_svo_konlpy

def analyze_svo(text: str, lang: str, api_key: str = None, method: str = "etri"):
    """
    언어별 SVO 추출 통합 함수
    
    Args:
        text: 분석할 텍스트
        lang: 언어 ("ko" 또는 "en")
        api_key: ETRI API 키 (한국어 ETRI 방식 사용 시)
        method: 분석 방법 ("etri" 또는 "konlpy" - 한국어만 해당)
    """
    if lang == "ko":
        if method == "konlpy":
            return analyze_svo_konlpy(text)
        else:
            return analyze_svo_ko(text, api_key)
    return analyze_svo_en(text)
