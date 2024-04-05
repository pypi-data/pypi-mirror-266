"""ISO 3166-2 ID standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ID
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ID-AC": (Entity("Aceh", "ID-AC", "PROVINCE", "id", "ID-SM"),),
        "ID-BA": (Entity("Bali", "ID-BA", "PROVINCE", "id", "ID-NU"),),
        "ID-BB": (Entity("Kepulauan Bangka Belitung", "ID-BB", "PROVINCE", "id", "ID-SM"),),
        "ID-BE": (Entity("Bengkulu", "ID-BE", "PROVINCE", "id", "ID-SM"),),
        "ID-BT": (Entity("Banten", "ID-BT", "PROVINCE", "id", "ID-JW"),),
        "ID-GO": (Entity("Gorontalo", "ID-GO", "PROVINCE", "id", "ID-SL"),),
        "ID-JA": (Entity("Jambi", "ID-JA", "PROVINCE", "id", "ID-SM"),),
        "ID-JB": (Entity("Jawa Barat", "ID-JB", "PROVINCE", "id", "ID-JW"),),
        "ID-JI": (Entity("Jawa Timur", "ID-JI", "PROVINCE", "id", "ID-JW"),),
        "ID-JK": (Entity("Jakarta Raya", "ID-JK", "CAPITAL DISTRICT", "id", "ID-JW"),),
        "ID-JT": (Entity("Jawa Tengah", "ID-JT", "PROVINCE", "id", "ID-JW"),),
        "ID-JW": (Entity("Jawa", "ID-JW", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-KA": (Entity("Kalimantan", "ID-KA", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-KB": (Entity("Kalimantan Barat", "ID-KB", "PROVINCE", "id", "ID-KA"),),
        "ID-KI": (Entity("Kalimantan Timur", "ID-KI", "PROVINCE", "id", "ID-KA"),),
        "ID-KR": (Entity("Kepulauan Riau", "ID-KR", "PROVINCE", "id", "ID-SM"),),
        "ID-KS": (Entity("Kalimantan Selatan", "ID-KS", "PROVINCE", "id", "ID-KA"),),
        "ID-KT": (Entity("Kalimantan Tengah", "ID-KT", "PROVINCE", "id", "ID-KA"),),
        "ID-KU": (Entity("Kalimantan Utara", "ID-KU", "PROVINCE", "id", "ID-KA"),),
        "ID-LA": (Entity("Lampung", "ID-LA", "PROVINCE", "id", "ID-SM"),),
        "ID-MA": (Entity("Maluku", "ID-MA", "PROVINCE", "id", "ID-ML"),),
        "ID-ML": (Entity("Maluku", "ID-ML", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-MU": (Entity("Maluku Utara", "ID-MU", "PROVINCE", "id", "ID-ML"),),
        "ID-NB": (Entity("Nusa Tenggara Barat", "ID-NB", "PROVINCE", "id", "ID-NU"),),
        "ID-NT": (Entity("Nusa Tenggara Timur", "ID-NT", "PROVINCE", "id", "ID-NU"),),
        "ID-NU": (Entity("Nusa Tenggara", "ID-NU", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-PA": (Entity("Papua", "ID-PA", "PROVINCE", "id", "ID-PP"),),
        "ID-PB": (Entity("Papua Barat", "ID-PB", "PROVINCE", "id", "ID-PP"),),
        "ID-PD": (Entity("Papua Barat Daya", "ID-PD", "PROVINCE", "id", "ID-PP"),),
        "ID-PE": (Entity("Papua Pengunungan", "ID-PE", "PROVINCE", "id", "ID-PP"),),
        "ID-PP": (Entity("Papua", "ID-PP", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-PS": (Entity("Papua Selatan", "ID-PS", "PROVINCE", "id", "ID-PP"),),
        "ID-PT": (Entity("Papua Tengah", "ID-PT", "PROVINCE", "id", "ID-PP"),),
        "ID-RI": (Entity("Riau", "ID-RI", "PROVINCE", "id", "ID-SM"),),
        "ID-SA": (Entity("Sulawesi Utara", "ID-SA", "PROVINCE", "id", "ID-SL"),),
        "ID-SB": (Entity("Sumatera Barat", "ID-SB", "PROVINCE", "id", "ID-SM"),),
        "ID-SG": (Entity("Sulawesi Tenggara", "ID-SG", "PROVINCE", "id", "ID-SL"),),
        "ID-SL": (Entity("Sulawesi", "ID-SL", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-SM": (Entity("Sumatera", "ID-SM", "GEOGRAPHICAL UNIT", "id", ""),),
        "ID-SN": (Entity("Sulawesi Selatan", "ID-SN", "PROVINCE", "id", "ID-SL"),),
        "ID-SR": (Entity("Sulawesi Barat", "ID-SR", "PROVINCE", "id", "ID-SL"),),
        "ID-SS": (Entity("Sumatera Selatan", "ID-SS", "PROVINCE", "id", "ID-SM"),),
        "ID-ST": (Entity("Sulawesi Tengah", "ID-ST", "PROVINCE", "id", "ID-SL"),),
        "ID-SU": (Entity("Sumatera Utara", "ID-SU", "PROVINCE", "id", "ID-SM"),),
        "ID-YO": (Entity("Yogyakarta", "ID-YO", "SPECIAL REGION", "id", "ID-JW"),),
    }
