from sentence_transformers import SentenceTransformer, util
import torch
import numpy as np
from typing import List, Tuple, Dict, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentenceSimilarityCalculator:
    """
    SBERT를 이용한 문장 유사도 계산 클래스
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        SBERT 모델 초기화
        
        Args:
            model_name (str): 사용할 SBERT 모델명
                - 'all-MiniLM-L6-v2': 빠르고 가벼운 모델 (기본값)
                - 'all-mpnet-base-v2': 더 정확하지만 느린 모델
                - 'paraphrase-multilingual-MiniLM-L12-v2': 다국어 지원
        """
        self.model_name = model_name
        logger.info(f"Loading SBERT model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info("SBERT model loaded successfully")
    
    def calculate_similarity(self, sentence1: str, sentence2: str) -> Dict[str, Any]:
        """
        두 문장 간의 유사도를 계산
        
        Args:
            sentence1 (str): 첫 번째 문장
            sentence2 (str): 두 번째 문장
            
        Returns:
            Dict[str, Any]: 유사도 정보를 담은 딕셔너리
        """
        try:
            # 문장을 임베딩으로 변환
            embeddings = self.model.encode([sentence1, sentence2], convert_to_tensor=True)
            
            # 코사인 유사도 계산
            cosine_similarity = util.pytorch_cos_sim(embeddings[0], embeddings[1]).item()
            
            # 유클리드 거리 계산
            euclidean_distance = torch.dist(embeddings[0], embeddings[1]).item()
            
            # 유사도 점수 (0-1 범위로 정규화)
            similarity_score = float(cosine_similarity)
            
            return {
                "sentence1": sentence1,
                "sentence2": sentence2,
                "cosine_similarity": similarity_score,
                "euclidean_distance": euclidean_distance,
                "similarity_percentage": round(similarity_score * 100, 2),
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return {
                "error": str(e),
                "sentence1": sentence1,
                "sentence2": sentence2
            }
    
    def calculate_batch_similarity(self, sentence_pairs: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
        """
        여러 문장 쌍의 유사도를 일괄 계산
        
        Args:
            sentence_pairs (List[Tuple[str, str]]): 문장 쌍들의 리스트
            
        Returns:
            List[Dict[str, Any]]: 각 문장 쌍의 유사도 정보 리스트
        """
        results = []
        
        for i, (sentence1, sentence2) in enumerate(sentence_pairs):
            logger.info(f"Processing pair {i+1}/{len(sentence_pairs)}")
            result = self.calculate_similarity(sentence1, sentence2)
            results.append(result)
        
        return results
    
    def find_most_similar(self, query_sentence: str, candidate_sentences: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        쿼리 문장과 가장 유사한 문장들을 찾기
        
        Args:
            query_sentence (str): 쿼리 문장
            candidate_sentences (List[str]): 후보 문장들
            top_k (int): 반환할 상위 유사 문장 수
            
        Returns:
            List[Dict[str, Any]]: 유사도 순으로 정렬된 결과 리스트
        """
        try:
            # 쿼리 문장과 후보 문장들을 임베딩
            query_embedding = self.model.encode(query_sentence, convert_to_tensor=True)
            candidate_embeddings = self.model.encode(candidate_sentences, convert_to_tensor=True)
            
            # 코사인 유사도 계산
            similarities = util.pytorch_cos_sim(query_embedding, candidate_embeddings)[0]
            
            # 상위 k개 결과 추출
            top_results = torch.topk(similarities, min(top_k, len(candidate_sentences)))
            
            results = []
            for score, idx in zip(top_results.values, top_results.indices):
                results.append({
                    "sentence": candidate_sentences[idx],
                    "similarity_score": float(score),
                    "similarity_percentage": round(float(score) * 100, 2),
                    "rank": len(results) + 1
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error finding most similar sentences: {str(e)}")
            return [{"error": str(e)}]

# 사용 예시
if __name__ == "__main__":
    # SBERT 계산기 초기화
    calculator = SentenceSimilarityCalculator()
    
    # 예시 문장들
    sentence1 = "안녕하세요, 오늘 날씨가 좋네요."
    sentence2 = "안녕하세요, 오늘 날씨가 정말 좋습니다."
    sentence3 = "오늘은 비가 많이 와서 우산을 써야겠어요."
    
    # 두 문장 간 유사도 계산
    print("=== 두 문장 간 유사도 계산 ===")
    result = calculator.calculate_similarity(sentence1, sentence2)
    print(f"문장1: {result['sentence1']}")
    print(f"문장2: {result['sentence2']}")
    print(f"코사인 유사도: {result['cosine_similarity']:.4f}")
    print(f"유사도 퍼센트: {result['similarity_percentage']}%")
    print(f"유클리드 거리: {result['euclidean_distance']:.4f}")
    
    # 가장 유사한 문장 찾기
    print("\n=== 가장 유사한 문장 찾기 ===")
    candidates = [sentence2, sentence3, "오늘 날씨가 흐려요.", "안녕하세요, 반갑습니다."]
    similar_results = calculator.find_most_similar(sentence1, candidates, top_k=3)
    
    for result in similar_results:
        print(f"순위 {result['rank']}: {result['sentence']}")
        print(f"  유사도: {result['similarity_percentage']}%") 