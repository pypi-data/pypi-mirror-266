"""ISO 3166-2 TZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TZ-01": (Entity("Arusha", "TZ-01", "REGION", "sw", ""),),
        "TZ-02": (Entity("Dar es Salaam", "TZ-02", "REGION", "sw", ""),),
        "TZ-03": (Entity("Dodoma", "TZ-03", "REGION", "sw", ""),),
        "TZ-04": (Entity("Iringa", "TZ-04", "REGION", "sw", ""),),
        "TZ-05": (Entity("Kagera", "TZ-05", "REGION", "sw", ""),),
        "TZ-06": (
            Entity("Kaskazini Pemba", "TZ-06", "REGION", "sw", ""),
            Entity("Pemba North", "TZ-06", "REGION", "en", ""),
        ),
        "TZ-07": (
            Entity("Kaskazini Unguja", "TZ-07", "REGION", "sw", ""),
            Entity("Zanzibar North", "TZ-07", "REGION", "en", ""),
        ),
        "TZ-08": (Entity("Kigoma", "TZ-08", "REGION", "sw", ""),),
        "TZ-09": (Entity("Kilimanjaro", "TZ-09", "REGION", "sw", ""),),
        "TZ-10": (
            Entity("Kusini Pemba", "TZ-10", "REGION", "sw", ""),
            Entity("Pemba South", "TZ-10", "REGION", "en", ""),
        ),
        "TZ-11": (
            Entity("Kusini Unguja", "TZ-11", "REGION", "sw", ""),
            Entity("Zanzibar South", "TZ-11", "REGION", "en", ""),
        ),
        "TZ-12": (Entity("Lindi", "TZ-12", "REGION", "sw", ""),),
        "TZ-13": (Entity("Mara", "TZ-13", "REGION", "sw", ""),),
        "TZ-14": (Entity("Mbeya", "TZ-14", "REGION", "sw", ""),),
        "TZ-15": (
            Entity("Mjini Magharibi", "TZ-15", "REGION", "sw", ""),
            Entity("Zanzibar West", "TZ-15", "REGION", "en", ""),
        ),
        "TZ-16": (Entity("Morogoro", "TZ-16", "REGION", "sw", ""),),
        "TZ-17": (Entity("Mtwara", "TZ-17", "REGION", "sw", ""),),
        "TZ-18": (Entity("Mwanza", "TZ-18", "REGION", "sw", ""),),
        "TZ-19": (
            Entity("Coast", "TZ-19", "REGION", "en", ""),
            Entity("Pwani", "TZ-19", "REGION", "sw", ""),
        ),
        "TZ-20": (Entity("Rukwa", "TZ-20", "REGION", "sw", ""),),
        "TZ-21": (Entity("Ruvuma", "TZ-21", "REGION", "sw", ""),),
        "TZ-22": (Entity("Shinyanga", "TZ-22", "REGION", "sw", ""),),
        "TZ-23": (Entity("Singida", "TZ-23", "REGION", "sw", ""),),
        "TZ-24": (Entity("Tabora", "TZ-24", "REGION", "sw", ""),),
        "TZ-25": (Entity("Tanga", "TZ-25", "REGION", "sw", ""),),
        "TZ-26": (Entity("Manyara", "TZ-26", "REGION", "sw", ""),),
        "TZ-27": (Entity("Geita", "TZ-27", "REGION", "sw", ""),),
        "TZ-28": (Entity("Katavi", "TZ-28", "REGION", "sw", ""),),
        "TZ-29": (Entity("Njombe", "TZ-29", "REGION", "sw", ""),),
        "TZ-30": (Entity("Simiyu", "TZ-30", "REGION", "sw", ""),),
        "TZ-31": (
            Entity("Songwe", "TZ-31", "REGION", "en", ""),
            Entity("Songwe", "TZ-31", "REGION", "sw", ""),
        ),
    }
