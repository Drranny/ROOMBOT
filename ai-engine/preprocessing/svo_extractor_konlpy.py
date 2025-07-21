# -*- coding:utf-8 -*-
from konlpy.tag import Okt, Komoran, Hannanum
import re

class KoreanSVOExtractor:
    def __init__(self, tagger_type="okt"):
        """
        한국어 SVO 추출기 초기화
        tagger_type: "okt", "komoran", "hannanum"
        """
        if tagger_type == "okt":
            self.tagger = Okt()
        elif tagger_type == "komoran":
            self.tagger = Komoran()
        elif tagger_type == "hannanum":
            self.tagger = Hannanum()
        else:
            raise ValueError("tagger_type must be 'okt', 'komoran', or 'hannanum'")
    
    def extract_svo(self, text: str):
        """
        한국어 텍스트에서 SVO 추출
        """
        # 형태소 분석
        morphemes = self.tagger.pos(text)
        
        # 문장 구조 분석
        subject = None
        verb = None
        object_text = None
        predicate_type = "VV"
        
        # 주어, 서술어, 목적어 찾기
        for i, (word, pos) in enumerate(morphemes):
            # 주어 찾기 (명사 + 주격 조사)
            if pos in ['Noun', 'NNP', 'NNG'] and i + 1 < len(morphemes):
                next_word, next_pos = morphemes[i + 1]
                if next_pos in ['JKS', 'JX', 'Josa'] and next_word in ['이', '가', '은', '는']:
                    # 주어 구성: 앞의 소유격 + 명사 + 주격조사
                    subject_parts = []
                    # 앞의 소유격 조사 찾기
                    if i > 0 and morphemes[i-1][1] in ['JKG', 'Josa'] and morphemes[i-1][0] == '의':
                        subject_parts.append(morphemes[i-1][0])
                    subject_parts.append(word)
                    subject_parts.append(next_word)
                    subject = ''.join(subject_parts)
            
            # 목적어 찾기 (명사)
            if pos in ['Noun', 'NNP', 'NNG']:
                # 주어가 이미 찾아졌고, 서술어 앞에 있는 명사
                if subject and not object_text:
                    object_text = word
            
            # 서술어 찾기 (동사, 형용사, 서술격조사)
            if pos in ['Verb', 'VV', 'VA', 'VX', 'Josa'] and word in ['이다', '있다', '없다']:
                verb = word
                if pos == 'VA':
                    predicate_type = "VA"
                elif pos == 'VX':
                    predicate_type = "VX"
                else:
                    predicate_type = "VV"
        
        # 주어가 없으면 첫 번째 명사를 주어로 설정
        if not subject:
            for word, pos in morphemes:
                if pos in ['Noun', 'NNP', 'NNG']:
                    subject = word
                    break
        
        # 서술어가 없으면 마지막 동사/형용사를 서술어로 설정
        if not verb:
            for word, pos in reversed(morphemes):
                if pos in ['Verb', 'VV', 'VA', 'VX', 'VCP', 'VCN']:
                    verb = word
                    if pos == 'VA':
                        predicate_type = "VA"
                    elif pos == 'VX':
                        predicate_type = "VX"
                    elif pos in ['VCP', 'VCN']:
                        predicate_type = "VCP"
                    else:
                        predicate_type = "VV"
                    break
        
        return {
            "S": subject if subject else "주어",
            "V": verb if verb else "동사",
            "O": object_text if object_text else None,
            "predicate_type": predicate_type,
            "has_object": object_text is not None
        }

def analyze_svo_konlpy(text: str, tagger_type: str = "okt"):
    """
    KoNLPy를 사용한 한국어 SVO 분석
    """
    try:
        extractor = KoreanSVOExtractor(tagger_type)
        result = extractor.extract_svo(text)
        
        return {
            "sentence": text,
            "language": "ko",
            "svo": {
                "subject": result["S"],
                "verb": result["V"],
                "object": result["O"] if result["O"] else "없음",
                "predicate_type": result["predicate_type"],
                "has_object": result["has_object"]
            }
        }
    except Exception as e:
        print(f"KoNLPy SVO 분석 오류: {e}")
        return {
            "sentence": text,
            "language": "ko",
            "svo": {
                "subject": "주어",
                "verb": "동사",
                "object": "없음",
                "predicate_type": "VV",
                "has_object": False
            }
        }

 