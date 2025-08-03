#!/usr/bin/env python3
"""
할루시네이션 판단 로직 테스트 스크립트
"""

import requests
import json

def test_wikipedia_analysis():
    """Wikipedia 기반 할루시네이션 분석 테스트"""
    
    # 테스트 데이터
    test_cases = [
        {
            "query": "세종대왕은 1397년에 태어났다.",
            "keywords": ["세종대왕", "1397년", "태어났다"],
            "main_keyword": "세종대왕"
        },
        {
            "query": "윤동주는 한국의 독립운동가이자 시인이었다.",
            "keywords": ["윤동주", "독립운동가", "시인"],
            "main_keyword": "윤동주"
        },
        {
            "query": "김연아는 2010년 밴쿠버 올림픽에서 금메달을 땄다.",
            "keywords": ["김연아", "2010년", "밴쿠버", "올림픽", "금메달"],
            "main_keyword": "김연아"
        }
    ]
    
    print("=== Wikipedia 기반 할루시네이션 분석 테스트 ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"테스트 케이스 {i}: {test_case['query']}")
        print(f"키워드: {test_case['keywords']}")
        print(f"대표 키워드: {test_case['main_keyword']}")
        
        try:
            # Wikipedia 분석 API 호출
            response = requests.post(
                "http://localhost:8000/analyze/wikipedia",
                json={
                    "query": test_case["query"],
                    "keywords": test_case["keywords"],
                    "main_keyword": test_case["main_keyword"],
                    "top_k": 3,
                    "save_excel": False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 분석 성공!")
                print(f"후보 문장 수: {len(result.get('candidates', []))}")
                
                # 상위 3개 후보 출력
                for j, candidate in enumerate(result.get('candidates', [])[:3], 1):
                    print(f"  {j}. 유사도: {candidate.get('similarity', 0):.3f}")
                    print(f"     문장: {candidate.get('sentence', '')[:100]}...")
                    print(f"     NLI: {candidate.get('nli_label', 'unknown')} ({candidate.get('nli_score', 0):.3f})")
                    print()
            else:
                print(f"❌ 분석 실패: {response.status_code}")
                print(f"오류: {response.text}")
                
        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
        
        print("-" * 50)

def test_sentence_similarity():
    """문장 유사도 계산 테스트"""
    
    print("\n=== 문장 유사도 계산 테스트 ===\n")
    
    # 테스트 문장 쌍들
    test_pairs = [
        ("세종대왕은 1397년에 태어났다.", "세종대왕은 1397년에 태어났다."),  # 동일 문장
        ("세종대왕은 1397년에 태어났다.", "세종대왕은 1397년에 태어났습니다."),  # 유사 문장
        ("세종대왕은 1397년에 태어났다.", "윤동주는 한국의 독립운동가이자 시인이었다."),  # 다른 주제
        ("김연아는 2010년 밴쿠버 올림픽에서 금메달을 땄다.", "김연아는 2010년 밴쿠버 올림픽에서 금메달을 땄다."),  # 동일 문장
    ]
    
    for i, (sentence1, sentence2) in enumerate(test_pairs, 1):
        print(f"테스트 케이스 {i}:")
        print(f"  문장1: {sentence1}")
        print(f"  문장2: {sentence2}")
        
        try:
            # 유사도 계산 API 호출 (직접 계산)
            from backend.services.sentence_similarity import SentenceSimilarityCalculator
            
            calculator = SentenceSimilarityCalculator('paraphrase-multilingual-MiniLM-L12-v2')
            result = calculator.calculate_similarity(sentence1, sentence2)
            
            print(f"  유사도: {result.get('cosine_similarity', 0):.4f}")
            print(f"  유사도 %: {result.get('similarity_percentage', 0):.2f}%")
            
        except Exception as e:
            print(f"  ❌ 오류: {str(e)}")
        
        print()

if __name__ == "__main__":
    print("🤖 ROOMBOT 할루시네이션 판단 로직 테스트")
    print("=" * 50)
    
    # 1. 문장 유사도 테스트
    test_sentence_similarity()
    
    # 2. Wikipedia 분석 테스트
    test_wikipedia_analysis()
    
    print("\n✅ 테스트 완료!") 