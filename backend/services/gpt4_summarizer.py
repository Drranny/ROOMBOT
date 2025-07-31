import os
import time
from openai import OpenAI, RateLimitError, OpenAIError
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 API 키 읽기
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일에 API 키를 추가해주세요.")

client = OpenAI(api_key=api_key)

def summarize_with_gpt4(text: str, keywords: list = None) -> str:
    """
    GPT-4o-mini를 사용하여 텍스트를 요약합니다.
    
    Args:
        text: 요약할 텍스트
        keywords: 관련 키워드 리스트 (선택사항)
    
    Returns:
        요약된 텍스트
    """
    try:
        # 키워드 정보가 있으면 프롬프트에 포함
        keyword_info = ""
        if keywords:
            keyword_info = f"\n관련 키워드: {', '.join(keywords)}"
        
        prompt = f"""
Summarize the following text concisely in English.{keyword_info}

Original text: {text}

Summary rules:
1. Include only key information
2. Use natural English sentences
3. Keep within 50 characters
4. Include relevant keyword information
5. Include only accurate facts

Summary:"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 최신 GPT-4o-mini 사용
            messages=[
                {"role": "system", "content": "You are a text summarization expert. Summarize key content concisely and accurately in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 낮은 temperature로 일관성 확보
            max_tokens=100,
        )
        
        # API 한도 방지를 위한 대기 (0.5초로 단축)
        time.sleep(0.5)
        
        return response.choices[0].message.content.strip()

    except RateLimitError:
        return "OpenAI API rate limit exceeded. Please try again later."
    except OpenAIError as e:
        return f"OpenAI API error: {str(e)}"
    except Exception as e:
        return f"Unknown error: {str(e)}" 