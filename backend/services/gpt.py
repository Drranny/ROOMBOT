import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 API 키 가져오기 (curl에서 사용한 키로 업데이트)
api_key = os.getenv("OPENAI_API_KEY", "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")
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")

client = OpenAI(api_key=api_key)

def detect_language(text: str) -> str:
    """
    텍스트의 언어를 감지하는 함수
    """
    # 간단한 언어 감지 (한국어 vs 영어)
    korean_chars = sum(1 for char in text if '\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af')
    english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
    
    # 한국어 문자가 더 많으면 한국어, 아니면 영어
    if korean_chars > english_chars:
        return "ko"
    else:
        return "en"

def call_gpt(user_input: str) -> str:
    """
    OpenAI API를 사용하여 GPT 응답을 가져오는 함수
    """
    try:
        # 언어 감지
        language = detect_language(user_input)
        
        # 언어별 시스템 프롬프트 설정
        if language == "en":
            system_prompt = """You are an AI that provides clear SVO (Subject-Verb-Object) structured answers.

Response writing rules:
1. Provide answers with clear Subject (S), Verb (V), Object (O) structure
2. If there are multiple SVOs in one sentence, break them into separate clear sentences
3. Maintain accurate information like years, dates, etc.
4. Minimize unnecessary modifiers or adverbs
5. Avoid complex sentence structures or nested clauses
6. Deliver key information concisely and clearly
7. Use specific verbs rather than generic ones like "is" or "does"
8. Don't include unknown information or speculation, only provide certain facts

Example:
❌ "King Sejong created Hangul in 1443, and it was officially announced as 'Hunminjeongeum' in 1446."
✅ "King Sejong created Hangul. King Sejong created Hangul in 1443. King Sejong announced Hunminjeongeum in 1446."

Please explain naturally and concisely."""
        else:
            system_prompt = """너는 SVO(주어-동사-목적어) 구조가 명확한 답변을 주는 AI야. 

답변 작성 규칙:
1. 주어(S), 동사(V), 목적어(O)가 명확한 문장으로 답변해
2. 하나의 문장에 여러 SVO가 있으면 문장을 끊어서 각각 명확하게 표현해
3. 년도, 날짜 등 정확한 정보는 그대로 유지해
4. 불필요한 수식어나 부사어는 최소화해
5. 복잡한 문장 구조나 중첩된 절은 피해
6. 핵심 정보를 간결하고 명확하게 전달해
7. "~입니다", "~합니다" 같은 서술어보다는 구체적인 동사를 사용해
8. 미상의 정보나 추측은 포함하지 말고 확실한 정보만 제공해

예시:
❌ "세종대왕이 한글을 창제한 날짜는 1443년으로 알려져 있으며, 1446년에 '훈민정음'이라는 이름으로 공식 발표되었습니다."
✅ "세종대왕이 한글을 창제했다. 세종대왕이 1443년에 한글을 창제했다. 세종대왕이 1446년에 훈민정음을 발표했다."

질문에 대해 자연스럽고 간결하게 설명해줘."""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.5,
            max_tokens=180,
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"상세 오류: {e}")
        return f"오류가 발생했습니다: {str(e)}"

# 테스트용 함수
def test_gpt():
    """GPT 연결 테스트"""
    try:
        result = call_gpt("안녕하세요! 간단한 인사말을 해주세요.")
        print("✅ GPT 연결 성공!")
        print(f"응답: {result}")
        return True
    except Exception as e:
        print(f"❌ GPT 연결 실패: {e}")
        return False

if __name__ == "__main__":
    test_gpt()
