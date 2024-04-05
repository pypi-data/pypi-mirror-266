"""ISO 3166-2 CA standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CA
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CA-AB": (
            Entity("Alberta", "CA-AB", "PROVINCE", "en", ""),
            Entity("Alberta", "CA-AB", "PROVINCE", "fr", ""),
        ),
        "CA-BC": (
            Entity("British Columbia", "CA-BC", "PROVINCE", "en", ""),
            Entity("Colombie-Britannique", "CA-BC", "PROVINCE", "fr", ""),
        ),
        "CA-MB": (
            Entity("Manitoba", "CA-MB", "PROVINCE", "en", ""),
            Entity("Manitoba", "CA-MB", "PROVINCE", "fr", ""),
        ),
        "CA-NB": (
            Entity("New Brunswick", "CA-NB", "PROVINCE", "en", ""),
            Entity("Nouveau-Brunswick", "CA-NB", "PROVINCE", "fr", ""),
        ),
        "CA-NL": (
            Entity("Newfoundland and Labrador", "CA-NL", "PROVINCE", "en", ""),
            Entity("Terre-Neuve-et-Labrador", "CA-NL", "PROVINCE", "fr", ""),
        ),
        "CA-NS": (
            Entity("Nouvelle-Écosse", "CA-NS", "PROVINCE", "fr", ""),
            Entity("Nova Scotia", "CA-NS", "PROVINCE", "en", ""),
        ),
        "CA-NT": (
            Entity("Northwest Territories", "CA-NT", "TERRITORY", "en", ""),
            Entity("Territoires du Nord-Ouest", "CA-NT", "TERRITORY", "fr", ""),
        ),
        "CA-NU": (
            Entity("Nunavut", "CA-NU", "TERRITORY", "en", ""),
            Entity("Nunavut", "CA-NU", "TERRITORY", "fr", ""),
        ),
        "CA-ON": (
            Entity("Ontario", "CA-ON", "PROVINCE", "en", ""),
            Entity("Ontario", "CA-ON", "PROVINCE", "fr", ""),
        ),
        "CA-PE": (
            Entity("Prince Edward Island", "CA-PE", "PROVINCE", "en", ""),
            Entity("Île-du-Prince-Édouard", "CA-PE", "PROVINCE", "fr", ""),
        ),
        "CA-QC": (
            Entity("Quebec", "CA-QC", "PROVINCE", "en", ""),
            Entity("Québec", "CA-QC", "PROVINCE", "fr", ""),
        ),
        "CA-SK": (
            Entity("Saskatchewan", "CA-SK", "PROVINCE", "en", ""),
            Entity("Saskatchewan", "CA-SK", "PROVINCE", "fr", ""),
        ),
        "CA-YT": (
            Entity("Yukon", "CA-YT", "TERRITORY", "en", ""),
            Entity("Yukon", "CA-YT", "TERRITORY", "fr", ""),
        ),
    }
