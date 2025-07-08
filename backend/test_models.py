#!/usr/bin/env python3
"""
여러 SBERT 모델을 비교 테스트하는 스크립트
"""

import requests
import json
import time
from typing import List, Dict, Any

# 서버 설정
SERVERS = {
    "multilingual-minilm": "http://localhost:8000",  # 기존 서버
    "mpnet-base": "http://localhost:8001",
    "multilingual-mpnet": "http://localhost:8002", 
    "t5-base": "http://localhost:8003"
}

# 테스트 문장 쌍들
TEST_PAIRS = [
    ("Python is a popular programming language.", "Python is a popular language."),
    ("JavaScript is widely used in web development.", "JavaScript is used for web development."),
    ("The weather is nice today.", "It's raining heavily today."),
    ("This product is really effective.", "This product doesn't work at all."),
    ("I'm learning Python.", "I'm studying Python."),
    ("That movie was really fun.", "I enjoyed watching that movie."),
    ("I went to the library today.", "I went to the library yesterday."),
    ("The cat is on the bed.", "The dog is on the bed."),
    ("King Sejong founded Joseon in 1392.", "Joseon was founded by Yi Seong-gye in 1392."),
    ("GPT speaks Korean fluently.", "GPT doesn't understand Korean."),
    ("He was holding a flower in his hand.", "He solved the problem with his hands."),
    ("AI wrote the text.", "AI is installed in robotic vacuum cleaners."),
    ("I bought a computer today.", "Yesterday, my friend bought a laptop."),
    ("He works out every day.", "Exercise is good for your health."),
    ("Bananas are yellow.", "Paris is the capital of France."),
    ("I have an exam tomorrow.", "I drank coffee today."),
]

def test_similarity_endpoint(server_url: str, sentence1: str, sentence2: str) -> Dict[str, Any]:
    """단일 유사도 계산 테스트"""
    try:
        response = requests.post(
            f"{server_url}/similarity",
            json={
                "sentence1": sentence1,
                "sentence2": sentence2
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

def test_batch_similarity(server_url: str, sentence_pairs: List[List[str]]) -> Dict[str, Any]:
    """배치 유사도 계산 테스트"""
    try:
        response = requests.post(
            f"{server_url}/batch-similarity",
            json={
                "sentence_pairs": sentence_pairs
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

def test_find_similar(server_url: str, query: str, candidates: List[str], top_k: int = 3) -> Dict[str, Any]:
    """유사한 문장 찾기 테스트"""
    try:
        response = requests.post(
            f"{server_url}/find-similar",
            json={
                "query_sentence": query,
                "candidate_sentences": candidates,
                "top_k": top_k
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

def check_server_health(server_url: str) -> bool:
    """서버 헬스 체크"""
    try:
        response = requests.get(f"{server_url}/health", timeout=10)
        return response.status_code == 200
    except:
        return False

def print_results(server_name: str, results: Dict[str, Any]):
    """결과 출력"""
    print(f"\n=== {server_name} 결과 ===")
    if "error" in results:
        print(f"❌ 오류: {results['error']}")
    else:
        print(f"✅ 성공")
        if "cosine_similarity" in results:
            print(f"   코사인 유사도: {results['cosine_similarity']:.4f}")
            print(f"   유클리드 거리: {results['euclidean_distance']:.4f}")
            print(f"   유사도 퍼센트: {results['similarity_percentage']:.2f}%")
        elif "results" in results:
            print(f"   총 {results.get('total_pairs', len(results['results']))}개 쌍 처리됨")
        elif "query_sentence" in results:
            print(f"   쿼리: {results['query_sentence']}")
            print(f"   상위 {results.get('top_k', 3)}개 결과:")
            for i, result in enumerate(results['results'][:3], 1):
                print(f"     {i}. {result['sentence']} (유사도: {result['similarity']:.4f})")

def main():
    print("🤖 SBERT 모델 비교 테스트 시작")
    print("=" * 50)
    
    # 서버 상태 확인
    print("서버 상태 확인 중...")
    for server_name, server_url in SERVERS.items():
        if check_server_health(server_url):
            print(f"✅ {server_name}: {server_url} - 정상")
        else:
            print(f"❌ {server_name}: {server_url} - 연결 실패")
    
    print("\n" + "=" * 50)
    
    # 1. 단일 유사도 계산 테스트
    print("\n📊 단일 유사도 계산 테스트")
    print("-" * 30)
    
    for i, (sentence1, sentence2) in enumerate(TEST_PAIRS, 1):
        print(f"\n테스트 {i}: '{sentence1}' vs '{sentence2}'")
        
        for server_name, server_url in SERVERS.items():
            if check_server_health(server_url):
                start_time = time.time()
                result = test_similarity_endpoint(server_url, sentence1, sentence2)
                end_time = time.time()
                
                print(f"  {server_name}: ", end="")
                if "error" not in result:
                    print(f"{result.get('cosine_similarity', 0):.4f} ({end_time - start_time:.2f}s)")
                else:
                    print(f"오류: {result['error']}")
            else:
                print(f"  {server_name}: 서버 연결 실패")
    
    # 2. 배치 유사도 계산 테스트
    print("\n\n📋 배치 유사도 계산 테스트")
    print("-" * 30)
    
    batch_pairs = [list(pair) for pair in TEST_PAIRS[:3]]  # 처음 3개 쌍만 테스트
    
    for server_name, server_url in SERVERS.items():
        if check_server_health(server_url):
            print(f"\n{server_name}:")
            start_time = time.time()
            result = test_batch_similarity(server_url, batch_pairs)
            end_time = time.time()
            
            if "error" not in result:
                print(f"  ✅ {result.get('total_pairs', 0)}개 쌍 처리 완료 ({end_time - start_time:.2f}s)")
                for i, pair_result in enumerate(result.get('results', [])[:2]):
                    print(f"    {i+1}. 유사도: {pair_result.get('cosine_similarity', 0):.4f}")
            else:
                print(f"  ❌ 오류: {result['error']}")
        else:
            print(f"\n{server_name}: 서버 연결 실패")
    
    # 3. 유사한 문장 찾기 테스트
    print("\n\n🔍 유사한 문장 찾기 테스트")
    print("-" * 30)
    
    query = "안녕하세요"
    candidates = [
        "안녕",
        "반갑습니다", 
        "Hello",
        "Good morning",
        "안녕하세요 반갑습니다",
        "오늘 날씨가 좋네요",
        "이 음식은 맛있습니다"
    ]
    
    for server_name, server_url in SERVERS.items():
        if check_server_health(server_url):
            print(f"\n{server_name}:")
            start_time = time.time()
            result = test_find_similar(server_url, query, candidates, top_k=3)
            end_time = time.time()
            
            if "error" not in result:
                print(f"  ✅ 쿼리: '{query}' ({end_time - start_time:.2f}s)")
                for i, item in enumerate(result.get('results', [])[:3], 1):
                    print(f"    {i}. '{item.get('sentence', '')}' (유사도: {item.get('similarity', 0):.4f})")
            else:
                print(f"  ❌ 오류: {result['error']}")
        else:
            print(f"\n{server_name}: 서버 연결 실패")
    
    print("\n" + "=" * 50)
    print("🎉 테스트 완료!")

if __name__ == "__main__":
    main() 