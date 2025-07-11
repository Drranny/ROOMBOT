import re
from typing import List, Dict, Tuple, Optional

class SentenceValidator:
    """문장 품질 검증 및 전처리 클래스"""
    
    def __init__(self):
        # 분석 불가능한 문장 패턴들
        self.invalid_patterns = [
            r'^[^\w가-힣]*$',  # 특수문자만 있는 문장
            r'^[0-9\s\-\.]+$',  # 숫자와 기호만 있는 문장
            r'^[A-Za-z\s]+$',   # 영어만 있는 문장 (한국어 분석 대상이므로)
            r'^[가-힣\s]*$',    # 한글과 공백만 있는 문장 (의미 없음)
        ]
        
        # 인사말/감탄문 패턴
        self.greeting_patterns = [
            r'안녕하세요',
            r'안녕하십니까',
            r'반갑습니다',
            r'고맙습니다',
            r'감사합니다',
            r'죄송합니다',
            r'미안합니다',
            r'좋은 하루',
            r'좋은 밤',
            r'잘 가세요',
            r'안녕히 가세요',
            r'안녕히 계세요'
        ]
        
        # 감탄문 패턴
        self.exclamation_patterns = [
            r'정말 좋네요',
            r'정말 예쁘네요',
            r'정말 멋지네요',
            r'너무 좋아요',
            r'너무 예뻐요',
            r'너무 멋져요',
            r'와!',
            r'우와!',
            r'대박!',
            r'짱!'
        ]
        
        # 너무 짧은 문장 (의미 분석 불가)
        self.min_length = 5
        
        # 너무 긴 문장 (분석 복잡도 증가)
        self.max_length = 200

    def validate_sentence(self, sentence: str) -> Dict[str, any]:
        """
        단일 문장 검증
        
        Returns:
            {
                "is_valid": bool,
                "reason": str,
                "cleaned_text": str,
                "sentence_type": str
            }
        """
        if not sentence or not sentence.strip():
            return {
                "is_valid": False,
                "reason": "빈 문장",
                "cleaned_text": "",
                "sentence_type": "empty"
            }
        
        # 기본 전처리
        cleaned = self._preprocess_sentence(sentence)
        
        # 길이 검증
        if len(cleaned) < self.min_length:
            return {
                "is_valid": False,
                "reason": f"너무 짧음 ({len(cleaned)}자)",
                "cleaned_text": cleaned,
                "sentence_type": "too_short"
            }
        
        if len(cleaned) > self.max_length:
            return {
                "is_valid": False,
                "reason": f"너무 김 ({len(cleaned)}자)",
                "cleaned_text": cleaned,
                "sentence_type": "too_long"
            }
        
        # 패턴 검증
        for pattern in self.invalid_patterns:
            if re.match(pattern, cleaned):
                return {
                    "is_valid": False,
                    "reason": "분석 불가능한 패턴",
                    "cleaned_text": cleaned,
                    "sentence_type": "invalid_pattern"
                }
        
        # 인사말 검증 (부분 매칭으로 변경)
        is_greeting = False
        for pattern in self.greeting_patterns:
            if pattern in cleaned and len(cleaned) < 20:  # 짧은 인사말만 필터링
                is_greeting = True
                break
        
        if is_greeting:
            return {
                "is_valid": False,
                "reason": "인사말",
                "cleaned_text": cleaned,
                "sentence_type": "greeting"
            }
        
        # 감탄문 검증 (부분 매칭으로 변경)
        is_exclamation = False
        for pattern in self.exclamation_patterns:
            if pattern in cleaned and len(cleaned) < 15:  # 짧은 감탄문만 필터링
                is_exclamation = True
                break
        
        if is_exclamation:
            return {
                "is_valid": False,
                "reason": "감탄문",
                "cleaned_text": cleaned,
                "sentence_type": "exclamation"
            }
        
        # 문장 구조 검증
        if not self._has_valid_structure(cleaned):
            return {
                "is_valid": False,
                "reason": "유효하지 않은 문장 구조",
                "cleaned_text": cleaned,
                "sentence_type": "invalid_structure"
            }
        
        return {
            "is_valid": True,
            "reason": "검증 통과",
            "cleaned_text": cleaned,
            "sentence_type": "valid"
        }

    def validate_text(self, text: str) -> Dict[str, any]:
        """
        전체 텍스트 검증 및 문장 분리
        
        Returns:
            {
                "valid_sentences": List[str],
                "invalid_sentences": List[Dict],
                "summary": Dict
            }
        """
        if not text or not text.strip():
            return {
                "valid_sentences": [],
                "invalid_sentences": [],
                "summary": {
                    "total": 0,
                    "valid": 0,
                    "invalid": 0,
                    "valid_rate": 0.0
                }
            }
        
        # 문장 분리
        sentences = self._split_sentences(text)
        
        valid_sentences = []
        invalid_sentences = []
        
        for sentence in sentences:
            result = self.validate_sentence(sentence)
            if result["is_valid"]:
                valid_sentences.append(result["cleaned_text"])
            else:
                invalid_sentences.append({
                    "original": sentence,
                    "cleaned": result["cleaned_text"],
                    "reason": result["reason"],
                    "type": result["sentence_type"]
                })
        
        total = len(sentences)
        valid_count = len(valid_sentences)
        
        return {
            "valid_sentences": valid_sentences,
            "invalid_sentences": invalid_sentences,
            "summary": {
                "total": total,
                "valid": valid_count,
                "invalid": total - valid_count,
                "valid_rate": (valid_count / total * 100) if total > 0 else 0.0
            }
        }

    def _preprocess_sentence(self, sentence: str) -> str:
        """문장 전처리"""
        # 앞뒤 공백 제거
        cleaned = sentence.strip()
        
        # 연속된 공백을 하나로
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # 문장 부호 정규화
        cleaned = re.sub(r'[。．]', '.', cleaned)
        cleaned = re.sub(r'[！]', '!', cleaned)
        cleaned = re.sub(r'[？]', '?', cleaned)
        
        return cleaned

    def _split_sentences(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분리"""
        # 한국어 문장 분리 패턴
        sentence_pattern = r'[.!?。！？]\s*'
        sentences = re.split(sentence_pattern, text)
        
        # 빈 문장 제거 및 정리
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence:
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences

    def _has_valid_structure(self, sentence: str) -> bool:
        """문장 구조 유효성 검사"""
        # 한글이 포함되어 있는지 확인
        if not re.search(r'[가-힣]', sentence):
            return False
        
        # 너무 많은 특수문자 (50% 이상)
        special_char_ratio = len(re.findall(r'[^\w가-힣\s]', sentence)) / len(sentence)
        if special_char_ratio > 0.5:
            return False
        
        return True

    def remove_duplicates(self, sentences: List[str]) -> List[str]:
        """중복 문장 제거"""
        seen = set()
        unique_sentences = []
        
        for sentence in sentences:
            # 정규화된 형태로 비교
            normalized = self._normalize_for_comparison(sentence)
            if normalized not in seen:
                seen.add(normalized)
                unique_sentences.append(sentence)
        
        return unique_sentences

    def _normalize_for_comparison(self, sentence: str) -> str:
        """문장 비교를 위한 정규화"""
        # 소문자 변환 (영어가 있는 경우)
        normalized = sentence.lower()
        
        # 공백 정규화
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # 문장 부호 제거
        normalized = re.sub(r'[.!?。！？,，]', '', normalized)
        
        return normalized.strip()


# 사용 예시
if __name__ == "__main__":
    validator = SentenceValidator()
    
    # 테스트 케이스들
    test_cases = [
        "안녕하세요, 저는 김철수입니다.",  # 인사말
        "오늘 날씨가 정말 좋네요!",  # 감탄문
        "세종대왕은 1397년에 태어났다.",  # 유효한 문장
        "윤동주는 한국의 독립운동가이자 시인이었다.",  # 유효한 문장
        "12345",  # 숫자만
        "!!!",  # 특수문자만
        "너무 짧음",  # 너무 짧음
        "이것은 매우 긴 문장입니다. " * 50,  # 너무 김
        "",  # 빈 문장
    ]
    
    print("=== 단일 문장 검증 테스트 ===")
    for i, test_case in enumerate(test_cases, 1):
        result = validator.validate_sentence(test_case)
        print(f"{i}. '{test_case[:30]}...' -> {result['is_valid']} ({result['reason']})")
    
    print("\n=== 전체 텍스트 검증 테스트 ===")
    test_text = """
    안녕하세요, 저는 김철수입니다.
    세종대왕은 1397년에 태어났다.
    오늘 날씨가 정말 좋네요!
    윤동주는 한국의 독립운동가이자 시인이었다.
    12345
    세종대왕은 1397년에 태어났다.  # 중복
    """
    
    result = validator.validate_text(test_text)
    print(f"총 문장 수: {result['summary']['total']}")
    print(f"유효한 문장: {result['summary']['valid']}")
    print(f"무효한 문장: {result['summary']['invalid']}")
    print(f"유효률: {result['summary']['valid_rate']:.1f}%")
    
    print("\n유효한 문장들:")
    for sentence in result['valid_sentences']:
        print(f"  - {sentence}")
    
    print("\n무효한 문장들:")
    for invalid in result['invalid_sentences']:
        print(f"  - {invalid['original']} ({invalid['reason']})") 