from openai import OpenAI
import httpx

from config import API_GPT, PROXY


def gpt(message):
    # Настройка прокси
    proxy = PROXY  # Замените на адрес вашего прокси
    proxies = {
        "http://": proxy,
        "https://": proxy,
    }

    # Создаем HTTP-клиент с поддержкой прокси
    http_client = httpx.Client(proxies=proxies)

    client = OpenAI(
    api_key=API_GPT,
    http_client=http_client
    )

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=message
    )
    lala = completion.choices[0].message
    return lala.content