"""ISO 3166-2 KH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KH-1": (
            Entity("Banteay Mean Choăy", "KH-1", "PROVINCE", "km", ""),
            Entity("Bântéay Méan Choăy", "KH-1", "PROVINCE", "km", ""),
        ),
        "KH-10": (
            Entity("Kracheh", "KH-10", "PROVINCE", "km", ""),
            Entity("Krâchéh", "KH-10", "PROVINCE", "km", ""),
        ),
        "KH-11": (
            Entity("Mondol Kiri", "KH-11", "PROVINCE", "km", ""),
            Entity("Môndól Kiri", "KH-11", "PROVINCE", "km", ""),
        ),
        "KH-12": (
            Entity("Phnom Penh", "KH-12", "AUTONOMOUS MUNICIPALITY", "km", ""),
            Entity("Phnum Pénh", "KH-12", "AUTONOMOUS MUNICIPALITY", "km", ""),
        ),
        "KH-13": (
            Entity("Preah Vihear", "KH-13", "PROVINCE", "km", ""),
            Entity("Preăh Vihéar", "KH-13", "PROVINCE", "km", ""),
        ),
        "KH-14": (
            Entity("Prey Veaeng", "KH-14", "PROVINCE", "km", ""),
            Entity("Prey Vêng", "KH-14", "PROVINCE", "km", ""),
        ),
        "KH-15": (
            Entity("Pousaat", "KH-15", "PROVINCE", "km", ""),
            Entity("Poŭthĭsăt", "KH-15", "PROVINCE", "km", ""),
        ),
        "KH-16": (
            Entity("Rotanak Kiri", "KH-16", "PROVINCE", "km", ""),
            Entity("Rôtânôkiri", "KH-16", "PROVINCE", "km", ""),
        ),
        "KH-17": (
            Entity("Siem Reab", "KH-17", "PROVINCE", "km", ""),
            Entity("Siĕmréab", "KH-17", "PROVINCE", "km", ""),
        ),
        "KH-18": (
            Entity("Preah Sihanouk", "KH-18", "PROVINCE", "km", ""),
            Entity("Preăh Seihânŭ", "KH-18", "PROVINCE", "km", ""),
        ),
        "KH-19": (
            Entity("Stoĕng Trêng", "KH-19", "PROVINCE", "km", ""),
            Entity("Stueng Traeng", "KH-19", "PROVINCE", "km", ""),
        ),
        "KH-2": (
            Entity("Baat Dambang", "KH-2", "PROVINCE", "km", ""),
            Entity("Bătdâmbâng", "KH-2", "PROVINCE", "km", ""),
        ),
        "KH-20": (
            Entity("Svaay Rieng", "KH-20", "PROVINCE", "km", ""),
            Entity("Svay Riĕng", "KH-20", "PROVINCE", "km", ""),
        ),
        "KH-21": (
            Entity("Taakaev", "KH-21", "PROVINCE", "km", ""),
            Entity("Takêv", "KH-21", "PROVINCE", "km", ""),
        ),
        "KH-22": (
            Entity("Otdar Mean Chey", "KH-22", "PROVINCE", "km", ""),
            Entity("Ŏtdâr Méan Choăy", "KH-22", "PROVINCE", "km", ""),
        ),
        "KH-23": (
            Entity("Kaeb", "KH-23", "PROVINCE", "km", ""),
            Entity("Kêb", "KH-23", "PROVINCE", "km", ""),
        ),
        "KH-24": (
            Entity("Pailin", "KH-24", "PROVINCE", "km", ""),
            Entity("Pailĭn", "KH-24", "PROVINCE", "km", ""),
        ),
        "KH-25": (
            Entity("Tbong Khmum", "KH-25", "PROVINCE", "km", ""),
            Entity("Tbong Khmŭm", "KH-25", "PROVINCE", "km", ""),
        ),
        "KH-3": (
            Entity("Kampong Chaam", "KH-3", "PROVINCE", "km", ""),
            Entity("Kâmpóng Cham", "KH-3", "PROVINCE", "km", ""),
        ),
        "KH-4": (
            Entity("Kampong Chhnang", "KH-4", "PROVINCE", "km", ""),
            Entity("Kâmpóng Chhnăng", "KH-4", "PROVINCE", "km", ""),
        ),
        "KH-5": (
            Entity("Kampong Spueu", "KH-5", "PROVINCE", "km", ""),
            Entity("Kâmpóng Spœ", "KH-5", "PROVINCE", "km", ""),
        ),
        "KH-6": (
            Entity("Kampong Thum", "KH-6", "PROVINCE", "km", ""),
            Entity("Kâmpóng Thum", "KH-6", "PROVINCE", "km", ""),
        ),
        "KH-7": (
            Entity("Kampot", "KH-7", "PROVINCE", "km", ""),
            Entity("Kâmpôt", "KH-7", "PROVINCE", "km", ""),
        ),
        "KH-8": (
            Entity("Kandaal", "KH-8", "PROVINCE", "km", ""),
            Entity("Kândal", "KH-8", "PROVINCE", "km", ""),
        ),
        "KH-9": (
            Entity("Kaoh Kong", "KH-9", "PROVINCE", "km", ""),
            Entity("Kaôh Kŏng", "KH-9", "PROVINCE", "km", ""),
        ),
    }
