"""ISO 3166-2 ET standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:ET
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "ET-AA": (
            Entity("Addis Ababa", "ET-AA", "ADMINISTRATION", "en", ""),
            Entity("Ādīs Ābeba", "ET-AA", "ADMINISTRATION", "am", ""),
        ),
        "ET-AF": (
            Entity("Afar", "ET-AF", "REGIONAL STATE", "en", ""),
            Entity("Āfar", "ET-AF", "REGIONAL STATE", "am", ""),
        ),
        "ET-AM": (
            Entity("Amara", "ET-AM", "REGIONAL STATE", "en", ""),
            Entity("Āmara", "ET-AM", "REGIONAL STATE", "am", ""),
        ),
        "ET-BE": (
            Entity("Benshangul-Gumaz", "ET-BE", "REGIONAL STATE", "en", ""),
            Entity("Bīnshangul Gumuz", "ET-BE", "REGIONAL STATE", "am", ""),
        ),
        "ET-DD": (
            Entity("Dire Dawa", "ET-DD", "ADMINISTRATION", "en", ""),
            Entity("Dirē Dawa", "ET-DD", "ADMINISTRATION", "am", ""),
        ),
        "ET-GA": (
            Entity("Gambela Peoples", "ET-GA", "REGIONAL STATE", "en", ""),
            Entity("Gambēla Hizboch", "ET-GA", "REGIONAL STATE", "am", ""),
        ),
        "ET-HA": (
            Entity("Harari People", "ET-HA", "REGIONAL STATE", "en", ""),
            Entity("Hārerī Hizb", "ET-HA", "REGIONAL STATE", "am", ""),
        ),
        "ET-OR": (
            Entity("Oromia", "ET-OR", "REGIONAL STATE", "en", ""),
            Entity("Oromīya", "ET-OR", "REGIONAL STATE", "am", ""),
        ),
        "ET-SI": (
            Entity("Sidama", "ET-SI", "REGIONAL STATE", "en", ""),
            Entity("Sīdama", "ET-SI", "REGIONAL STATE", "am", ""),
        ),
        "ET-SN": (
            Entity("Southern Nations", "ET-SN", "REGIONAL STATE", "en", ""),
            Entity("YeDebub Bihēroch Bihēreseboch na Hizboch", "ET-SN", "REGIONAL STATE", "am", ""),
        ),
        "ET-SO": (
            Entity("Somali", "ET-SO", "REGIONAL STATE", "en", ""),
            Entity("Sumalē", "ET-SO", "REGIONAL STATE", "am", ""),
        ),
        "ET-SW": (
            Entity("Southwest Ethiopia Peoples", "ET-SW", "REGIONAL STATE", "en", ""),
            Entity("YeDebub M‘irab Ītyop’iya Hizboch", "ET-SW", "REGIONAL STATE", "am", ""),
        ),
        "ET-TI": (
            Entity("Tigrai", "ET-TI", "REGIONAL STATE", "en", ""),
            Entity("Tigray", "ET-TI", "REGIONAL STATE", "am", ""),
        ),
    }
