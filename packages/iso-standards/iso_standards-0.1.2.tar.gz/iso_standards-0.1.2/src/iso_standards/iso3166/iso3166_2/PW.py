"""ISO 3166-2 PW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PW-002": (
            Entity("Aimeliik", "PW-002", "STATE", "en", ""),
            Entity("Aimeliik", "PW-002", "STATE", "", ""),
        ),
        "PW-004": (
            Entity("Airai", "PW-004", "STATE", "en", ""),
            Entity("Airai", "PW-004", "STATE", "", ""),
        ),
        "PW-010": (
            Entity("Angaur", "PW-010", "STATE", "en", ""),
            Entity("Angaur", "PW-010", "STATE", "", ""),
        ),
        "PW-050": (
            Entity("Hatohobei", "PW-050", "STATE", "en", ""),
            Entity("Hatohobei", "PW-050", "STATE", "", ""),
        ),
        "PW-100": (
            Entity("Kayangel", "PW-100", "STATE", "en", ""),
            Entity("Kayangel", "PW-100", "STATE", "", ""),
        ),
        "PW-150": (
            Entity("Koror", "PW-150", "STATE", "en", ""),
            Entity("Koror", "PW-150", "STATE", "", ""),
        ),
        "PW-212": (
            Entity("Melekeok", "PW-212", "STATE", "en", ""),
            Entity("Melekeok", "PW-212", "STATE", "", ""),
        ),
        "PW-214": (
            Entity("Ngaraard", "PW-214", "STATE", "en", ""),
            Entity("Ngaraard", "PW-214", "STATE", "", ""),
        ),
        "PW-218": (
            Entity("Ngarchelong", "PW-218", "STATE", "en", ""),
            Entity("Ngarchelong", "PW-218", "STATE", "", ""),
        ),
        "PW-222": (
            Entity("Ngardmau", "PW-222", "STATE", "en", ""),
            Entity("Ngardmau", "PW-222", "STATE", "", ""),
        ),
        "PW-224": (
            Entity("Ngatpang", "PW-224", "STATE", "en", ""),
            Entity("Ngatpang", "PW-224", "STATE", "", ""),
        ),
        "PW-226": (
            Entity("Ngchesar", "PW-226", "STATE", "en", ""),
            Entity("Ngchesar", "PW-226", "STATE", "", ""),
        ),
        "PW-227": (
            Entity("Ngeremlengui", "PW-227", "STATE", "en", ""),
            Entity("Ngeremlengui", "PW-227", "STATE", "", ""),
        ),
        "PW-228": (
            Entity("Ngiwal", "PW-228", "STATE", "en", ""),
            Entity("Ngiwal", "PW-228", "STATE", "", ""),
        ),
        "PW-350": (
            Entity("Peleliu", "PW-350", "STATE", "en", ""),
            Entity("Peleliu", "PW-350", "STATE", "", ""),
        ),
        "PW-370": (
            Entity("Sonsorol", "PW-370", "STATE", "en", ""),
            Entity("Sonsorol", "PW-370", "STATE", "", ""),
        ),
    }
