"""ISO 3166-2 RU standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:RU
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "RU-AD": (
            Entity("Adygeja", "RU-AD", "REPUBLIC", "ru", ""),
            Entity("Adygeya", "RU-AD", "REPUBLIC", "ru", ""),
        ),
        "RU-AL": (
            Entity("Altaj", "RU-AL", "REPUBLIC", "ru", ""),
            Entity("Altay", "RU-AL", "REPUBLIC", "ru", ""),
        ),
        "RU-ALT": (
            Entity("Altajskij kraj", "RU-ALT", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Altayskiy kray", "RU-ALT", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-AMU": (
            Entity("Amurskaja oblast'", "RU-AMU", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Amurskaya oblast'", "RU-AMU", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-ARK": (
            Entity("Arhangel'skaja oblast'", "RU-ARK", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Arkhangel'skaya oblast'", "RU-ARK", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-AST": (
            Entity("Astrahanskaja oblast'", "RU-AST", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Astrakhanskaya oblast'", "RU-AST", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-BA": (
            Entity("Bashkortostan", "RU-BA", "REPUBLIC", "ru", ""),
            Entity("Baškortostan", "RU-BA", "REPUBLIC", "ru", ""),
        ),
        "RU-BEL": (
            Entity("Belgorodskaja oblast'", "RU-BEL", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Belgorodskaya oblast'", "RU-BEL", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-BRY": (
            Entity("Brjanskaja oblast'", "RU-BRY", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Bryanskaya oblast'", "RU-BRY", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-BU": (
            Entity("Burjatija", "RU-BU", "REPUBLIC", "ru", ""),
            Entity("Buryatiya", "RU-BU", "REPUBLIC", "ru", ""),
        ),
        "RU-CE": (
            Entity("Chechenskaya Respublika", "RU-CE", "REPUBLIC", "ru", ""),
            Entity("Čečenskaja Respublika", "RU-CE", "REPUBLIC", "ru", ""),
        ),
        "RU-CHE": (
            Entity("Chelyabinskaya oblast'", "RU-CHE", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Čeljabinskaja oblast'", "RU-CHE", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-CHU": (
            Entity("Chukotskiy avtonomnyy okrug", "RU-CHU", "AUTONOMOUS DISTRICT", "ru", ""),
            Entity("Čukotskij avtonomnyj okrug", "RU-CHU", "AUTONOMOUS DISTRICT", "ru", ""),
        ),
        "RU-CU": (
            Entity("Chuvashskaya Respublika", "RU-CU", "REPUBLIC", "ru", ""),
            Entity("Čuvašskaja Respublika", "RU-CU", "REPUBLIC", "ru", ""),
        ),
        "RU-DA": (
            Entity("Dagestan", "RU-DA", "REPUBLIC", "ru", ""),
            Entity("Dagestan", "RU-DA", "REPUBLIC", "ru", ""),
        ),
        "RU-IN": (
            Entity("Ingushetiya", "RU-IN", "REPUBLIC", "ru", ""),
            Entity("Ingušetija", "RU-IN", "REPUBLIC", "ru", ""),
        ),
        "RU-IRK": (
            Entity("Irkutskaja oblast'", "RU-IRK", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Irkutskaya oblast'", "RU-IRK", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-IVA": (
            Entity("Ivanovskaja oblast'", "RU-IVA", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Ivanovskaya oblast'", "RU-IVA", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KAM": (
            Entity("Kamchatskiy kray", "RU-KAM", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Kamčatskij kraj", "RU-KAM", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-KB": (
            Entity("Kabardino-Balkarskaja Respublika", "RU-KB", "REPUBLIC", "ru", ""),
            Entity("Kabardino-Balkarskaya Respublika", "RU-KB", "REPUBLIC", "ru", ""),
        ),
        "RU-KC": (
            Entity("Karachayevo-Cherkesskaya Respublika", "RU-KC", "REPUBLIC", "ru", ""),
            Entity("Karačaevo-Čerkesskaja Respublika", "RU-KC", "REPUBLIC", "ru", ""),
        ),
        "RU-KDA": (
            Entity("Krasnodarskij kraj", "RU-KDA", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Krasnodarskiy kray", "RU-KDA", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-KEM": (
            Entity("Kemerovskaja oblast'", "RU-KEM", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kemerovskaya oblast'", "RU-KEM", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KGD": (
            Entity("Kaliningradskaja oblast'", "RU-KGD", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kaliningradskaya oblast'", "RU-KGD", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KGN": (
            Entity("Kurganskaja oblast'", "RU-KGN", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kurganskaya oblast'", "RU-KGN", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KHA": (
            Entity("Habarovskij kraj", "RU-KHA", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Khabarovskiy kray", "RU-KHA", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-KHM": (
            Entity("Hanty-Mansijskij avtonomnyj okrug", "RU-KHM", "AUTONOMOUS DISTRICT", "ru", ""),
            Entity("Khanty-Mansiyskiy avtonomnyy okrug", "RU-KHM", "AUTONOMOUS DISTRICT", "ru", ""),
        ),
        "RU-KIR": (
            Entity("Kirovskaja oblast'", "RU-KIR", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kirovskaya oblast'", "RU-KIR", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KK": (
            Entity("Hakasija", "RU-KK", "REPUBLIC", "ru", ""),
            Entity("Khakasiya", "RU-KK", "REPUBLIC", "ru", ""),
        ),
        "RU-KL": (
            Entity("Kalmykija", "RU-KL", "REPUBLIC", "ru", ""),
            Entity("Kalmykiya", "RU-KL", "REPUBLIC", "ru", ""),
        ),
        "RU-KLU": (
            Entity("Kaluzhskaya oblast'", "RU-KLU", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kalužskaja oblast'", "RU-KLU", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KO": (
            Entity("Komi", "RU-KO", "REPUBLIC", "ru", ""),
            Entity("Komi", "RU-KO", "REPUBLIC", "ru", ""),
        ),
        "RU-KOS": (
            Entity("Kostromskaja oblast'", "RU-KOS", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kostromskaya oblast'", "RU-KOS", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KR": (
            Entity("Karelija", "RU-KR", "REPUBLIC", "ru", ""),
            Entity("Kareliya", "RU-KR", "REPUBLIC", "ru", ""),
        ),
        "RU-KRS": (
            Entity("Kurskaja oblast'", "RU-KRS", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Kurskaya oblast'", "RU-KRS", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-KYA": (
            Entity("Krasnojarskij kraj", "RU-KYA", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Krasnoyarskiy kray", "RU-KYA", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-LEN": (
            Entity("Leningradskaja oblast'", "RU-LEN", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Leningradskaya oblast'", "RU-LEN", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-LIP": (
            Entity("Lipeckaja oblast'", "RU-LIP", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Lipetskaya oblast'", "RU-LIP", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-MAG": (
            Entity("Magadanskaja oblast'", "RU-MAG", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Magadanskaya oblast'", "RU-MAG", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-ME": (
            Entity("Marij Èl", "RU-ME", "REPUBLIC", "ru", ""),
            Entity("Mariy El", "RU-ME", "REPUBLIC", "ru", ""),
        ),
        "RU-MO": (
            Entity("Mordovija", "RU-MO", "REPUBLIC", "ru", ""),
            Entity("Mordoviya", "RU-MO", "REPUBLIC", "ru", ""),
        ),
        "RU-MOS": (
            Entity("Moskovskaja oblast'", "RU-MOS", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Moskovskaya oblast'", "RU-MOS", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-MOW": (
            Entity("Moskva", "RU-MOW", "AUTONOMOUS CITY", "ru", ""),
            Entity("Moskva", "RU-MOW", "AUTONOMOUS CITY", "ru", ""),
        ),
        "RU-MUR": (
            Entity("Murmanskaja oblast'", "RU-MUR", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Murmanskaya oblast'", "RU-MUR", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-NEN": (
            Entity("Neneckij avtonomnyj okrug", "RU-NEN", "AUTONOMOUS DISTRICT", "ru", ""),
            Entity("Nenetskiy avtonomnyy okrug", "RU-NEN", "AUTONOMOUS DISTRICT", "ru", ""),
        ),
        "RU-NGR": (
            Entity("Novgorodskaja oblast'", "RU-NGR", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Novgorodskaya oblast'", "RU-NGR", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-NIZ": (
            Entity("Nizhegorodskaya oblast'", "RU-NIZ", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Nižegorodskaja oblast'", "RU-NIZ", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-NVS": (
            Entity("Novosibirskaja oblast'", "RU-NVS", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Novosibirskaya oblast'", "RU-NVS", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-OMS": (
            Entity("Omskaja oblast'", "RU-OMS", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Omskaya oblast'", "RU-OMS", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-ORE": (
            Entity("Orenburgskaja oblast'", "RU-ORE", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Orenburgskaya oblast'", "RU-ORE", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-ORL": (
            Entity("Orlovskaja oblast'", "RU-ORL", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Orlovskaya oblast'", "RU-ORL", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-PER": (
            Entity("Permskij kraj", "RU-PER", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Permskiy kray", "RU-PER", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-PNZ": (
            Entity("Penzenskaja oblast'", "RU-PNZ", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Penzenskaya oblast'", "RU-PNZ", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-PRI": (
            Entity("Primorskij kraj", "RU-PRI", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Primorskiy kray", "RU-PRI", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-PSK": (
            Entity("Pskovskaja oblast'", "RU-PSK", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Pskovskaya oblast'", "RU-PSK", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-ROS": (
            Entity("Rostovskaja oblast'", "RU-ROS", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Rostovskaya oblast'", "RU-ROS", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-RYA": (
            Entity("Rjazanskaja oblast'", "RU-RYA", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Ryazanskaya oblast'", "RU-RYA", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-SA": (
            Entity("Saha", "RU-SA", "REPUBLIC", "ru", ""),
            Entity("Sakha", "RU-SA", "REPUBLIC", "ru", ""),
        ),
        "RU-SAK": (
            Entity("Sahalinskaja oblast'", "RU-SAK", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Sakhalinskaya oblast'", "RU-SAK", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-SAM": (
            Entity("Samarskaja oblast'", "RU-SAM", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Samarskaya oblast'", "RU-SAM", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-SAR": (
            Entity("Saratovskaja oblast'", "RU-SAR", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Saratovskaya oblast'", "RU-SAR", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-SE": (
            Entity("Severnaja Osetija", "RU-SE", "REPUBLIC", "ru", ""),
            Entity("Severnaya Osetiya", "RU-SE", "REPUBLIC", "ru", ""),
        ),
        "RU-SMO": (
            Entity("Smolenskaja oblast'", "RU-SMO", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Smolenskaya oblast'", "RU-SMO", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-SPE": (
            Entity("Sankt-Peterburg", "RU-SPE", "AUTONOMOUS CITY", "ru", ""),
            Entity("Sankt-Peterburg", "RU-SPE", "AUTONOMOUS CITY", "ru", ""),
        ),
        "RU-STA": (
            Entity("Stavropol'skij kraj", "RU-STA", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Stavropol'skiy kray", "RU-STA", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
        "RU-SVE": (
            Entity("Sverdlovskaja oblast'", "RU-SVE", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Sverdlovskaya oblast'", "RU-SVE", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-TA": (
            Entity("Tatarstan", "RU-TA", "REPUBLIC", "ru", ""),
            Entity("Tatarstan", "RU-TA", "REPUBLIC", "ru", ""),
        ),
        "RU-TAM": (
            Entity("Tambovskaja oblast'", "RU-TAM", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Tambovskaya oblast'", "RU-TAM", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-TOM": (
            Entity("Tomskaja oblast'", "RU-TOM", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Tomskaya oblast'", "RU-TOM", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-TUL": (
            Entity("Tul'skaja oblast'", "RU-TUL", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Tul'skaya oblast'", "RU-TUL", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-TVE": (
            Entity("Tverskaja oblast'", "RU-TVE", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Tverskaya oblast'", "RU-TVE", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-TY": (
            Entity("Tyva", "RU-TY", "REPUBLIC", "ru", ""),
            Entity("Tyva", "RU-TY", "REPUBLIC", "ru", ""),
        ),
        "RU-TYU": (
            Entity("Tjumenskaja oblast'", "RU-TYU", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Tyumenskaya oblast'", "RU-TYU", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-UD": (
            Entity("Udmurtskaja Respublika", "RU-UD", "REPUBLIC", "ru", ""),
            Entity("Udmurtskaya Respublika", "RU-UD", "REPUBLIC", "ru", ""),
        ),
        "RU-ULY": (
            Entity("Ul'janovskaja oblast'", "RU-ULY", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Ul'yanovskaya oblast'", "RU-ULY", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-VGG": (
            Entity("Volgogradskaja oblast'", "RU-VGG", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Volgogradskaya oblast'", "RU-VGG", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-VLA": (
            Entity("Vladimirskaja oblast'", "RU-VLA", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Vladimirskaya oblast'", "RU-VLA", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-VLG": (
            Entity("Vologodskaja oblast'", "RU-VLG", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Vologodskaya oblast'", "RU-VLG", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-VOR": (
            Entity("Voronezhskaya oblast'", "RU-VOR", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Voronežskaja oblast'", "RU-VOR", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-YAN": (
            Entity("Jamalo-Neneckij avtonomnyj okrug", "RU-YAN", "AUTONOMOUS DISTRICT", "ru", ""),
            Entity("Yamalo-Nenetskiy avtonomnyy okrug", "RU-YAN", "AUTONOMOUS DISTRICT", "ru", ""),
        ),
        "RU-YAR": (
            Entity("Jaroslavskaja oblast'", "RU-YAR", "ADMINISTRATIVE REGION", "ru", ""),
            Entity("Yaroslavskaya oblast'", "RU-YAR", "ADMINISTRATIVE REGION", "ru", ""),
        ),
        "RU-YEV": (
            Entity("Evrejskaja avtonomnaja oblast'", "RU-YEV", "AUTONOMOUS REGION", "ru", ""),
            Entity("Yevreyskaya avtonomnaya oblast'", "RU-YEV", "AUTONOMOUS REGION", "ru", ""),
        ),
        "RU-ZAB": (
            Entity("Zabajkal'skij kraj", "RU-ZAB", "ADMINISTRATIVE TERRITORY", "ru", ""),
            Entity("Zabaykal'skiy kray", "RU-ZAB", "ADMINISTRATIVE TERRITORY", "ru", ""),
        ),
    }
