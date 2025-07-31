import nltk
import logging
from typing import List, Set
import re

logger = logging.getLogger(__name__)

class SynonymFinder:
    def __init__(self):
        """키워드 유사어 찾기 서비스"""
        # NLTK 데이터 다운로드 (처음 실행시)
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
            nltk.download('omw-1.4')  # Open Multilingual Wordnet
        
        self.wn = nltk.corpus.wordnet
    
    def find_synonyms(self, keyword: str) -> List[str]:
        """
        키워드의 유사어를 찾습니다.
        
        Args:
            keyword: 찾을 키워드
            
        Returns:
            유사어 리스트
        """
        synonyms = []
        
        try:
            # 영어 유사어 찾기
            english_synonyms = self._get_english_synonyms(keyword)
            synonyms.extend(english_synonyms)
            
            # 한국어 유사어 찾기 (간단한 매핑 + WordNet 활용)
            korean_synonyms = self._get_korean_synonyms(keyword)
            synonyms.extend(korean_synonyms)
            
            # 중복 제거 및 정리
            unique_synonyms = list(set(synonyms))
            
            logger.info(f"키워드 '{keyword}'의 유사어: {unique_synonyms}")
            return unique_synonyms
            
        except Exception as e:
            logger.error(f"유사어 찾기 중 오류: {str(e)}")
            return []
    
    def _get_english_synonyms(self, keyword: str) -> List[str]:
        """영어 유사어 찾기 (WordNet 사용)"""
        synonyms = []
        
        try:
            # 키워드 정규화 (특수문자 제거, 소문자 변환)
            normalized_keyword = re.sub(r'[^a-zA-Z0-9\s]', '', keyword.lower()).strip()
            
            # WordNet에서 synsets 찾기
            synsets = self.wn.synsets(normalized_keyword)
            
            # synsets가 없으면 키워드를 분해해서 시도
            if not synsets:
                # 하이픈, 공백, 언더스코어로 분리
                words = re.split(r'[-_\s]', normalized_keyword)
                for word in words:
                    if len(word) > 2:  # 2글자 이상만
                        word_synsets = self.wn.synsets(word)
                        synsets.extend(word_synsets)
            
            # 더 적극적인 유사어 검색
            for synset in synsets:
                # lemma names (기본 형태)
                for lemma in synset.lemmas():
                    synonym = lemma.name()
                    if synonym != normalized_keyword and synonym not in synonyms:
                        synonyms.append(synonym)
                
                # hypernyms (상위어) - 더 넓은 범위
                for hypernym in synset.hypernyms():
                    for lemma in hypernym.lemmas():
                        synonym = lemma.name()
                        if synonym != normalized_keyword and synonym not in synonyms:
                            synonyms.append(synonym)
                    # 상위어의 상위어도 포함
                    for h_hypernym in hypernym.hypernyms():
                        for lemma in h_hypernym.lemmas():
                            synonym = lemma.name()
                            if synonym != normalized_keyword and synonym not in synonyms:
                                synonyms.append(synonym)
                
                # hyponyms (하위어)
                for hyponym in synset.hyponyms():
                    for lemma in hyponym.lemmas():
                        synonym = lemma.name()
                        if synonym != normalized_keyword and synonym not in synonyms:
                            synonyms.append(synonym)
                
                # holonyms (전체어) - 일부 synset에서만 사용 가능
                try:
                    for holonym in synset.holonyms():
                        for lemma in holonym.lemmas():
                            synonym = lemma.name()
                            if synonym != normalized_keyword and synonym not in synonyms:
                                synonyms.append(synonym)
                except AttributeError:
                    pass  # holonyms가 지원되지 않는 경우 무시
                
                # meronyms (부분어) - 일부 synset에서만 사용 가능
                try:
                    for meronym in synset.meronyms():
                        for lemma in meronym.lemmas():
                            synonym = lemma.name()
                            if synonym != normalized_keyword and synonym not in synonyms:
                                synonyms.append(synonym)
                except AttributeError:
                    pass  # meronyms가 지원되지 않는 경우 무시
            
            logger.info(f"키워드 '{keyword}' -> 정규화: '{normalized_keyword}', synsets: {len(synsets)}, 유사어: {synonyms}")
            
        except Exception as e:
            logger.error(f"영어 유사어 찾기 중 오류: {str(e)}")
        
        return list(set(synonyms))
    
    def _get_domain_synonyms(self, keyword: str) -> List[str]:
        """도메인 특화 유사어 찾기 (범용적 접근)"""
        # 수동 매핑 제거 - WordNet만 사용
        return []
    
    def _get_korean_synonyms(self, keyword: str) -> List[str]:
        """한국어 유사어 찾기 (WordNet 기반)"""
        synonyms = []
        
        try:
            # 한국어 단어를 영어로 번역해서 WordNet 검색
            korean_to_english = {
                "왕": "king",
                "왕조": "dynasty", 
                "건국": "foundation",
                "회군": "retreat",
                "통치": "rule",
                "정복": "conquest",
                "전쟁": "war",
                "평화": "peace",
                "정치": "politics",
                "정부": "government",
                "군주": "monarch",
                "제국": "empire",
                "왕국": "kingdom",
                "통치자": "ruler",
                "권력": "power",
                "권위": "authority",
                "지배": "domination",
                "정복자": "conqueror",
                "영웅": "hero",
                "지도자": "leader"
            }
            
            if keyword in korean_to_english:
                english_word = korean_to_english[keyword]
                english_synonyms = self._get_english_synonyms(english_word)
                # 영어 유사어를 한국어로 다시 매핑 (간단한 역매핑)
                english_to_korean = {v: k for k, v in korean_to_english.items()}
                for eng_syn in english_synonyms:
                    if eng_syn in english_to_korean:
                        synonyms.append(english_to_korean[eng_syn])
                        
        except Exception as e:
            logger.error(f"한국어 WordNet 검색 중 오류: {str(e)}")
        
        return list(set(synonyms))
    
    def find_all_synonyms(self, keywords: List[str]) -> List[str]:
        """
        여러 키워드의 모든 유사어를 찾습니다.
        
        Args:
            keywords: 키워드 리스트
            
        Returns:
            모든 유사어 리스트 (중복 제거)
        """
        all_synonyms = []
        
        for keyword in keywords:
            synonyms = self.find_synonyms(keyword)
            all_synonyms.extend(synonyms)
        
        # 중복 제거 및 정리
        unique_synonyms = list(set(all_synonyms))
        
        logger.info(f"전체 키워드 {keywords}의 유사어: {unique_synonyms}")
        return unique_synonyms
    
    def _get_synonym_group(self, keyword: str) -> str:
        """
        키워드가 속한 유사어 그룹을 반환합니다.
        
        Args:
            keyword: 키워드
            
        Returns:
            유사어 그룹 ID (문자열)
        """
        try:
            # WordNet에서 synsets 찾기
            synsets = self.wn.synsets(keyword.lower())
            
            if synsets:
                # 첫 번째 synset의 이름을 그룹 ID로 사용
                return f"synset_{synsets[0].name()}"
            else:
                # WordNet에 없는 경우 키워드 자체를 그룹으로 반환
                return keyword
                
        except Exception as e:
            logger.error(f"유사어 그룹 찾기 중 오류: {str(e)}")
            return keyword
    
    def _remove_similar_keywords(self, keywords: List[str]) -> List[str]:
        """
        유사한 키워드들을 제거합니다 (같은 의미의 키워드는 1개만 유지)
        
        Args:
            keywords: 키워드 리스트
            
        Returns:
            중복 제거된 키워드 리스트
        """
        unique_keywords = []
        used_groups = set()
        
        for keyword in keywords:
            # 해당 키워드의 유사어 그룹 확인
            group = self._get_synonym_group(keyword)
            
            # 이미 해당 그룹의 키워드가 사용되었는지 확인
            if group not in used_groups:
                unique_keywords.append(keyword)
                used_groups.add(group)
        
        return unique_keywords 