"""ISO 3166-2 FI standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:FI
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "FI-01": (
            Entity("Ahvenanmaan maakunta", "FI-01", "REGION", "fi", ""),
            Entity("Landskapet Åland", "FI-01", "REGION", "sv", ""),
        ),
        "FI-02": (
            Entity("Etelä-Karjala", "FI-02", "REGION", "fi", ""),
            Entity("Södra Karelen", "FI-02", "REGION", "sv", ""),
        ),
        "FI-03": (
            Entity("Etelä-Pohjanmaa", "FI-03", "REGION", "fi", ""),
            Entity("Södra Österbotten", "FI-03", "REGION", "sv", ""),
        ),
        "FI-04": (
            Entity("Etelä-Savo", "FI-04", "REGION", "fi", ""),
            Entity("Södra Savolax", "FI-04", "REGION", "sv", ""),
        ),
        "FI-05": (
            Entity("Kainuu", "FI-05", "REGION", "fi", ""),
            Entity("Kajanaland", "FI-05", "REGION", "sv", ""),
        ),
        "FI-06": (
            Entity("Egentliga Tavastland", "FI-06", "REGION", "sv", ""),
            Entity("Kanta-Häme", "FI-06", "REGION", "fi", ""),
        ),
        "FI-07": (
            Entity("Keski-Pohjanmaa", "FI-07", "REGION", "fi", ""),
            Entity("Mellersta Österbotten", "FI-07", "REGION", "sv", ""),
        ),
        "FI-08": (
            Entity("Keski-Suomi", "FI-08", "REGION", "fi", ""),
            Entity("Mellersta Finland", "FI-08", "REGION", "sv", ""),
        ),
        "FI-09": (
            Entity("Kymenlaakso", "FI-09", "REGION", "fi", ""),
            Entity("Kymmenedalen", "FI-09", "REGION", "sv", ""),
        ),
        "FI-10": (
            Entity("Lappi", "FI-10", "REGION", "fi", ""),
            Entity("Lappland", "FI-10", "REGION", "sv", ""),
        ),
        "FI-11": (
            Entity("Birkaland", "FI-11", "REGION", "sv", ""),
            Entity("Pirkanmaa", "FI-11", "REGION", "fi", ""),
        ),
        "FI-12": (
            Entity("Pohjanmaa", "FI-12", "REGION", "fi", ""),
            Entity("Österbotten", "FI-12", "REGION", "sv", ""),
        ),
        "FI-13": (
            Entity("Norra Karelen", "FI-13", "REGION", "sv", ""),
            Entity("Pohjois-Karjala", "FI-13", "REGION", "fi", ""),
        ),
        "FI-14": (
            Entity("Norra Österbotten", "FI-14", "REGION", "sv", ""),
            Entity("Pohjois-Pohjanmaa", "FI-14", "REGION", "fi", ""),
        ),
        "FI-15": (
            Entity("Norra Savolax", "FI-15", "REGION", "sv", ""),
            Entity("Pohjois-Savo", "FI-15", "REGION", "fi", ""),
        ),
        "FI-16": (
            Entity("Päijänne-Tavastland", "FI-16", "REGION", "sv", ""),
            Entity("Päijät-Häme", "FI-16", "REGION", "fi", ""),
        ),
        "FI-17": (
            Entity("Satakunta", "FI-17", "REGION", "fi", ""),
            Entity("Satakunta", "FI-17", "REGION", "sv", ""),
        ),
        "FI-18": (
            Entity("Nyland", "FI-18", "REGION", "sv", ""),
            Entity("Uusimaa", "FI-18", "REGION", "fi", ""),
        ),
        "FI-19": (
            Entity("Egentliga Finland", "FI-19", "REGION", "sv", ""),
            Entity("Varsinais-Suomi", "FI-19", "REGION", "fi", ""),
        ),
    }
