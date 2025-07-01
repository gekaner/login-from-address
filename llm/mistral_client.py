import threading
import time
from mistralai import Mistral

from config import API_KEY

def mistral(message):

    timeout = 60

    """Вызывает API Mistral с таймаутом."""
    client = Mistral(api_key=API_KEY)
    model_name = "mistral-large-latest"


    result = [None]  # Используем список, чтобы изменить его внутри потока

    def call_api():
        
        response = client.chat.complete(
                model=model_name,
                messages=message
            )
        print(response)
        result[0] = response.choices[0].message.content


    thread = threading.Thread(target=call_api)
    thread.start()
    thread.join(timeout)  # Ждем `timeout` секунд

    if thread.is_alive():
        return None

    time.sleep(1)
    return str(result[0]) if result[0] else None