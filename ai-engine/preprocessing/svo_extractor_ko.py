# -*- coding:utf-8 -*-
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

ETRI_API_URL = "http://epretx.etri.re.kr:8000/api/WiseNLU"
ETRI_SPOKEN_API_URL = "http://epretx.etri.re.kr:8000/api/WiseNLU_spoken"
DEFAULT_ANALYSIS_CODE = "srl"  # 의미역 분석 (소문자로 다시 시도)

def extract_svo_korean_etri(text: str, api_key: str = None):
    if api_key is None:
        api_key = os.getenv("ETRI_API_KEY")  # 환경변수에서 가져옴
        if api_key is None:
            raise ValueError("ETRI API 키가 제공되지 않았습니다.")

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": api_key
    }

    payload = {
        "argument": {
            "text": text,
            "analysis_code": DEFAULT_ANALYSIS_CODE
        }
    }

    response = requests.post(ETRI_API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        raise Exception(f"ETRI API 호출 실패: {response.status_code} - {response.text}")

    data = response.json()
    print(f"API Response: {json.dumps(data, indent=2, ensure_ascii=False)}")  # 전체 응답 출력
    
    sentences = data.get("return_object", {}).get("sentence", [])

    svo_list = []
    for sentence in sentences:
        # SRL 필드에서 의미역 정보 추출
        srl_list = sentence.get("SRL", [])
        for srl in srl_list:
            verb = srl.get("verb", "")
            subject = None
            obj = None
            
            # argument에서 주어(ARG0)와 목적어(ARG1, ARG2) 찾기
            for arg in srl.get("argument", []):
                arg_type = arg.get("type", "")
                arg_text = arg.get("text", "")
                
                if arg_type == "ARG0":  # 주어
                    subject = arg_text
                elif arg_type in ["ARG1", "ARG2"]:  # 목적어
                    obj = arg_text
            
            # SVO가 모두 있는 경우만 추가
            if subject and verb and obj:
                svo_list.append({
                    "S": subject,
                    "V": verb,
                    "O": obj
                })
        
        # 기존 semantic_role 필드도 확인 (하위 호환성)
        semantic_roles = sentence.get("semantic_role", [])
        for srl in semantic_roles:
            verb = srl.get("predicate", {}).get("text", "")
            subject = None
            obj = None
            for arg in srl.get("argument", []):
                if arg["type"] == "ARG0":
                    subject = arg["text"]
                elif arg["type"] in ["ARG1", "ARG2"]:
                    obj = arg["text"]
            if subject and verb and obj:
                svo_list.append({
                    "S": subject,
                    "V": verb,
                    "O": obj
                })

    return svo_list


def extract_svo_korean_etri_spoken(text: str, api_key: str = None):
    """구어체 ETRI API를 사용한 SVO 추출"""
    if api_key is None:
        api_key = os.getenv("ETRI_API_KEY")  # 환경변수에서 가져옴
        if api_key is None:
            raise ValueError("ETRI API 키가 제공되지 않았습니다.")

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Authorization": api_key
    }

    payload = {
        "argument": {
            "text": text,
            "analysis_code": DEFAULT_ANALYSIS_CODE
        }
    }

    try:
        response = requests.post(ETRI_SPOKEN_API_URL, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            print(f"구어체 API HTTP 오류: {response.status_code}")
            # 구어체 API 실패 시 일반 API로 폴백
            print("구어체 API 실패, 일반 API로 재시도...")
            return extract_svo_korean_etri(text, api_key)

        data = response.json()
        print(f"구어체 API Response: {json.dumps(data, indent=2, ensure_ascii=False)}")  # 전체 응답 출력
        
        # 빈 응답 체크
        if not data.get("return_object") or not data["return_object"].get("sentence"):
            print("구어체 API 빈 응답, 일반 API로 재시도...")
            return extract_svo_korean_etri(text, api_key)
        
        sentences = data.get("return_object", {}).get("sentence", [])

        svo_list = []
        for sentence in sentences:
            # SRL 필드에서 의미역 정보 추출
            srl_list = sentence.get("SRL", [])
            for srl in srl_list:
                verb = srl.get("verb", "")
                subject = None
                obj = None
                
                # argument에서 주어(ARG0)와 목적어(ARG1, ARG2) 찾기
                for arg in srl.get("argument", []):
                    arg_type = arg.get("type", "")
                    arg_text = arg.get("text", "")
                    
                    if arg_type == "ARG0":  # 주어
                        subject = arg_text
                    elif arg_type in ["ARG1", "ARG2"]:  # 목적어
                        obj = arg_text
                
                # SVO가 모두 있는 경우만 추가
                if subject and verb and obj:
                    svo_list.append({
                        "S": subject,
                        "V": verb,
                        "O": obj
                    })
            
            # 기존 semantic_role 필드도 확인 (하위 호환성)
            semantic_roles = sentence.get("semantic_role", [])
            for srl in semantic_roles:
                verb = srl.get("predicate", {}).get("text", "")
                subject = None
                obj = None
                for arg in srl.get("argument", []):
                    if arg["type"] == "ARG0":
                        subject = arg["text"]
                    elif arg["type"] in ["ARG1", "ARG2"]:
                        obj = arg["text"]
                if subject and verb and obj:
                    svo_list.append({
                        "S": subject,
                        "V": verb,
                        "O": obj
                    })

        return svo_list
        
    except Exception as e:
        print(f"구어체 API 오류: {e}")
        print("일반 API로 재시도...")
        return extract_svo_korean_etri(text, api_key)


if __name__ == "__main__":
    # 핵심 테스트 케이스들 (성공/실패 패턴 분석용)
    test_sentences = [
        # ✅ 성공 예상 - 명확한 SVO
        "학생이 책을 읽는다.",
        "엄마가 밥을 짓는다.",
        "개가 고양이를 쫓는다.",
        
        # ❌ 실패 예상 - 복잡한 구조
        "윤동주는 한국의 독립운동가이자 시인이었다.",
        "안녕하세요, 저는 김철수입니다.",
        "오늘 날씨가 정말 좋네요",
        
        # 테스트용 간단한 문장들
        "나는 사과를 먹었다.",
        "그는 나에게 선물을 주었다.",
        "아이가 친구와 함께 놀았다.",
    ]
    
    # 환경변수에서 API 키를 가져오거나, 직접 입력
    api_key = os.getenv("ETRI_API_KEY")
    if api_key is None:
        print("ETRI_API_KEY 환경변수가 설정되지 않았습니다.")
        exit(1)
    
    print(f"API Key: {api_key[:10]}...")  # API 키 앞 10자리만 출력
    print(f"\n=== 한국어 SVO 추출 패턴 분석 ===\n")
    
    success_count = 0
    total_count = len(test_sentences)
    
    # 각 테스트 케이스 실행
    for i, text in enumerate(test_sentences, 1):
        print(f"--- Test {i}: {text} ---")
        try:
            results = extract_svo_korean_etri(text, api_key)
            if results:
                success_count += 1
                print(f"✅ SUCCESS - Found {len(results)} SVO triples:")
                for j, r in enumerate(results, 1):
                    print(f"  {j}. S: {r['S']}, V: {r['V']}, O: {r['O']}")
            else:
                print("❌ FAILED - No SVO triples found")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        print()
    
    # 구어체 API 테스트 (폴백 기능 포함)
    print("=== 구어체 API 테스트 (폴백 기능 포함) ===")
    spoken_test_cases = [
        "안녕하세요 홍길동 교수입니다",
        "오늘 날씨가 정말 좋네요",
        "저는 한국어를 배우고 있어요"
    ]
    
    for i, text in enumerate(spoken_test_cases, 1):
        print(f"--- Spoken Test {i}: {text} ---")
        try:
            results = extract_svo_korean_etri_spoken(text, api_key)
            if results:
                print(f"✅ SUCCESS - Found {len(results)} SVO triples:")
                for j, r in enumerate(results, 1):
                    print(f"  {j}. S: {r['S']}, V: {r['V']}, O: {r['O']}")
            else:
                print("❌ FAILED - No SVO triples found")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        print()
    
    # 통계 출력
    print("=== 테스트 결과 요약 ===")
    print(f"총 테스트 케이스: {total_count}")
    print(f"성공: {success_count}")
    print(f"실패: {total_count - success_count}")
    print(f"성공률: {success_count/total_count*100:.1f}%")
    
    print("\n=== 성공/실패 패턴 분석 ===")
    print("✅ 성공하는 문장: 명확한 주어-동사-목적어 구조")
    print("❌ 실패하는 문장: 복잡한 서술, 인사말, 형용사 서술어")
    print("💡 구어체 API는 현재 빈 응답을 반환하여 일반 API로 폴백됨")
