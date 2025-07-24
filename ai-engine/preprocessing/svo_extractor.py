from .svo_extractor_en import analyze_svo_from_text as analyze_svo_en
from .svo_extractor_ko import analyze_svo_ko
from .sentence_validator import SentenceValidator

def analyze_svo(text: str, lang: str = "en", api_key: str = None):
    """
    텍스트에서 SVO 구조를 추출하는 통합 함수
    
    Args:
        text (str): 분석할 텍스트
        lang (str): 언어 ("en" 또는 "ko")
        api_key (str): ETRI API 키 (한국어 분석 시 필요)
    
    Returns:
        dict: SVO 분석 결과
    """
    if lang == "ko":
        return analyze_svo_ko(text, api_key)
    else:
        return analyze_svo_en(text)

def validate_and_analyze_svo(text: str, lang: str = "en", api_key: str = None):
    """
    문장 검증 후 SVO 분석을 수행하는 통합 함수
    
    Args:
        text (str): 분석할 텍스트
        lang (str): 언어 ("en" 또는 "ko")
        api_key (str): ETRI API 키 (한국어 분석 시 필요)
    
    Returns:
        dict: 검증 및 SVO 분석 결과
    """
    validator = SentenceValidator()
    
    # 문장 검증
    validation_result = validator.validate_text(text)
    
    # 유효한 문장들만 SVO 분석
    valid_sentences = validation_result.get("valid_sentences", [])
    svo_results = []
    
    for sentence_info in valid_sentences:
        sentence = sentence_info.get("sentence", "")
        if sentence:
            svo_result = analyze_svo(sentence, lang, api_key)
            svo_results.append({
                "sentence": sentence,
                "svo": svo_result,
                "validation": sentence_info
            })
    
    return {
        "validation": validation_result,
        "svo_analysis": svo_results,
        "summary": {
            "total_sentences": len(validation_result.get("valid_sentences", [])),
            "analyzed_sentences": len(svo_results),
            "language": lang
        }
    }
