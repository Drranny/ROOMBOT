import os
from openai import OpenAI, RateLimitError, OpenAIError
from dotenv import load_dotenv

load_dotenv()

# 환경변수에서 API 키 읽기
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY 환경변수가 설정되지 않았습니다. .env 파일에 API 키를 추가해주세요.")

client = OpenAI(api_key=api_key)

def call_gpt(user_input: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "너는 문장이 매끄럽고 중복 없는 답변을 주는 AI야. 질문에 대해 자연스럽고 간결하게 설명해줘."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.5,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except RateLimitError:
        return "OpenAI API 사용 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
    except OpenAIError as e:
        return f"OpenAI API 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"알 수 없는 오류가 발생했습니다: {str(e)}"
