import logging
import json
import requests
from typing import List, Dict, Any, Optional

from config import DADATA_TOKEN

logger = logging.getLogger(__name__)


def fetch_dadata_suggestion(extracted_address: str) -> Optional[Dict[str, Any]]:
    """Получает данные из DaData по извлечённому адресу."""

    url = "http://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/address"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Token {DADATA_TOKEN}"
    }
    data = {"query": extracted_address}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        result = response.json()

        logger.info("Данные от DaData получены", extra={"result": result})
        return result["suggestions"][0] if result.get("suggestions") else None

    except requests.RequestException as e:
        logger.error("Ошибка при запросе к DaData", exc_info=True, extra={"error": str(e)})
        return None