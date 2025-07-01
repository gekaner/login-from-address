import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def build_extraction_prompt(prompt_data: List[Dict[str, Any]], example_addresses: str) -> str:
    """Создаёт текст промпта для извлечения адреса."""

    prompt_name = "address_identification"
    template = next(
        (item["template"] for item in prompt_data if item["name"] == prompt_name),
        ""
    ).replace("<", "{").replace(">", "}")

    if not template:
        logger.warning("Шаблон для промпта не найден", extra={"prompt_name": prompt_name})
        return ""

    formatted_prompt = template.format(example=example_addresses)

    return formatted_prompt