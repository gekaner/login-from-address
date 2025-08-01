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
    city_fias = fias_data["city_fias"]

    house_data = redis_client.fetch_house_data(fias_id)
    if not house_data:
        logger.warning("Дом не найден по FIAS ID", extra={"fias_id": fias_id})
        return {'login': None, 'houseid': None, 'fiasid': fias_id, 'city_fias': city_fias}

    house_id = get_house_id(house_data)

    login_data = redis_client.fetch_login_data(house_id)
    if not isinstance(login_data, dict):
        logger.warning("Логины не найдены для дома", extra={"house_id": house_id})
        return {'login': None, 'houseid': house_id, 'fiasid': fias_id, 'city_fias': city_fias}

    logins = list(login_data.keys())


    login = determine_login(logins, login_data, flat_number)

    logger.info("Поиск завершён", extra={
        "login": login,
        "house_id": house_id,
        "fias_id": fias_id
    })

    return {'login': login, 'houseid': house_id, 'fiasid': fias_id, 'city_fias': city_fias}


def get_house_id(house_data: Dict[str, Any]) -> str:
    """Извлекает ID дома из данных Redis."""
    house_id = list(house_data.keys())[0].split(":")[1]
    logger.debug("Извлечён ID дома", extra={"house_id": house_id})
    return house_id


def match_logins_by_flat(login_data: Dict[str, Any], flat_number: int) -> List[str]:
    """Фильтрует логины по номеру квартиры."""
    logger.info(f'МАССИВЧИК ЛОГИНЧИКОВ!!!!! {login_data}', extra={'login_data': login_data})
    logger.info(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! {flat_number}", extra={"flat_number": flat_number})
    for login in login_data:
        loginchik = login_data[login]['login']
        kvartirka = login_data[login]['flat']
        logger.info(f'ЛОГИНЧИК {loginchik} КВАРТИРКА {kvartirka}', extra={'login': loginchik, 'flat':kvartirka})
        logger.info(f'ОКЕЙ ЛАДНО ТИП КВАРТИРКИ: {type(kvartirka)}, ТИП КВАРТИРКИ ИЗ ДАДАТЫ: {type(flat_number)}', extra={'kv': kvartirka, 'kvda': flat_number})
    matched = [login for login in login_data if login_data[login]['flat'] == int(flat_number)]
    logger.info(f"&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&& {matched}", extra={"matched": matched})
    return matched


def select_login_based_on_service(mes: str, logins: List[str], login_data: Dict[str, Any]) -> Optional[str]:
    """Выбирает логин на основе наличия сервиса в данных о логинах."""
    first_login, second_login = logins[0], logins[1]
    first_service = login_data[first_login].get('services', None)
    logger.info(f'ПЕРВЫЙ ЛОГИНЧИК СЕРВИСЫ!!!!!!!!!!!!!: {first_service}')
    second_service = login_data[second_login].get('services', None)
    logger.info(f'ВТОРОЙ ЛОГИНЧИК СЕРВИСЫ!!!!!!!!!!!!!: {second_service}')

    logger.debug("Сравнение логинов по наличию сервиса", extra={
        "first_login": first_login,
        "first_service": first_service,
        "second_login": second_login,
        "second_service": second_service
    })

    if (first_service is None or first_service == []) and second_service is not None:
        selected = second_login.split(':')[1]
        logger.info("Выбран второй логин", extra={"login": selected})
        return selected
    elif (second_service is None or second_service == []) and first_service is not None:
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