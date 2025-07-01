import logging
import yaml
from fastapi import FastAPI
from services.login_finder import find_login
import logging.config
import os

# ----> Загружаем конфигурацию логгирования <----
with open("config/logging_config.yaml", "r") as f:
    config = yaml.safe_load(f)
    logging.config.dictConfig(config)

# Теперь логгер работает!
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/adress")
async def process_request(query: str):
    logger.info(f"Получен запрос на поиск логина. query = {query}", extra={"query": query})
    try:
        result = find_login(query)
        logger.info("Логин найден", extra={"result": result})
        return result
    except Exception as e:
        logger.error("Ошибка при обработке запроса", exc_info=True, extra={"error": str(e)})
        return {"error": "Internal Server Error"}