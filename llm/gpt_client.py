from openai import OpenAI
from httpx import Client, Proxy
from config import API_GPT, PROXY

def gpt(message):
    http_client = Client(proxy=PROXY)

    client = OpenAI(
        api_key=API_GPT,
        http_client=http_client
    )

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=message
    )

    return completion.choices[0].message.content