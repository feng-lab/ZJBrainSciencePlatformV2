from pathlib import Path
from typing import TypeAlias

import yaml

from app.common.config import config
from app.model.enum_filed import MessageLocale

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
