"""ISO 3166-2 MV standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MV
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MV-00": (
            Entity("Ariatholhu Dhekunuburi", "MV-00", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("South Ari Atoll", "MV-00", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-01": (
            Entity("Addu", "MV-01", "CITY", "dv", ""),
            Entity("Addu City", "MV-01", "CITY", "en", ""),
        ),
        "MV-02": (
            Entity("Ariatholhu Uthuruburi", "MV-02", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("North Ari Atoll", "MV-02", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-03": (
            Entity("Faadhippolhu", "MV-03", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Faadhippolhu", "MV-03", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-04": (
            Entity("Felidheatholhu", "MV-04", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Felidhu Atoll", "MV-04", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-05": (
            Entity("Hahdhunmathi", "MV-05", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Hahdhunmathi", "MV-05", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-07": (
            Entity("North Thiladhunmathi", "MV-07", "ADMINISTRATIVE ATOLL", "en", ""),
            Entity("Thiladhunmathee Uthuruburi", "MV-07", "ADMINISTRATIVE ATOLL", "dv", ""),
        ),
        "MV-08": (
            Entity("Kolhumadulu", "MV-08", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Kolhumadulu", "MV-08", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-12": (
            Entity("Mulakatholhu", "MV-12", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Mulaku Atoll", "MV-12", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-13": (
            Entity("Maalhosmadulu Uthuruburi", "MV-13", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("North Maalhosmadulu", "MV-13", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-14": (
            Entity("Nilandheatholhu Uthuruburi", "MV-14", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("North Nilandhe Atoll", "MV-14", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-17": (
            Entity("Nilandheatholhu Dhekunuburi", "MV-17", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("South Nilandhe Atoll", "MV-17", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-20": (
            Entity("Maalhosmadulu Dhekunuburi", "MV-20", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("South Maalhosmadulu", "MV-20", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-23": (
            Entity("South Thiladhunmathi", "MV-23", "ADMINISTRATIVE ATOLL", "en", ""),
            Entity("Thiladhunmathee Dhekunuburi", "MV-23", "ADMINISTRATIVE ATOLL", "dv", ""),
        ),
        "MV-24": (
            Entity("Miladhunmadulu Uthuruburi", "MV-24", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("North Miladhunmadulu", "MV-24", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-25": (
            Entity("Miladhunmadulu Dhekunuburi", "MV-25", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("South Miladhunmadulu", "MV-25", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-26": (
            Entity("Maaleatholhu", "MV-26", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Male Atoll", "MV-26", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-27": (
            Entity("Huvadhuatholhu Uthuruburi", "MV-27", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("North Huvadhu Atoll", "MV-27", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-28": (
            Entity("Huvadhuatholhu Dhekunuburi", "MV-28", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("South Huvadhu Atoll", "MV-28", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-29": (
            Entity("Fuvammulah", "MV-29", "ADMINISTRATIVE ATOLL", "dv", ""),
            Entity("Fuvammulah", "MV-29", "ADMINISTRATIVE ATOLL", "en", ""),
        ),
        "MV-MLE": (
            Entity("Maale", "MV-MLE", "CITY", "dv", ""),
            Entity("Male", "MV-MLE", "CITY", "en", ""),
        ),
    }
