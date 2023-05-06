from enum import StrEnum
from pathlib import Path
from typing import Any, TypeAlias

import yaml

from app.common.config import config


class MessageLocale(StrEnum):
    zh_CN = "zh_CN"
    en_US = "en_US"


MessageTemplateKey: TypeAlias = tuple[str, MessageLocale]
MessageLocalizationConfig: TypeAlias = dict[MessageTemplateKey, str]


def load_message_localization_config(path: Path) -> MessageLocalizationConfig:
    with open(path, mode="rt", encoding="UTF-8") as file:
        raw_data: list[dict[str, str]] = yaml.safe_load(file)

    result: MessageLocalizationConfig = {}
    for entry in raw_data:
        message_id = entry["message_id"]
        for locale, template in entry.items():
            if locale == "message_id":
                continue
            locale = MessageLocale(locale)
            result[message_id, locale] = template
    return result


msg_l12n_config: MessageLocalizationConfig = load_message_localization_config(
    config.MESSAGE_LOCALIZATION_YAML_PATH
)


def translate_message(message_id: str, locale: MessageLocale, *format_args: Any) -> str:
    template = msg_l12n_config[message_id, locale]
    return template.format(*format_args)
