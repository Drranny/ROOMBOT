#!/usr/bin/env python3
import os
import sys

# Set Java home
os.environ['JAVA_HOME'] = '/Library/Java/JavaVirtualMachines/jdk-21.jdk/Contents/Home'

try:
    from konlpy.tag import Okt
    print("KoNLPy imported successfully")
    
    # Test Okt
    okt = Okt()
    print("Okt initialized successfully")
    
    # Test with a simple Korean sentence
    text = "안녕하세요 반갑습니다"
    result = okt.pos(text)
    print(f"POS tagging result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc() 