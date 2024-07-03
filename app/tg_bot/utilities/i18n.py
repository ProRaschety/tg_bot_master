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
                               "locales/ru/fire_model.ftl",
                               "locales/ru/fire_category.ftl",
                               "locales/ru/admin.ftl",
                               "locales/ru/owner.ftl",
                               "locales/ru/handbooks.ftl",
                               "locales/ru/tools.ftl",
                               "locales/ru/units_measurement.ftl",
                               "locales/ru/data_base_subs.ftl",
                               "locales/ru/fire_accident.ftl",
                               "locales/ru/fds_tools.ftl",
                               "locales/ru/terms_acronyms.ftl",
                               "locales/ru/equations.ftl",
                               "locales/ru/reports.ftl",
                               "locales/ru/probit.ftl",
                               "locales/ru/static/paths.ftl",
                               "locales/ru/other.ftl"])),
            FluentTranslator(
                locale="en",
                translator=FluentBundle.from_files(
                    locale="en-US",
                    filenames=["locales/en/user.ftl",
                               "locales/en/fire_resistance.ftl",
                               "locales/en/fire_risk.ftl",
                               "locales/en/fire_model.ftl",
                               "locales/en/fire_category.ftl",
                               "locales/en/admin.ftl",
                               "locales/en/owner.ftl",
                               "locales/en/handbooks.ftl",
                               "locales/en/tools.ftl",
                               "locales/en/units_measurement.ftl",
                               "locales/en/data_base_subs.ftl",
                               "locales/en/fire_accident.ftl",
                               "locales/en/fds_tools.ftl",
                               "locales/en/terms_acronyms.ftl",
                               "locales/en/equations.ftl",
                               "locales/en/reports.ftl",
                               "locales/en/probit.ftl",
                               "locales/en/static/paths.ftl",
                               "locales/en/other.ftl"]))
        ],
    )
    return translator_hub
