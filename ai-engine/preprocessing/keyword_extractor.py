import re
import sys
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
        self.ko_taggers = {}
        
        # 한국어 태거 초기화 (에러 처리 포함)
        if lang == "ko":
            self._init_korean_taggers()
        
        # 영어 spaCy 모델 초기화
        if lang == "en":
            self._init_english_model()
    
    def _init_korean_taggers(self):
        """한국어 태거들을 안전하게 초기화"""
        try:
            self.ko_taggers['okt'] = Okt()
            print("✅ Okt 태거 초기화 성공")
        except Exception as e:
            print(f"⚠️  Okt 태거 초기화 실패: {e}")
            print("💡 Java가 설치되어 있는지 확인해주세요: brew install openjdk@11")
        
        try:
            self.ko_taggers['komoran'] = Komoran()
            print("✅ Komoran 태거 초기화 성공")
        except Exception as e:
            print(f"⚠️  Komoran 태거 초기화 실패: {e}")
        
        try:
            self.ko_taggers['hannanum'] = Hannanum()
            print("✅ Hannanum 태거 초기화 성공")
        except Exception as e:
            print(f"⚠️  Hannanum 태거 초기화 실패: {e}")
    
    def _init_english_model(self):
        """영어 spaCy 모델 초기화"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
            print("✅ spaCy 영어 모델 로드 성공")
        except OSError:
            print("❌ spaCy 영어 모델이 설치되지 않았습니다.")
            print("💡 다음 명령어를 실행해주세요: python -m spacy download en_core_web_sm")
        except Exception as e:
            print(f"❌ spaCy 모델 로드 중 오류 발생: {e}")
    
    def extract_keywords(self, text: str, method: str = "okt") -> Dict[str, Any]:
        """
        문장에서 중요한 키워드를 추출.
        
        Args:
            text: 분석할 텍스트
            method: 한국어 태거 방법 ("okt", "komoran", "hannanum")
        
        Returns:
            키워드 추출 결과 딕셔너리
        """
        if not text or not text.strip():
            return {
                "error": "입력 텍스트가 비어있습니다.",
                "original_text": text,
                "language": self.lang
            }
        
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
        # 사용 가능한 태거 확인
        if not self.ko_taggers:
            return {
                "error": "사용 가능한 한국어 태거가 없습니다. Java 설치를 확인해주세요.",
                "original_text": text,
                "language": "ko"
            }
        
        # 선택된 태거가 사용 가능한지 확인
        if method not in self.ko_taggers:
            available_methods = list(self.ko_taggers.keys())
            return {
                "error": f"'{method}' 태거를 사용할 수 없습니다. 사용 가능한 태거: {available_methods}",
                "original_text": text,
                "language": "ko",
                "available_methods": available_methods
            }
        
        try:
            # 문장 정제
            cleaned_text = self._clean_text(text)
            words = cleaned_text.split()
            word_count = len(words)
            
            # 형태소 분석
            tagger = self.ko_taggers[method]
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
        except Exception as e:
            return {
                "error": f"키워드 추출 중 오류 발생: {str(e)}",
                "original_text": text,
                "language": "ko",
                "method": method
            }
    
    def _extract_keywords_en(self, text: str) -> Dict[str, Any]:
        """
        영어 키워드 추출
        """
        if not self.nlp:
            return {
                "error": "spaCy 모델이 로드되지 않았습니다. 'python -m spacy download en_core_web_sm' 실행 필요",
                "original_text": text,
                "language": "en"
            }
        
        try:
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
        except Exception as e:
            return {
                "error": f"영어 키워드 추출 중 오류 발생: {str(e)}",
                "original_text": text,
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
    print("🔍 키워드 추출 테스트를 시작합니다...")
    print("=" * 50)
    
    # 테스트 케이스
    test_cases = [
        {
            "text": "세종대왕은 1392년에 조선을 건국했다.",
            "lang": "ko",
            "method": "okt"
        },
        {
            "text": "날씨가 좋다.",
            "lang": "ko", 
            "method": "okt"
        },
        {
            "text": "아이가 공원에서 친구들과 함께 놀고 있다.",
            "lang": "ko",
            "method": "okt"
        },
        {
            "text": "The weather is beautiful today.",
            "lang": "en",
            "method": "okt"
        },
        {
            "text": "John and Mary eat an apple and a banana.",
            "lang": "en",
            "method": "okt"
        },
        {
            "text": "",  # 빈 텍스트 테스트
            "lang": "ko",
            "method": "okt"
        }
    ]
    
    # 각 테스트 케이스 실행
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 테스트 {i}: {test_case['text'][:30]}{'...' if len(test_case['text']) > 30 else ''}")
        print("-" * 40)
        
        try:
            result = extract_keywords(
                test_case['text'], 
                lang=test_case['lang'], 
                method=test_case['method']
            )
            
            # 결과 출력
            if 'error' in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print(f"✅ 언어: {result['language']}")
                print(f"📊 단어 수: {result['word_count']}")
                print(f"🔑 추출 키워드 수: {result['keyword_count']}")
                print(f"📝 키워드: {[kw['word'] for kw in result['keywords']]}")
                
        except Exception as e:
            print(f"❌ 예상치 못한 오류: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 키워드 추출 테스트 완료!")
    
    # 사용 가능한 태거 확인
    print("\n🔧 사용 가능한 한국어 태거:")
    try:
        extractor = KeywordExtractor("ko")
        available_taggers = list(extractor.ko_taggers.keys())
        if available_taggers:
            print(f"✅ 사용 가능: {', '.join(available_taggers)}")
        else:
            print("❌ 사용 가능한 태거가 없습니다. Java 설치를 확인해주세요.")
    except Exception as e:
        print(f"❌ 태거 확인 중 오류: {str(e)}")
