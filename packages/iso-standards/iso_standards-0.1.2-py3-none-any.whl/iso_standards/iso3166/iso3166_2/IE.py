"""ISO 3166-2 IE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:IE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "IE-C": (
            Entity("Connacht", "IE-C", "PROVINCE", "ga", ""),
            Entity("Connaught", "IE-C", "PROVINCE", "en", ""),
        ),
        "IE-CE": (
            Entity("An Clár", "IE-CE", "COUNTY", "ga", "IE-M"),
            Entity("Clare", "IE-CE", "COUNTY", "en", "IE-M"),
        ),
        "IE-CN": (
            Entity("An Cabhán", "IE-CN", "COUNTY", "ga", "IE-U"),
            Entity("Cavan", "IE-CN", "COUNTY", "en", "IE-U"),
        ),
        "IE-CO": (
            Entity("Corcaigh", "IE-CO", "COUNTY", "ga", "IE-M"),
            Entity("Cork", "IE-CO", "COUNTY", "en", "IE-M"),
        ),
        "IE-CW": (
            Entity("Carlow", "IE-CW", "COUNTY", "en", "IE-L"),
            Entity("Ceatharlach", "IE-CW", "COUNTY", "ga", "IE-L"),
        ),
        "IE-D": (
            Entity("Baile Átha Cliath", "IE-D", "COUNTY", "ga", "IE-L"),
            Entity("Dublin", "IE-D", "COUNTY", "en", "IE-L"),
        ),
        "IE-DL": (
            Entity("Donegal", "IE-DL", "COUNTY", "en", "IE-U"),
            Entity("Dún na nGall", "IE-DL", "COUNTY", "ga", "IE-U"),
        ),
        "IE-G": (
            Entity("Gaillimh", "IE-G", "COUNTY", "ga", "IE-C"),
            Entity("Galway", "IE-G", "COUNTY", "en", "IE-C"),
        ),
        "IE-KE": (
            Entity("Cill Dara", "IE-KE", "COUNTY", "ga", "IE-L"),
            Entity("Kildare", "IE-KE", "COUNTY", "en", "IE-L"),
        ),
        "IE-KK": (
            Entity("Cill Chainnigh", "IE-KK", "COUNTY", "ga", "IE-L"),
            Entity("Kilkenny", "IE-KK", "COUNTY", "en", "IE-L"),
        ),
        "IE-KY": (
            Entity("Ciarraí", "IE-KY", "COUNTY", "ga", "IE-M"),
            Entity("Kerry", "IE-KY", "COUNTY", "en", "IE-M"),
        ),
        "IE-L": (
            Entity("Laighin", "IE-L", "PROVINCE", "ga", ""),
            Entity("Leinster", "IE-L", "PROVINCE", "en", ""),
        ),
        "IE-LD": (
            Entity("An Longfort", "IE-LD", "COUNTY", "ga", "IE-L"),
            Entity("Longford", "IE-LD", "COUNTY", "en", "IE-L"),
        ),
        "IE-LH": (
            Entity("Louth", "IE-LH", "COUNTY", "en", "IE-L"),
            Entity("Lú", "IE-LH", "COUNTY", "ga", "IE-L"),
        ),
        "IE-LK": (
            Entity("Limerick", "IE-LK", "COUNTY", "en", "IE-M"),
            Entity("Luimneach", "IE-LK", "COUNTY", "ga", "IE-M"),
        ),
        "IE-LM": (
            Entity("Leitrim", "IE-LM", "COUNTY", "en", "IE-C"),
            Entity("Liatroim", "IE-LM", "COUNTY", "ga", "IE-C"),
        ),
        "IE-LS": (
            Entity("Laois", "IE-LS", "COUNTY", "en", "IE-L"),
            Entity("Laois", "IE-LS", "COUNTY", "ga", "IE-L"),
        ),
        "IE-M": (
            Entity("An Mhumhain", "IE-M", "PROVINCE", "ga", ""),
            Entity("Munster", "IE-M", "PROVINCE", "en", ""),
        ),
        "IE-MH": (
            Entity("An Mhí", "IE-MH", "COUNTY", "ga", "IE-L"),
            Entity("Meath", "IE-MH", "COUNTY", "en", "IE-L"),
        ),
        "IE-MN": (
            Entity("Monaghan", "IE-MN", "COUNTY", "en", "IE-U"),
            Entity("Muineachán", "IE-MN", "COUNTY", "ga", "IE-U"),
        ),
        "IE-MO": (
            Entity("Maigh Eo", "IE-MO", "COUNTY", "ga", "IE-C"),
            Entity("Mayo", "IE-MO", "COUNTY", "en", "IE-C"),
        ),
        "IE-OY": (
            Entity("Offaly", "IE-OY", "COUNTY", "en", "IE-L"),
            Entity("Uíbh Fhailí", "IE-OY", "COUNTY", "ga", "IE-L"),
        ),
        "IE-RN": (
            Entity("Ros Comáin", "IE-RN", "COUNTY", "ga", "IE-C"),
            Entity("Roscommon", "IE-RN", "COUNTY", "en", "IE-C"),
        ),
        "IE-SO": (
            Entity("Sligeach", "IE-SO", "COUNTY", "ga", "IE-C"),
            Entity("Sligo", "IE-SO", "COUNTY", "en", "IE-C"),
        ),
        "IE-TA": (
            Entity("Tiobraid Árann", "IE-TA", "COUNTY", "ga", "IE-M"),
            Entity("Tipperary", "IE-TA", "COUNTY", "en", "IE-M"),
        ),
        "IE-U": (
            Entity("Ulaidh", "IE-U", "PROVINCE", "ga", ""),
            Entity("Ulster", "IE-U", "PROVINCE", "en", ""),
        ),
        "IE-WD": (
            Entity("Port Láirge", "IE-WD", "COUNTY", "ga", "IE-M"),
            Entity("Waterford", "IE-WD", "COUNTY", "en", "IE-M"),
        ),
        "IE-WH": (
            Entity("An Iarmhí", "IE-WH", "COUNTY", "ga", "IE-L"),
            Entity("Westmeath", "IE-WH", "COUNTY", "en", "IE-L"),
        ),
        "IE-WW": (
            Entity("Cill Mhantáin", "IE-WW", "COUNTY", "ga", "IE-L"),
            Entity("Wicklow", "IE-WW", "COUNTY", "en", "IE-L"),
        ),
        "IE-WX": (
            Entity("Loch Garman", "IE-WX", "COUNTY", "ga", "IE-L"),
            Entity("Wexford", "IE-WX", "COUNTY", "en", "IE-L"),
        ),
    }
