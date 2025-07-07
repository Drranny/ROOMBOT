# -*- coding: utf-8 -*-
import openai
import sys

openai.api_key = "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"

client = openai.OpenAI(api_key=openai.api_key)

try:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "파이썬에서 리스트와 튜플의 차이는 뭐야?"}]
    )
    sys.stdout.buffer.write((response.choices[0].message.content + '\n').encode('utf-8'))
except Exception as e:
    sys.stdout.buffer.write((str(e) + '\n').encode('utf-8'))