#!/usr/bin/env python3
"""
NLI(Natural Language Inference) 테스트용 스크립트 (SBERT와 별개, 독립 실행)
"""

from typing import List, Tuple

# NLI 테스트 케이스 (premise, hypothesis, gold label)
NLI_TESTS: List[Tuple[str, str, str]] = [
    ("A soccer game with multiple males playing.", "Some men are playing a sport.", "entailment"),
    ("A man inspects the uniform of a figure in some East Asian country.", "The man is sleeping.", "contradiction"),
    ("A woman is reading.", "A woman is eating.", "neutral"),
    # ... 추가 케이스 가능
]

def dummy_similarity(premise: str, hypothesis: str) -> float:
    """(임시) 두 문장 유사도 점수 반환 - 실제 모델 inference로 대체 가능"""
    # 예시: 완전 일치면 1.0, 일부 단어 겹치면 0.7, 전혀 다르면 0.2
    if premise == hypothesis:
        return 1.0
    elif any(word in hypothesis for word in premise.split()):
        return 0.7
    else:
        return 0.2

def nli_label_from_score(score: float) -> str:
    """유사도 점수 → NLI label 변환 규칙"""
    if score >= 0.8:
        return "entailment"
    elif score <= 0.4:
        return "contradiction"
    else:
        return "neutral"

def main():
    print("NLI 테스트 시작 (SBERT와 별개)")
    print("=" * 40)
    for i, (premise, hypothesis, gold) in enumerate(NLI_TESTS, 1):
        score = dummy_similarity(premise, hypothesis)
        pred = nli_label_from_score(score)
        print(f"[{i}] Premise: {premise}")
        print(f"    Hypothesis: {hypothesis}")
        print(f"    Gold: {gold} | Pred: {pred} | Score: {score:.2f}")
        print("-" * 30)

if __name__ == "__main__":
    main() 