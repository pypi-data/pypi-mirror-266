"""ISO 3166-2 MW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:MW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "MW-BA": (
            Entity("Balaka", "MW-BA", "DISTRICT", "en", "MW-S"),
            Entity("Balaka", "MW-BA", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-BL": (
            Entity("Blantyre", "MW-BL", "DISTRICT", "en", "MW-S"),
            Entity("Blantyre", "MW-BL", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-C": (
            Entity("Central Region", "MW-C", "REGION", "en", ""),
            Entity("Chapakati", "MW-C", "REGION", "ny", ""),
        ),
        "MW-CK": (
            Entity("Chikwawa", "MW-CK", "DISTRICT", "en", "MW-S"),
            Entity("Chikwawa", "MW-CK", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-CR": (
            Entity("Chiradzulu", "MW-CR", "DISTRICT", "en", "MW-S"),
            Entity("Chiradzulu", "MW-CR", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-CT": (
            Entity("Chitipa", "MW-CT", "DISTRICT", "en", "MW-N"),
            Entity("Chitipa", "MW-CT", "DISTRICT", "ny", "MW-N"),
        ),
        "MW-DE": (
            Entity("Dedza", "MW-DE", "DISTRICT", "en", "MW-C"),
            Entity("Dedza", "MW-DE", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-DO": (
            Entity("Dowa", "MW-DO", "DISTRICT", "en", "MW-C"),
            Entity("Dowa", "MW-DO", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-KR": (
            Entity("Karonga", "MW-KR", "DISTRICT", "en", "MW-N"),
            Entity("Karonga", "MW-KR", "DISTRICT", "ny", "MW-N"),
        ),
        "MW-KS": (
            Entity("Kasungu", "MW-KS", "DISTRICT", "en", "MW-C"),
            Entity("Kasungu", "MW-KS", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-LI": (
            Entity("Lilongwe", "MW-LI", "DISTRICT", "en", "MW-C"),
            Entity("Lilongwe", "MW-LI", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-LK": (
            Entity("Likoma", "MW-LK", "DISTRICT", "en", "MW-N"),
            Entity("Likoma", "MW-LK", "DISTRICT", "ny", "MW-N"),
        ),
        "MW-MC": (
            Entity("Mchinji", "MW-MC", "DISTRICT", "en", "MW-C"),
            Entity("Mchinji", "MW-MC", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-MG": (
            Entity("Mangochi", "MW-MG", "DISTRICT", "en", "MW-S"),
            Entity("Mangochi", "MW-MG", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-MH": (
            Entity("Machinga", "MW-MH", "DISTRICT", "en", "MW-S"),
            Entity("Machinga", "MW-MH", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-MU": (
            Entity("Mulanje", "MW-MU", "DISTRICT", "en", "MW-S"),
            Entity("Mulanje", "MW-MU", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-MW": (
            Entity("Mwanza", "MW-MW", "DISTRICT", "en", "MW-S"),
            Entity("Mwanza", "MW-MW", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-MZ": (
            Entity("Mzimba", "MW-MZ", "DISTRICT", "en", "MW-N"),
            Entity("Mzimba", "MW-MZ", "DISTRICT", "ny", "MW-N"),
        ),
        "MW-N": (
            Entity("Chakumpoto", "MW-N", "REGION", "ny", ""),
            Entity("Northern Region", "MW-N", "REGION", "en", ""),
        ),
        "MW-NB": (
            Entity("Nkhata Bay", "MW-NB", "DISTRICT", "en", "MW-N"),
            Entity("Nkhata Bay", "MW-NB", "DISTRICT", "ny", "MW-N"),
        ),
        "MW-NE": (
            Entity("Neno", "MW-NE", "DISTRICT", "en", "MW-S"),
            Entity("Neno", "MW-NE", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-NI": (
            Entity("Ntchisi", "MW-NI", "DISTRICT", "en", "MW-C"),
            Entity("Ntchisi", "MW-NI", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-NK": (
            Entity("Nkhotakota", "MW-NK", "DISTRICT", "en", "MW-C"),
            Entity("Nkhotakota", "MW-NK", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-NS": (
            Entity("Nsanje", "MW-NS", "DISTRICT", "en", "MW-S"),
            Entity("Nsanje", "MW-NS", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-NU": (
            Entity("Ntcheu", "MW-NU", "DISTRICT", "en", "MW-C"),
            Entity("Ntcheu", "MW-NU", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-PH": (
            Entity("Phalombe", "MW-PH", "DISTRICT", "en", "MW-S"),
            Entity("Phalombe", "MW-PH", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-RU": (
            Entity("Rumphi", "MW-RU", "DISTRICT", "en", "MW-N"),
            Entity("Rumphi", "MW-RU", "DISTRICT", "ny", "MW-N"),
        ),
        "MW-S": (
            Entity("Chakumwera", "MW-S", "REGION", "ny", ""),
            Entity("Southern Region", "MW-S", "REGION", "en", ""),
        ),
        "MW-SA": (
            Entity("Salima", "MW-SA", "DISTRICT", "en", "MW-C"),
            Entity("Salima", "MW-SA", "DISTRICT", "ny", "MW-C"),
        ),
        "MW-TH": (
            Entity("Thyolo", "MW-TH", "DISTRICT", "en", "MW-S"),
            Entity("Thyolo", "MW-TH", "DISTRICT", "ny", "MW-S"),
        ),
        "MW-ZO": (
            Entity("Zomba", "MW-ZO", "DISTRICT", "en", "MW-S"),
            Entity("Zomba", "MW-ZO", "DISTRICT", "ny", "MW-S"),
        ),
    }
