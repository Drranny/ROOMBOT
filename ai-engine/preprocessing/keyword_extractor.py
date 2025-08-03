import re
from typing import List, Dict, Any
from collections import Counter
import spacy

# Try to import KoNLPy, but handle the case where it fails
try:
    from konlpy.tag import Okt, Komoran, Hannanum
    # 실제로 초기화를 시도해보기
    test_okt = Okt()
    KONLPY_AVAILABLE = True
except Exception as e:
    print(f"Warning: KoNLPy not available: {e}")
    print("Korean NLP functionality will be disabled. Only English processing will work.")
    KONLPY_AVAILABLE = False
    # Create dummy classes for when KoNLPy is not available
    class Okt:
        def pos(self, text):
            return []
    
    class Komoran:
        def pos(self, text):
            return []
    
    class Hannanum:
        def pos(self, text):
            return []

class KeywordExtractor:
    """
    문장 길이에 따라 중요한 키워드를 추출하는 클래스
    """
    
    def __init__(self, lang: str = "ko"):
        self.lang = lang
        self.nlp = None
        
        if lang == "en":
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("spaCy 영어 모델이 설치되지 않았습니다. 'python -m spacy download en_core_web_sm' 실행 필요")
        
        # 한국어 태거 초기화 (only if KoNLPy is available)
        if KONLPY_AVAILABLE:
            try:
                self.ko_taggers = {
                    'okt': Okt(),
                    'komoran': Komoran(),
                    'hannanum': Hannanum()
                }
            except Exception as e:
                print(f"KoNLPy 초기화 실패: {e}")
                self.ko_taggers = {}
        else:
            self.ko_taggers = {}
    
    def extract_keywords(self, text: str, method: str = "okt") -> Dict[str, Any]:
        """
        문장에서 중요한 키워드를 추출.
        
        Args:
            text: 분석할 텍스트
            method: 한국어 태거 방법 ("okt", "komoran", "hannanum")
        
        Returns:
            키워드 추출 결과 딕셔너리
        """
        if self.lang == "ko":
            if not KONLPY_AVAILABLE or not self.ko_taggers:
                return {
                    "error": "KoNLPy가 설치되지 않았습니다. 한국어 처리가 불가능합니다.",
                    "original_text": text,
                    "language": "ko"
                }
            return self._extract_keywords_ko(text, method)
        else:
            return self._extract_keywords_en(text)
    
    def _extract_keywords_ko(self, text: str, method: str = "okt") -> Dict[str, Any]:
        """
        한국어 키워드 추출
        """
        # 문장 정제
        cleaned_text = self._clean_text(text)
        words = cleaned_text.split()
        word_count = len(words)
        
        # 형태소 분석
        tagger = self.ko_taggers.get(method, self.ko_taggers['okt'])
        pos_tags = tagger.pos(cleaned_text)
        
        # 의미있는 단어만 추출
        keywords = self._extract_all_words_ko(pos_tags, word_count)
        keyword_count = len(keywords)
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "word_count": word_count,
            "keyword_count": keyword_count,
            "keywords": keywords,
            "method": method,
            "language": "ko"
        }
    
    def _extract_keywords_en(self, text: str) -> Dict[str, Any]:
        """
        영어 키워드 추출
        """
        if not self.nlp:
            return {"error": "spaCy 모델이 로드되지 않았습니다."}
        
        # 문장 정제
        cleaned_text = self._clean_text(text)
        doc = self.nlp(cleaned_text)
        word_count = len([token for token in doc if not token.is_space])
        
        # 의미있는 단어만 추출
        keywords = self._extract_all_words_en(doc, word_count)
        keyword_count = len(keywords)
        
        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "word_count": word_count,
            "keyword_count": keyword_count,
            "keywords": keywords,
            "language": "en"
        }
    
    def _extract_all_words_ko(self, pos_tags: List[tuple], keyword_count: int) -> List[Dict[str, str]]:
        """
        한국어 의미있는 단어만 추출 (조사, 접속사 등 제외)
        """
        # 제외할 품사들
        exclude_pos = [
            'JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC',  # 조사
            'EP', 'EF', 'EC', 'ETN', 'ETM',  # 어미
            'XSN', 'XSV', 'XSA', 'XSM',  # 접미사
            'SF', 'SP', 'SS', 'SE', 'SO', 'SW',  # 기호
            'UN', 'UV', 'UE',  # 미분석
        ]
        
        keywords = []
        for word, pos in pos_tags:
            if len(word) > 0 and pos not in exclude_pos:
                keywords.append({
                    'word': word,
                    'pos': pos
                })
        
        return keywords[:keyword_count]
    
    def _extract_all_words_en(self, doc, keyword_count: int) -> List[Dict[str, str]]:
        """
        영어 의미있는 단어만 추출 (관사, 접속사 등 제외)
        """
        # 제외할 품사들
        exclude_pos = [
            'DET',  # 관사 (a, an, the)
            'CCONJ',  # 접속사 (and, or, but)
            'SCONJ',  # 종속접속사 (if, because)
            'AUX',  # 보조동사 (is, are, have)
            'PART',  # 분사 (to)
            'PUNCT',  # 구두점
            'SPACE',  # 공백
        ]
        
        keywords = []
        for token in doc:
            if (not token.is_space and 
                len(token.text) > 0 and 
                token.pos_ not in exclude_pos and
                not token.is_stop):  # 불용어도 제외
                keywords.append({
                    'word': token.text,
                    'pos': token.pos_
                })
        
        return keywords[:keyword_count]
    
    def _clean_text(self, text: str) -> str:
        """
        텍스트 정제
        """
        # 특수문자 제거 (마침표, 쉼표, 물음표, 느낌표는 유지)
        text = re.sub(r'[^\w\s\.\,\?\!]', '', text)
        # 연속된 공백 제거
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

def extract_keywords(text: str, lang: str = "ko", method: str = "okt") -> Dict[str, Any]:
    """
    키워드 추출 통합 함수
    
    Args:
        text: 분석할 텍스트
        lang: 언어 ("ko" 또는 "en")
        method: 한국어 태거 방법 ("okt", "komoran", "hannanum")
    
    Returns:
        키워드 추출 결과
    """
    extractor = KeywordExtractor(lang)
    return extractor.extract_keywords(text, method)

if __name__ == "__main__":
    # 테스트 코드
    test_cases = [
        "세종대왕은 1392년에 조선을 건국했다.",  # 4단어
        "날씨가 좋다.",  # 2단어
        "아이가 공원에서 친구들과 함께 놀고 있다.",  # 7단어
        "The weather is beautiful today.",  # 5단어 (영어)
        "John and Mary eat an apple and a banana.",  # 9단어 (영어)
    ]
    
    for text in test_cases:
        lang = "en" if any(ord(c) < 128 for c in text) else "ko"
        result = extract_keywords(text, lang)
        print(f"\n문장: {text}")
        print(f"단어 수: {result.get('word_count', 'N/A')}")
        print(f"추출 키워드 수: {result.get('keyword_count', 'N/A')}")
        if 'error' in result:
            print(f"오류: {result['error']}")
        else:
            print(f"키워드: {result.get('keywords', [])}") 