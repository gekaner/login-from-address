import logging
from typing import Optional, Dict, List, Any

from infrastructure import redis_client
from services.address_processor import get_fias_id_from_address, extract_address_from_message

# Инициализируем логгер
logger = logging.getLogger(__name__)


def find_login(message: str) -> Dict[str, Optional[str]]:
    """Основная функция поиска логина на основе входящего сообщения."""

    extracted_address = extract_address_from_message(message)
    if not extracted_address:
        logger.warning("Не удалось извлечь адрес из сообщения", extra={"input_message": message})
        return {'login': None, 'houseid': None, 'fiasid': None}

    fias_data = get_fias_id_from_address(extracted_address)
    if not fias_data:
        logger.warning("FIAS ID не найден для адреса", extra={"address": extracted_address})
        return {'login': None, 'houseid': None, 'fiasid': None}

    fias_id = fias_data["fias_id"]
    flat_number = fias_data["flat_number"]

    house_data = redis_client.fetch_house_data(fias_id)
    if not house_data:
        logger.warning("Дом не найден по FIAS ID", extra={"fias_id": fias_id})
        return {'login': None, 'houseid': None, 'fiasid': fias_id}

    house_id = get_house_id(house_data)

    login_data = redis_client.fetch_login_data(house_id)
    if not isinstance(login_data, dict):
        logger.warning("Логины не найдены для дома", extra={"house_id": house_id})
        return {'login': None, 'houseid': house_id, 'fiasid': fias_id}

    logins = list(login_data.keys())


    login = determine_login(logins, login_data, flat_number)

    logger.info("Поиск завершён", extra={
        "login": login,
        "house_id": house_id,
        "fias_id": fias_id
    })

    return {'login': login, 'houseid': house_id, 'fiasid': fias_id}


def get_house_id(house_data: Dict[str, Any]) -> str:
    """Извлекает ID дома из данных Redis."""
    house_id = list(house_data.keys())[0].split(":")[1]
    logger.debug("Извлечён ID дома", extra={"house_id": house_id})
    return house_id


def match_logins_by_flat(login_data: Dict[str, Any], flat_number: int) -> List[str]:
    """Фильтрует логины по номеру квартиры."""
    matched = [login for login in login_data if login_data[login]['flat'] == flat_number]
    return matched


def select_login_based_on_service(mes: str, logins: List[str], login_data: Dict[str, Any]) -> Optional[str]:
    """Выбирает логин на основе наличия сервиса в данных о логинах."""
    first_login, second_login = logins[0], logins[1]
    first_service = login_data[first_login].get('service', None)
    second_service = login_data[second_login].get('service', None)

    logger.debug("Сравнение логинов по наличию сервиса", extra={
        "first_login": first_login,
        "first_service": first_service,
        "second_login": second_login,
        "second_service": second_service
    })

    if first_service is None and second_service is not None:
        selected = second_login.split(':')[1]
        logger.info("Выбран второй логин", extra={"login": selected})
        return selected
    elif second_service is None and first_service is not None:
        selected = first_login.split(':')[1]
        logger.info("Выбран первый логин", extra={"login": selected})
        return selected
    else:
        logger.debug("Сервис отсутствует у обоих логинов")
        return None


def determine_login(logins: List[str], login_data: Dict[str, Any], flat_number: Optional[int]) -> Optional[str]:
    """Определяет подходящий логин на основе количества совпадений и наличия сервиса."""
    if flat_number:
        matching_logins = match_logins_by_flat(login_data, flat_number)
        count = len(matching_logins)
        if count == 1:
            selected = matching_logins[0].split(':')[1]
            return selected
        elif count == 2:
            logger.debug("Найдено два логина по квартире", extra={"logins": matching_logins})
            return select_login_based_on_service("", matching_logins, login_data)
        logger.warning("Совпадений по квартире не найдено", extra={"flat_number": flat_number})
        return None
    else:
        count = len(logins)
        if count == 1:
            selected = logins[0].split(':')[1]
            logger.info("Найден один логин без указания квартиры", extra={"login": selected})
            return selected
        elif count == 2:
            logger.debug("Найдено два логина без указания квартиры", extra={"logins": logins})
            return select_login_based_on_service("", logins, login_data)
        logger.warning("Логины не найдены", extra={"logins_count": count})
        return None