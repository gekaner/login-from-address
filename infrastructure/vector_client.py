import logging
from typing import List, Dict, Any, Optional
import requests

from config import HTTP_VECTOR, TIMEOUT

logger = logging.getLogger(__name__)


def fetch_address_suggestions(message: str) -> Optional[List[Dict[str, Any]]]:
    """
    Получает список возможных адресов из внешнего сервиса с таймаутом.
    В случае ошибки возвращает None.
    """
    url = f"{HTTP_VECTOR}address?query={message}"

    try:
        with requests.Session() as session:
            response = session.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            result = response.json()
            return result

    except requests.Timeout:
        logger.error("Превышен таймаут при запросе к Vector", extra={"url": url, "timeout": TIMEOUT})
        return None

    except requests.RequestException as e:
        logger.error("Ошибка при запросе к Vector", exc_info=True, extra={"url": url, "error": str(e)})
        return None