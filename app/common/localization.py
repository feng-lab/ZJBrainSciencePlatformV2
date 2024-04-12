from contextvars import ContextVar
from enum import StrEnum
from pathlib import Path
from typing import Any, TypeAlias

import yaml

from app.common.config import config


class MessageLocale(StrEnum):
    zh_CN = "zh-CN"
    en_US = "en-US"


class Entity(StrEnum):
    user = "user"
    file = "file"
    experiment = "experiment"
    device = "device"
    human_subject = "human subject"
    task = "task"
    paradigm = "paradigm"
    atlas = "atlas"
    atlas_region = "atlas_region"
    atlas_region_link = "atlas_region_link"
    atlas_behavioral_domain = "atlas_behavioral_domain"
    atlas_paradigm_class = "atlas_paradigm_class"
    dataset = "dataset"
    dataset_file = "dataset_file"
    eeg_data = "eeg_data"
    species = "species"


MessageTemplateKey: TypeAlias = tuple[str, MessageLocale]
LocalizationConfig: TypeAlias = dict[MessageTemplateKey, str]


def load_localization_config(path: Path, id_name: str) -> LocalizationConfig:
    with open(path, encoding="UTF-8") as file:
        config_entries: list[dict[str, str]] = yaml.safe_load(file)

    result: LocalizationConfig = {}
    for entry in config_entries:
        template_id = entry[id_name]
        for locale, template in entry.items():
            if locale != id_name:
                locale = MessageLocale(locale)
                result[template_id, locale] = template
    return result


message_l12n_config: LocalizationConfig = load_localization_config(config.MESSAGE_LOCALIZATION_YAML_PATH, "message_id")
entity_l12n_config: LocalizationConfig = load_localization_config(config.ENTITY_LOCALIZATION_YAML_PATH, "entity_id")

locale_ctxvar = ContextVar("locale", default=MessageLocale.zh_CN)


def translate_message(message_id: str, *format_args: Any) -> str:
    locale = locale_ctxvar.get()
    template = message_l12n_config[message_id, locale]
    return template.format(*format_args)


def translate_entity(entity: str | Entity) -> str:
    locale = locale_ctxvar.get()
    entity_value = entity_l12n_config[entity, locale]
    return entity_value
