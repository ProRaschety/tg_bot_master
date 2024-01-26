import logging
from datetime import datetime

from asyncpg import Connection

from app.infrastructure.database.models.climate_model import ClimateModel, ClimateRegion

log = logging.getLogger(__name__)

regions = [
    {
        "ID": 1,
        "REGION": "Алтайский край"
    },
    {
        "ID": 2,
        "REGION": "Республика Алтай"
    },
    {
        "ID": 3,
        "REGION": "Амурская область"
    },
    {
        "ID": 4,
        "REGION": "Архангельская область"
    },
    {
        "ID": 5,
        "REGION": "Ненецкий автономный округ"
    },
    {
        "ID": 6,
        "REGION": "Астраханская область"
    },
    {
        "ID": 7,
        "REGION": "Республика Башкортостан"
    },
    {
        "ID": 8,
        "REGION": "Белгородская область"
    },
    {
        "ID": 9,
        "REGION": "Брянская область"
    },
    {
        "ID": 10,
        "REGION": "Республика Бурятия"
    },
    {
        "ID": 11,
        "REGION": "Владимирская область"
    },
    {
        "ID": 12,
        "REGION": "Волгоградская область"
    },
    {
        "ID": 13,
        "REGION": "Вологодская область"
    },
    {
        "ID": 14,
        "REGION": "Воронежская область"
    },
    {
        "ID": 15,
        "REGION": "Нижегородская область"
    },
    {
        "ID": 16,
        "REGION": "Республика Дагестан"
    },
    {
        "ID": 17,
        "REGION": "Ивановская область"
    },
    {
        "ID": 18,
        "REGION": "Иркутская область"
    },
    {
        "ID": 19,
        "REGION": "Кабардино-Балкарская Республика"
    },
    {
        "ID": 20,
        "REGION": "Калининградская область"
    },
    {
        "ID": 21,
        "REGION": "Тверская область"
    },
    {
        "ID": 22,
        "REGION": "Республика Калмыкия"
    },
    {
        "ID": 23,
        "REGION": "Калужская область"
    },
    {
        "ID": 24,
        "REGION": "Камчатский край"
    },
    {
        "ID": 25,
        "REGION": "Республика Карелия"
    },
    {
        "ID": 26,
        "REGION": "Кемеровская область"
    },
    {
        "ID": 27,
        "REGION": "Кировская область"
    },
    {
        "ID": 28,
        "REGION": "Республика Коми"
    },
    {
        "ID": 29,
        "REGION": "Костромская область"
    },
    {
        "ID": 30,
        "REGION": "Краснодарский край"
    },
    {
        "ID": 31,
        "REGION": "Республика Адыгея"
    },
    {
        "ID": 32,
        "REGION": "Красноярский край"
    },
    {
        "ID": 33,
        "REGION": "Республика Хакасия"
    },
    {
        "ID": 34,
        "REGION": "Самарская область"
    },
    {
        "ID": 35,
        "REGION": "Курганская область"
    },
    {
        "ID": 36,
        "REGION": "Курская область"
    },
    {
        "ID": 37,
        "REGION": "Ленинградская область"
    },
    {
        "ID": 38,
        "REGION": "Липецкая область"
    },
    {
        "ID": 39,
        "REGION": "Магаданская область"
    },
    {
        "ID": 40,
        "REGION": "Чукотский автономный округ"
    },
    {
        "ID": 41,
        "REGION": "Республика Марий Эл"
    },
    {
        "ID": 42,
        "REGION": "Республика Мордовия"
    },
    {
        "ID": 43,
        "REGION": "Московская область"
    },
    {
        "ID": 44,
        "REGION": "Мурманская область"
    },
    {
        "ID": 45,
        "REGION": "Новгородская область"
    },
    {
        "ID": 46,
        "REGION": "Новосибирская область"
    },
    {
        "ID": 47,
        "REGION": "Омская область"
    },
    {
        "ID": 48,
        "REGION": "Оренбургская область"
    },
    {
        "ID": 49,
        "REGION": "Орловская область"
    },
    {
        "ID": 50,
        "REGION": "Пензенская область"
    },
    {
        "ID": 51,
        "REGION": "Пермский край"
    },
    {
        "ID": 52,
        "REGION": "Приморский край"
    },
    {
        "ID": 53,
        "REGION": "Псковская область"
    },
    {
        "ID": 54,
        "REGION": "Ростовская область"
    },
    {
        "ID": 55,
        "REGION": "Рязанская область"
    },
    {
        "ID": 56,
        "REGION": "Саратовская область"
    },
    {
        "ID": 57,
        "REGION": "Сахалинская область"
    },
    {
        "ID": 58,
        "REGION": "Республика Северная Осетия - Алания"
    },
    {
        "ID": 59,
        "REGION": "Свердловская область"
    },
    {
        "ID": 60,
        "REGION": "Смоленская область"
    },
    {
        "ID": 61,
        "REGION": "Ставропольский край"
    },
    {
        "ID": 62,
        "REGION": "Тамбовская область"
    },
    {
        "ID": 63,
        "REGION": "Республика Татарстан"
    },
    {
        "ID": 64,
        "REGION": "Томская область"
    },
    {
        "ID": 65,
        "REGION": "Республика Тыва"
    },
    {
        "ID": 66,
        "REGION": "Тульская область"
    },
    {
        "ID": 67,
        "REGION": "Тюменская область"
    },
    {
        "ID": 68,
        "REGION": "Ханты-Мансийский автономный округ - Югра"
    },
    {
        "ID": 69,
        "REGION": "Ямало-Ненецкий автономный округ"
    },
    {
        "ID": 70,
        "REGION": "Удмуртская Республика"
    },
    {
        "ID": 71,
        "REGION": "Ульяновская область"
    },
    {
        "ID": 72,
        "REGION": "Хабаровский край"
    },
    {
        "ID": 73,
        "REGION": "Еврейская автономная область"
    },
    {
        "ID": 74,
        "REGION": "Челябинская область"
    },
    {
        "ID": 75,
        "REGION": "Чеченская Республика"
    },
    {
        "ID": 76,
        "REGION": "Забайкальский край"
    },
    {
        "ID": 77,
        "REGION": "Республика Чувашия"
    },
    {
        "ID": 78,
        "REGION": "Республика Саха (Якутия)"
    },
    {
        "ID": 79,
        "REGION": "Ярославская область"
    },
    {
        "ID": 80,
        "REGION": "Республика Крым"
    }
]
cities = [
    {
        "CITY": "Алейск",
        "ID": 1,
        "LATITUDE": 52.492167,
        "LONGITUDE": 82.779448,
        "REGIONID": 1
    },
    {
        "CITY": "Барнаул",
        "ID": 2,
        "LATITUDE": 53.355084,
        "LONGITUDE": 83.769948,
        "REGIONID": 1
    },
    {
        "CITY": "Бийск",
        "ID": 3,
        "LATITUDE": 52.539297,
        "LONGITUDE": 85.21382,
        "REGIONID": 1
    },
    {
        "CITY": "Змеиногорск",
        "ID": 4,
        "LATITUDE": 51.158015,
        "LONGITUDE": 82.18727,
        "REGIONID": 1
    },
    {
        "CITY": "Родино",
        "ID": 5,
        "LATITUDE": 52.496191,
        "LONGITUDE": 80.210482,
        "REGIONID": 1
    },
    {
        "CITY": "Рубцовск",
        "ID": 6,
        "LATITUDE": 51.501207,
        "LONGITUDE": 81.2078,
        "REGIONID": 1
    },
    {
        "CITY": "Славгород",
        "ID": 7,
        "LATITUDE": 52.999375,
        "LONGITUDE": 78.64594,
        "REGIONID": 1
    },
    {
        "CITY": "Катанда",
        "ID": 8,
        "LATITUDE": 50.164731,
        "LONGITUDE": 86.177532,
        "REGIONID": 2
    },
    {
        "CITY": "Кош-Агач",
        "ID": 9,
        "LATITUDE": 49.99647,
        "LONGITUDE": 88.661661,
        "REGIONID": 2
    },
    {
        "CITY": "Онгудай",
        "ID": 10,
        "LATITUDE": 50.749658,
        "LONGITUDE": 86.133775,
        "REGIONID": 2
    },
    {
        "CITY": "Архара",
        "ID": 11,
        "LATITUDE": 49.422293,
        "LONGITUDE": 130.087102,
        "REGIONID": 3
    },
    {
        "CITY": "Белогорск",
        "ID": 12,
        "LATITUDE": 50.921287,
        "LONGITUDE": 128.473917,
        "REGIONID": 3
    },
    {
        "CITY": "Благовещенск",
        "ID": 13,
        "LATITUDE": 50.290658,
        "LONGITUDE": 127.527173,
        "REGIONID": 3
    },
    {
        "CITY": "Бомнак",
        "ID": 14,
        "LATITUDE": 54.710235,
        "LONGITUDE": 128.850374,
        "REGIONID": 3
    },
    {
        "CITY": "Бысса",
        "ID": 15,
        "LATITUDE": 52.405506,
        "LONGITUDE": 130.525588,
        "REGIONID": 3
    },
    {
        "CITY": "Завитинск",
        "ID": 16,
        "LATITUDE": 50.106518,
        "LONGITUDE": 129.439309,
        "REGIONID": 3
    },
    {
        "CITY": "Зея",
        "ID": 17,
        "LATITUDE": 53.734033,
        "LONGITUDE": 127.265889,
        "REGIONID": 3
    },
    {
        "CITY": "Норск",
        "ID": 18,
        "LATITUDE": 52.334685,
        "LONGITUDE": 129.900325,
        "REGIONID": 3
    },
    {
        "CITY": "Поярково",
        "ID": 19,
        "LATITUDE": 49.626349,
        "LONGITUDE": 128.65755,
        "REGIONID": 3
    },
    {
        "CITY": "Сковородино",
        "ID": 20,
        "LATITUDE": 53.987177,
        "LONGITUDE": 123.943632,
        "REGIONID": 3
    },
    {
        "CITY": "Тында",
        "ID": 21,
        "LATITUDE": 55.154656,
        "LONGITUDE": 124.729236,
        "REGIONID": 3
    },
    {
        "CITY": "Усть-Нюкжа",
        "ID": 22,
        "LATITUDE": 56.561592,
        "LONGITUDE": 121.592858,
        "REGIONID": 3
    },
    {
        "CITY": "Шимановск",
        "ID": 23,
        "LATITUDE": 51.999509,
        "LONGITUDE": 127.676123,
        "REGIONID": 3
    },
    {
        "CITY": "Экимчан",
        "ID": 24,
        "LATITUDE": 53.068764,
        "LONGITUDE": 132.943844,
        "REGIONID": 3
    },
    {
        "CITY": "Архангельск",
        "ID": 25,
        "LATITUDE": 64.539393,
        "LONGITUDE": 40.516939,
        "REGIONID": 4
    },
    {
        "CITY": "Койнас",
        "ID": 26,
        "LATITUDE": 64.754164,
        "LONGITUDE": 47.637686,
        "REGIONID": 4
    },
    {
        "CITY": "Котлас",
        "ID": 27,
        "LATITUDE": 61.25297,
        "LONGITUDE": 46.633217,
        "REGIONID": 4
    },
    {
        "CITY": "Мезень",
        "ID": 28,
        "LATITUDE": 65.839904,
        "LONGITUDE": 44.25314,
        "REGIONID": 4
    },
    {
        "CITY": "Онега",
        "ID": 29,
        "LATITUDE": 63.906914,
        "LONGITUDE": 38.100336,
        "REGIONID": 4
    },
    {
        "CITY": "Шенкурск",
        "ID": 30,
        "LATITUDE": 62.10565,
        "LONGITUDE": 42.899612,
        "REGIONID": 4
    },
    {
        "CITY": "Индига",
        "ID": 31,
        "LATITUDE": 67.656602,
        "LONGITUDE": 49.036193,
        "REGIONID": 5
    },
    {
        "CITY": "Канин Нос",
        "ID": 32,
        "LATITUDE": 68.560146,
        "LONGITUDE": 43.671175,
        "REGIONID": 5
    },
    {
        "CITY": "Нарьян-Мар",
        "ID": 33,
        "LATITUDE": 67.63805,
        "LONGITUDE": 53.006926,
        "REGIONID": 5
    },
    {
        "CITY": "Хоседа-Хард",
        "ID": 34,
        "LATITUDE": 67.041342,
        "LONGITUDE": 59.412255,
        "REGIONID": 5
    },
    {
        "CITY": "Астрахань",
        "ID": 35,
        "LATITUDE": 46.347869,
        "LONGITUDE": 48.033574,
        "REGIONID": 6
    },
    {
        "CITY": "Верхний Баскунчак",
        "ID": 36,
        "LATITUDE": 48.225632,
        "LONGITUDE": 46.721908,
        "REGIONID": 6
    },
    {
        "CITY": "Белорецк",
        "ID": 37,
        "LATITUDE": 53.967621,
        "LONGITUDE": 58.410023,
        "REGIONID": 7
    },
    {
        "CITY": "Мелеуз",
        "ID": 38,
        "LATITUDE": 52.958964,
        "LONGITUDE": 55.92831,
        "REGIONID": 7
    },
    {
        "CITY": "Уфа",
        "ID": 39,
        "LATITUDE": 54.735147,
        "LONGITUDE": 55.958727,
        "REGIONID": 7
    },
    {
        "CITY": "Янаул",
        "ID": 40,
        "LATITUDE": 56.264957,
        "LONGITUDE": 54.929824,
        "REGIONID": 7
    },
    {
        "CITY": "Белгород",
        "ID": 41,
        "LATITUDE": 50.59566,
        "LONGITUDE": 36.587223,
        "REGIONID": 8
    },
    {
        "CITY": "Брянск",
        "ID": 42,
        "LATITUDE": 53.243325,
        "LONGITUDE": 34.363731,
        "REGIONID": 9
    },
    {
        "CITY": "Кяхта",
        "ID": 43,
        "LATITUDE": 50.355214,
        "LONGITUDE": 106.449903,
        "REGIONID": 10
    },
    {
        "CITY": "Монды",
        "ID": 44,
        "LATITUDE": 51.675784,
        "LONGITUDE": 100.996357,
        "REGIONID": 10
    },
    {
        "CITY": "Улан-Удэ",
        "ID": 45,
        "LATITUDE": 51.834464,
        "LONGITUDE": 107.584574,
        "REGIONID": 10
    },
    {
        "CITY": "Владимир",
        "ID": 46,
        "LATITUDE": 56.129057,
        "LONGITUDE": 40.406635,
        "REGIONID": 11
    },
    {
        "CITY": "Волгоград",
        "ID": 47,
        "LATITUDE": 48.707073,
        "LONGITUDE": 44.51693,
        "REGIONID": 12
    },
    {
        "CITY": "Камышин",
        "ID": 48,
        "LATITUDE": 50.083698,
        "LONGITUDE": 45.407367,
        "REGIONID": 12
    },
    {
        "CITY": "Котельниково",
        "ID": 49,
        "LATITUDE": 47.631528,
        "LONGITUDE": 43.142625,
        "REGIONID": 12
    },
    {
        "CITY": "Эльтон",
        "ID": 50,
        "LATITUDE": 49.127244,
        "LONGITUDE": 46.845229,
        "REGIONID": 12
    },
    {
        "CITY": "Вологда",
        "ID": 51,
        "LATITUDE": 59.220496,
        "LONGITUDE": 39.891523,
        "REGIONID": 13
    },
    {
        "CITY": "Вытегра",
        "ID": 52,
        "LATITUDE": 61.006355,
        "LONGITUDE": 36.449511,
        "REGIONID": 13
    },
    {
        "CITY": "Тотьма",
        "ID": 53,
        "LATITUDE": 59.973487,
        "LONGITUDE": 42.758873,
        "REGIONID": 13
    },
    {
        "CITY": "Воронеж",
        "ID": 54,
        "LATITUDE": 51.660781,
        "LONGITUDE": 39.200269,
        "REGIONID": 14
    },
    {
        "CITY": "Арзамас",
        "ID": 55,
        "LATITUDE": 55.386666,
        "LONGITUDE": 43.815687,
        "REGIONID": 15
    },
    {
        "CITY": "Нижний Новгород",
        "ID": 56,
        "LATITUDE": 61.050829,
        "LONGITUDE": 49.963362,
        "REGIONID": 15
    },
    {
        "CITY": "Дербент",
        "ID": 57,
        "LATITUDE": 42.057669,
        "LONGITUDE": 48.288776,
        "REGIONID": 16
    },
    {
        "CITY": "Махачкала",
        "ID": 58,
        "LATITUDE": 42.98306,
        "LONGITUDE": 47.504682,
        "REGIONID": 16
    },
    {
        "CITY": "Иваново",
        "ID": 59,
        "LATITUDE": 57.000348,
        "LONGITUDE": 40.973921,
        "REGIONID": 17
    },
    {
        "CITY": "Братск",
        "ID": 60,
        "LATITUDE": 56.151362,
        "LONGITUDE": 101.63408,
        "REGIONID": 18
    },
    {
        "CITY": "Ербогачен",
        "ID": 61,
        "LATITUDE": 61.274892,
        "LONGITUDE": 108.006495,
        "REGIONID": 18
    },
    {
        "CITY": "Зима",
        "ID": 62,
        "LATITUDE": 53.92072,
        "LONGITUDE": 102.049065,
        "REGIONID": 18
    },
    {
        "CITY": "Иркутск",
        "ID": 63,
        "LATITUDE": 52.286387,
        "LONGITUDE": 104.28066,
        "REGIONID": 18
    },
    {
        "CITY": "Киренск",
        "ID": 64,
        "LATITUDE": 57.775723,
        "LONGITUDE": 108.110816,
        "REGIONID": 18
    },
    {
        "CITY": "Марково",
        "ID": 65,
        "LATITUDE": 57.332787,
        "LONGITUDE": 107.063991,
        "REGIONID": 18
    },
    {
        "CITY": "Тайшет",
        "ID": 66,
        "LATITUDE": 55.940502,
        "LONGITUDE": 98.002982,
        "REGIONID": 18
    },
    {
        "CITY": "Тулун",
        "ID": 67,
        "LATITUDE": 54.55712,
        "LONGITUDE": 100.578038,
        "REGIONID": 18
    },
    {
        "CITY": "Нальчик",
        "ID": 68,
        "LATITUDE": 43.485259,
        "LONGITUDE": 43.607072,
        "REGIONID": 19
    },
    {
        "CITY": "Калининград",
        "ID": 69,
        "LATITUDE": 54.70739,
        "LONGITUDE": 20.507307,
        "REGIONID": 20
    },
    {
        "CITY": "Бежецк",
        "ID": 70,
        "LATITUDE": 57.78567,
        "LONGITUDE": 36.693871,
        "REGIONID": 21
    },
    {
        "CITY": "Тверь",
        "ID": 71,
        "LATITUDE": 56.859611,
        "LONGITUDE": 35.911896,
        "REGIONID": 21
    },
    {
        "CITY": "Элиста",
        "ID": 72,
        "LATITUDE": 46.307743,
        "LONGITUDE": 44.269759,
        "REGIONID": 22
    },
    {
        "CITY": "Калуга",
        "ID": 73,
        "LATITUDE": 54.513845,
        "LONGITUDE": 36.261215,
        "REGIONID": 23
    },
    {
        "CITY": "Ключи",
        "ID": 74,
        "LATITUDE": 56.322434,
        "LONGITUDE": 160.844915,
        "REGIONID": 24
    },
    {
        "CITY": "Начики",
        "ID": 75,
        "LATITUDE": 57.838692,
        "LONGITUDE": 161.749419,
        "REGIONID": 24
    },
    {
        "CITY": "Петропавловск-Камчатский",
        "ID": 76,
        "LATITUDE": 53.024075,
        "LONGITUDE": 158.643566,
        "REGIONID": 24
    },
    {
        "CITY": "Семлячики",
        "ID": 77,
        "LATITUDE": 54.063648,
        "LONGITUDE": 159.575475,
        "REGIONID": 24
    },
    {
        "CITY": "Соболево",
        "ID": 78,
        "LATITUDE": 54.29885,
        "LONGITUDE": 155.946087,
        "REGIONID": 24
    },
    {
        "CITY": "Усть-Воямполка",
        "ID": 79,
        "LATITUDE": 58.506678,
        "LONGITUDE": 159.173392,
        "REGIONID": 24
    },
    {
        "CITY": "Усть-Камчатск",
        "ID": 80,
        "LATITUDE": 56.239678,
        "LONGITUDE": 162.536128,
        "REGIONID": 24
    },
    {
        "CITY": "Усть-Хайрюзово",
        "ID": 81,
        "LATITUDE": 57.08974,
        "LONGITUDE": 156.736021,
        "REGIONID": 24
    },
    {
        "CITY": "Кемь",
        "ID": 82,
        "LATITUDE": 64.954356,
        "LONGITUDE": 34.594894,
        "REGIONID": 25
    },
    {
        "CITY": "Олонец",
        "ID": 83,
        "LATITUDE": 60.979719,
        "LONGITUDE": 32.972034,
        "REGIONID": 25
    },
    {
        "CITY": "Паданы",
        "ID": 84,
        "LATITUDE": 63.286475,
        "LONGITUDE": 33.415855,
        "REGIONID": 25
    },
    {
        "CITY": "Петрозаводск",
        "ID": 85,
        "LATITUDE": 61.787374,
        "LONGITUDE": 34.354325,
        "REGIONID": 25
    },
    {
        "CITY": "Кемерово",
        "ID": 86,
        "LATITUDE": 55.354968,
        "LONGITUDE": 86.087314,
        "REGIONID": 26
    },
    {
        "CITY": "Киселевск",
        "ID": 87,
        "LATITUDE": 54.006025,
        "LONGITUDE": 86.636679,
        "REGIONID": 26
    },
    {
        "CITY": "Кондома",
        "ID": 88,
        "LATITUDE": 52.819686,
        "LONGITUDE": 87.276073,
        "REGIONID": 26
    },
    {
        "CITY": "Мариинск",
        "ID": 89,
        "LATITUDE": 56.206952,
        "LONGITUDE": 87.742263,
        "REGIONID": 26
    },
    {
        "CITY": "Тайга",
        "ID": 90,
        "LATITUDE": 56.065138,
        "LONGITUDE": 85.631024,
        "REGIONID": 26
    },
    {
        "CITY": "Киров",
        "ID": 91,
        "LATITUDE": 58.603581,
        "LONGITUDE": 49.667978,
        "REGIONID": 27
    },
    {
        "CITY": "Воркута",
        "ID": 92,
        "LATITUDE": 67.49741,
        "LONGITUDE": 64.061091,
        "REGIONID": 28
    },
    {
        "CITY": "Печора",
        "ID": 93,
        "LATITUDE": 65.148602,
        "LONGITUDE": 57.223977,
        "REGIONID": 28
    },
    {
        "CITY": "Сыктывкар",
        "ID": 94,
        "LATITUDE": 61.668831,
        "LONGITUDE": 50.836461,
        "REGIONID": 28
    },
    {
        "CITY": "Троицко-Печорск",
        "ID": 95,
        "LATITUDE": 62.717125,
        "LONGITUDE": 56.161665,
        "REGIONID": 28
    },
    {
        "CITY": "Усть-Щугор",
        "ID": 96,
        "LATITUDE": 64.361005,
        "LONGITUDE": 57.685057,
        "REGIONID": 28
    },
    {
        "CITY": "Ухта",
        "ID": 97,
        "LATITUDE": 63.562626,
        "LONGITUDE": 53.684022,
        "REGIONID": 28
    },
    {
        "CITY": "Кострома",
        "ID": 98,
        "LATITUDE": 57.767961,
        "LONGITUDE": 40.926858,
        "REGIONID": 29
    },
    {
        "CITY": "Шарья",
        "ID": 99,
        "LATITUDE": 58.369849,
        "LONGITUDE": 45.518264,
        "REGIONID": 29
    },
    {
        "CITY": "Краснодар",
        "ID": 100,
        "LATITUDE": 45.03547,
        "LONGITUDE": 38.975313,
        "REGIONID": 30
    },
    {
        "CITY": "Сочи",
        "ID": 101,
        "LATITUDE": 43.585525,
        "LONGITUDE": 39.723062,
        "REGIONID": 30
    },
    {
        "CITY": "Тихорецк",
        "ID": 102,
        "LATITUDE": 45.85468,
        "LONGITUDE": 40.125929,
        "REGIONID": 30
    },
    {
        "CITY": "Майкоп",
        "ID": 103,
        "LATITUDE": 44.608865,
        "LONGITUDE": 40.098548,
        "REGIONID": 31
    },
    {
        "CITY": "Ачинск",
        "ID": 104,
        "LATITUDE": 56.269496,
        "LONGITUDE": 90.495231,
        "REGIONID": 32
    },
    {
        "CITY": "Байкит",
        "ID": 105,
        "LATITUDE": 61.678423,
        "LONGITUDE": 96.377965,
        "REGIONID": 32
    },
    {
        "CITY": "Богучаны",
        "ID": 106,
        "LATITUDE": 58.379896,
        "LONGITUDE": 97.445119,
        "REGIONID": 32
    },
    {
        "CITY": "Ванавара",
        "ID": 107,
        "LATITUDE": 60.344273,
        "LONGITUDE": 102.283409,
        "REGIONID": 32
    },
    {
        "CITY": "Верхнеимбатск",
        "ID": 108,
        "LATITUDE": 63.154856,
        "LONGITUDE": 87.967192,
        "REGIONID": 32
    },
    {
        "CITY": "Волочанка",
        "ID": 109,
        "LATITUDE": 70.976083,
        "LONGITUDE": 94.541377,
        "REGIONID": 32
    },
    {
        "CITY": "Диксон",
        "ID": 110,
        "LATITUDE": 73.503434,
        "LONGITUDE": 80.349505,
        "REGIONID": 32
    },
    {
        "CITY": "Дудинка",
        "ID": 111,
        "LATITUDE": 69.403185,
        "LONGITUDE": 86.190818,
        "REGIONID": 32
    },
    {
        "CITY": "Енисейск",
        "ID": 112,
        "LATITUDE": 58.448619,
        "LONGITUDE": 92.165163,
        "REGIONID": 32
    },
    {
        "CITY": "Игарка",
        "ID": 113,
        "LATITUDE": 67.466954,
        "LONGITUDE": 86.567715,
        "REGIONID": 32
    },
    {
        "CITY": "Канск",
        "ID": 114,
        "LATITUDE": 56.205045,
        "LONGITUDE": 95.705055,
        "REGIONID": 32
    },
    {
        "CITY": "Красноярск",
        "ID": 115,
        "LATITUDE": 56.010563,
        "LONGITUDE": 92.852572,
        "REGIONID": 32
    },
    {
        "CITY": "Минусинск",
        "ID": 116,
        "LATITUDE": 53.710564,
        "LONGITUDE": 91.687268,
        "REGIONID": 32
    },
    {
        "CITY": "Тура",
        "ID": 117,
        "LATITUDE": 64.272252,
        "LONGITUDE": 100.206396,
        "REGIONID": 32
    },
    {
        "CITY": "Туруханск",
        "ID": 118,
        "LATITUDE": 65.793214,
        "LONGITUDE": 87.95917,
        "REGIONID": 32
    },
    {
        "CITY": "Хатанга",
        "ID": 119,
        "LATITUDE": 71.980467,
        "LONGITUDE": 102.48341,
        "REGIONID": 32
    },
    {
        "CITY": "Челюскин, мыс",
        "ID": 120,
        "LATITUDE": 77.721041,
        "LONGITUDE": 104.258571,
        "REGIONID": 32
    },
    {
        "CITY": "Ярцево",
        "ID": 121,
        "LATITUDE": 60.247729,
        "LONGITUDE": 90.215621,
        "REGIONID": 32
    },
    {
        "CITY": "Абакан",
        "ID": 122,
        "LATITUDE": 53.721152,
        "LONGITUDE": 91.442387,
        "REGIONID": 33
    },
    {
        "CITY": "Шира",
        "ID": 123,
        "LATITUDE": 54.487191,
        "LONGITUDE": 89.962817,
        "REGIONID": 33
    },
    {
        "CITY": "Самара",
        "ID": 124,
        "LATITUDE": 55.445972,
        "LONGITUDE": 78.311111,
        "REGIONID": 34
    },
    {
        "CITY": "Курган",
        "ID": 125,
        "LATITUDE": 55.441004,
        "LONGITUDE": 65.341118,
        "REGIONID": 35
    },
    {
        "CITY": "Курск",
        "ID": 126,
        "LATITUDE": 51.730361,
        "LONGITUDE": 36.192647,
        "REGIONID": 36
    },
    {
        "CITY": "Выборг",
        "ID": 127,
        "LATITUDE": 55.445972,
        "LONGITUDE": 78.311111,
        "REGIONID": 37
    },
    {
        "CITY": "Санкт-Петербург",
        "ID": 128,
        "LATITUDE": 59.939095,
        "LONGITUDE": 30.315868,
        "REGIONID": 37
    },
    {
        "CITY": "Тихвин",
        "ID": 129,
        "LATITUDE": 59.644209,
        "LONGITUDE": 33.542096,
        "REGIONID": 37
    },
    {
        "CITY": "Липецк",
        "ID": 130,
        "LATITUDE": 52.60882,
        "LONGITUDE": 39.59922,
        "REGIONID": 38
    },
    {
        "CITY": "Магадан",
        "ID": 131,
        "LATITUDE": 59.565155,
        "LONGITUDE": 150.808586,
        "REGIONID": 39
    },
    {
        "CITY": "Омсукчан",
        "ID": 132,
        "LATITUDE": 62.515447,
        "LONGITUDE": 155.783357,
        "REGIONID": 39
    },
    {
        "CITY": "Палатка",
        "ID": 133,
        "LATITUDE": 60.101647,
        "LONGITUDE": 150.934772,
        "REGIONID": 39
    },
    {
        "CITY": "Среднекан",
        "ID": 134,
        "LATITUDE": 62.443402,
        "LONGITUDE": 152.322265,
        "REGIONID": 39
    },
    {
        "CITY": "Сусуман",
        "ID": 135,
        "LATITUDE": 62.780464,
        "LONGITUDE": 148.153687,
        "REGIONID": 39
    },
    {
        "CITY": "Островное",
        "ID": 136,
        "LATITUDE": 68.917185,
        "LONGITUDE": 170.79973,
        "REGIONID": 40
    },
    {
        "CITY": "Омолон",
        "ID": 137,
        "LATITUDE": 65.235572,
        "LONGITUDE": 160.537592,
        "REGIONID": 40
    },
    {
        "CITY": "Усть-Олой",
        "ID": 138,
        "LATITUDE": 66.626,
        "LONGITUDE": 159.25,
        "REGIONID": 40
    },
    {
        "CITY": "Эньмувеем",
        "ID": 139,
        "LATITUDE": 67.221744,
        "LONGITUDE": 172.165466,
        "REGIONID": 40
    },
    {
        "CITY": "Анадырь",
        "ID": 140,
        "LATITUDE": 64.733115,
        "LONGITUDE": 177.508924,
        "REGIONID": 40
    },
    {
        "CITY": "Йошкар-Ола",
        "ID": 141,
        "LATITUDE": 56.631011,
        "LONGITUDE": 47.890975,
        "REGIONID": 41
    },
    {
        "CITY": "Саранск",
        "ID": 142,
        "LATITUDE": 54.187211,
        "LONGITUDE": 45.183642,
        "REGIONID": 42
    },
    {
        "CITY": "Дмитров",
        "ID": 143,
        "LATITUDE": 56.343942,
        "LONGITUDE": 37.520348,
        "REGIONID": 43
    },
    {
        "CITY": "Москва",
        "ID": 144,
        "LATITUDE": 55.753215,
        "LONGITUDE": 37.622504,
        "REGIONID": 43
    },
    {
        "CITY": "Кашира",
        "ID": 145,
        "LATITUDE": 54.834589,
        "LONGITUDE": 38.15154,
        "REGIONID": 43
    },
    {
        "CITY": "Кандалакша",
        "ID": 146,
        "LATITUDE": 67.151252,
        "LONGITUDE": 32.412823,
        "REGIONID": 44
    },
    {
        "CITY": "Ковдор",
        "ID": 147,
        "LATITUDE": 67.562914,
        "LONGITUDE": 30.474025,
        "REGIONID": 44
    },
    {
        "CITY": "Краснощелье",
        "ID": 148,
        "LATITUDE": 67.349847,
        "LONGITUDE": 37.053197,
        "REGIONID": 44
    },
    {
        "CITY": "Ловозеро",
        "ID": 149,
        "LATITUDE": 68.00466,
        "LONGITUDE": 35.014147,
        "REGIONID": 44
    },
    {
        "CITY": "Мончегорск",
        "ID": 150,
        "LATITUDE": 67.938931,
        "LONGITUDE": 32.937116,
        "REGIONID": 44
    },
    {
        "CITY": "Мурманск",
        "ID": 151,
        "LATITUDE": 68.970682,
        "LONGITUDE": 33.074981,
        "REGIONID": 44
    },
    {
        "CITY": "Пялица",
        "ID": 152,
        "LATITUDE": 66.402013,
        "LONGITUDE": 39.300422,
        "REGIONID": 44
    },
    {
        "CITY": "Боровичи",
        "ID": 153,
        "LATITUDE": 58.388219,
        "LONGITUDE": 33.914025,
        "REGIONID": 45
    },
    {
        "CITY": "Великий Новгород",
        "ID": 154,
        "LATITUDE": 58.52281,
        "LONGITUDE": 31.269915,
        "REGIONID": 45
    },
    {
        "CITY": "Карасук",
        "ID": 155,
        "LATITUDE": 53.731934,
        "LONGITUDE": 78.04936,
        "REGIONID": 46
    },
    {
        "CITY": "Кочки",
        "ID": 156,
        "LATITUDE": 54.333337,
        "LONGITUDE": 80.490613,
        "REGIONID": 46
    },
    {
        "CITY": "Кыштовка",
        "ID": 157,
        "LATITUDE": 56.562356,
        "LONGITUDE": 76.622754,
        "REGIONID": 46
    },
    {
        "CITY": "Барабинск",
        "ID": 158,
        "LATITUDE": 55.350412,
        "LONGITUDE": 78.341923,
        "REGIONID": 46
    },
    {
        "CITY": "Болотное",
        "ID": 159,
        "LATITUDE": 55.672001,
        "LONGITUDE": 84.385447,
        "REGIONID": 46
    },
    {
        "CITY": "Купино",
        "ID": 160,
        "LATITUDE": 54.366046,
        "LONGITUDE": 77.297254,
        "REGIONID": 46
    },
    {
        "CITY": "Новосибирск",
        "ID": 161,
        "LATITUDE": 55.030199,
        "LONGITUDE": 82.92043,
        "REGIONID": 46
    },
    {
        "CITY": "Татарск",
        "ID": 162,
        "LATITUDE": 55.214532,
        "LONGITUDE": 75.97409,
        "REGIONID": 46
    },
    {
        "CITY": "Чулым",
        "ID": 163,
        "LATITUDE": 55.091258,
        "LONGITUDE": 80.963288,
        "REGIONID": 46
    },
    {
        "CITY": "Омск",
        "ID": 164,
        "LATITUDE": 54.989342,
        "LONGITUDE": 73.368212,
        "REGIONID": 47
    },
    {
        "CITY": "Тара",
        "ID": 165,
        "LATITUDE": 56.901838,
        "LONGITUDE": 74.371981,
        "REGIONID": 47
    },
    {
        "CITY": "Черлак",
        "ID": 166,
        "LATITUDE": 54.155114,
        "LONGITUDE": 74.804456,
        "REGIONID": 47
    },
    {
        "CITY": "Кувандык",
        "ID": 167,
        "LATITUDE": 51.478483,
        "LONGITUDE": 57.361168,
        "REGIONID": 48
    },
    {
        "CITY": "Оренбург",
        "ID": 168,
        "LATITUDE": 51.768199,
        "LONGITUDE": 55.096955,
        "REGIONID": 48
    },
    {
        "CITY": "Сорочинск",
        "ID": 169,
        "LATITUDE": 52.429092,
        "LONGITUDE": 53.151016,
        "REGIONID": 48
    },
    {
        "CITY": "Орел",
        "ID": 170,
        "LATITUDE": 52.970371,
        "LONGITUDE": 36.063837,
        "REGIONID": 49
    },
    {
        "CITY": "Земетчино",
        "ID": 171,
        "LATITUDE": 53.496016,
        "LONGITUDE": 42.614568,
        "REGIONID": 50
    },
    {
        "CITY": "Пенза",
        "ID": 172,
        "LATITUDE": 53.195063,
        "LONGITUDE": 45.018316,
        "REGIONID": 50
    },
    {
        "CITY": "Бисер",
        "ID": 173,
        "LATITUDE": 58.512141,
        "LONGITUDE": 58.877057,
        "REGIONID": 51
    },
    {
        "CITY": "Пермь",
        "ID": 174,
        "LATITUDE": 58.010374,
        "LONGITUDE": 56.229398,
        "REGIONID": 51
    },
    {
        "CITY": "Владивосток",
        "ID": 175,
        "LATITUDE": 43.115536,
        "LONGITUDE": 131.885485,
        "REGIONID": 52
    },
    {
        "CITY": "Дальнереченск",
        "ID": 176,
        "LATITUDE": 45.93085,
        "LONGITUDE": 133.731738,
        "REGIONID": 52
    },
    {
        "CITY": "Партизанск",
        "ID": 177,
        "LATITUDE": 43.119813,
        "LONGITUDE": 133.123246,
        "REGIONID": 52
    },
    {
        "CITY": "Рудная Пристань",
        "ID": 178,
        "LATITUDE": 44.365531,
        "LONGITUDE": 135.820294,
        "REGIONID": 52
    },
    {
        "CITY": "Анучино",
        "ID": 179,
        "LATITUDE": 43.964007,
        "LONGITUDE": 133.054408,
        "REGIONID": 52
    },
    {
        "CITY": "Астраханка",
        "ID": 180,
        "LATITUDE": 51.52936,
        "LONGITUDE": 69.789315,
        "REGIONID": 52
    },
    {
        "CITY": "Богополь",
        "ID": 181,
        "LATITUDE": 44.248394,
        "LONGITUDE": 135.456818,
        "REGIONID": 52
    },
    {
        "CITY": "Мельничное",
        "ID": 182,
        "LATITUDE": 45.43468,
        "LONGITUDE": 135.519691,
        "REGIONID": 52
    },
    {
        "CITY": "Преображение",
        "ID": 183,
        "LATITUDE": 42.900767,
        "LONGITUDE": 133.902768,
        "REGIONID": 52
    },
    {
        "CITY": "Чугуевка",
        "ID": 184,
        "LATITUDE": 44.158533,
        "LONGITUDE": 133.860072,
        "REGIONID": 52
    },
    {
        "CITY": "Великие Луки",
        "ID": 185,
        "LATITUDE": 56.34265,
        "LONGITUDE": 30.523397,
        "REGIONID": 53
    },
    {
        "CITY": "Псков",
        "ID": 186,
        "LATITUDE": 57.816915,
        "LONGITUDE": 28.334625,
        "REGIONID": 53
    },
    {
        "CITY": "Таганрог",
        "ID": 187,
        "LATITUDE": 47.208735,
        "LONGITUDE": 38.936694,
        "REGIONID": 54
    },
    {
        "CITY": "Миллерово",
        "ID": 188,
        "LATITUDE": 48.92173,
        "LONGITUDE": 40.394849,
        "REGIONID": 54
    },
    {
        "CITY": "Ростов-на-Дону",
        "ID": 189,
        "LATITUDE": 47.222078,
        "LONGITUDE": 39.720349,
        "REGIONID": 54
    },
    {
        "CITY": "Рязань",
        "ID": 190,
        "LATITUDE": 54.629216,
        "LONGITUDE": 39.736375,
        "REGIONID": 55
    },
    {
        "CITY": "Балашов",
        "ID": 191,
        "LATITUDE": 51.554601,
        "LONGITUDE": 43.146469,
        "REGIONID": 56
    },
    {
        "CITY": "Саратов",
        "ID": 192,
        "LATITUDE": 51.533103,
        "LONGITUDE": 46.034158,
        "REGIONID": 56
    },
    {
        "CITY": "Александровск-Сахалинский",
        "ID": 193,
        "LATITUDE": 50.894564,
        "LONGITUDE": 142.1594,
        "REGIONID": 57
    },
    {
        "CITY": "Долинск",
        "ID": 194,
        "LATITUDE": 47.32624,
        "LONGITUDE": 142.79344,
        "REGIONID": 57
    },
    {
        "CITY": "Макаров",
        "ID": 195,
        "LATITUDE": 48.622695,
        "LONGITUDE": 142.781807,
        "REGIONID": 57
    },
    {
        "CITY": "Корсаков",
        "ID": 196,
        "LATITUDE": 46.633785,
        "LONGITUDE": 142.78027,
        "REGIONID": 57
    },
    {
        "CITY": "Курильск",
        "ID": 197,
        "LATITUDE": 45.225174,
        "LONGITUDE": 147.883761,
        "REGIONID": 57
    },
    {
        "CITY": "Невельск",
        "ID": 198,
        "LATITUDE": 46.652828,
        "LONGITUDE": 141.863126,
        "REGIONID": 57
    },
    {
        "CITY": "Оха",
        "ID": 199,
        "LATITUDE": 53.584521,
        "LONGITUDE": 142.947186,
        "REGIONID": 57
    },
    {
        "CITY": "Поронайск",
        "ID": 200,
        "LATITUDE": 49.22038,
        "LONGITUDE": 143.08956,
        "REGIONID": 57
    },
    {
        "CITY": "Холмск",
        "ID": 201,
        "LATITUDE": 47.040905,
        "LONGITUDE": 142.041622,
        "REGIONID": 57
    },
    {
        "CITY": "Южно-Курильск",
        "ID": 202,
        "LATITUDE": 44.026063,
        "LONGITUDE": 145.863288,
        "REGIONID": 57
    },
    {
        "CITY": "Южно-Сахалинск",
        "ID": 203,
        "LATITUDE": 46.959155,
        "LONGITUDE": 142.738023,
        "REGIONID": 57
    },
    {
        "CITY": "Владикавказ",
        "ID": 204,
        "LATITUDE": 43.021064,
        "LONGITUDE": 44.681897,
        "REGIONID": 58
    },
    {
        "CITY": "Екатеринбург",
        "ID": 205,
        "LATITUDE": 56.838011,
        "LONGITUDE": 60.597465,
        "REGIONID": 59
    },
    {
        "CITY": "Смоленск",
        "ID": 206,
        "LATITUDE": 54.782635,
        "LONGITUDE": 32.045251,
        "REGIONID": 60
    },
    {
        "CITY": "Арзгир",
        "ID": 207,
        "LATITUDE": 45.369657,
        "LONGITUDE": 44.221304,
        "REGIONID": 61
    },
    {
        "CITY": "Ставрополь",
        "ID": 208,
        "LATITUDE": 45.044521,
        "LONGITUDE": 41.969083,
        "REGIONID": 61
    },
    {
        "CITY": "Тамбов",
        "ID": 209,
        "LATITUDE": 52.721219,
        "LONGITUDE": 41.452274,
        "REGIONID": 62
    },
    {
        "CITY": "Бугульма",
        "ID": 210,
        "LATITUDE": 54.536413,
        "LONGITUDE": 52.789489,
        "REGIONID": 63
    },
    {
        "CITY": "Казань",
        "ID": 211,
        "LATITUDE": 55.796289,
        "LONGITUDE": 49.108795,
        "REGIONID": 63
    },
    {
        "CITY": "Александровское",
        "ID": 212,
        "LATITUDE": 60.426119,
        "LONGITUDE": 77.868466,
        "REGIONID": 64
    },
    {
        "CITY": "Колпашево",
        "ID": 213,
        "LATITUDE": 58.311384,
        "LONGITUDE": 82.902679,
        "REGIONID": 64
    },
    {
        "CITY": "Средний Васюган",
        "ID": 214,
        "LATITUDE": 59.221086,
        "LONGITUDE": 78.237243,
        "REGIONID": 64
    },
    {
        "CITY": "Томск",
        "ID": 215,
        "LATITUDE": 56.48464,
        "LONGITUDE": 84.947649,
        "REGIONID": 64
    },
    {
        "CITY": "Усть-Озерное",
        "ID": 216,
        "LATITUDE": 58.903101,
        "LONGITUDE": 87.741607,
        "REGIONID": 64
    },
    {
        "CITY": "Кызыл",
        "ID": 217,
        "LATITUDE": 51.719086,
        "LONGITUDE": 94.437757,
        "REGIONID": 65
    },
    {
        "CITY": "Тула",
        "ID": 218,
        "LATITUDE": 54.193122,
        "LONGITUDE": 37.617348,
        "REGIONID": 66
    },
    {
        "CITY": "Демьянское",
        "ID": 219,
        "LATITUDE": 59.594284,
        "LONGITUDE": 69.3245,
        "REGIONID": 67
    },
    {
        "CITY": "Тобольск",
        "ID": 220,
        "LATITUDE": 58.203791,
        "LONGITUDE": 68.265711,
        "REGIONID": 67
    },
    {
        "CITY": "Тюмень",
        "ID": 221,
        "LATITUDE": 57.153033,
        "LONGITUDE": 65.534328,
        "REGIONID": 67
    },
    {
        "CITY": "Березово",
        "ID": 222,
        "LATITUDE": 63.935222,
        "LONGITUDE": 65.053882,
        "REGIONID": 68
    },
    {
        "CITY": "Кондинское",
        "ID": 223,
        "LATITUDE": 59.650891,
        "LONGITUDE": 67.414339,
        "REGIONID": 68
    },
    {
        "CITY": "Леуши",
        "ID": 224,
        "LATITUDE": 59.623579,
        "LONGITUDE": 65.751594,
        "REGIONID": 68
    },
    {
        "CITY": "Октябрьское",
        "ID": 225,
        "LATITUDE": 62.459084,
        "LONGITUDE": 66.045209,
        "REGIONID": 68
    },
    {
        "CITY": "Сосьва",
        "ID": 226,
        "LATITUDE": 59.1744,
        "LONGITUDE": 61.849376,
        "REGIONID": 68
    },
    {
        "CITY": "Сургут",
        "ID": 227,
        "LATITUDE": 61.254509,
        "LONGITUDE": 73.367902,
        "REGIONID": 68
    },
    {
        "CITY": "Угут",
        "ID": 228,
        "LATITUDE": 60.508787,
        "LONGITUDE": 74.054201,
        "REGIONID": 68
    },
    {
        "CITY": "Ханты-Мансийск",
        "ID": 229,
        "LATITUDE": 61.008627,
        "LONGITUDE": 69.042204,
        "REGIONID": 68
    },
    {
        "CITY": "Марресаля",
        "ID": 230,
        "LATITUDE": 69.713824,
        "LONGITUDE": 66.812523,
        "REGIONID": 69
    },
    {
        "CITY": "Надым",
        "ID": 231,
        "LATITUDE": 65.527025,
        "LONGITUDE": 72.540055,
        "REGIONID": 69
    },
    {
        "CITY": "Салехард",
        "ID": 232,
        "LATITUDE": 66.529844,
        "LONGITUDE": 66.614399,
        "REGIONID": 69
    },
    {
        "CITY": "Тарко-Сале",
        "ID": 233,
        "LATITUDE": 64.911819,
        "LONGITUDE": 77.761055,
        "REGIONID": 69
    },
    {
        "CITY": "Уренгой",
        "ID": 234,
        "LATITUDE": 65.961949,
        "LONGITUDE": 78.372691,
        "REGIONID": 69
    },
    {
        "CITY": "Глазов",
        "ID": 235,
        "LATITUDE": 58.14081,
        "LONGITUDE": 52.674235,
        "REGIONID": 70
    },
    {
        "CITY": "Ижевск",
        "ID": 236,
        "LATITUDE": 56.862454,
        "LONGITUDE": 53.232561,
        "REGIONID": 70
    },
    {
        "CITY": "Сарапул",
        "ID": 237,
        "LATITUDE": 56.461218,
        "LONGITUDE": 53.803687,
        "REGIONID": 70
    },
    {
        "CITY": "Ульяновск",
        "ID": 238,
        "LATITUDE": 54.314192,
        "LONGITUDE": 48.403132,
        "REGIONID": 71
    },
    {
        "CITY": "Аян",
        "ID": 239,
        "LATITUDE": 56.460517,
        "LONGITUDE": 138.176234,
        "REGIONID": 72
    },
    {
        "CITY": "Байдуков",
        "ID": 240,
        "LATITUDE": 56.138283,
        "LONGITUDE": 47.257951,
        "REGIONID": 72
    },
    {
        "CITY": "Гвасюги",
        "ID": 241,
        "LATITUDE": 47.669593,
        "LONGITUDE": 136.180914,
        "REGIONID": 72
    },
    {
        "CITY": "Джаорэ",
        "ID": 242,
        "LATITUDE": 52.658229,
        "LONGITUDE": 141.283632,
        "REGIONID": 72
    },
    {
        "CITY": "Охотск",
        "ID": 243,
        "LATITUDE": 59.36113,
        "LONGITUDE": 143.225493,
        "REGIONID": 72
    },
    {
        "CITY": "Николаевск-на-Амуре",
        "ID": 244,
        "LATITUDE": 53.14217,
        "LONGITUDE": 140.726625,
        "REGIONID": 72
    },
    {
        "CITY": "Советская Гавань",
        "ID": 245,
        "LATITUDE": 48.966446,
        "LONGITUDE": 140.285128,
        "REGIONID": 72
    },
    {
        "CITY": "Комсомольск-на-Амуре",
        "ID": 246,
        "LATITUDE": 50.549923,
        "LONGITUDE": 137.007948,
        "REGIONID": 72
    },
    {
        "CITY": "Им. Полины Осипенко",
        "ID": 247,
        "LATITUDE": 52.421079,
        "LONGITUDE": 136.493689,
        "REGIONID": 72
    },
    {
        "CITY": "Бикин",
        "ID": 248,
        "LATITUDE": 46.818592,
        "LONGITUDE": 134.255034,
        "REGIONID": 72
    },
    {
        "CITY": "Вяземский",
        "ID": 249,
        "LATITUDE": 47.535352,
        "LONGITUDE": 134.755297,
        "REGIONID": 72
    },
    {
        "CITY": "Хабаровск",
        "ID": 250,
        "LATITUDE": 48.480223,
        "LONGITUDE": 135.071917,
        "REGIONID": 72
    },
    {
        "CITY": "Чумикан",
        "ID": 251,
        "LATITUDE": 54.718624,
        "LONGITUDE": 135.313258,
        "REGIONID": 72
    },
    {
        "CITY": "Екатерино-Никольское",
        "ID": 252,
        "LATITUDE": 47.751476,
        "LONGITUDE": 130.970927,
        "REGIONID": 73
    },
    {
        "CITY": "Облучье",
        "ID": 253,
        "LATITUDE": 49.020287,
        "LONGITUDE": 131.05969,
        "REGIONID": 73
    },
    {
        "CITY": "Челябинск",
        "ID": 254,
        "LATITUDE": 55.165162,
        "LONGITUDE": 61.4306,
        "REGIONID": 74
    },
    {
        "CITY": "Грозный",
        "ID": 255,
        "LATITUDE": 43.316343,
        "LONGITUDE": 45.675098,
        "REGIONID": 75
    },
    {
        "CITY": "Агинское",
        "ID": 256,
        "LATITUDE": 51.107514,
        "LONGITUDE": 114.541747,
        "REGIONID": 76
    },
    {
        "CITY": "Александровский Завод",
        "ID": 257,
        "LATITUDE": 50.924393,
        "LONGITUDE": 117.935547,
        "REGIONID": 76
    },
    {
        "CITY": "Борзя",
        "ID": 258,
        "LATITUDE": 50.391551,
        "LONGITUDE": 116.527042,
        "REGIONID": 76
    },
    {
        "CITY": "Дарасун",
        "ID": 259,
        "LATITUDE": 51.650578,
        "LONGITUDE": 113.966853,
        "REGIONID": 76
    },
    {
        "CITY": "Калакан",
        "ID": 260,
        "LATITUDE": 34.760724,
        "LONGITUDE": 69.182054,
        "REGIONID": 76
    },
    {
        "CITY": "Красный Чикой",
        "ID": 261,
        "LATITUDE": 50.363943,
        "LONGITUDE": 108.755618,
        "REGIONID": 76
    },
    {
        "CITY": "Средний Калар",
        "ID": 262,
        "LATITUDE": 55.861661,
        "LONGITUDE": 117.377962,
        "REGIONID": 76
    },
    {
        "CITY": "Тунгокочен",
        "ID": 263,
        "LATITUDE": 53.533956,
        "LONGITUDE": 115.615207,
        "REGIONID": 76
    },
    {
        "CITY": "Тупик",
        "ID": 264,
        "LATITUDE": 54.428211,
        "LONGITUDE": 119.942895,
        "REGIONID": 76
    },
    {
        "CITY": "Чара",
        "ID": 265,
        "LATITUDE": 56.901725,
        "LONGITUDE": 118.259093,
        "REGIONID": 76
    },
    {
        "CITY": "Акша",
        "ID": 266,
        "LATITUDE": 50.285088,
        "LONGITUDE": 113.277018,
        "REGIONID": 76
    },
    {
        "CITY": "Могоча",
        "ID": 267,
        "LATITUDE": 53.741677,
        "LONGITUDE": 119.756417,
        "REGIONID": 76
    },
    {
        "CITY": "Нерчинск",
        "ID": 268,
        "LATITUDE": 51.977049,
        "LONGITUDE": 116.569114,
        "REGIONID": 76
    },
    {
        "CITY": "Нерчинский Завод",
        "ID": 269,
        "LATITUDE": 51.321975,
        "LONGITUDE": 119.66014,
        "REGIONID": 76
    },
    {
        "CITY": "Чита",
        "ID": 270,
        "LATITUDE": 52.051986,
        "LONGITUDE": 113.46613,
        "REGIONID": 76
    },
    {
        "CITY": "Чебоксары",
        "ID": 271,
        "LATITUDE": 56.139918,
        "LONGITUDE": 47.247728,
        "REGIONID": 77
    },
    {
        "CITY": "Порецкое",
        "ID": 272,
        "LATITUDE": 0,
        "LONGITUDE": 46.312013,
        "REGIONID": 77
    },
    {
        "CITY": "Батамай",
        "ID": 273,
        "LATITUDE": 63.524595,
        "LONGITUDE": 129.419762,
        "REGIONID": 78
    },
    {
        "CITY": "Джалинда",
        "ID": 274,
        "LATITUDE": 53.488253,
        "LONGITUDE": 123.896012,
        "REGIONID": 78
    },
    {
        "CITY": "Иэма",
        "ID": 275,
        "LATITUDE": 31.265685,
        "LONGITUDE": 34.810256,
        "REGIONID": 78
    },
    {
        "CITY": "Крест-Хальджай",
        "ID": 276,
        "LATITUDE": 62.811728,
        "LONGITUDE": 134.518043,
        "REGIONID": 78
    },
    {
        "CITY": "Ленск",
        "ID": 277,
        "LATITUDE": 60.713735,
        "LONGITUDE": 114.911853,
        "REGIONID": 78
    },
    {
        "CITY": "Нера",
        "ID": 278,
        "LATITUDE": 44.843432,
        "LONGITUDE": 21.36227,
        "REGIONID": 78
    },
    {
        "CITY": "Саскылах",
        "ID": 279,
        "LATITUDE": 71.965426,
        "LONGITUDE": 114.093192,
        "REGIONID": 78
    },
    {
        "CITY": "Токо",
        "ID": 280,
        "LATITUDE": 56.171082,
        "LONGITUDE": 131.007049,
        "REGIONID": 78
    },
    {
        "CITY": "Томмот",
        "ID": 281,
        "LATITUDE": 58.95867,
        "LONGITUDE": 126.287588,
        "REGIONID": 78
    },
    {
        "CITY": "Тяня",
        "ID": 282,
        "LATITUDE": 59.056312,
        "LONGITUDE": 119.790649,
        "REGIONID": 78
    },
    {
        "CITY": "Алдан",
        "ID": 283,
        "LATITUDE": 58.605616,
        "LONGITUDE": 125.396123,
        "REGIONID": 78
    },
    {
        "CITY": "Амга",
        "ID": 284,
        "LATITUDE": 60.900648,
        "LONGITUDE": 131.976807,
        "REGIONID": 78
    },
    {
        "CITY": "Верхоянск",
        "ID": 285,
        "LATITUDE": 67.550161,
        "LONGITUDE": 133.390702,
        "REGIONID": 78
    },
    {
        "CITY": "Вилюйск",
        "ID": 286,
        "LATITUDE": 63.751722,
        "LONGITUDE": 121.627326,
        "REGIONID": 78
    },
    {
        "CITY": "Витим",
        "ID": 287,
        "LATITUDE": 59.429471,
        "LONGITUDE": 112.557809,
        "REGIONID": 78
    },
    {
        "CITY": "Джарджан",
        "ID": 288,
        "LATITUDE": 68.732014,
        "LONGITUDE": 124.019611,
        "REGIONID": 78
    },
    {
        "CITY": "Жиганск",
        "ID": 289,
        "LATITUDE": 66.767581,
        "LONGITUDE": 123.374226,
        "REGIONID": 78
    },
    {
        "CITY": "Зырянка",
        "ID": 290,
        "LATITUDE": 65.736267,
        "LONGITUDE": 150.890458,
        "REGIONID": 78
    },
    {
        "CITY": "Исить",
        "ID": 291,
        "LATITUDE": 60.812131,
        "LONGITUDE": 125.326696,
        "REGIONID": 78
    },
    {
        "CITY": "Кюсюр",
        "ID": 292,
        "LATITUDE": 70.686205,
        "LONGITUDE": 127.361695,
        "REGIONID": 78
    },
    {
        "CITY": "Нагорный",
        "ID": 293,
        "LATITUDE": 50.401709,
        "LONGITUDE": 128.982157,
        "REGIONID": 78
    },
    {
        "CITY": "Нюрба",
        "ID": 294,
        "LATITUDE": 63.282823,
        "LONGITUDE": 118.324239,
        "REGIONID": 78
    },
    {
        "CITY": "Оймякон",
        "ID": 295,
        "LATITUDE": 63.464527,
        "LONGITUDE": 142.789074,
        "REGIONID": 78
    },
    {
        "CITY": "Олекминск",
        "ID": 296,
        "LATITUDE": 60.375796,
        "LONGITUDE": 120.406013,
        "REGIONID": 78
    },
    {
        "CITY": "Оленек",
        "ID": 297,
        "LATITUDE": 68.502381,
        "LONGITUDE": 112.447316,
        "REGIONID": 78
    },
    {
        "CITY": "Охотский Перевоз",
        "ID": 298,
        "LATITUDE": 61.878065,
        "LONGITUDE": 135.526446,
        "REGIONID": 78
    },
    {
        "CITY": "Сангар",
        "ID": 299,
        "LATITUDE": 63.923462,
        "LONGITUDE": 127.46642,
        "REGIONID": 78
    },
    {
        "CITY": "Среднеколымск",
        "ID": 300,
        "LATITUDE": 67.458183,
        "LONGITUDE": 153.707009,
        "REGIONID": 78
    },
    {
        "CITY": "Сунтар",
        "ID": 301,
        "LATITUDE": 62.160619,
        "LONGITUDE": 117.647601,
        "REGIONID": 78
    },
    {
        "CITY": "Сухана",
        "ID": 302,
        "LATITUDE": 68.718795,
        "LONGITUDE": 118.027974,
        "REGIONID": 78
    },
    {
        "CITY": "Томпо",
        "ID": 303,
        "LATITUDE": 63.914588,
        "LONGITUDE": 135.851978,
        "REGIONID": 78
    },
    {
        "CITY": "Туой-Хая",
        "ID": 304,
        "LATITUDE": 62.5307,
        "LONGITUDE": 111.239399,
        "REGIONID": 78
    },
    {
        "CITY": "Усть-Мая",
        "ID": 305,
        "LATITUDE": 60.415628,
        "LONGITUDE": 134.540734,
        "REGIONID": 78
    },
    {
        "CITY": "Усть-Мома",
        "ID": 306,
        "LATITUDE": 66.409803,
        "LONGITUDE": 143.386791,
        "REGIONID": 78
    },
    {
        "CITY": "Чульман",
        "ID": 307,
        "LATITUDE": 56.840582,
        "LONGITUDE": 124.904632,
        "REGIONID": 78
    },
    {
        "CITY": "Шелагонцы",
        "ID": 308,
        "LATITUDE": 65.061105,
        "LONGITUDE": 119.845953,
        "REGIONID": 78
    },
    {
        "CITY": "Якутск",
        "ID": 309,
        "LATITUDE": 62.028103,
        "LONGITUDE": 129.732663,
        "REGIONID": 78
    },
    {
        "CITY": "Ярославль",
        "ID": 310,
        "LATITUDE": 57.626569,
        "LONGITUDE": 39.893787,
        "REGIONID": 79
    },
    {
        "CITY": "Керчь",
        "ID": 311,
        "LATITUDE": 45.356219,
        "LONGITUDE": 36.467378,
        "REGIONID": 80
    },
    {
        "CITY": "Севастополь",
        "ID": 312,
        "LATITUDE": 44.616841,
        "LONGITUDE": 33.525495,
        "REGIONID": 80
    },
    {
        "CITY": "Симферополь",
        "ID": 313,
        "LATITUDE": 44.948237,
        "LONGITUDE": 34.100318,
        "REGIONID": 80
    },
    {
        "CITY": "Феодосия",
        "ID": 314,
        "LATITUDE": 45.031929,
        "LONGITUDE": 35.382429,
        "REGIONID": 80
    },
    {
        "CITY": "Ялта",
        "ID": 315,
        "LATITUDE": 44.498231,
        "LONGITUDE": 34.169317,
        "REGIONID": 80
    }
]
climates = [
    {
        "CITYID": 1,
        "CWind": 14.0,
        "ID": 1,
        "PWindE": 10.0,
        "PWindN": 9.0,
        "PWindNE": 22.0,
        "PWindNW": 8.0,
        "PWindS": 10.0,
        "PWindSE": 5.0,
        "PWindSW": 26.0,
        "PWindW": 10.0,
        "Temperature": 42.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 2,
        "CWind": 17.0,
        "ID": 2,
        "PWindE": 8.0,
        "PWindN": 10.0,
        "PWindNE": 17.0,
        "PWindNW": 10.0,
        "PWindS": 13.0,
        "PWindSE": 12.0,
        "PWindSW": 16.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 3,
        "CWind": 10.0,
        "ID": 3,
        "PWindE": 15.0,
        "PWindN": 7.0,
        "PWindNE": 18.0,
        "PWindNW": 9.0,
        "PWindS": 8.0,
        "PWindSE": 10.0,
        "PWindSW": 19.0,
        "PWindW": 14.0,
        "Temperature": 40.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 4,
        "CWind": 32.0,
        "ID": 4,
        "PWindE": 2.0,
        "PWindN": 12.0,
        "PWindNE": 23.0,
        "PWindNW": 4.0,
        "PWindS": 22.0,
        "PWindSE": 21.0,
        "PWindSW": 10.0,
        "PWindW": 6.0,
        "Temperature": 40.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 5,
        "CWind": 5.0,
        "ID": 5,
        "PWindE": 11.0,
        "PWindN": 10.0,
        "PWindNE": 15.0,
        "PWindNW": 12.0,
        "PWindS": 12.0,
        "PWindSE": 9.0,
        "PWindSW": 17.0,
        "PWindW": 14.0,
        "Temperature": 42.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 6,
        "CWind": 18.0,
        "ID": 6,
        "PWindE": 5.0,
        "PWindN": 11.0,
        "PWindNE": 27.0,
        "PWindNW": 8.0,
        "PWindS": 17.0,
        "PWindSE": 5.0,
        "PWindSW": 19.0,
        "PWindW": 8.0,
        "Temperature": 41.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 7,
        "CWind": 7.0,
        "ID": 7,
        "PWindE": 13.0,
        "PWindN": 14.0,
        "PWindNE": 13.0,
        "PWindNW": 16.0,
        "PWindS": 11.0,
        "PWindSE": 8.0,
        "PWindSW": 11.0,
        "PWindW": 14.0,
        "Temperature": 40.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 8,
        "CWind": 33.0,
        "ID": 8,
        "PWindE": 4.0,
        "PWindN": 21.0,
        "PWindNE": 5.0,
        "PWindNW": 17.0,
        "PWindS": 23.0,
        "PWindSE": 7.0,
        "PWindSW": 12.0,
        "PWindW": 11.0,
        "Temperature": 37.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 9,
        "CWind": 32.0,
        "ID": 9,
        "PWindE": 22.0,
        "PWindN": 8.0,
        "PWindNE": 13.0,
        "PWindNW": 14.0,
        "PWindS": 5.0,
        "PWindSE": 8.0,
        "PWindSW": 6.0,
        "PWindW": 24.0,
        "Temperature": 33.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 10,
        "CWind": 42.0,
        "ID": 10,
        "PWindE": 9.0,
        "PWindN": 6.0,
        "PWindNE": 2.0,
        "PWindNW": 27.0,
        "PWindS": 5.0,
        "PWindSE": 9.0,
        "PWindSW": 8.0,
        "PWindW": 34.0,
        "Temperature": 38.0,
        "WindVelocity": 2.3
    },
    {
        "CITYID": 11,
        "CWind": 16.0,
        "ID": 11,
        "PWindE": 18.0,
        "PWindN": 4.0,
        "PWindNE": 4.0,
        "PWindNW": 10.0,
        "PWindS": 13.0,
        "PWindSE": 39.0,
        "PWindSW": 5.0,
        "PWindW": 7.0,
        "Temperature": 37.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 12,
        "CWind": 6.0,
        "ID": 12,
        "PWindE": 12.0,
        "PWindN": 14.0,
        "PWindNE": 9.0,
        "PWindNW": 9.0,
        "PWindS": 22.0,
        "PWindSE": 19.0,
        "PWindSW": 9.0,
        "PWindW": 6.0,
        "Temperature": 42.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 13,
        "CWind": 17.0,
        "ID": 13,
        "PWindE": 10.0,
        "PWindN": 13.0,
        "PWindNE": 13.0,
        "PWindNW": 13.0,
        "PWindS": 21.0,
        "PWindSE": 15.0,
        "PWindSW": 9.0,
        "PWindW": 6.0,
        "Temperature": 39.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 14,
        "CWind": 9.0,
        "ID": 14,
        "PWindE": 43.0,
        "PWindN": 4.0,
        "PWindNE": 14.0,
        "PWindNW": 5.0,
        "PWindS": 7.0,
        "PWindSE": 13.0,
        "PWindSW": 8.0,
        "PWindW": 6.0,
        "Temperature": 36.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 15,
        "CWind": 30.0,
        "ID": 15,
        "PWindE": 10.0,
        "PWindN": 17.0,
        "PWindNE": 14.0,
        "PWindNW": 13.0,
        "PWindS": 10.0,
        "PWindSE": 15.0,
        "PWindSW": 12.0,
        "PWindW": 9.0,
        "Temperature": 36.0,
        "WindVelocity": 2.6
    },
    {
        "CITYID": 16,
        "CWind": 16.0,
        "ID": 16,
        "PWindE": 13.0,
        "PWindN": 8.0,
        "PWindNE": 6.0,
        "PWindNW": 9.0,
        "PWindS": 15.0,
        "PWindSE": 32.0,
        "PWindSW": 10.0,
        "PWindW": 7.0,
        "Temperature": 37.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 17,
        "CWind": 39.0,
        "ID": 17,
        "PWindE": 36.0,
        "PWindN": 23.0,
        "PWindNE": 6.0,
        "PWindNW": 9.0,
        "PWindS": 4.0,
        "PWindSE": 10.0,
        "PWindSW": 4.0,
        "PWindW": 8.0,
        "Temperature": 36.0,
        "WindVelocity": 3.2
    },
    {
        "CITYID": 18,
        "CWind": 33.0,
        "ID": 18,
        "PWindE": 8.0,
        "PWindN": 14.0,
        "PWindNE": 23.0,
        "PWindNW": 7.0,
        "PWindS": 17.0,
        "PWindSE": 11.0,
        "PWindSW": 13.0,
        "PWindW": 7.0,
        "Temperature": 35.0,
        "WindVelocity": 3.2
    },
    {
        "CITYID": 19,
        "CWind": 24.0,
        "ID": 19,
        "PWindE": 30.0,
        "PWindN": 8.0,
        "PWindNE": 6.0,
        "PWindNW": 8.0,
        "PWindS": 8.0,
        "PWindSE": 16.0,
        "PWindSW": 9.0,
        "PWindW": 15.0,
        "Temperature": 39.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 20,
        "CWind": 37.0,
        "ID": 20,
        "PWindE": 34.0,
        "PWindN": 10.0,
        "PWindNE": 16.0,
        "PWindNW": 9.0,
        "PWindS": 6.0,
        "PWindSE": 7.0,
        "PWindSW": 8.0,
        "PWindW": 10.0,
        "Temperature": 36.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 21,
        "CWind": 34.0,
        "ID": 21,
        "PWindE": 23.0,
        "PWindN": 11.0,
        "PWindNE": 12.0,
        "PWindNW": 4.0,
        "PWindS": 6.0,
        "PWindSE": 12.0,
        "PWindSW": 11.0,
        "PWindW": 21.0,
        "Temperature": 36.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 22,
        "CWind": 48.0,
        "ID": 22,
        "PWindE": 16.0,
        "PWindN": 23.0,
        "PWindNE": 19.0,
        "PWindNW": 9.0,
        "PWindS": 12.0,
        "PWindSE": 2.0,
        "PWindSW": 5.0,
        "PWindW": 14.0,
        "Temperature": 37.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 23,
        "CWind": 20.0,
        "ID": 23,
        "PWindE": 16.0,
        "PWindN": 10.0,
        "PWindNE": 13.0,
        "PWindNW": 14.0,
        "PWindS": 15.0,
        "PWindSE": 16.0,
        "PWindSW": 10.0,
        "PWindW": 6.0,
        "Temperature": 39.0,
        "WindVelocity": 3.2
    },
    {
        "CITYID": 24,
        "CWind": 43.0,
        "ID": 24,
        "PWindE": 32.0,
        "PWindN": 6.0,
        "PWindNE": 20.0,
        "PWindNW": 3.0,
        "PWindS": 5.0,
        "PWindSE": 7.0,
        "PWindSW": 19.0,
        "PWindW": 8.0,
        "Temperature": 35.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 25,
        "CWind": 3.0,
        "ID": 25,
        "PWindE": 15.0,
        "PWindN": 19.0,
        "PWindNE": 16.0,
        "PWindNW": 15.0,
        "PWindS": 8.0,
        "PWindSE": 11.0,
        "PWindSW": 9.0,
        "PWindW": 7.0,
        "Temperature": 34.0,
        "WindVelocity": 4.8
    },
    {
        "CITYID": 26,
        "CWind": 7.0,
        "ID": 26,
        "PWindE": 7.0,
        "PWindN": 21.0,
        "PWindNE": 11.0,
        "PWindNW": 22.0,
        "PWindS": 8.0,
        "PWindSE": 13.0,
        "PWindSW": 8.0,
        "PWindW": 10.0,
        "Temperature": 36.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 27,
        "CWind": 9.0,
        "ID": 27,
        "PWindE": 7.0,
        "PWindN": 16.0,
        "PWindNE": 14.0,
        "PWindNW": 21.0,
        "PWindS": 15.0,
        "PWindSE": 5.0,
        "PWindSW": 15.0,
        "PWindW": 7.0,
        "Temperature": 35.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 28,
        "CWind": 11.0,
        "ID": 28,
        "PWindE": 10.0,
        "PWindN": 22.0,
        "PWindNE": 14.0,
        "PWindNW": 19.0,
        "PWindS": 8.0,
        "PWindSE": 14.0,
        "PWindSW": 7.0,
        "PWindW": 6.0,
        "Temperature": 35.0,
        "WindVelocity": 5.9
    },
    {
        "CITYID": 29,
        "CWind": 7.0,
        "ID": 29,
        "PWindE": 12.0,
        "PWindN": 14.0,
        "PWindNE": 13.0,
        "PWindNW": 20.0,
        "PWindS": 7.0,
        "PWindSE": 19.0,
        "PWindSW": 7.0,
        "PWindW": 8.0,
        "Temperature": 36.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 30,
        "CWind": 8.0,
        "ID": 30,
        "PWindE": 12.0,
        "PWindN": 19.0,
        "PWindNE": 21.0,
        "PWindNW": 8.0,
        "PWindS": 16.0,
        "PWindSE": 13.0,
        "PWindSW": 7.0,
        "PWindW": 4.0,
        "Temperature": 36.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 31,
        "CWind": 4.0,
        "ID": 31,
        "PWindE": 11.0,
        "PWindN": 19.0,
        "PWindNE": 20.0,
        "PWindNW": 20.0,
        "PWindS": 3.0,
        "PWindSE": 8.0,
        "PWindSW": 8.0,
        "PWindW": 11.0,
        "Temperature": 32.0,
        "WindVelocity": 6.3
    },
    {
        "CITYID": 32,
        "CWind": 4.0,
        "ID": 32,
        "PWindE": 16.0,
        "PWindN": 18.0,
        "PWindNE": 28.0,
        "PWindNW": 9.0,
        "PWindS": 18.0,
        "PWindSE": 5.0,
        "PWindSW": 3.0,
        "PWindW": 3.0,
        "Temperature": 31.0,
        "WindVelocity": 7.6
    },
    {
        "CITYID": 33,
        "CWind": 4.0,
        "ID": 33,
        "PWindE": 9.0,
        "PWindN": 21.0,
        "PWindNE": 22.0,
        "PWindNW": 14.0,
        "PWindS": 9.0,
        "PWindSE": 9.0,
        "PWindSW": 8.0,
        "PWindW": 8.0,
        "Temperature": 34.0,
        "WindVelocity": 5.4
    },
    {
        "CITYID": 34,
        "CWind": 5.0,
        "ID": 34,
        "PWindE": 10.0,
        "PWindN": 23.0,
        "PWindNE": 16.0,
        "PWindNW": 17.0,
        "PWindS": 7.0,
        "PWindSE": 9.0,
        "PWindSW": 6.0,
        "PWindW": 12.0,
        "Temperature": 34.0,
        "WindVelocity": 4.8
    },
    {
        "CITYID": 35,
        "CWind": 4.0,
        "ID": 35,
        "PWindE": 11.0,
        "PWindN": 15.0,
        "PWindNE": 10.0,
        "PWindNW": 14.0,
        "PWindS": 10.0,
        "PWindSE": 12.0,
        "PWindSW": 14.0,
        "PWindW": 14.0,
        "Temperature": 41.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 36,
        "CWind": 12.0,
        "ID": 36,
        "PWindE": 11.0,
        "PWindN": 16.0,
        "PWindNE": 15.0,
        "PWindNW": 17.0,
        "PWindS": 6.0,
        "PWindSE": 6.0,
        "PWindSW": 10.0,
        "PWindW": 19.0,
        "Temperature": 45.0,
        "WindVelocity": 5.0
    },
    {
        "CITYID": 37,
        "CWind": 32.0,
        "ID": 37,
        "PWindE": 7.0,
        "PWindN": 14.0,
        "PWindNE": 14.0,
        "PWindNW": 7.0,
        "PWindS": 8.0,
        "PWindSE": 4.0,
        "PWindSW": 20.0,
        "PWindW": 26.0,
        "Temperature": 38.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 38,
        "CWind": 19.0,
        "ID": 38,
        "PWindE": 6.0,
        "PWindN": 26.0,
        "PWindNE": 11.0,
        "PWindNW": 13.0,
        "PWindS": 13.0,
        "PWindSE": 7.0,
        "PWindSW": 13.0,
        "PWindW": 11.0,
        "Temperature": 41.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 39,
        "CWind": 16.0,
        "ID": 39,
        "PWindE": 5.0,
        "PWindN": 19.0,
        "PWindNE": 9.0,
        "PWindNW": 20.0,
        "PWindS": 13.0,
        "PWindSE": 6.0,
        "PWindSW": 14.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 40,
        "CWind": 19.0,
        "ID": 40,
        "PWindE": 8.0,
        "PWindN": 13.0,
        "PWindNE": 20.0,
        "PWindNW": 12.0,
        "PWindS": 8.0,
        "PWindSE": 9.0,
        "PWindSW": 14.0,
        "PWindW": 16.0,
        "Temperature": 39.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 41,
        "CWind": 5.0,
        "ID": 41,
        "PWindE": 10.0,
        "PWindN": 13.0,
        "PWindNE": 18.0,
        "PWindNW": 19.0,
        "PWindS": 6.0,
        "PWindSE": 8.0,
        "PWindSW": 10.0,
        "PWindW": 16.0,
        "Temperature": 39.0,
        "WindVelocity": 4.9
    },
    {
        "CITYID": 42,
        "CWind": 16.0,
        "ID": 42,
        "PWindE": 11.0,
        "PWindN": 10.0,
        "PWindNE": 12.0,
        "PWindNW": 23.0,
        "PWindS": 7.0,
        "PWindSE": 6.0,
        "PWindSW": 10.0,
        "PWindW": 21.0,
        "Temperature": 38.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 43,
        "CWind": 55.0,
        "ID": 43,
        "PWindE": 6.0,
        "PWindN": 46.0,
        "PWindNE": 6.0,
        "PWindNW": 19.0,
        "PWindS": 10.0,
        "PWindSE": 4.0,
        "PWindSW": 6.0,
        "PWindW": 3.0,
        "Temperature": 40.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 44,
        "CWind": 54.0,
        "ID": 44,
        "PWindE": 38.0,
        "PWindN": 2.0,
        "PWindNE": 8.0,
        "PWindNW": 10.0,
        "PWindS": 3.0,
        "PWindSE": 8.0,
        "PWindSW": 10.0,
        "PWindW": 21.0,
        "Temperature": 34.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 45,
        "CWind": 16.0,
        "ID": 45,
        "PWindE": 14.0,
        "PWindN": 10.0,
        "PWindNE": 9.0,
        "PWindNW": 33.0,
        "PWindS": 3.0,
        "PWindSE": 1.0,
        "PWindSW": 13.0,
        "PWindW": 17.0,
        "Temperature": 40.0,
        "WindVelocity": 4.6
    },
    {
        "CITYID": 46,
        "CWind": 9.0,
        "ID": 46,
        "PWindE": 8.0,
        "PWindN": 17.0,
        "PWindNE": 13.0,
        "PWindNW": 19.0,
        "PWindS": 9.0,
        "PWindSE": 6.0,
        "PWindSW": 14.0,
        "PWindW": 14.0,
        "Temperature": 37.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 47,
        "CWind": 5.0,
        "ID": 47,
        "PWindE": 12.0,
        "PWindN": 14.0,
        "PWindNE": 15.0,
        "PWindNW": 22.0,
        "PWindS": 3.0,
        "PWindSE": 10.0,
        "PWindSW": 10.0,
        "PWindW": 14.0,
        "Temperature": 43.0,
        "WindVelocity": 6.7
    },
    {
        "CITYID": 48,
        "CWind": 6.0,
        "ID": 48,
        "PWindE": 9.0,
        "PWindN": 13.0,
        "PWindNE": 21.0,
        "PWindNW": 29.0,
        "PWindS": 6.0,
        "PWindSE": 6.0,
        "PWindSW": 5.0,
        "PWindW": 11.0,
        "Temperature": 42.0,
        "WindVelocity": 5.7
    },
    {
        "CITYID": 49,
        "CWind": 6.0,
        "ID": 49,
        "PWindE": 12.0,
        "PWindN": 9.0,
        "PWindNE": 10.0,
        "PWindNW": 23.0,
        "PWindS": 3.0,
        "PWindSE": 10.0,
        "PWindSW": 11.0,
        "PWindW": 22.0,
        "Temperature": 42.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 50,
        "CWind": 12.0,
        "ID": 50,
        "PWindE": 13.0,
        "PWindN": 13.0,
        "PWindNE": 14.0,
        "PWindNW": 21.0,
        "PWindS": 6.0,
        "PWindSE": 9.0,
        "PWindSW": 8.0,
        "PWindW": 16.0,
        "Temperature": 45.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 51,
        "CWind": 13.0,
        "ID": 51,
        "PWindE": 6.0,
        "PWindN": 14.0,
        "PWindNE": 18.0,
        "PWindNW": 17.0,
        "PWindS": 8.0,
        "PWindSE": 8.0,
        "PWindSW": 14.0,
        "PWindW": 15.0,
        "Temperature": 39.0,
        "WindVelocity": 4.6
    },
    {
        "CITYID": 52,
        "CWind": 13.0,
        "ID": 52,
        "PWindE": 9.0,
        "PWindN": 10.0,
        "PWindNE": 11.0,
        "PWindNW": 22.0,
        "PWindS": 6.0,
        "PWindSE": 18.0,
        "PWindSW": 9.0,
        "PWindW": 15.0,
        "Temperature": 36.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 53,
        "CWind": 10.0,
        "ID": 53,
        "PWindE": 9.0,
        "PWindN": 19.0,
        "PWindNE": 18.0,
        "PWindNW": 14.0,
        "PWindS": 8.0,
        "PWindSE": 6.0,
        "PWindSW": 16.0,
        "PWindW": 10.0,
        "Temperature": 37.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 54,
        "CWind": 9.0,
        "ID": 54,
        "PWindE": 11.0,
        "PWindN": 19.0,
        "PWindNE": 17.0,
        "PWindNW": 14.0,
        "PWindS": 6.0,
        "PWindSE": 7.0,
        "PWindSW": 9.0,
        "PWindW": 17.0,
        "Temperature": 41.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 55,
        "CWind": 11.0,
        "ID": 55,
        "PWindE": 10.0,
        "PWindN": 12.0,
        "PWindNE": 12.0,
        "PWindNW": 19.0,
        "PWindS": 8.0,
        "PWindSE": 10.0,
        "PWindSW": 11.0,
        "PWindW": 18.0,
        "Temperature": 40.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 56,
        "CWind": 17.0,
        "ID": 56,
        "PWindE": 16.0,
        "PWindN": 13.0,
        "PWindNE": 10.0,
        "PWindNW": 14.0,
        "PWindS": 8.0,
        "PWindSE": 8.0,
        "PWindSW": 14.0,
        "PWindW": 17.0,
        "Temperature": 38.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 57,
        "CWind": 21.0,
        "ID": 57,
        "PWindE": 9.0,
        "PWindN": 17.0,
        "PWindNE": 5.0,
        "PWindNW": 30.0,
        "PWindS": 8.0,
        "PWindSE": 23.0,
        "PWindSW": 1.0,
        "PWindW": 7.0,
        "Temperature": 39.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 58,
        "CWind": 11.0,
        "ID": 58,
        "PWindE": 14.0,
        "PWindN": 3.0,
        "PWindNE": 6.0,
        "PWindNW": 23.0,
        "PWindS": 5.0,
        "PWindSE": 34.0,
        "PWindSW": 1.0,
        "PWindW": 14.0,
        "Temperature": 39.0,
        "WindVelocity": 6.4
    },
    {
        "CITYID": 59,
        "CWind": 11.0,
        "ID": 59,
        "PWindE": 12.0,
        "PWindN": 13.0,
        "PWindNE": 14.0,
        "PWindNW": 13.0,
        "PWindS": 12.0,
        "PWindSE": 7.0,
        "PWindSW": 15.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 60,
        "CWind": 13.0,
        "ID": 60,
        "PWindE": 9.0,
        "PWindN": 14.0,
        "PWindNE": 13.0,
        "PWindNW": 22.0,
        "PWindS": 6.0,
        "PWindSE": 6.0,
        "PWindSW": 14.0,
        "PWindW": 16.0,
        "Temperature": 35.0,
        "WindVelocity": 2.8
    },
    {
        "CITYID": 61,
        "CWind": 23.0,
        "ID": 61,
        "PWindE": 14.0,
        "PWindN": 16.0,
        "PWindNE": 18.0,
        "PWindNW": 10.0,
        "PWindS": 11.0,
        "PWindSE": 8.0,
        "PWindSW": 14.0,
        "PWindW": 9.0,
        "Temperature": 36.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 62,
        "CWind": 21.0,
        "ID": 62,
        "PWindE": 13.0,
        "PWindN": 16.0,
        "PWindNE": 9.0,
        "PWindNW": 26.0,
        "PWindS": 5.0,
        "PWindSE": 13.0,
        "PWindSW": 6.0,
        "PWindW": 12.0,
        "Temperature": 37.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 63,
        "CWind": 11.0,
        "ID": 63,
        "PWindE": 5.0,
        "PWindN": 4.0,
        "PWindNE": 2.0,
        "PWindNW": 24.0,
        "PWindS": 9.0,
        "PWindSE": 32.0,
        "PWindSW": 6.0,
        "PWindW": 18.0,
        "Temperature": 37.0,
        "WindVelocity": 3.0
    },
    {
        "CITYID": 64,
        "CWind": 37.0,
        "ID": 64,
        "PWindE": 6.0,
        "PWindN": 20.0,
        "PWindNE": 22.0,
        "PWindNW": 14.0,
        "PWindS": 11.0,
        "PWindSE": 7.0,
        "PWindSW": 14.0,
        "PWindW": 6.0,
        "Temperature": 37.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 65,
        "CWind": 52.0,
        "ID": 65,
        "PWindE": 20.0,
        "PWindN": 7.0,
        "PWindNE": 12.0,
        "PWindNW": 7.0,
        "PWindS": 2.0,
        "PWindSE": 5.0,
        "PWindSW": 14.0,
        "PWindW": 33.0,
        "Temperature": 33.0,
        "WindVelocity": 3.0
    },
    {
        "CITYID": 66,
        "CWind": 26.0,
        "ID": 66,
        "PWindE": 12.0,
        "PWindN": 7.0,
        "PWindNE": 12.0,
        "PWindNW": 9.0,
        "PWindS": 4.0,
        "PWindSE": 9.0,
        "PWindSW": 15.0,
        "PWindW": 32.0,
        "Temperature": 36.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 67,
        "CWind": 32.0,
        "ID": 67,
        "PWindE": 11.0,
        "PWindN": 9.0,
        "PWindNE": 16.0,
        "PWindNW": 21.0,
        "PWindS": 3.0,
        "PWindSE": 19.0,
        "PWindSW": 6.0,
        "PWindW": 15.0,
        "Temperature": 37.0,
        "WindVelocity": 3.0
    },
    {
        "CITYID": 68,
        "CWind": 20.0,
        "ID": 68,
        "PWindE": 12.0,
        "PWindN": 6.0,
        "PWindNE": 9.0,
        "PWindNW": 9.0,
        "PWindS": 6.0,
        "PWindSE": 6.0,
        "PWindSW": 44.0,
        "PWindW": 8.0,
        "Temperature": 39.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 69,
        "CWind": 10.0,
        "ID": 69,
        "PWindE": 7.0,
        "PWindN": 12.0,
        "PWindNE": 7.0,
        "PWindNW": 14.0,
        "PWindS": 10.0,
        "PWindSE": 8.0,
        "PWindSW": 20.0,
        "PWindW": 22.0,
        "Temperature": 37.0,
        "WindVelocity": 5.4
    },
    {
        "CITYID": 70,
        "CWind": 9.0,
        "ID": 70,
        "PWindE": 9.0,
        "PWindN": 12.0,
        "PWindNE": 9.0,
        "PWindNW": 16.0,
        "PWindS": 9.0,
        "PWindSE": 8.0,
        "PWindSW": 16.0,
        "PWindW": 21.0,
        "Temperature": 36.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 71,
        "CWind": 16.0,
        "ID": 71,
        "PWindE": 8.0,
        "PWindN": 18.0,
        "PWindNE": 10.0,
        "PWindNW": 17.0,
        "PWindS": 5.0,
        "PWindSE": 5.0,
        "PWindSW": 17.0,
        "PWindW": 20.0,
        "Temperature": 39.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 72,
        "CWind": 16.0,
        "ID": 72,
        "PWindE": 14.0,
        "PWindN": 12.0,
        "PWindNE": 13.0,
        "PWindNW": 19.0,
        "PWindS": 2.0,
        "PWindSE": 9.0,
        "PWindSW": 7.0,
        "PWindW": 24.0,
        "Temperature": 43.0,
        "WindVelocity": 6.4
    },
    {
        "CITYID": 73,
        "CWind": 12.0,
        "ID": 73,
        "PWindE": 13.0,
        "PWindN": 14.0,
        "PWindNE": 14.0,
        "PWindNW": 13.0,
        "PWindS": 7.0,
        "PWindSE": 8.0,
        "PWindSW": 14.0,
        "PWindW": 17.0,
        "Temperature": 38.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 74,
        "CWind": 15.0,
        "ID": 74,
        "PWindE": 36.0,
        "PWindN": 1.0,
        "PWindNE": 12.0,
        "PWindNW": 16.0,
        "PWindS": 1.0,
        "PWindSE": 7.0,
        "PWindSW": 5.0,
        "PWindW": 22.0,
        "Temperature": 31.0,
        "WindVelocity": 5.8
    },
    {
        "CITYID": 75,
        "CWind": 38.0,
        "ID": 75,
        "PWindE": 18.0,
        "PWindN": 3.0,
        "PWindNE": 4.0,
        "PWindNW": 6.0,
        "PWindS": 14.0,
        "PWindSE": 24.0,
        "PWindSW": 21.0,
        "PWindW": 10.0,
        "Temperature": 30.0,
        "WindVelocity": 5.1
    },
    {
        "CITYID": 76,
        "CWind": 17.0,
        "ID": 76,
        "PWindE": 5.0,
        "PWindN": 14.0,
        "PWindNE": 1.0,
        "PWindNW": 19.0,
        "PWindS": 10.0,
        "PWindSE": 44.0,
        "PWindSW": 2.0,
        "PWindW": 5.0,
        "Temperature": 30.0,
        "WindVelocity": 6.8
    },
    {
        "CITYID": 77,
        "CWind": 19.0,
        "ID": 77,
        "PWindE": 4.0,
        "PWindN": 14.0,
        "PWindNE": 20.0,
        "PWindNW": 21.0,
        "PWindS": 23.0,
        "PWindSE": 8.0,
        "PWindSW": 5.0,
        "PWindW": 5.0,
        "Temperature": 34.0,
        "WindVelocity": 7.5
    },
    {
        "CITYID": 78,
        "CWind": 0.0,
        "ID": 78,
        "PWindE": 1.0,
        "PWindN": 15.0,
        "PWindNE": 2.0,
        "PWindNW": 16.0,
        "PWindS": 39.0,
        "PWindSE": 4.0,
        "PWindSW": 14.0,
        "PWindW": 9.0,
        "Temperature": 29.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 79,
        "CWind": 7.0,
        "ID": 79,
        "PWindE": 4.0,
        "PWindN": 22.0,
        "PWindNE": 5.0,
        "PWindNW": 8.0,
        "PWindS": 11.0,
        "PWindSE": 20.0,
        "PWindSW": 13.0,
        "PWindW": 17.0,
        "Temperature": 29.0,
        "WindVelocity": 6.0
    },
    {
        "CITYID": 80,
        "CWind": 12.0,
        "ID": 80,
        "PWindE": 1.0,
        "PWindN": 8.0,
        "PWindNE": 16.0,
        "PWindNW": 4.0,
        "PWindS": 51.0,
        "PWindSE": 11.0,
        "PWindSW": 5.0,
        "PWindW": 4.0,
        "Temperature": 30.0,
        "WindVelocity": 5.5
    },
    {
        "CITYID": 81,
        "CWind": 15.0,
        "ID": 81,
        "PWindE": 3.0,
        "PWindN": 26.0,
        "PWindNE": 2.0,
        "PWindNW": 15.0,
        "PWindS": 17.0,
        "PWindSE": 4.0,
        "PWindSW": 25.0,
        "PWindW": 8.0,
        "Temperature": 29.0,
        "WindVelocity": 6.3
    },
    {
        "CITYID": 82,
        "CWind": 6.0,
        "ID": 82,
        "PWindE": 13.0,
        "PWindN": 15.0,
        "PWindNE": 20.0,
        "PWindNW": 8.0,
        "PWindS": 9.0,
        "PWindSE": 14.0,
        "PWindSW": 11.0,
        "PWindW": 10.0,
        "Temperature": 33.0,
        "WindVelocity": 5.2
    },
    {
        "CITYID": 83,
        "CWind": 5.0,
        "ID": 83,
        "PWindE": 13.0,
        "PWindN": 11.0,
        "PWindNE": 13.0,
        "PWindNW": 8.0,
        "PWindS": 13.0,
        "PWindSE": 12.0,
        "PWindSW": 17.0,
        "PWindW": 13.0,
        "Temperature": 36.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 84,
        "CWind": 7.0,
        "ID": 84,
        "PWindE": 17.0,
        "PWindN": 13.0,
        "PWindNE": 16.0,
        "PWindNW": 10.0,
        "PWindS": 8.0,
        "PWindSE": 11.0,
        "PWindSW": 11.0,
        "PWindW": 14.0,
        "Temperature": 32.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 85,
        "CWind": 8.0,
        "ID": 85,
        "PWindE": 20.0,
        "PWindN": 12.0,
        "PWindNE": 8.0,
        "PWindNW": 8.0,
        "PWindS": 6.0,
        "PWindSE": 5.0,
        "PWindSW": 27.0,
        "PWindW": 14.0,
        "Temperature": 34.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 86,
        "CWind": 21.0,
        "ID": 86,
        "PWindE": 6.0,
        "PWindN": 14.0,
        "PWindNE": 9.0,
        "PWindNW": 14.0,
        "PWindS": 14.0,
        "PWindSE": 16.0,
        "PWindSW": 19.0,
        "PWindW": 8.0,
        "Temperature": 37.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 87,
        "CWind": 13.0,
        "ID": 87,
        "PWindE": 6.0,
        "PWindN": 12.0,
        "PWindNE": 10.0,
        "PWindNW": 14.0,
        "PWindS": 11.0,
        "PWindSE": 8.0,
        "PWindSW": 28.0,
        "PWindW": 11.0,
        "Temperature": 38.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 88,
        "CWind": 44.0,
        "ID": 88,
        "PWindE": 6.0,
        "PWindN": 15.0,
        "PWindNE": 6.0,
        "PWindNW": 14.0,
        "PWindS": 20.0,
        "PWindSE": 8.0,
        "PWindSW": 17.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 3.0
    },
    {
        "CITYID": 89,
        "CWind": 15.0,
        "ID": 89,
        "PWindE": 14.0,
        "PWindN": 6.0,
        "PWindNE": 11.0,
        "PWindNW": 10.0,
        "PWindS": 13.0,
        "PWindSE": 6.0,
        "PWindSW": 27.0,
        "PWindW": 13.0,
        "Temperature": 37.0,
        "WindVelocity": 3.0
    },
    {
        "CITYID": 90,
        "CWind": 17.0,
        "ID": 90,
        "PWindE": 8.0,
        "PWindN": 9.0,
        "PWindNE": 18.0,
        "PWindNW": 10.0,
        "PWindS": 14.0,
        "PWindSE": 10.0,
        "PWindSW": 20.0,
        "PWindW": 11.0,
        "Temperature": 36.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 91,
        "CWind": 3.0,
        "ID": 91,
        "PWindE": 13.0,
        "PWindN": 16.0,
        "PWindNE": 13.0,
        "PWindNW": 19.0,
        "PWindS": 6.0,
        "PWindSE": 10.0,
        "PWindSW": 8.0,
        "PWindW": 15.0,
        "Temperature": 37.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 92,
        "CWind": 5.0,
        "ID": 92,
        "PWindE": 10.0,
        "PWindN": 20.0,
        "PWindNE": 13.0,
        "PWindNW": 16.0,
        "PWindS": 10.0,
        "PWindSE": 13.0,
        "PWindSW": 9.0,
        "PWindW": 9.0,
        "Temperature": 34.0,
        "WindVelocity": 5.9
    },
    {
        "CITYID": 93,
        "CWind": 11.0,
        "ID": 93,
        "PWindE": 7.0,
        "PWindN": 27.0,
        "PWindNE": 7.0,
        "PWindNW": 15.0,
        "PWindS": 7.0,
        "PWindSE": 20.0,
        "PWindSW": 9.0,
        "PWindW": 8.0,
        "Temperature": 35.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 94,
        "CWind": 6.0,
        "ID": 94,
        "PWindE": 6.0,
        "PWindN": 20.0,
        "PWindNE": 15.0,
        "PWindNW": 17.0,
        "PWindS": 11.0,
        "PWindSE": 5.0,
        "PWindSW": 17.0,
        "PWindW": 9.0,
        "Temperature": 35.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 95,
        "CWind": 7.0,
        "ID": 95,
        "PWindE": 5.0,
        "PWindN": 23.0,
        "PWindNE": 10.0,
        "PWindNW": 21.0,
        "PWindS": 8.0,
        "PWindSE": 6.0,
        "PWindSW": 14.0,
        "PWindW": 13.0,
        "Temperature": 35.0,
        "WindVelocity": 5.0
    },
    {
        "CITYID": 96,
        "CWind": 26.0,
        "ID": 96,
        "PWindE": 6.0,
        "PWindN": 40.0,
        "PWindNE": 8.0,
        "PWindNW": 10.0,
        "PWindS": 10.0,
        "PWindSE": 9.0,
        "PWindSW": 8.0,
        "PWindW": 9.0,
        "Temperature": 36.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 97,
        "CWind": 9.0,
        "ID": 97,
        "PWindE": 10.0,
        "PWindN": 24.0,
        "PWindNE": 16.0,
        "PWindNW": 10.0,
        "PWindS": 8.0,
        "PWindSE": 10.0,
        "PWindSW": 9.0,
        "PWindW": 13.0,
        "Temperature": 35.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 98,
        "CWind": 6.0,
        "ID": 98,
        "PWindE": 7.0,
        "PWindN": 15.0,
        "PWindNE": 13.0,
        "PWindNW": 18.0,
        "PWindS": 11.0,
        "PWindSE": 10.0,
        "PWindSW": 12.0,
        "PWindW": 14.0,
        "Temperature": 37.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 99,
        "CWind": 8.0,
        "ID": 99,
        "PWindE": 10.0,
        "PWindN": 21.0,
        "PWindNE": 13.0,
        "PWindNW": 13.0,
        "PWindS": 11.0,
        "PWindSE": 9.0,
        "PWindSW": 9.0,
        "PWindW": 14.0,
        "Temperature": 36.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 100,
        "CWind": 12.0,
        "ID": 100,
        "PWindE": 13.0,
        "PWindN": 8.0,
        "PWindNE": 16.0,
        "PWindNW": 14.0,
        "PWindS": 7.0,
        "PWindSE": 4.0,
        "PWindSW": 20.0,
        "PWindW": 18.0,
        "Temperature": 42.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 101,
        "CWind": 12.0,
        "ID": 101,
        "PWindE": 9.0,
        "PWindN": 11.0,
        "PWindNE": 29.0,
        "PWindNW": 18.0,
        "PWindS": 5.0,
        "PWindSE": 11.0,
        "PWindSW": 6.0,
        "PWindW": 11.0,
        "Temperature": 39.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 102,
        "CWind": 13.0,
        "ID": 102,
        "PWindE": 15.0,
        "PWindN": 11.0,
        "PWindNE": 17.0,
        "PWindNW": 11.0,
        "PWindS": 5.0,
        "PWindSE": 5.0,
        "PWindSW": 17.0,
        "PWindW": 19.0,
        "Temperature": 42.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 103,
        "CWind": 8.0,
        "ID": 103,
        "PWindE": 14.0,
        "PWindN": 5.0,
        "PWindNE": 12.0,
        "PWindNW": 9.0,
        "PWindS": 30.0,
        "PWindSE": 8.0,
        "PWindSW": 10.0,
        "PWindW": 12.0,
        "Temperature": 41.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 104,
        "CWind": 7.0,
        "ID": 104,
        "PWindE": 19.0,
        "PWindN": 6.0,
        "PWindNE": 13.0,
        "PWindNW": 8.0,
        "PWindS": 12.0,
        "PWindSE": 8.0,
        "PWindSW": 16.0,
        "PWindW": 18.0,
        "Temperature": 37.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 105,
        "CWind": 41.0,
        "ID": 105,
        "PWindE": 10.0,
        "PWindN": 18.0,
        "PWindNE": 17.0,
        "PWindNW": 8.0,
        "PWindS": 12.0,
        "PWindSE": 12.0,
        "PWindSW": 12.0,
        "PWindW": 11.0,
        "Temperature": 39.0,
        "WindVelocity": 2.7
    },
    {
        "CITYID": 106,
        "CWind": 24.0,
        "ID": 106,
        "PWindE": 15.0,
        "PWindN": 5.0,
        "PWindNE": 14.0,
        "PWindNW": 7.0,
        "PWindS": 11.0,
        "PWindSE": 4.0,
        "PWindSW": 22.0,
        "PWindW": 22.0,
        "Temperature": 38.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 107,
        "CWind": 30.0,
        "ID": 107,
        "PWindE": 7.0,
        "PWindN": 20.0,
        "PWindNE": 20.0,
        "PWindNW": 10.0,
        "PWindS": 7.0,
        "PWindSE": 7.0,
        "PWindSW": 19.0,
        "PWindW": 10.0,
        "Temperature": 36.0,
        "WindVelocity": 3.2
    },
    {
        "CITYID": 108,
        "CWind": 16.0,
        "ID": 108,
        "PWindE": 12.0,
        "PWindN": 17.0,
        "PWindNE": 10.0,
        "PWindNW": 22.0,
        "PWindS": 13.0,
        "PWindSE": 13.0,
        "PWindSW": 6.0,
        "PWindW": 7.0,
        "Temperature": 35.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 109,
        "CWind": 7.0,
        "ID": 109,
        "PWindE": 20.0,
        "PWindN": 10.0,
        "PWindNE": 22.0,
        "PWindNW": 15.0,
        "PWindS": 3.0,
        "PWindSE": 6.0,
        "PWindSW": 6.0,
        "PWindW": 18.0,
        "Temperature": 36.0,
        "WindVelocity": 5.0
    },
    {
        "CITYID": 110,
        "CWind": 3.0,
        "ID": 110,
        "PWindE": 5.0,
        "PWindN": 25.0,
        "PWindNE": 31.0,
        "PWindNW": 10.0,
        "PWindS": 9.0,
        "PWindSE": 4.0,
        "PWindSW": 9.0,
        "PWindW": 7.0,
        "Temperature": 27.0,
        "WindVelocity": 7.0
    },
    {
        "CITYID": 111,
        "CWind": 8.0,
        "ID": 111,
        "PWindE": 14.0,
        "PWindN": 21.0,
        "PWindNE": 21.0,
        "PWindNW": 12.0,
        "PWindS": 8.0,
        "PWindSE": 9.0,
        "PWindSW": 7.0,
        "PWindW": 8.0,
        "Temperature": 32.0,
        "WindVelocity": 7.1
    },
    {
        "CITYID": 112,
        "CWind": 17.0,
        "ID": 112,
        "PWindE": 14.0,
        "PWindN": 3.0,
        "PWindNE": 5.0,
        "PWindNW": 15.0,
        "PWindS": 14.0,
        "PWindSE": 17.0,
        "PWindSW": 17.0,
        "PWindW": 15.0,
        "Temperature": 35.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 113,
        "CWind": 11.0,
        "ID": 113,
        "PWindE": 11.0,
        "PWindN": 18.0,
        "PWindNE": 11.0,
        "PWindNW": 17.0,
        "PWindS": 11.0,
        "PWindSE": 17.0,
        "PWindSW": 7.0,
        "PWindW": 8.0,
        "Temperature": 34.0,
        "WindVelocity": 5.1
    },
    {
        "CITYID": 114,
        "CWind": 23.0,
        "ID": 114,
        "PWindE": 19.0,
        "PWindN": 7.0,
        "PWindNE": 9.0,
        "PWindNW": 9.0,
        "PWindS": 4.0,
        "PWindSE": 11.0,
        "PWindSW": 15.0,
        "PWindW": 26.0,
        "Temperature": 38.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 115,
        "CWind": 24.0,
        "ID": 115,
        "PWindE": 10.0,
        "PWindN": 4.0,
        "PWindNE": 9.0,
        "PWindNW": 6.0,
        "PWindS": 11.0,
        "PWindSE": 3.0,
        "PWindSW": 41.0,
        "PWindW": 16.0,
        "Temperature": 38.0,
        "WindVelocity": 3.0
    },
    {
        "CITYID": 116,
        "CWind": 31.0,
        "ID": 116,
        "PWindE": 5.0,
        "PWindN": 15.0,
        "PWindNE": 19.0,
        "PWindNW": 11.0,
        "PWindS": 4.0,
        "PWindSE": 6.0,
        "PWindSW": 23.0,
        "PWindW": 17.0,
        "Temperature": 39.0,
        "WindVelocity": 2.8
    },
    {
        "CITYID": 117,
        "CWind": 26.0,
        "ID": 117,
        "PWindE": 15.0,
        "PWindN": 16.0,
        "PWindNE": 12.0,
        "PWindNW": 20.0,
        "PWindS": 3.0,
        "PWindSE": 7.0,
        "PWindSW": 10.0,
        "PWindW": 17.0,
        "Temperature": 39.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 118,
        "CWind": 8.0,
        "ID": 118,
        "PWindE": 13.0,
        "PWindN": 17.0,
        "PWindNE": 10.0,
        "PWindNW": 20.0,
        "PWindS": 12.0,
        "PWindSE": 14.0,
        "PWindSW": 6.0,
        "PWindW": 8.0,
        "Temperature": 36.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 119,
        "CWind": 3.0,
        "ID": 119,
        "PWindE": 14.0,
        "PWindN": 11.0,
        "PWindNE": 28.0,
        "PWindNW": 9.0,
        "PWindS": 6.0,
        "PWindSE": 10.0,
        "PWindSW": 9.0,
        "PWindW": 13.0,
        "Temperature": 37.0,
        "WindVelocity": 5.3
    },
    {
        "CITYID": 120,
        "CWind": 5.0,
        "ID": 120,
        "PWindE": 31.0,
        "PWindN": 2.0,
        "PWindNE": 13.0,
        "PWindNW": 4.0,
        "PWindS": 3.0,
        "PWindSE": 5.0,
        "PWindSW": 11.0,
        "PWindW": 31.0,
        "Temperature": 24.0,
        "WindVelocity": 8.2
    },
    {
        "CITYID": 121,
        "CWind": 13.0,
        "ID": 121,
        "PWindE": 15.0,
        "PWindN": 9.0,
        "PWindNE": 4.0,
        "PWindNW": 23.0,
        "PWindS": 9.0,
        "PWindSE": 27.0,
        "PWindSW": 5.0,
        "PWindW": 8.0,
        "Temperature": 36.0,
        "WindVelocity": 3.7
    },
    {
        "CITYID": 122,
        "CWind": 28.0,
        "ID": 122,
        "PWindE": 6.0,
        "PWindN": 29.0,
        "PWindNE": 8.0,
        "PWindNW": 7.0,
        "PWindS": 15.0,
        "PWindSE": 8.0,
        "PWindSW": 17.0,
        "PWindW": 10.0,
        "Temperature": 39.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 123,
        "CWind": 28.0,
        "ID": 123,
        "PWindE": 11.0,
        "PWindN": 14.0,
        "PWindNE": 7.0,
        "PWindNW": 18.0,
        "PWindS": 15.0,
        "PWindSE": 10.0,
        "PWindSW": 17.0,
        "PWindW": 8.0,
        "Temperature": 38.0,
        "WindVelocity": 3.2
    },
    {
        "CITYID": 124,
        "CWind": 6.0,
        "ID": 124,
        "PWindE": 13.0,
        "PWindN": 18.0,
        "PWindNE": 13.0,
        "PWindNW": 18.0,
        "PWindS": 4.0,
        "PWindSE": 6.0,
        "PWindSW": 10.0,
        "PWindW": 18.0,
        "Temperature": 40.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 125,
        "CWind": 1.1,
        "ID": 125,
        "PWindE": 8.3,
        "PWindN": 17.8,
        "PWindNE": 6.9,
        "PWindNW": 10.1,
        "PWindS": 14.1,
        "PWindSE": 4.3,
        "PWindSW": 21.4,
        "PWindW": 15.9,
        "Temperature": 41.0,
        "WindVelocity": 8.0
    },
    {
        "CITYID": 126,
        "CWind": 5.0,
        "ID": 126,
        "PWindE": 10.0,
        "PWindN": 14.0,
        "PWindNE": 16.0,
        "PWindNW": 19.0,
        "PWindS": 5.0,
        "PWindSE": 9.0,
        "PWindSW": 10.0,
        "PWindW": 17.0,
        "Temperature": 39.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 127,
        "CWind": 5.0,
        "ID": 127,
        "PWindE": 9.0,
        "PWindN": 12.0,
        "PWindNE": 18.0,
        "PWindNW": 9.0,
        "PWindS": 9.0,
        "PWindSE": 5.0,
        "PWindSW": 29.0,
        "PWindW": 9.0,
        "Temperature": 35.0,
        "WindVelocity": 5.6
    },
    {
        "CITYID": 128,
        "CWind": 15.0,
        "ID": 128,
        "PWindE": 9.0,
        "PWindN": 9.0,
        "PWindNE": 19.0,
        "PWindNW": 10.0,
        "PWindS": 8.0,
        "PWindSE": 8.0,
        "PWindSW": 15.0,
        "PWindW": 22.0,
        "Temperature": 37.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 129,
        "CWind": 14.0,
        "ID": 129,
        "PWindE": 13.0,
        "PWindN": 10.0,
        "PWindNE": 11.0,
        "PWindNW": 14.0,
        "PWindS": 10.0,
        "PWindSE": 11.0,
        "PWindSW": 18.0,
        "PWindW": 13.0,
        "Temperature": 38.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 130,
        "CWind": 7.0,
        "ID": 130,
        "PWindE": 9.0,
        "PWindN": 15.0,
        "PWindNE": 13.0,
        "PWindNW": 23.0,
        "PWindS": 6.0,
        "PWindSE": 8.0,
        "PWindSW": 10.0,
        "PWindW": 16.0,
        "Temperature": 41.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 131,
        "CWind": 0.4,
        "ID": 131,
        "PWindE": 24.4,
        "PWindN": 1.8,
        "PWindNE": 16.8,
        "PWindNW": 3.2,
        "PWindS": 0.7,
        "PWindSE": 14.0,
        "PWindSW": 3.2,
        "PWindW": 35.5,
        "Temperature": 26.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 132,
        "CWind": 14.0,
        "ID": 132,
        "PWindE": 2.0,
        "PWindN": 8.0,
        "PWindNE": 24.0,
        "PWindNW": 4.0,
        "PWindS": 6.0,
        "PWindSE": 1.0,
        "PWindSW": 31.0,
        "PWindW": 24.0,
        "Temperature": 34.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 133,
        "CWind": 45.0,
        "ID": 133,
        "PWindE": 21.0,
        "PWindN": 7.0,
        "PWindNE": 11.0,
        "PWindNW": 5.0,
        "PWindS": 2.0,
        "PWindSE": 3.0,
        "PWindSW": 11.0,
        "PWindW": 40.0,
        "Temperature": 33.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 134,
        "CWind": 27.0,
        "ID": 134,
        "PWindE": 7.0,
        "PWindN": 34.0,
        "PWindNE": 8.0,
        "PWindNW": 8.0,
        "PWindS": 9.0,
        "PWindSE": 18.0,
        "PWindSW": 10.0,
        "PWindW": 6.0,
        "Temperature": 36.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 135,
        "CWind": 26.0,
        "ID": 135,
        "PWindE": 11.0,
        "PWindN": 9.0,
        "PWindNE": 39.0,
        "PWindNW": 1.0,
        "PWindS": 14.0,
        "PWindSE": 4.0,
        "PWindSW": 17.0,
        "PWindW": 5.0,
        "Temperature": 35.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 136,
        "CWind": 27.0,
        "ID": 136,
        "PWindE": 15.0,
        "PWindN": 3.0,
        "PWindNE": 3.0,
        "PWindNW": 24.0,
        "PWindS": 6.0,
        "PWindSE": 15.0,
        "PWindSW": 6.0,
        "PWindW": 28.0,
        "Temperature": 35.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 137,
        "CWind": 26.0,
        "ID": 137,
        "PWindE": 13.0,
        "PWindN": 3.0,
        "PWindNE": 3.0,
        "PWindNW": 28.0,
        "PWindS": 5.0,
        "PWindSE": 29.0,
        "PWindSW": 3.0,
        "PWindW": 16.0,
        "Temperature": 33.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 138,
        "CWind": 3.6,
        "ID": 138,
        "PWindE": 7.3,
        "PWindN": 14.5,
        "PWindNE": 7.3,
        "PWindNW": 14.2,
        "PWindS": 11.8,
        "PWindSE": 5.4,
        "PWindSW": 11.2,
        "PWindW": 24.8,
        "Temperature": 34.0,
        "WindVelocity": 2.9
    },
    {
        "CITYID": 139,
        "CWind": 0,
        "ID": 139,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 33.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 140,
        "CWind": 9.0,
        "ID": 140,
        "PWindE": 9.0,
        "PWindN": 3.0,
        "PWindNE": 5.0,
        "PWindNW": 9.0,
        "PWindS": 20.0,
        "PWindSE": 43.0,
        "PWindSW": 2.0,
        "PWindW": 9.0,
        "Temperature": 30.0,
        "WindVelocity": 8.0
    },
    {
        "CITYID": 141,
        "CWind": 17.0,
        "ID": 141,
        "PWindE": 7.0,
        "PWindN": 15.0,
        "PWindNE": 16.0,
        "PWindNW": 19.0,
        "PWindS": 9.0,
        "PWindSE": 8.0,
        "PWindSW": 11.0,
        "PWindW": 15.0,
        "Temperature": 39.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 142,
        "CWind": 14.0,
        "ID": 142,
        "PWindE": 9.0,
        "PWindN": 13.0,
        "PWindNE": 9.0,
        "PWindNW": 17.0,
        "PWindS": 11.0,
        "PWindSE": 10.0,
        "PWindSW": 15.0,
        "PWindW": 16.0,
        "Temperature": 39.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 143,
        "CWind": 9.0,
        "ID": 143,
        "PWindE": 8.0,
        "PWindN": 12.0,
        "PWindNE": 8.0,
        "PWindNW": 22.0,
        "PWindS": 9.0,
        "PWindSE": 12.0,
        "PWindSW": 11.0,
        "PWindW": 18.0,
        "Temperature": 38.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 144,
        "CWind": 12.0,
        "ID": 144,
        "PWindE": 10.0,
        "PWindN": 17.0,
        "PWindNE": 10.0,
        "PWindNW": 22.0,
        "PWindS": 6.0,
        "PWindSE": 8.0,
        "PWindSW": 11.0,
        "PWindW": 16.0,
        "Temperature": 38.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 145,
        "CWind": 0,
        "ID": 145,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 146,
        "CWind": 13.0,
        "ID": 146,
        "PWindE": 6.0,
        "PWindN": 24.0,
        "PWindNE": 8.0,
        "PWindNW": 7.0,
        "PWindS": 5.0,
        "PWindSE": 45.0,
        "PWindSW": 3.0,
        "PWindW": 2.0,
        "Temperature": 32.0,
        "WindVelocity": 4.6
    },
    {
        "CITYID": 147,
        "CWind": 24.0,
        "ID": 147,
        "PWindE": 11.0,
        "PWindN": 15.0,
        "PWindNE": 5.0,
        "PWindNW": 18.0,
        "PWindS": 8.0,
        "PWindSE": 19.0,
        "PWindSW": 12.0,
        "PWindW": 12.0,
        "Temperature": 32.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 148,
        "CWind": 12.0,
        "ID": 148,
        "PWindE": 12.0,
        "PWindN": 13.0,
        "PWindNE": 25.0,
        "PWindNW": 9.0,
        "PWindS": 8.0,
        "PWindSE": 9.0,
        "PWindSW": 18.0,
        "PWindW": 6.0,
        "Temperature": 34.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 149,
        "CWind": 15.0,
        "ID": 149,
        "PWindE": 15.0,
        "PWindN": 15.0,
        "PWindNE": 17.0,
        "PWindNW": 15.0,
        "PWindS": 6.0,
        "PWindSE": 17.0,
        "PWindSW": 6.0,
        "PWindW": 9.0,
        "Temperature": 34.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 150,
        "CWind": 13.0,
        "ID": 150,
        "PWindE": 6.0,
        "PWindN": 24.0,
        "PWindNE": 14.0,
        "PWindNW": 12.0,
        "PWindS": 29.0,
        "PWindSE": 7.0,
        "PWindSW": 6.0,
        "PWindW": 2.0,
        "Temperature": 32.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 151,
        "CWind": 8.0,
        "ID": 151,
        "PWindE": 4.0,
        "PWindN": 36.0,
        "PWindNE": 18.0,
        "PWindNW": 7.0,
        "PWindS": 20.0,
        "PWindSE": 3.0,
        "PWindSW": 9.0,
        "PWindW": 3.0,
        "Temperature": 33.0,
        "WindVelocity": 5.4
    },
    {
        "CITYID": 152,
        "CWind": 0,
        "ID": 152,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 29.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 153,
        "CWind": 12.0,
        "ID": 153,
        "PWindE": 16.0,
        "PWindN": 6.0,
        "PWindNE": 9.0,
        "PWindNW": 15.0,
        "PWindS": 7.0,
        "PWindSE": 14.0,
        "PWindSW": 14.0,
        "PWindW": 19.0,
        "Temperature": 39.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 154,
        "CWind": 7.0,
        "ID": 154,
        "PWindE": 9.0,
        "PWindN": 13.0,
        "PWindNE": 14.0,
        "PWindNW": 11.0,
        "PWindS": 11.0,
        "PWindSE": 11.0,
        "PWindSW": 15.0,
        "PWindW": 16.0,
        "Temperature": 36.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 155,
        "CWind": 0,
        "ID": 155,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 40.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 156,
        "CWind": 0,
        "ID": 156,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 157,
        "CWind": 0,
        "ID": 157,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 158,
        "CWind": 4.0,
        "ID": 158,
        "PWindE": 10.0,
        "PWindN": 14.0,
        "PWindNE": 15.0,
        "PWindNW": 15.0,
        "PWindS": 9.0,
        "PWindSE": 10.0,
        "PWindSW": 13.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 159,
        "CWind": 6.0,
        "ID": 159,
        "PWindE": 10.0,
        "PWindN": 7.0,
        "PWindNE": 14.0,
        "PWindNW": 13.0,
        "PWindS": 13.0,
        "PWindSE": 8.0,
        "PWindSW": 20.0,
        "PWindW": 15.0,
        "Temperature": 36.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 160,
        "CWind": 3.0,
        "ID": 160,
        "PWindE": 10.0,
        "PWindN": 15.0,
        "PWindNE": 16.0,
        "PWindNW": 15.0,
        "PWindS": 9.0,
        "PWindSE": 8.0,
        "PWindSW": 12.0,
        "PWindW": 15.0,
        "Temperature": 40.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 161,
        "CWind": 18.0,
        "ID": 161,
        "PWindE": 11.0,
        "PWindN": 12.0,
        "PWindNE": 18.0,
        "PWindNW": 11.0,
        "PWindS": 11.0,
        "PWindSE": 10.0,
        "PWindSW": 15.0,
        "PWindW": 12.0,
        "Temperature": 37.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 162,
        "CWind": 5.0,
        "ID": 162,
        "PWindE": 11.0,
        "PWindN": 15.0,
        "PWindNE": 14.0,
        "PWindNW": 17.0,
        "PWindS": 8.0,
        "PWindSE": 8.0,
        "PWindSW": 12.0,
        "PWindW": 15.0,
        "Temperature": 40.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 163,
        "CWind": 10.0,
        "ID": 163,
        "PWindE": 8.0,
        "PWindN": 12.0,
        "PWindNE": 17.0,
        "PWindNW": 10.0,
        "PWindS": 12.0,
        "PWindSE": 11.0,
        "PWindSW": 18.0,
        "PWindW": 12.0,
        "Temperature": 40.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 164,
        "CWind": 7.0,
        "ID": 164,
        "PWindE": 10.0,
        "PWindN": 17.0,
        "PWindNE": 13.0,
        "PWindNW": 21.0,
        "PWindS": 9.0,
        "PWindSE": 6.0,
        "PWindSW": 11.0,
        "PWindW": 13.0,
        "Temperature": 40.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 165,
        "CWind": 10.0,
        "ID": 165,
        "PWindE": 9.0,
        "PWindN": 14.0,
        "PWindNE": 11.0,
        "PWindNW": 18.0,
        "PWindS": 11.0,
        "PWindSE": 14.0,
        "PWindSW": 10.0,
        "PWindW": 13.0,
        "Temperature": 38.0,
        "WindVelocity": 3.7
    },
    {
        "CITYID": 166,
        "CWind": 4.0,
        "ID": 166,
        "PWindE": 11.0,
        "PWindN": 16.0,
        "PWindNE": 15.0,
        "PWindNW": 17.0,
        "PWindS": 8.0,
        "PWindSE": 10.0,
        "PWindSW": 10.0,
        "PWindW": 13.0,
        "Temperature": 41.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 167,
        "CWind": 12.0,
        "ID": 167,
        "PWindE": 16.0,
        "PWindN": 7.0,
        "PWindNE": 17.0,
        "PWindNW": 19.0,
        "PWindS": 4.0,
        "PWindSE": 6.0,
        "PWindSW": 7.0,
        "PWindW": 24.0,
        "Temperature": 42.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 168,
        "CWind": 7.0,
        "ID": 168,
        "PWindE": 16.0,
        "PWindN": 20.0,
        "PWindNE": 15.0,
        "PWindNW": 17.0,
        "PWindS": 3.0,
        "PWindSE": 5.0,
        "PWindSW": 8.0,
        "PWindW": 16.0,
        "Temperature": 42.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 169,
        "CWind": 14.0,
        "ID": 169,
        "PWindE": 12.0,
        "PWindN": 13.0,
        "PWindNE": 11.0,
        "PWindNW": 25.0,
        "PWindS": 6.0,
        "PWindSE": 11.0,
        "PWindSW": 9.0,
        "PWindW": 13.0,
        "Temperature": 41.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 170,
        "CWind": 9.0,
        "ID": 170,
        "PWindE": 6.0,
        "PWindN": 16.0,
        "PWindNE": 14.0,
        "PWindNW": 21.0,
        "PWindS": 8.0,
        "PWindSE": 6.0,
        "PWindSW": 13.0,
        "PWindW": 16.0,
        "Temperature": 40.0,
        "WindVelocity": 4.6
    },
    {
        "CITYID": 171,
        "CWind": 18.0,
        "ID": 171,
        "PWindE": 9.0,
        "PWindN": 16.0,
        "PWindNE": 11.0,
        "PWindNW": 20.0,
        "PWindS": 5.0,
        "PWindSE": 11.0,
        "PWindSW": 13.0,
        "PWindW": 15.0,
        "Temperature": 41.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 172,
        "CWind": 0.0,
        "ID": 172,
        "PWindE": 7.0,
        "PWindN": 18.0,
        "PWindNE": 6.0,
        "PWindNW": 26.0,
        "PWindS": 10.0,
        "PWindSE": 12.0,
        "PWindSW": 10.0,
        "PWindW": 11.0,
        "Temperature": 40.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 173,
        "CWind": 12.0,
        "ID": 173,
        "PWindE": 10.0,
        "PWindN": 11.0,
        "PWindNE": 24.0,
        "PWindNW": 17.0,
        "PWindS": 6.0,
        "PWindSE": 5.0,
        "PWindSW": 11.0,
        "PWindW": 16.0,
        "Temperature": 35.0,
        "WindVelocity": 3.2
    },
    {
        "CITYID": 174,
        "CWind": 13.0,
        "ID": 174,
        "PWindE": 10.0,
        "PWindN": 18.0,
        "PWindNE": 10.0,
        "PWindNW": 14.0,
        "PWindS": 10.0,
        "PWindSE": 12.0,
        "PWindSW": 12.0,
        "PWindW": 14.0,
        "Temperature": 37.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 175,
        "CWind": 4.0,
        "ID": 175,
        "PWindE": 3.0,
        "PWindN": 8.0,
        "PWindNE": 1.0,
        "PWindNW": 3.0,
        "PWindS": 15.0,
        "PWindSE": 63.0,
        "PWindSW": 5.0,
        "PWindW": 2.0,
        "Temperature": 34.0,
        "WindVelocity": 5.9
    },
    {
        "CITYID": 176,
        "CWind": 15.0,
        "ID": 176,
        "PWindE": 12.0,
        "PWindN": 6.0,
        "PWindNE": 6.0,
        "PWindNW": 5.0,
        "PWindS": 14.0,
        "PWindSE": 5.0,
        "PWindSW": 43.0,
        "PWindW": 9.0,
        "Temperature": 37.0,
        "WindVelocity": 7.4
    },
    {
        "CITYID": 177,
        "CWind": 20.0,
        "ID": 177,
        "PWindE": 1.0,
        "PWindN": 9.0,
        "PWindNE": 4.0,
        "PWindNW": 4.0,
        "PWindS": 53.0,
        "PWindSE": 10.0,
        "PWindSW": 17.0,
        "PWindW": 2.0,
        "Temperature": 37.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 178,
        "CWind": 33.0,
        "ID": 178,
        "PWindE": 49.0,
        "PWindN": 1.0,
        "PWindNE": 14.0,
        "PWindNW": 4.0,
        "PWindS": 2.0,
        "PWindSE": 9.0,
        "PWindSW": 3.0,
        "PWindW": 18.0,
        "Temperature": 38.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 179,
        "CWind": 0,
        "ID": 179,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 180,
        "CWind": 0,
        "ID": 180,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 37.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 181,
        "CWind": 0,
        "ID": 181,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 40.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 182,
        "CWind": 0,
        "ID": 182,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 37.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 183,
        "CWind": 0,
        "ID": 183,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 34.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 184,
        "CWind": 0,
        "ID": 184,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 185,
        "CWind": 20.0,
        "ID": 185,
        "PWindE": 6.0,
        "PWindN": 10.0,
        "PWindNE": 8.0,
        "PWindNW": 17.0,
        "PWindS": 12.0,
        "PWindSE": 11.0,
        "PWindSW": 17.0,
        "PWindW": 19.0,
        "Temperature": 38.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 186,
        "CWind": 7.0,
        "ID": 186,
        "PWindE": 11.0,
        "PWindN": 10.0,
        "PWindNE": 10.0,
        "PWindNW": 16.0,
        "PWindS": 10.0,
        "PWindSE": 10.0,
        "PWindSW": 15.0,
        "PWindW": 18.0,
        "Temperature": 36.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 187,
        "CWind": 0,
        "ID": 187,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 41.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 188,
        "CWind": 22.0,
        "ID": 188,
        "PWindE": 17.0,
        "PWindN": 14.0,
        "PWindNE": 22.0,
        "PWindNW": 14.0,
        "PWindS": 5.0,
        "PWindSE": 7.0,
        "PWindSW": 7.0,
        "PWindW": 14.0,
        "Temperature": 42.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 189,
        "CWind": 9.0,
        "ID": 189,
        "PWindE": 20.0,
        "PWindN": 13.0,
        "PWindNE": 13.0,
        "PWindNW": 11.0,
        "PWindS": 3.0,
        "PWindSE": 5.0,
        "PWindSW": 12.0,
        "PWindW": 23.0,
        "Temperature": 40.0,
        "WindVelocity": 8.3
    },
    {
        "CITYID": 190,
        "CWind": 9.0,
        "ID": 190,
        "PWindE": 10.0,
        "PWindN": 13.0,
        "PWindNE": 9.0,
        "PWindNW": 19.0,
        "PWindS": 8.0,
        "PWindSE": 9.0,
        "PWindSW": 12.0,
        "PWindW": 20.0,
        "Temperature": 40.0,
        "WindVelocity": 5.1
    },
    {
        "CITYID": 191,
        "CWind": 8.0,
        "ID": 191,
        "PWindE": 9.0,
        "PWindN": 16.0,
        "PWindNE": 14.0,
        "PWindNW": 14.0,
        "PWindS": 8.0,
        "PWindSE": 13.0,
        "PWindSW": 12.0,
        "PWindW": 14.0,
        "Temperature": 42.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 192,
        "CWind": 11.0,
        "ID": 192,
        "PWindE": 9.0,
        "PWindN": 12.0,
        "PWindNE": 11.0,
        "PWindNW": 28.0,
        "PWindS": 8.0,
        "PWindSE": 8.0,
        "PWindSW": 6.0,
        "PWindW": 18.0,
        "Temperature": 41.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 193,
        "CWind": 11.0,
        "ID": 193,
        "PWindE": 2.0,
        "PWindN": 13.0,
        "PWindNE": 4.0,
        "PWindNW": 11.0,
        "PWindS": 14.0,
        "PWindSE": 25.0,
        "PWindSW": 26.0,
        "PWindW": 5.0,
        "Temperature": 35.0,
        "WindVelocity": 5.4
    },
    {
        "CITYID": 194,
        "CWind": 12.0,
        "ID": 194,
        "PWindE": 4.0,
        "PWindN": 21.0,
        "PWindNE": 19.0,
        "PWindNW": 5.0,
        "PWindS": 30.0,
        "PWindSE": 2.0,
        "PWindSW": 15.0,
        "PWindW": 4.0,
        "Temperature": 35.0,
        "WindVelocity": 4.8
    },
    {
        "CITYID": 195,
        "CWind": 0,
        "ID": 195,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 36.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 196,
        "CWind": 13.0,
        "ID": 196,
        "PWindE": 11.0,
        "PWindN": 4.0,
        "PWindNE": 26.0,
        "PWindNW": 2.0,
        "PWindS": 23.0,
        "PWindSE": 9.0,
        "PWindSW": 21.0,
        "PWindW": 4.0,
        "Temperature": 30.0,
        "WindVelocity": 4.8
    },
    {
        "CITYID": 197,
        "CWind": 23.0,
        "ID": 197,
        "PWindE": 30.0,
        "PWindN": 12.0,
        "PWindNE": 4.0,
        "PWindNW": 17.0,
        "PWindS": 7.0,
        "PWindSE": 16.0,
        "PWindSW": 5.0,
        "PWindW": 9.0,
        "Temperature": 32.0,
        "WindVelocity": 5.6
    },
    {
        "CITYID": 198,
        "CWind": 2.0,
        "ID": 198,
        "PWindE": 26.0,
        "PWindN": 10.0,
        "PWindNE": 12.0,
        "PWindNW": 5.0,
        "PWindS": 21.0,
        "PWindSE": 10.0,
        "PWindSW": 13.0,
        "PWindW": 3.0,
        "Temperature": 31.0,
        "WindVelocity": 5.1
    },
    {
        "CITYID": 199,
        "CWind": 8.0,
        "ID": 199,
        "PWindE": 7.0,
        "PWindN": 5.0,
        "PWindNE": 16.0,
        "PWindNW": 9.0,
        "PWindS": 8.0,
        "PWindSE": 42.0,
        "PWindSW": 8.0,
        "PWindW": 5.0,
        "Temperature": 38.0,
        "WindVelocity": 6.9
    },
    {
        "CITYID": 200,
        "CWind": 20.0,
        "ID": 200,
        "PWindE": 5.0,
        "PWindN": 8.0,
        "PWindNE": 3.0,
        "PWindNW": 4.0,
        "PWindS": 50.0,
        "PWindSE": 21.0,
        "PWindSW": 6.0,
        "PWindW": 3.0,
        "Temperature": 36.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 201,
        "CWind": 13.0,
        "ID": 201,
        "PWindE": 11.0,
        "PWindN": 8.0,
        "PWindNE": 5.0,
        "PWindNW": 8.0,
        "PWindS": 13.0,
        "PWindSE": 24.0,
        "PWindSW": 27.0,
        "PWindW": 4.0,
        "Temperature": 30.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 202,
        "CWind": 12.0,
        "ID": 202,
        "PWindE": 21.0,
        "PWindN": 3.0,
        "PWindNE": 23.0,
        "PWindNW": 11.0,
        "PWindS": 20.0,
        "PWindSE": 15.0,
        "PWindSW": 5.0,
        "PWindW": 2.0,
        "Temperature": 31.0,
        "WindVelocity": 6.4
    },
    {
        "CITYID": 203,
        "CWind": 14.0,
        "ID": 203,
        "PWindE": 2.0,
        "PWindN": 36.0,
        "PWindNE": 3.0,
        "PWindNW": 4.0,
        "PWindS": 35.0,
        "PWindSE": 9.0,
        "PWindSW": 9.0,
        "PWindW": 2.0,
        "Temperature": 35.0,
        "WindVelocity": 5.0
    },
    {
        "CITYID": 204,
        "CWind": 29.0,
        "ID": 204,
        "PWindE": 6.0,
        "PWindN": 6.0,
        "PWindNE": 7.0,
        "PWindNW": 9.0,
        "PWindS": 23.0,
        "PWindSE": 22.0,
        "PWindSW": 12.0,
        "PWindW": 15.0,
        "Temperature": 38.0,
        "WindVelocity": 7.7
    },
    {
        "CITYID": 205,
        "CWind": 10.0,
        "ID": 205,
        "PWindE": 6.0,
        "PWindN": 15.0,
        "PWindNE": 12.0,
        "PWindNW": 17.0,
        "PWindS": 10.0,
        "PWindSE": 11.0,
        "PWindSW": 11.0,
        "PWindW": 18.0,
        "Temperature": 38.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 206,
        "CWind": 8.0,
        "ID": 206,
        "PWindE": 12.0,
        "PWindN": 12.0,
        "PWindNE": 12.0,
        "PWindNW": 19.0,
        "PWindS": 9.0,
        "PWindSE": 6.0,
        "PWindSW": 11.0,
        "PWindW": 19.0,
        "Temperature": 37.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 207,
        "CWind": 31.0,
        "ID": 207,
        "PWindE": 22.0,
        "PWindN": 6.0,
        "PWindNE": 6.0,
        "PWindNW": 21.0,
        "PWindS": 4.0,
        "PWindSE": 13.0,
        "PWindSW": 8.0,
        "PWindW": 20.0,
        "Temperature": 43.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 208,
        "CWind": 22.0,
        "ID": 208,
        "PWindE": 15.0,
        "PWindN": 7.0,
        "PWindNE": 9.0,
        "PWindNW": 20.0,
        "PWindS": 2.0,
        "PWindSE": 10.0,
        "PWindSW": 10.0,
        "PWindW": 27.0,
        "Temperature": 40.0,
        "WindVelocity": 5.8
    },
    {
        "CITYID": 209,
        "CWind": 8.0,
        "ID": 209,
        "PWindE": 9.0,
        "PWindN": 16.0,
        "PWindNE": 9.0,
        "PWindNW": 17.0,
        "PWindS": 9.0,
        "PWindSE": 13.0,
        "PWindSW": 12.0,
        "PWindW": 15.0,
        "Temperature": 41.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 210,
        "CWind": 12.0,
        "ID": 210,
        "PWindE": 5.0,
        "PWindN": 17.0,
        "PWindNE": 15.0,
        "PWindNW": 18.0,
        "PWindS": 9.0,
        "PWindSE": 7.0,
        "PWindSW": 14.0,
        "PWindW": 15.0,
        "Temperature": 39.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 211,
        "CWind": 10.0,
        "ID": 211,
        "PWindE": 11.0,
        "PWindN": 16.0,
        "PWindNE": 13.0,
        "PWindNW": 18.0,
        "PWindS": 10.0,
        "PWindSE": 10.0,
        "PWindSW": 8.0,
        "PWindW": 14.0,
        "Temperature": 39.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 212,
        "CWind": 15.0,
        "ID": 212,
        "PWindE": 11.0,
        "PWindN": 19.0,
        "PWindNE": 11.0,
        "PWindNW": 19.0,
        "PWindS": 5.0,
        "PWindSE": 14.0,
        "PWindSW": 9.0,
        "PWindW": 12.0,
        "Temperature": 35.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 213,
        "CWind": 24.0,
        "ID": 213,
        "PWindE": 10.0,
        "PWindN": 10.0,
        "PWindNE": 13.0,
        "PWindNW": 12.0,
        "PWindS": 15.0,
        "PWindSE": 14.0,
        "PWindSW": 13.0,
        "PWindW": 13.0,
        "Temperature": 35.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 214,
        "CWind": 9.0,
        "ID": 214,
        "PWindE": 11.0,
        "PWindN": 15.0,
        "PWindNE": 13.0,
        "PWindNW": 14.0,
        "PWindS": 9.0,
        "PWindSE": 10.0,
        "PWindSW": 14.0,
        "PWindW": 14.0,
        "Temperature": 37.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 215,
        "CWind": 12.0,
        "ID": 215,
        "PWindE": 10.0,
        "PWindN": 15.0,
        "PWindNE": 17.0,
        "PWindNW": 7.0,
        "PWindS": 28.0,
        "PWindSE": 8.0,
        "PWindSW": 9.0,
        "PWindW": 6.0,
        "Temperature": 36.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 216,
        "CWind": 18.0,
        "ID": 216,
        "PWindE": 9.0,
        "PWindN": 11.0,
        "PWindNE": 13.0,
        "PWindNW": 11.0,
        "PWindS": 16.0,
        "PWindSE": 13.0,
        "PWindSW": 14.0,
        "PWindW": 13.0,
        "Temperature": 36.0,
        "WindVelocity": 9.1
    },
    {
        "CITYID": 217,
        "CWind": 22.0,
        "ID": 217,
        "PWindE": 23.0,
        "PWindN": 22.0,
        "PWindNE": 17.0,
        "PWindNW": 18.0,
        "PWindS": 2.0,
        "PWindSE": 4.0,
        "PWindSW": 6.0,
        "PWindW": 8.0,
        "Temperature": 41.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 218,
        "CWind": 10.0,
        "ID": 218,
        "PWindE": 12.0,
        "PWindN": 12.0,
        "PWindNE": 10.0,
        "PWindNW": 19.0,
        "PWindS": 5.0,
        "PWindSE": 8.0,
        "PWindSW": 12.0,
        "PWindW": 22.0,
        "Temperature": 39.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 219,
        "CWind": 12.0,
        "ID": 219,
        "PWindE": 10.0,
        "PWindN": 20.0,
        "PWindNE": 11.0,
        "PWindNW": 15.0,
        "PWindS": 12.0,
        "PWindSE": 11.0,
        "PWindSW": 11.0,
        "PWindW": 10.0,
        "Temperature": 37.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 220,
        "CWind": 9.0,
        "ID": 220,
        "PWindE": 5.0,
        "PWindN": 20.0,
        "PWindNE": 13.0,
        "PWindNW": 19.0,
        "PWindS": 6.0,
        "PWindSE": 13.0,
        "PWindSW": 9.0,
        "PWindW": 15.0,
        "Temperature": 40.0,
        "WindVelocity": 4.8
    },
    {
        "CITYID": 221,
        "CWind": 14.0,
        "ID": 221,
        "PWindE": 7.0,
        "PWindN": 19.0,
        "PWindNE": 10.0,
        "PWindNW": 24.0,
        "PWindS": 6.0,
        "PWindSE": 8.0,
        "PWindSW": 12.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 222,
        "CWind": 10.0,
        "ID": 222,
        "PWindE": 7.0,
        "PWindN": 25.0,
        "PWindNE": 24.0,
        "PWindNW": 13.0,
        "PWindS": 8.0,
        "PWindSE": 9.0,
        "PWindSW": 7.0,
        "PWindW": 7.0,
        "Temperature": 34.0,
        "WindVelocity": 5.9
    },
    {
        "CITYID": 223,
        "CWind": 8.0,
        "ID": 223,
        "PWindE": 9.0,
        "PWindN": 20.0,
        "PWindNE": 15.0,
        "PWindNW": 13.0,
        "PWindS": 9.0,
        "PWindSE": 9.0,
        "PWindSW": 12.0,
        "PWindW": 13.0,
        "Temperature": 36.0,
        "WindVelocity": 4.4
    },
    {
        "CITYID": 224,
        "CWind": 0,
        "ID": 224,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 36.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 225,
        "CWind": 6.0,
        "ID": 225,
        "PWindE": 10.0,
        "PWindN": 30.0,
        "PWindNE": 20.0,
        "PWindNW": 12.0,
        "PWindS": 3.0,
        "PWindSE": 10.0,
        "PWindSW": 5.0,
        "PWindW": 10.0,
        "Temperature": 35.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 226,
        "CWind": 20.0,
        "ID": 226,
        "PWindE": 5.0,
        "PWindN": 14.0,
        "PWindNE": 9.0,
        "PWindNW": 14.0,
        "PWindS": 13.0,
        "PWindSE": 7.0,
        "PWindSW": 21.0,
        "PWindW": 17.0,
        "Temperature": 35.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 227,
        "CWind": 10.0,
        "ID": 227,
        "PWindE": 15.0,
        "PWindN": 22.0,
        "PWindNE": 13.0,
        "PWindNW": 12.0,
        "PWindS": 7.0,
        "PWindSE": 8.0,
        "PWindSW": 10.0,
        "PWindW": 13.0,
        "Temperature": 35.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 228,
        "CWind": 17.0,
        "ID": 228,
        "PWindE": 8.0,
        "PWindN": 26.0,
        "PWindNE": 8.0,
        "PWindNW": 17.0,
        "PWindS": 11.0,
        "PWindSE": 9.0,
        "PWindSW": 11.0,
        "PWindW": 10.0,
        "Temperature": 36.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 229,
        "CWind": 10.0,
        "ID": 229,
        "PWindE": 8.0,
        "PWindN": 14.0,
        "PWindNE": 36.0,
        "PWindNW": 4.0,
        "PWindS": 9.0,
        "PWindSE": 4.0,
        "PWindSW": 18.0,
        "PWindW": 7.0,
        "Temperature": 35.0,
        "WindVelocity": 6.6
    },
    {
        "CITYID": 230,
        "CWind": 0,
        "ID": 230,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 30.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 231,
        "CWind": 0,
        "ID": 231,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 35.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 232,
        "CWind": 7.0,
        "ID": 232,
        "PWindE": 9.0,
        "PWindN": 13.0,
        "PWindNE": 33.0,
        "PWindNW": 15.0,
        "PWindS": 7.0,
        "PWindSE": 6.0,
        "PWindSW": 8.0,
        "PWindW": 9.0,
        "Temperature": 33.0,
        "WindVelocity": 6.5
    },
    {
        "CITYID": 233,
        "CWind": 14.0,
        "ID": 233,
        "PWindE": 8.0,
        "PWindN": 24.0,
        "PWindNE": 15.0,
        "PWindNW": 21.0,
        "PWindS": 7.0,
        "PWindSE": 9.0,
        "PWindSW": 8.0,
        "PWindW": 8.0,
        "Temperature": 36.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 234,
        "CWind": 0,
        "ID": 234,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 34.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 235,
        "CWind": 17.0,
        "ID": 235,
        "PWindE": 11.0,
        "PWindN": 12.0,
        "PWindNE": 16.0,
        "PWindNW": 17.0,
        "PWindS": 5.0,
        "PWindSE": 10.0,
        "PWindSW": 10.0,
        "PWindW": 19.0,
        "Temperature": 38.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 236,
        "CWind": 18.0,
        "ID": 236,
        "PWindE": 9.0,
        "PWindN": 13.0,
        "PWindNE": 16.0,
        "PWindNW": 21.0,
        "PWindS": 7.0,
        "PWindSE": 6.0,
        "PWindSW": 16.0,
        "PWindW": 12.0,
        "Temperature": 37.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 237,
        "CWind": 0,
        "ID": 237,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 38.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 238,
        "CWind": 0,
        "ID": 238,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 239,
        "CWind": 0,
        "ID": 239,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 33.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 240,
        "CWind": 0,
        "ID": 240,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 30.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 241,
        "CWind": 0,
        "ID": 241,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 40.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 242,
        "CWind": 0,
        "ID": 242,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 32.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 243,
        "CWind": 0,
        "ID": 243,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 32.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 244,
        "CWind": 10.0,
        "ID": 244,
        "PWindE": 46.0,
        "PWindN": 8.0,
        "PWindNE": 20.0,
        "PWindNW": 3.0,
        "PWindS": 1.0,
        "PWindSE": 15.0,
        "PWindSW": 2.0,
        "PWindW": 5.0,
        "Temperature": 35.0,
        "WindVelocity": 5.3
    },
    {
        "CITYID": 245,
        "CWind": 0,
        "ID": 245,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 36.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 246,
        "CWind": 17.0,
        "ID": 246,
        "PWindE": 5.0,
        "PWindN": 31.0,
        "PWindNE": 14.0,
        "PWindNW": 4.0,
        "PWindS": 35.0,
        "PWindSE": 9.0,
        "PWindSW": 2.0,
        "PWindW": 0.0,
        "Temperature": 36.0,
        "WindVelocity": 5.5
    },
    {
        "CITYID": 247,
        "CWind": 0,
        "ID": 247,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 37.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 248,
        "CWind": 30.0,
        "ID": 248,
        "PWindE": 7.0,
        "PWindN": 7.0,
        "PWindNE": 3.0,
        "PWindNW": 9.0,
        "PWindS": 12.0,
        "PWindSE": 47.0,
        "PWindSW": 7.0,
        "PWindW": 8.0,
        "Temperature": 38.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 249,
        "CWind": 36.0,
        "ID": 249,
        "PWindE": 10.0,
        "PWindN": 10.0,
        "PWindNE": 22.0,
        "PWindNW": 5.0,
        "PWindS": 9.0,
        "PWindSE": 11.0,
        "PWindSW": 19.0,
        "PWindW": 14.0,
        "Temperature": 39.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 250,
        "CWind": 9.0,
        "ID": 250,
        "PWindE": 17.0,
        "PWindN": 3.0,
        "PWindNE": 25.0,
        "PWindNW": 4.0,
        "PWindS": 4.0,
        "PWindSE": 5.0,
        "PWindSW": 35.0,
        "PWindW": 7.0,
        "Temperature": 40.0,
        "WindVelocity": 6.0
    },
    {
        "CITYID": 251,
        "CWind": 23.0,
        "ID": 251,
        "PWindE": 21.0,
        "PWindN": 6.0,
        "PWindNE": 45.0,
        "PWindNW": 1.0,
        "PWindS": 0.0,
        "PWindSE": 1.0,
        "PWindSW": 13.0,
        "PWindW": 13.0,
        "Temperature": 36.0,
        "WindVelocity": 5.1
    },
    {
        "CITYID": 252,
        "CWind": 21.0,
        "ID": 252,
        "PWindE": 19.0,
        "PWindN": 11.0,
        "PWindNE": 21.0,
        "PWindNW": 16.0,
        "PWindS": 8.0,
        "PWindSE": 9.0,
        "PWindSW": 11.0,
        "PWindW": 5.0,
        "Temperature": 40.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 253,
        "CWind": 0,
        "ID": 253,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 38.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 254,
        "CWind": 2.0,
        "ID": 254,
        "PWindE": 7.0,
        "PWindN": 20.0,
        "PWindNE": 12.0,
        "PWindNW": 25.0,
        "PWindS": 7.0,
        "PWindSE": 5.0,
        "PWindSW": 12.0,
        "PWindW": 12.0,
        "Temperature": 40.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 255,
        "CWind": 43.0,
        "ID": 255,
        "PWindE": 27.0,
        "PWindN": 3.0,
        "PWindNE": 5.0,
        "PWindNW": 18.0,
        "PWindS": 7.0,
        "PWindSE": 7.0,
        "PWindSW": 13.0,
        "PWindW": 20.0,
        "Temperature": 41.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 256,
        "CWind": 0,
        "ID": 256,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 40.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 257,
        "CWind": 0,
        "ID": 257,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 258,
        "CWind": 0,
        "ID": 258,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 41.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 259,
        "CWind": 0,
        "ID": 259,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 40.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 260,
        "CWind": 0,
        "ID": 260,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 37.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 261,
        "CWind": 0,
        "ID": 261,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 262,
        "CWind": 0,
        "ID": 262,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 36.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 263,
        "CWind": 0,
        "ID": 263,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 37.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 264,
        "CWind": 0,
        "ID": 264,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 37.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 265,
        "CWind": 0,
        "ID": 265,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 35.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 266,
        "CWind": 53.0,
        "ID": 266,
        "PWindE": 10.0,
        "PWindN": 22.0,
        "PWindNE": 12.0,
        "PWindNW": 21.0,
        "PWindS": 10.0,
        "PWindSE": 6.0,
        "PWindSW": 11.0,
        "PWindW": 8.0,
        "Temperature": 40.0,
        "WindVelocity": 3.3
    },
    {
        "CITYID": 267,
        "CWind": 39.0,
        "ID": 267,
        "PWindE": 12.0,
        "PWindN": 11.0,
        "PWindNE": 10.0,
        "PWindNW": 30.0,
        "PWindS": 10.0,
        "PWindSE": 13.0,
        "PWindSW": 6.0,
        "PWindW": 8.0,
        "Temperature": 38.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 268,
        "CWind": 49.0,
        "ID": 268,
        "PWindE": 19.0,
        "PWindN": 11.0,
        "PWindNE": 19.0,
        "PWindNW": 11.0,
        "PWindS": 8.0,
        "PWindSE": 10.0,
        "PWindSW": 12.0,
        "PWindW": 10.0,
        "Temperature": 42.0,
        "WindVelocity": 4.5
    },
    {
        "CITYID": 269,
        "CWind": 47.0,
        "ID": 269,
        "PWindE": 15.0,
        "PWindN": 9.0,
        "PWindNE": 17.0,
        "PWindNW": 17.0,
        "PWindS": 9.0,
        "PWindSE": 9.0,
        "PWindSW": 11.0,
        "PWindW": 13.0,
        "Temperature": 40.0,
        "WindVelocity": 2.8
    },
    {
        "CITYID": 270,
        "CWind": 42.0,
        "ID": 270,
        "PWindE": 3.0,
        "PWindN": 15.0,
        "PWindNE": 4.0,
        "PWindNW": 12.0,
        "PWindS": 14.0,
        "PWindSE": 13.0,
        "PWindSW": 16.0,
        "PWindW": 23.0,
        "Temperature": 41.0,
        "WindVelocity": 3.1
    },
    {
        "CITYID": 271,
        "CWind": 0,
        "ID": 271,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 40.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 272,
        "CWind": 12.0,
        "ID": 272,
        "PWindE": 8.0,
        "PWindN": 14.0,
        "PWindNE": 10.0,
        "PWindNW": 19.0,
        "PWindS": 7.0,
        "PWindSE": 10.0,
        "PWindSW": 15.0,
        "PWindW": 17.0,
        "Temperature": 40.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 273,
        "CWind": 0,
        "ID": 273,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 38.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 274,
        "CWind": 0,
        "ID": 274,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 35.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 275,
        "CWind": 0,
        "ID": 275,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 32.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 276,
        "CWind": 0,
        "ID": 276,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 38.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 277,
        "CWind": 0,
        "ID": 277,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 278,
        "CWind": 0,
        "ID": 278,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 35.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 279,
        "CWind": 0,
        "ID": 279,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 36.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 280,
        "CWind": 0,
        "ID": 280,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 35.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 281,
        "CWind": 0,
        "ID": 281,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 38.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 282,
        "CWind": 0,
        "ID": 282,
        "PWindE": 0,
        "PWindN": 0,
        "PWindNE": 0,
        "PWindNW": 0,
        "PWindS": 0,
        "PWindSE": 0,
        "PWindSW": 0,
        "PWindW": 0,
        "Temperature": 39.0,
        "WindVelocity": 0
    },
    {
        "CITYID": 283,
        "CWind": 21.0,
        "ID": 283,
        "PWindE": 6.0,
        "PWindN": 13.0,
        "PWindNE": 15.0,
        "PWindNW": 10.0,
        "PWindS": 14.0,
        "PWindSE": 6.0,
        "PWindSW": 22.0,
        "PWindW": 14.0,
        "Temperature": 35.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 284,
        "CWind": 26.0,
        "ID": 284,
        "PWindE": 14.0,
        "PWindN": 11.0,
        "PWindNE": 13.0,
        "PWindNW": 14.0,
        "PWindS": 5.0,
        "PWindSE": 8.0,
        "PWindSW": 15.0,
        "PWindW": 20.0,
        "Temperature": 39.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 285,
        "CWind": 37.0,
        "ID": 285,
        "PWindE": 3.0,
        "PWindN": 29.0,
        "PWindNE": 33.0,
        "PWindNW": 5.0,
        "PWindS": 6.0,
        "PWindSE": 1.0,
        "PWindSW": 19.0,
        "PWindW": 4.0,
        "Temperature": 37.0,
        "WindVelocity": 3.7
    },
    {
        "CITYID": 286,
        "CWind": 14.0,
        "ID": 286,
        "PWindE": 14.0,
        "PWindN": 19.0,
        "PWindNE": 14.0,
        "PWindNW": 14.0,
        "PWindS": 6.0,
        "PWindSE": 6.0,
        "PWindSW": 13.0,
        "PWindW": 14.0,
        "Temperature": 37.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 287,
        "CWind": 42.0,
        "ID": 287,
        "PWindE": 5.0,
        "PWindN": 39.0,
        "PWindNE": 7.0,
        "PWindNW": 10.0,
        "PWindS": 17.0,
        "PWindSE": 7.0,
        "PWindSW": 8.0,
        "PWindW": 7.0,
        "Temperature": 37.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 288,
        "CWind": 14.0,
        "ID": 288,
        "PWindE": 3.0,
        "PWindN": 44.0,
        "PWindNE": 13.0,
        "PWindNW": 10.0,
        "PWindS": 12.0,
        "PWindSE": 5.0,
        "PWindSW": 9.0,
        "PWindW": 4.0,
        "Temperature": 37.0,
        "WindVelocity": 5.9
    },
    {
        "CITYID": 289,
        "CWind": 7.0,
        "ID": 289,
        "PWindE": 3.0,
        "PWindN": 39.0,
        "PWindNE": 13.0,
        "PWindNW": 10.0,
        "PWindS": 7.0,
        "PWindSE": 15.0,
        "PWindSW": 6.0,
        "PWindW": 7.0,
        "Temperature": 35.0,
        "WindVelocity": 6.6
    },
    {
        "CITYID": 290,
        "CWind": 14.0,
        "ID": 290,
        "PWindE": 5.0,
        "PWindN": 33.0,
        "PWindNE": 5.0,
        "PWindNW": 24.0,
        "PWindS": 14.0,
        "PWindSE": 16.0,
        "PWindSW": 1.0,
        "PWindW": 2.0,
        "Temperature": 37.0,
        "WindVelocity": 5.4
    },
    {
        "CITYID": 291,
        "CWind": 33.0,
        "ID": 291,
        "PWindE": 26.0,
        "PWindN": 4.0,
        "PWindNE": 15.0,
        "PWindNW": 3.0,
        "PWindS": 3.0,
        "PWindSE": 5.0,
        "PWindSW": 16.0,
        "PWindW": 28.0,
        "Temperature": 37.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 292,
        "CWind": 15.0,
        "ID": 292,
        "PWindE": 4.0,
        "PWindN": 13.0,
        "PWindNE": 52.0,
        "PWindNW": 5.0,
        "PWindS": 5.0,
        "PWindSE": 1.0,
        "PWindSW": 15.0,
        "PWindW": 5.0,
        "Temperature": 34.0,
        "WindVelocity": 6.7
    },
    {
        "CITYID": 293,
        "CWind": 56.0,
        "ID": 293,
        "PWindE": 13.0,
        "PWindN": 33.0,
        "PWindNE": 8.0,
        "PWindNW": 4.0,
        "PWindS": 21.0,
        "PWindSE": 6.0,
        "PWindSW": 7.0,
        "PWindW": 8.0,
        "Temperature": 38.0,
        "WindVelocity": 5.0
    },
    {
        "CITYID": 294,
        "CWind": 22.0,
        "ID": 294,
        "PWindE": 14.0,
        "PWindN": 16.0,
        "PWindNE": 22.0,
        "PWindNW": 11.0,
        "PWindS": 5.0,
        "PWindSE": 5.0,
        "PWindSW": 17.0,
        "PWindW": 10.0,
        "Temperature": 37.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 295,
        "CWind": 32.0,
        "ID": 295,
        "PWindE": 28.0,
        "PWindN": 5.0,
        "PWindNE": 7.0,
        "PWindNW": 23.0,
        "PWindS": 4.0,
        "PWindSE": 13.0,
        "PWindSW": 3.0,
        "PWindW": 17.0,
        "Temperature": 35.0,
        "WindVelocity": 4.0
    },
    {
        "CITYID": 296,
        "CWind": 29.0,
        "ID": 296,
        "PWindE": 14.0,
        "PWindN": 13.0,
        "PWindNE": 32.0,
        "PWindNW": 10.0,
        "PWindS": 2.0,
        "PWindSE": 3.0,
        "PWindSW": 7.0,
        "PWindW": 19.0,
        "Temperature": 38.0,
        "WindVelocity": 3.7
    },
    {
        "CITYID": 297,
        "CWind": 22.0,
        "ID": 297,
        "PWindE": 16.0,
        "PWindN": 23.0,
        "PWindNE": 23.0,
        "PWindNW": 10.0,
        "PWindS": 7.0,
        "PWindSE": 8.0,
        "PWindSW": 5.0,
        "PWindW": 8.0,
        "Temperature": 36.0,
        "WindVelocity": 3.9
    },
    {
        "CITYID": 298,
        "CWind": 41.0,
        "ID": 298,
        "PWindE": 2.0,
        "PWindN": 26.0,
        "PWindNE": 8.0,
        "PWindNW": 7.0,
        "PWindS": 32.0,
        "PWindSE": 11.0,
        "PWindSW": 8.0,
        "PWindW": 6.0,
        "Temperature": 36.0,
        "WindVelocity": 2.8
    },
    {
        "CITYID": 299,
        "CWind": 16.0,
        "ID": 299,
        "PWindE": 20.0,
        "PWindN": 4.0,
        "PWindNE": 8.0,
        "PWindNW": 42.0,
        "PWindS": 4.0,
        "PWindSE": 9.0,
        "PWindSW": 3.0,
        "PWindW": 10.0,
        "Temperature": 36.0,
        "WindVelocity": 7.3
    },
    {
        "CITYID": 300,
        "CWind": 19.0,
        "ID": 300,
        "PWindE": 11.0,
        "PWindN": 31.0,
        "PWindNE": 22.0,
        "PWindNW": 11.0,
        "PWindS": 8.0,
        "PWindSE": 5.0,
        "PWindSW": 5.0,
        "PWindW": 7.0,
        "Temperature": 37.0,
        "WindVelocity": 3.8
    },
    {
        "CITYID": 301,
        "CWind": 31.0,
        "ID": 301,
        "PWindE": 14.0,
        "PWindN": 22.0,
        "PWindNE": 13.0,
        "PWindNW": 13.0,
        "PWindS": 8.0,
        "PWindSE": 5.0,
        "PWindSW": 13.0,
        "PWindW": 12.0,
        "Temperature": 38.0,
        "WindVelocity": 3.5
    },
    {
        "CITYID": 302,
        "CWind": 21.0,
        "ID": 302,
        "PWindE": 5.0,
        "PWindN": 25.0,
        "PWindNE": 20.0,
        "PWindNW": 18.0,
        "PWindS": 11.0,
        "PWindSE": 5.0,
        "PWindSW": 9.0,
        "PWindW": 7.0,
        "Temperature": 36.0,
        "WindVelocity": 3.4
    },
    {
        "CITYID": 303,
        "CWind": 32.0,
        "ID": 303,
        "PWindE": 1.0,
        "PWindN": 32.0,
        "PWindNE": 5.0,
        "PWindNW": 14.0,
        "PWindS": 33.0,
        "PWindSE": 10.0,
        "PWindSW": 3.0,
        "PWindW": 2.0,
        "Temperature": 37.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 304,
        "CWind": 13.0,
        "ID": 304,
        "PWindE": 12.0,
        "PWindN": 18.0,
        "PWindNE": 17.0,
        "PWindNW": 9.0,
        "PWindS": 13.0,
        "PWindSE": 8.0,
        "PWindSW": 12.0,
        "PWindW": 11.0,
        "Temperature": 36.0,
        "WindVelocity": 2.7
    },
    {
        "CITYID": 305,
        "CWind": 32.0,
        "ID": 305,
        "PWindE": 8.0,
        "PWindN": 10.0,
        "PWindNE": 14.0,
        "PWindNW": 14.0,
        "PWindS": 12.0,
        "PWindSE": 16.0,
        "PWindSW": 15.0,
        "PWindW": 11.0,
        "Temperature": 36.0,
        "WindVelocity": 4.3
    },
    {
        "CITYID": 306,
        "CWind": 28.0,
        "ID": 306,
        "PWindE": 3.0,
        "PWindN": 19.0,
        "PWindNE": 3.0,
        "PWindNW": 29.0,
        "PWindS": 18.0,
        "PWindSE": 9.0,
        "PWindSW": 14.0,
        "PWindW": 5.0,
        "Temperature": 38.0,
        "WindVelocity": 4.7
    },
    {
        "CITYID": 307,
        "CWind": 49.0,
        "ID": 307,
        "PWindE": 4.0,
        "PWindN": 10.0,
        "PWindNE": 11.0,
        "PWindNW": 19.0,
        "PWindS": 21.0,
        "PWindSE": 8.0,
        "PWindSW": 16.0,
        "PWindW": 11.0,
        "Temperature": 35.0,
        "WindVelocity": 2.9
    },
    {
        "CITYID": 308,
        "CWind": 42.0,
        "ID": 308,
        "PWindE": 16.0,
        "PWindN": 20.0,
        "PWindNE": 14.0,
        "PWindNW": 12.0,
        "PWindS": 11.0,
        "PWindSE": 6.0,
        "PWindSW": 8.0,
        "PWindW": 13.0,
        "Temperature": 36.0,
        "WindVelocity": 3.6
    },
    {
        "CITYID": 309,
        "CWind": 16.0,
        "ID": 309,
        "PWindE": 11.0,
        "PWindN": 11.0,
        "PWindNE": 17.0,
        "PWindNW": 18.0,
        "PWindS": 10.0,
        "PWindSE": 13.0,
        "PWindSW": 6.0,
        "PWindW": 14.0,
        "Temperature": 38.0,
        "WindVelocity": 4.1
    },
    {
        "CITYID": 310,
        "CWind": 8.0,
        "ID": 310,
        "PWindE": 9.0,
        "PWindN": 14.0,
        "PWindNE": 15.0,
        "PWindNW": 20.0,
        "PWindS": 8.0,
        "PWindSE": 7.0,
        "PWindSW": 11.0,
        "PWindW": 16.0,
        "Temperature": 37.0,
        "WindVelocity": 4.2
    },
    {
        "CITYID": 311,
        "CWind": 4.0,
        "ID": 311,
        "PWindE": 4.0,
        "PWindN": 21.0,
        "PWindNE": 11.0,
        "PWindNW": 23.0,
        "PWindS": 11.0,
        "PWindSE": 6.0,
        "PWindSW": 8.0,
        "PWindW": 16.0,
        "Temperature": 38.0,
        "WindVelocity": 6.5
    },
    {
        "CITYID": 312,
        "CWind": 10.0,
        "ID": 312,
        "PWindE": 22.0,
        "PWindN": 6.0,
        "PWindNE": 16.0,
        "PWindNW": 18.0,
        "PWindS": 9.0,
        "PWindSE": 2.0,
        "PWindSW": 7.0,
        "PWindW": 20.0,
        "Temperature": 38.0,
        "WindVelocity": 6.1
    },
    {
        "CITYID": 313,
        "CWind": 13.0,
        "ID": 313,
        "PWindE": 17.0,
        "PWindN": 6.0,
        "PWindNE": 12.0,
        "PWindNW": 8.0,
        "PWindS": 6.0,
        "PWindSE": 20.0,
        "PWindSW": 14.0,
        "PWindW": 17.0,
        "Temperature": 40.0,
        "WindVelocity": 5.1
    },
    {
        "CITYID": 314,
        "CWind": 13.0,
        "ID": 314,
        "PWindE": 5.0,
        "PWindN": 9.0,
        "PWindNE": 13.0,
        "PWindNW": 26.0,
        "PWindS": 9.0,
        "PWindSE": 8.0,
        "PWindSW": 8.0,
        "PWindW": 22.0,
        "Temperature": 39.0,
        "WindVelocity": 5.0
    },
    {
        "CITYID": 315,
        "CWind": 12.0,
        "ID": 315,
        "PWindE": 14.0,
        "PWindN": 29.0,
        "PWindNE": 5.0,
        "PWindNW": 22.0,
        "PWindS": 14.0,
        "PWindSE": 10.0,
        "PWindSW": 2.0,
        "PWindW": 4.0,
        "Temperature": 39.0,
        "WindVelocity": 3.6
    }
]


class _ClimateDB:
    __table_regions__ = "regions"
    __table_cities__ = "cities"
    __table_climate__ = "climate"

    def __init__(self, connect: Connection):
        self.connect = connect

    async def create_table_regions(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS regions(
                    id SERIAL PRIMARY KEY,
                    region VARCHAR(50) NOT NULL UNIQUE
                );
            ''')
            log.info("Created table '%s'", self.__table_regions__)

    async def create_table_cities(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS cities(
                    id SERIAL PRIMARY KEY,
                    regionid INTEGER references regions(id),
                    city VARCHAR(30) NOT NULL UNIQUE,
                    longitude REAL NOT NULL,
                    latitude REAL NOT NULL
                );
            ''')
            log.info("Created table '%s'", self.__table_cities__)

    async def create_table_climate(self) -> None:
        async with self.connect.transaction():
            await self.connect.execute('''
                CREATE TABLE IF NOT EXISTS climate(
                    id SERIAL PRIMARY KEY,
                    cityid INTEGER references cities(id) NOT NULL UNIQUE,
                    CWind REAL,
                    PWindE REAL,
                    PWindN REAL,
                    PWindNE REAL,
                    PWindNW REAL,
                    PWindS REAL,
                    PWindSE REAL,
                    PWindSW REAL,
                    PWindW REAL,
                    Temperature REAL,
                    WindVelocity REAL
                );
            ''')
            log.info("Created table '%s'", self.__table_climate__)

    async def add_regions(self) -> None:
        async with self.connect.transaction():
            for region in regions:
                await self.connect.execute('''
                    INSERT INTO regions(region)
                    VALUES($1) ON CONFLICT DO NOTHING;
                ''', region['REGION']
                )
            log.info("Region added. db='%s'", self.__table_regions__)

    async def add_cities(self) -> None:
        async with self.connect.transaction():
            for city in cities:
                await self.connect.execute('''
                    INSERT INTO cities(regionid, city, longitude, latitude)
                    VALUES($1, $2, $3, $4) ON CONFLICT DO NOTHING;
                ''', city['REGIONID'], city['CITY'], city['LONGITUDE'], city['LATITUDE']
                )
                # log.info(
                #     "City added. db='%s', region=%s, city=%s, longitude=%d, latitude=%d",
                #     self.__table_cities__, city['REGIONID'], city['CITY'], city['LONGITUDE'], city['LATITUDE']
                # )
            log.info("City added. db='%s'", self.__table_cities__)

    async def add_climates(self) -> None:
        async with self.connect.transaction():
            for climate_data in climates:
                await self.connect.execute('''
                    INSERT INTO climate(CITYID, CWind, PWindE, PWindN,PWindNE,PWindNW,
                    PWindS,PWindSE,PWindSW,PWindW,Temperature,WindVelocity)
                    VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12) ON CONFLICT DO NOTHING;
                ''', climate_data['CITYID'], climate_data['CWind'], climate_data['PWindE'], climate_data['PWindN'],
                    climate_data['PWindNE'], climate_data['PWindNW'], climate_data[
                        'PWindS'], climate_data['PWindSE'], climate_data['PWindSW'],
                    climate_data['PWindW'], climate_data['Temperature'], climate_data['WindVelocity']
                )
                # log.info(
                #     "City added. db='%s', cityid=%s, CWind=%d, PWindE=%d, PWindN=%d, PWindNE=%d, PWindNW=%d, PWindS=%d, PWindSE=%d, PWindSW=%d, PWindW=%d, Temperature=%d, WindVelocity=%d",
                #     self.__table_climate__, climate_data['CITYID'], climate_data[
                #         'CWind'], climate_data['PWindE'], climate_data['PWindN'],
                #     climate_data['PWindNE'], climate_data['PWindNW'], climate_data[
                #         'PWindS'], climate_data['PWindSE'], climate_data['PWindSW'],
                #     climate_data['PWindW'], climate_data['Temperature'], climate_data['WindVelocity']
                # )
            log.info("City added. db='%s'", self.__table_climate__)

    async def get_climate_region_list(self) -> dict:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT id, region
                FROM regions;
            ''')
            data = await cursor.fetch(100)
            # log.info(data)
            return data
            # return ClimateRegion(data) if data else None

    async def get_climate_cities_list(self, *, region: str) -> dict:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT cities.id, cities.city
                FROM cities
                JOIN regions ON cities.regionid = regions.id
                WHERE regions.region=$1;
            ''', region
                                               )
            data = await cursor.fetch(100)
            # log.info(data)
            return data

    async def get_climate_cities(self) -> dict:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT cities.id, cities.city
                FROM cities
                JOIN regions ON cities.regionid = regions.id;
            ''')
            data = await cursor.fetch(320)
            # log.info(data)
            return data

    async def get_climate_record(self, *, city: str) -> ClimateModel | None:
        async with self.connect.transaction():
            cursor = await self.connect.cursor('''
                SELECT regions.region, cities.city, climate.cwind, climate.pwinde, climate.pwindn, climate.pwindne, climate.pwindnw, climate.pwinds, climate.pwindse, climate.pwindsw,climate.pwindw, climate.temperature, climate.windvelocity
                FROM climate
                JOIN cities ON climate.cityid = cities.id
                JOIN regions ON regions.id = cities.regionid
                WHERE cities.city=$1;
            ''', city
                                               )
            data = await cursor.fetchrow()
            return ClimateModel(**data) if data else None
