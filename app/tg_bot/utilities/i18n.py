from fluent_compiler.bundle import FluentBundle

from fluentogram import FluentTranslator, TranslatorHub


def create_translator_hub() -> TranslatorHub:
    translator_hub = TranslatorHub(
        {
            "ru": ("ru", "en"),
            "en": ("en", "ru")
        },
        [
            FluentTranslator(
                locale="ru",
                translator=FluentBundle.from_files(
                    locale="ru-RU",
                    filenames=["locales/ru/user.ftl",
                               "locales/ru/fire_resistance.ftl",
                               "locales/ru/fire_risk.ftl",
                               "locales/ru/fire_category.ftl",
                               "locales/ru/admin.ftl",
                               "locales/ru/data_base_subs.ftl",
                               "locales/ru/other.ftl"])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["locales/en/user.ftl",
                               "locales/ru/fire_resistance.ftl",
                               "locales/ru/fire_risk.ftl",
                               "locales/ru/fire_category.ftl",
                               "locales/ru/admin.ftl",
                               "locales/ru/data_base_subs.ftl",
                               "locales/ru/other.ftl"]))
        ],
    )
    return translator_hub
