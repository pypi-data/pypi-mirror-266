"""ISO 3166-2 HT standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:HT
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "HT-AR": (
            Entity("Artibonite", "HT-AR", "DEPARTMENT", "fr", ""),
            Entity("Latibonit", "HT-AR", "DEPARTMENT", "ht", ""),
        ),
        "HT-CE": (
            Entity("Centre", "HT-CE", "DEPARTMENT", "fr", ""),
            Entity("Sant", "HT-CE", "DEPARTMENT", "ht", ""),
        ),
        "HT-GA": (
            Entity("Grandans", "HT-GA", "DEPARTMENT", "ht", ""),
            Entity("Grande’Anse", "HT-GA", "DEPARTMENT", "fr", ""),
        ),
        "HT-ND": (
            Entity("Nord", "HT-ND", "DEPARTMENT", "fr", ""),
            Entity("Nò", "HT-ND", "DEPARTMENT", "ht", ""),
        ),
        "HT-NE": (
            Entity("Nord-Est", "HT-NE", "DEPARTMENT", "fr", ""),
            Entity("Nòdès", "HT-NE", "DEPARTMENT", "ht", ""),
        ),
        "HT-NI": (
            Entity("Nip", "HT-NI", "DEPARTMENT", "ht", ""),
            Entity("Nippes", "HT-NI", "DEPARTMENT", "fr", ""),
        ),
        "HT-NO": (
            Entity("Nord-Ouest", "HT-NO", "DEPARTMENT", "fr", ""),
            Entity("Nòdwès", "HT-NO", "DEPARTMENT", "ht", ""),
        ),
        "HT-OU": (
            Entity("Lwès", "HT-OU", "DEPARTMENT", "ht", ""),
            Entity("Ouest", "HT-OU", "DEPARTMENT", "fr", ""),
        ),
        "HT-SD": (
            Entity("Sid", "HT-SD", "DEPARTMENT", "ht", ""),
            Entity("Sud", "HT-SD", "DEPARTMENT", "fr", ""),
        ),
        "HT-SE": (
            Entity("Sidès", "HT-SE", "DEPARTMENT", "ht", ""),
            Entity("Sud-Est", "HT-SE", "DEPARTMENT", "fr", ""),
        ),
    }
