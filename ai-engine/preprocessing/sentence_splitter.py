import re

def split_sentences(text: str):
    """
    마침표/느낌표/물음표 + 인용부호/괄호 등 뒤에서
    공백이 없어도 문장 경계로 분리.
    """
    # 문장 끝 패턴: 마침표/느낌표/물음표 + 인용부호/괄호 0~2개
    # 그 뒤에 공백이 없거나, 바로 한글/영문 대문자가 오면 분리
    pattern = re.compile(r'([.!?][\"\'”’)]*)(?=[^\s])')
    parts = []
    start = 0
    for match in pattern.finditer(text):
        end = match.end()
        parts.append(text[start:end].strip())
        start = end
    last = text[start:].strip()
    if last:
        parts.append(last)
    return [s for s in parts if s]

def to_structured_json(answer: str):
    """
    입력 텍스트를 문장 단위로 분리하고, 각 문장을 구조화된 JSON 형태로 반환합니다.
    - sentence_id: 1부터 시작하는 문장 번호
    - text: 문장 내용
    - is_hallucinated: 환각 여부(초기값 None)
    - source_candidates: 출처 후보(초기값 빈 리스트)
    """
    sentences = split_sentences(answer)
    return {
        "original_answer": answer,
        "sentences": [
            {
                "sentence_id": i + 1,
                "text": s,
                "is_hallucinated": None,
                "source_candidates": []
            }
            for i, s in enumerate(sentences)
        ]
    }
'''# backend/api/analyze.py

from fastapi import APIRouter, Body
from ai_engine.preprocessing.sentence_splitter import to_structured_json

router = APIRouter()

@router.post("/analyze")
def analyze(gpt_response: str = Body(...)):
    return to_structured_json(gpt_response) 백엔드 api에서 호출하게될 코드
'''

# 테스트 코드
import json

def test():
    test_text = '세종대왕은 1392년에 조선을 건국했다.세종대왕의 아버지는 태조 이성계이다.'
    print("문장 분리 결과:")
    for i, s in enumerate(split_sentences(test_text), 1):
        print(f"{i}: {s}")

    print("\n구조화 JSON 결과:")
    print(json.dumps(to_structured_json(test_text), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    test()