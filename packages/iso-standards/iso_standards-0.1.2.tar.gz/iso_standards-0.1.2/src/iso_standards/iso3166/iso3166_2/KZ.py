"""ISO 3166-2 KZ standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KZ
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KZ-10": (
            Entity("Abajskaja oblast’", "KZ-10", "REGION", "ru", ""),
            Entity("Abay oblysy", "KZ-10", "REGION", "kk", ""),
            Entity("Abayskaya oblast’", "KZ-10", "REGION", "ru", ""),
        ),
        "KZ-11": (
            Entity("Akmolinskaja oblast'", "KZ-11", "REGION", "ru", ""),
            Entity("Akmolinskaya oblast'", "KZ-11", "REGION", "ru", ""),
            Entity("Aqmola oblysy", "KZ-11", "REGION", "kk", ""),
        ),
        "KZ-15": (
            Entity("Aktjubinskaja oblast'", "KZ-15", "REGION", "ru", ""),
            Entity("Aktyubinskaya oblast'", "KZ-15", "REGION", "ru", ""),
            Entity("Aqtöbe oblysy", "KZ-15", "REGION", "kk", ""),
        ),
        "KZ-19": (
            Entity("Almatinskaja oblast'", "KZ-19", "REGION", "ru", ""),
            Entity("Almatinskaya oblast'", "KZ-19", "REGION", "ru", ""),
            Entity("Almaty oblysy", "KZ-19", "REGION", "kk", ""),
        ),
        "KZ-23": (
            Entity("Atyrauskaja oblast'", "KZ-23", "REGION", "ru", ""),
            Entity("Atyrauskaya oblast'", "KZ-23", "REGION", "ru", ""),
            Entity("Atyraū oblysy", "KZ-23", "REGION", "kk", ""),
        ),
        "KZ-27": (
            Entity("Batys Qazaqstan oblysy", "KZ-27", "REGION", "kk", ""),
            Entity("Zapadno-Kazahstanskaja oblast'", "KZ-27", "REGION", "ru", ""),
            Entity("Zapadno-Kazakhstanskaya oblast'", "KZ-27", "REGION", "ru", ""),
        ),
        "KZ-31": (
            Entity("Zhambyl oblysy", "KZ-31", "REGION", "kk", ""),
            Entity("Zhambylskaya oblast'", "KZ-31", "REGION", "ru", ""),
            Entity("Žambylskaja oblast'", "KZ-31", "REGION", "ru", ""),
        ),
        "KZ-33": (
            Entity("Zhetisū oblysy", "KZ-33", "REGION", "kk", ""),
            Entity("Zhetysuskaya oblast’", "KZ-33", "REGION", "ru", ""),
            Entity("Žetysuskaja oblast’", "KZ-33", "REGION", "ru", ""),
        ),
        "KZ-35": (
            Entity("Karagandinskaja oblast'", "KZ-35", "REGION", "ru", ""),
            Entity("Karagandinskaya oblast'", "KZ-35", "REGION", "ru", ""),
            Entity("Qaraghandy oblysy", "KZ-35", "REGION", "kk", ""),
        ),
        "KZ-39": (
            Entity("Kostanajskaja oblast'", "KZ-39", "REGION", "ru", ""),
            Entity("Kostanayskaya oblast'", "KZ-39", "REGION", "ru", ""),
            Entity("Qostanay oblysy", "KZ-39", "REGION", "kk", ""),
        ),
        "KZ-43": (
            Entity("Kyzylordinskaja oblast'", "KZ-43", "REGION", "ru", ""),
            Entity("Kyzylordinskaya oblast'", "KZ-43", "REGION", "ru", ""),
            Entity("Qyzylorda oblysy", "KZ-43", "REGION", "kk", ""),
        ),
        "KZ-47": (
            Entity("Mangghystaū oblysy", "KZ-47", "REGION", "kk", ""),
            Entity("Mangistauskaya oblast'", "KZ-47", "REGION", "ru", ""),
            Entity("Mangystauskaja oblast'", "KZ-47", "REGION", "ru", ""),
        ),
        "KZ-55": (
            Entity("Pavlodar oblysy", "KZ-55", "REGION", "kk", ""),
            Entity("Pavlodarskaja oblast'", "KZ-55", "REGION", "ru", ""),
            Entity("Pavlodarskaya oblast'", "KZ-55", "REGION", "ru", ""),
        ),
        "KZ-59": (
            Entity("Severo-Kazahstanskaja oblast'", "KZ-59", "REGION", "ru", ""),
            Entity("Severo-Kazakhstanskaya oblast'", "KZ-59", "REGION", "ru", ""),
            Entity("Soltüstik Qazaqstan oblysy", "KZ-59", "REGION", "kk", ""),
        ),
        "KZ-61": (
            Entity("Turkestankaya oblast'", "KZ-61", "REGION", "ru", ""),
            Entity("Turkestanskaja oblast'", "KZ-61", "REGION", "ru", ""),
            Entity("Türkistan oblysy", "KZ-61", "REGION", "kk", ""),
        ),
        "KZ-62": (
            Entity("Ulytauskaja oblast’", "KZ-62", "REGION", "ru", ""),
            Entity("Ulytauskaya oblast’", "KZ-62", "REGION", "ru", ""),
            Entity("Ulytaū oblysy", "KZ-62", "REGION", "kk", ""),
        ),
        "KZ-63": (
            Entity("Shyghys Qazaqstan oblysy", "KZ-63", "REGION", "kk", ""),
            Entity("Vostochno-Kazakhstanskaya oblast'", "KZ-63", "REGION", "ru", ""),
            Entity("Vostočno-Kazahstanskaja oblast'", "KZ-63", "REGION", "ru", ""),
        ),
        "KZ-71": (
            Entity("Astana", "KZ-71", "CITY", "kk", ""),
            Entity("Astana", "KZ-71", "CITY", "ru", ""),
            Entity("Astana", "KZ-71", "CITY", "ru", ""),
        ),
        "KZ-75": (
            Entity("Almaty", "KZ-75", "CITY", "kk", ""),
            Entity("Almaty", "KZ-75", "CITY", "ru", ""),
            Entity("Almaty", "KZ-75", "CITY", "ru", ""),
        ),
        "KZ-79": (
            Entity("Shymkent", "KZ-79", "CITY", "kk", ""),
            Entity("Shymkent", "KZ-79", "CITY", "ru", ""),
            Entity("Šimkent", "KZ-79", "CITY", "ru", ""),
        ),
    }
