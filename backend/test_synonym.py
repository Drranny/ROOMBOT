#!/usr/bin/env python3
"""
유사어 검색 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.synonym_finder import SynonymFinder

def test_synonym_finder():
    """유사어 검색 테스트"""
    print("=== 유사어 검색 테스트 ===")
    
    synonym_finder = SynonymFinder()
    
    # 테스트 키워드들
    test_keywords = [
        "Yi Seong-gye",
        "Joseon", 
        "king",
        "dynasty",
        "foundation",
        "1392"
    ]
    
    for keyword in test_keywords:
        print(f"\n키워드: '{keyword}'")
        synonyms = synonym_finder.find_synonyms(keyword)
        print(f"유사어: {synonyms}")
        
        # 유사어 그룹도 확인
        group = synonym_finder._get_synonym_group(keyword)
        print(f"유사어 그룹: {group}")

if __name__ == "__main__":
    test_synonym_finder() 