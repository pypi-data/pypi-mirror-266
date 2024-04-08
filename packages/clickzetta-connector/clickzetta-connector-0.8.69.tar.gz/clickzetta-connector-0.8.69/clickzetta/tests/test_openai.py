import openai
import json


def test_openai_1():
    openai.api_key = ''

    q = "用python实现冒泡算法"
    rsp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": q}
        ]
    )
    print(rsp.get("choices")[0]["message"]["content"])
