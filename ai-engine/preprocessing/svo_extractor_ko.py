# -*- coding:utf-8 -*-
import urllib3
import json
import os
from dotenv import load_dotenv

load_dotenv()

ETRI_API_URL = "http://epretx.etri.re.kr:8000/api/WiseNLU"
ETRI_SPOKEN_API_URL = "http://epretx.etri.re.kr:8000/api/WiseNLU_spoken"


def call_etri_api(text, analysis_code="srl", api_key=None, api_url=None):
    if api_key is None:
        api_key = os.getenv("ETRI_API_KEY")
    if api_url is None:
        api_url = ETRI_API_URL
    request_json = {
        "argument": {
            "text": text,
            "analysis_code": analysis_code
        }
    }
    http = urllib3.PoolManager()
    response = http.request(
        "POST",
        api_url,
        headers={"Content-Type": "application/json; charset=UTF-8", "Authorization": api_key},
        body=json.dumps(request_json)
    )
    if response.status != 200:
        raise Exception(f"ETRI API 호출 실패: {response.status} - {response.data}")
    return json.loads(response.data.decode("utf-8"))


def extract_svo_from_etri_response(data):
    """ETRI API 응답에서 SVO 추출 (SRL + 형태소 분석 조합)"""
    svo_list = []
    sentences = data.get("return_object", {}).get("sentence", [])
    
    for sentence in sentences:
        # 1. SRL 기반 SVO 추출 (동사 중심)
        srl_list = sentence.get("SRL", [])
        for srl in srl_list:
            verb = srl.get("verb", "")
            subject = None
            obj = None
            for arg in srl.get("argument", []):
                arg_type = arg.get("type", "")
                arg_text = arg.get("text", "")
                if arg_type == "ARG0":
                    subject = arg_text
                elif arg_type in ["ARG1", "ARG2"]:
                    obj = arg_text
            if subject and verb and obj:
                svo_list.append({
                    "S": subject,
                    "V": verb,
                    "O": obj,
                    "method": "SRL"
                })
        
        # 2. 형태소 분석 기반 SVO 추출 (형용사 서술어 포함)
        morphemes = sentence.get("morp", [])
        if morphemes:
            morpheme_svos = extract_svo_from_morphemes(morphemes)
            svo_list.extend(morpheme_svos)
    
    return svo_list

def extract_svo_from_morphemes(morphemes):
    """형태소 분석 결과에서 SVO 추출 (형용사 서술어 포함, '이자/이다' 패턴 후처리)"""
    svo_list = []
    
    # 형태소를 단어 단위로 그룹화
    words = []
    current_word = {"text": "", "pos": "", "lemma": ""}
    
    for morpheme in morphemes:
        lemma = morpheme.get("lemma", "")
        pos = morpheme.get("type", "")
        
        # 명사 + 조사, 동사 + 어미 등을 하나의 단어로 그룹화
        if pos in ["JKS", "JKO", "JKG", "JX", "EC", "EF", "ETM"]:  # 조사, 어미
            current_word["text"] += lemma
            current_word["pos"] = pos
        else:
            if current_word["text"]:
                words.append(current_word)
            current_word = {"text": lemma, "pos": pos, "lemma": lemma}
    
    if current_word["text"]:
        words.append(current_word)
    
    # SVO 패턴 찾기
    subjects = []
    verbs = []
    objects = []
    
    for i, word in enumerate(words):
        # 주어 찾기 (명사 + 주격조사)
        if word["pos"] in ["NNG", "NNP", "NNB"] and i + 1 < len(words):
            if words[i + 1]["pos"] == "JKS":  # 주격조사
                subjects.append(word["text"])
        
        # 동사/형용사 찾기
        if word["pos"] in ["VV", "VA", "VCP"]:  # 동사, 형용사, 보조동사
            verbs.append(word["lemma"])
        
        # 목적어 찾기 (명사 + 목적격조사)
        if word["pos"] in ["NNG", "NNP", "NNB"] and i + 1 < len(words):
            if words[i + 1]["pos"] == "JKO":  # 목적격조사
                objects.append(word["text"])
    
    # "~이자 ~이다" 및 "~이다" 패턴 후처리
    # 예: 김연아는 피겨스케이팅 선수이자 올림픽 메달리스트이다.
    #     김치찌개는 ... 음식이자 ... 요리이다.
    for i, word in enumerate(words):
        # 1. "이자" 패턴
        if word["lemma"] == "이자":
            # 주어: 앞의 명사
            subject = ""
            for j in range(i - 1, -1, -1):
                if words[j]["pos"] in ["NNG", "NNP", "NNB"]:
                    subject = words[j]["text"]
                    break
            # 목적어1: 바로 앞 명사
            obj1 = subject
            # 목적어2: 바로 뒤 명사
            obj2 = ""
            for j in range(i + 1, len(words)):
                if words[j]["pos"] in ["NNG", "NNP", "NNB"]:
                    obj2 = words[j]["text"]
                    break
            # "이다"가 뒤에 있으면 SVO 2개 생성
            for k in range(i + 1, len(words)):
                if words[k]["lemma"] == "이다":
                    if subject and obj1:
                        svo_list.append({"S": subject, "V": "이다", "O": obj1, "method": "pattern_이자"})
                    if subject and obj2:
                        svo_list.append({"S": subject, "V": "이다", "O": obj2, "method": "pattern_이자"})
                    break
        # 2. "이다" 단독 패턴 (A는 B이다)
        if word["lemma"] == "이다":
            # 주어: 앞의 명사
            subject = ""
            obj = ""
            for j in range(i - 1, -1, -1):
                if words[j]["pos"] in ["NNG", "NNP", "NNB"]:
                    if not obj:
                        obj = words[j]["text"]
                    elif not subject:
                        subject = words[j]["text"]
                        break
            if subject and obj:
                svo_list.append({"S": subject, "V": "이다", "O": obj, "method": "pattern_이다"})
    
    # 일반적인 SVO 조합 생성
    for subject in subjects:
        for verb in verbs:
            for obj in objects:
                svo_list.append({
                    "S": subject,
                    "V": verb,
                    "O": obj,
                    "method": "morpheme_analysis"
                })
    
    return svo_list


def analyze_svo_ko(text, api_key=None, analysis_code="srl", api_url=None):
    """한국어 SVO 분석 메인 함수 (ETRI 공식 예제 기반)"""
    try:
        # SRL과 형태소 분석을 개별적으로 수행
        svo_list = []
        
        # 1. SRL 분석
        try:
            srl_data = call_etri_api(text, analysis_code="srl", api_key=api_key, api_url=api_url)
            srl_svos = extract_svo_from_srl_only(srl_data)
            svo_list.extend(srl_svos)
        except Exception as e:
            print(f"SRL 분석 실패: {e}")
        
        # 2. 형태소 분석
        try:
            morp_data = call_etri_api(text, analysis_code="morp", api_key=api_key, api_url=api_url)
            morp_svos = extract_svo_from_morp_only(morp_data)
            svo_list.extend(morp_svos)
        except Exception as e:
            print(f"형태소 분석 실패: {e}")
        
        # 중복 제거
        unique_svos = remove_duplicate_svos(svo_list)
        
        return {
            "svo_list": unique_svos,
            "raw_response": {"srl": srl_data if 'srl_data' in locals() else None, "morp": morp_data if 'morp_data' in locals() else None},
            "success": True
        }
    except Exception as e:
        return {
            "svo_list": [],
            "raw_response": None,
            "success": False,
            "error": str(e)
        }

def extract_svo_from_srl_only(data):
    """SRL 분석 결과에서만 SVO 추출"""
    svo_list = []
    sentences = data.get("return_object", {}).get("sentence", [])
    
    for sentence in sentences:
        srl_list = sentence.get("SRL", [])
        for srl in srl_list:
            verb = srl.get("verb", "")
            subject = None
            obj = None
            for arg in srl.get("argument", []):
                arg_type = arg.get("type", "")
                arg_text = arg.get("text", "")
                if arg_type == "ARG0":
                    subject = arg_text
                elif arg_type in ["ARG1", "ARG2"]:
                    obj = arg_text
            if subject and verb and obj:
                svo_list.append({
                    "S": subject,
                    "V": verb,
                    "O": obj,
                    "method": "SRL"
                })
    
    return svo_list

def extract_svo_from_morp_only(data):
    """형태소 분석 결과에서만 SVO 추출"""
    svo_list = []
    sentences = data.get("return_object", {}).get("sentence", [])
    
    for sentence in sentences:
        morphemes = sentence.get("morp", [])
        if morphemes:
            morpheme_svos = extract_svo_from_morphemes(morphemes)
            svo_list.extend(morpheme_svos)
    
    return svo_list

def remove_duplicate_svos(svo_list):
    """중복 SVO 제거"""
    seen = set()
    unique_svos = []
    
    for svo in svo_list:
        # 정규화된 키 생성
        key = f"{svo['S']}_{svo['V']}_{svo['O']}"
        if key not in seen:
            seen.add(key)
            unique_svos.append(svo)
    
    return unique_svos


if __name__ == "__main__":
    api_key = os.getenv("ETRI_API_KEY")
    if not api_key:
        print("ETRI_API_KEY 환경변수가 설정되지 않았습니다.")
        exit(1)
    
    # 다양한 테스트 문장들
    test_cases = [
        {
            "name": "간단한 문장",
            "text": "학생이 책을 읽는다."
        },
        {
            "name": "복합 문장",
            "text": "세종대왕은 조선의 제4대 왕이자 한글을 창제한 인물이다."
        },
        {
            "name": "긴 복합문장 (공식 예제)",
            "text": (
                "윤동주(尹東柱, 1917년 12월 30일 ~ 1945년 2월 16일)는 한국의 독립운동가, 시인, 작가이다."
                "중국 만저우 지방 지린 성 연변 용정에서 출생하여 명동학교에서 수학하였고, 숭실중학교와 연희전문학교를 졸업하였다. "
                "숭실중학교 때 처음 시를 발표하였고, 1939년 연희전문 2학년 재학 중 소년(少年) 지에 시를 발표하며 정식으로 문단에 데뷔했다. "
                "일본 유학 후 도시샤 대학 재학 중 , 1943년 항일운동을 했다는 혐의로 일본 경찰에 체포되어 후쿠오카 형무소(福岡刑務所)에 투옥, 100여 편의 시를 남기고 27세의 나이에 옥중에서 요절하였다. "
                "사인이 일본의 생체실험이라는 견해가 있고 그의 사후 일본군에 의한 마루타, 생체실험설이 제기되었으나 불확실하다. "
                "사후에 그의 시집 《하늘과 바람과 별과 시》가 출간되었다. "
                "일제 강점기 후반의 양심적 지식인으로 인정받았으며, 그의 시는 일제와 조선총독부에 대한 비판과 자아성찰 등을 소재로 하였다. "
                "그의 친구이자 사촌인 송몽규 역시 독립운동에 가담하려다가 체포되어 일제의 생체 실험으로 의문의 죽음을 맞는다. "
                "1990년대 후반 이후 그의 창씨개명 '히라누마'가 알려져 논란이 일기도 했다. 본명 외에 윤동주(尹童柱), 윤주(尹柱)라는 필명도 사용하였다."
            )
        },
        {
            "name": "스포츠 관련 문장",
            "text": "김연아는 피겨스케이팅 선수이자 올림픽 메달리스트이다."
        },
        {
            "name": "음식 관련 문장",
            "text": "김치찌개는 한국의 대표적인 음식이자 세계적으로 유명한 요리이다."
        }
    ]
    
    print("=== 한국어 SVO 추출 테스트 ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"--- Test {i}: {test_case['name']} ---")
        print(f"[INPUT] {test_case['text'][:50]}...")
        
        result = analyze_svo_ko(test_case['text'], api_key=api_key, analysis_code="srl")
        
        if result["success"]:
            print(f"[RESULT] 총 SVO 추출: {len(result['svo_list'])}")
            for j, svo in enumerate(result["svo_list"], 1):
                print(f"  {j}. S: {svo['S']}, V: {svo['V']}, O: {svo['O']}")
        else:
            print(f"[ERROR] 분석 실패: {result['error']}")
        
        print()
