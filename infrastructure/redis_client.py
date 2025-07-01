import logging
import json
from typing import List, Dict, Any, Optional
import requests

from config import HTTP_REDIS

logger = logging.getLogger(__name__)


def fetch_prompt_data(prompt_scheme: str) -> List[Dict[str, Any]]:
    """Загружает данные промпта из Redis."""
    url = f"{HTTP_REDIS}{prompt_scheme}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_text = response.text
        parsed_json = json.loads(raw_text)

        if isinstance(parsed_json, str):
            parsed_json = json.loads(parsed_json)
        return parsed_json

    except requests.RequestException as e:
        logger.error("Ошибка при запросе к Redis (промпты)", exc_info=True, extra={"error": str(e)})
        return []

    except json.JSONDecodeError as e:
        logger.error("Ошибка разбора JSON из Redis", exc_info=True, extra={"error": str(e)})
        return []


def fetch_house_data(fias_id: str) -> Optional[Dict[str, Any]]:
    """Получает данные о доме из Redis по FIAS ID."""
    url = f"{HTTP_REDIS}raw?query=FT.SEARCH%20idx:adds.fias%20%27@fiasUUID:%27{fias_id}%27"

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_text = response.text
        parsed_json = json.loads(raw_text)

        if isinstance(parsed_json, str):
            parsed_json = json.loads(parsed_json)

        return parsed_json

    except requests.RequestException as e:
        logger.error("Ошибка при запросе к Redis (дом)", exc_info=True, extra={"error": str(e)})
        return None

    except json.JSONDecodeError as e:
        logger.error("Ошибка разбора JSON из Redis", exc_info=True, extra={"error": str(e)})
        return None


def fetch_login_data(house_id: str) -> Dict[str, Any]:
    """Получает список логинов, связанных с домом."""
    url = (
        f"{HTTP_REDIS}raw?query=FT.SEARCH%20idx:login%20%27@houseId:[{house_id}%20{house_id}]%27%20Limit%200%20500"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        raw_text = response.text
        parsed_json = json.loads(raw_text)

        if isinstance(parsed_json, str):
            parsed_json = json.loads(parsed_json)
        return parsed_json

    except requests.RequestException as e:
        logger.error("Ошибка при запросе к Redis (логины)", exc_info=True, extra={"error": str(e)})
        return {}

    except json.JSONDecodeError as e:
        logger.error("Ошибка разбора JSON из Redis", exc_info=True, extra={"error": str(e)})
        return {}