import os
from openai import OpenAI, RateLimitError, OpenAIError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key="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")

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
