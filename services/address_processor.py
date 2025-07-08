import logging
from typing import Optional, Dict, Any

from infrastructure import dadata_client, vector_client, redis_client
from services.prompt_builder import build_extraction_prompt

logger = logging.getLogger(__name__)


def extract_address_from_message(message: str) -> Optional[str]:
    """Извлекает точный адрес из сообщения с помощью LLM."""

    address_suggestions = vector_client.fetch_address_suggestions(message)
    if not address_suggestions:
        logger.warning("Не найдено адресных подсказок", extra={"input_message": message})
        return None

    example_addresses = ", ".join(addr['address'] for addr in address_suggestions[:3])

    prompt_data = redis_client.fetch_prompt_data("scheme:prompt")
    if not prompt_data:
        logger.warning("Промпт не найден", extra={"prompt_scheme": "scheme:prompt"})
        return None

    prompt = build_extraction_prompt(prompt_data, example_addresses)

    return extract_address_with_llm(prompt, message)


def extract_address_with_llm(prompt: str, message: str) -> str:
    """Использует LLM для извлечения точного адреса из сообщения."""

    from llm import gpt_client
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": message.replace("'", '"').replace('\"', '"')}
    ]

    try:
        result = gpt_client.gpt(messages)
        return result
    except Exception as e:
        logger.error("Ошибка при вызове LLM", exc_info=True, extra={"error": str(e)})
        return ""


def get_fias_id_from_address(extracted_address: str) -> Optional[Dict[str, Any]]:
    """Получает FIAS ID через DaData по извлечённому адресу."""

    suggestion = dadata_client.fetch_dadata_suggestion(extracted_address)
    if not suggestion:
        logger.warning("DaData не вернул данных", extra={"address": extracted_address})
        return None

    fias_id = (suggestion["data"].get("house_fias_id") or suggestion["data"]["fias_id"]).replace("-", "%20")
    flat_number = suggestion["data"].get("flat")

    return {
        "fias_id": fias_id,
        "flat_number": flat_number
    }