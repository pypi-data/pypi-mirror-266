"""ISO 3166-2 RS standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:RS
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "RS-00": (Entity("Beograd", "RS-00", "CITY", "sr", ""),),
        "RS-01": (Entity("Severnobački okrug", "RS-01", "DISTRICT", "sr", "RS-VO"),),
        "RS-02": (Entity("Srednjebanatski okrug", "RS-02", "DISTRICT", "sr", "RS-VO"),),
        "RS-03": (Entity("Severnobanatski okrug", "RS-03", "DISTRICT", "sr", "RS-VO"),),
        "RS-04": (Entity("Južnobanatski okrug", "RS-04", "DISTRICT", "sr", "RS-VO"),),
        "RS-05": (Entity("Zapadnobački okrug", "RS-05", "DISTRICT", "sr", "RS-VO"),),
        "RS-06": (Entity("Južnobački okrug", "RS-06", "DISTRICT", "sr", "RS-VO"),),
        "RS-07": (Entity("Sremski okrug", "RS-07", "DISTRICT", "sr", "RS-VO"),),
        "RS-08": (Entity("Mačvanski okrug", "RS-08", "DISTRICT", "sr", ""),),
        "RS-09": (Entity("Kolubarski okrug", "RS-09", "DISTRICT", "sr", ""),),
        "RS-10": (Entity("Podunavski okrug", "RS-10", "DISTRICT", "sr", ""),),
        "RS-11": (Entity("Braničevski okrug", "RS-11", "DISTRICT", "sr", ""),),
        "RS-12": (Entity("Šumadijski okrug", "RS-12", "DISTRICT", "sr", ""),),
        "RS-13": (Entity("Pomoravski okrug", "RS-13", "DISTRICT", "sr", ""),),
        "RS-14": (Entity("Borski okrug", "RS-14", "DISTRICT", "sr", ""),),
        "RS-15": (Entity("Zaječarski okrug", "RS-15", "DISTRICT", "sr", ""),),
        "RS-16": (Entity("Zlatiborski okrug", "RS-16", "DISTRICT", "sr", ""),),
        "RS-17": (Entity("Moravički okrug", "RS-17", "DISTRICT", "sr", ""),),
        "RS-18": (Entity("Raški okrug", "RS-18", "DISTRICT", "sr", ""),),
        "RS-19": (Entity("Rasinski okrug", "RS-19", "DISTRICT", "sr", ""),),
        "RS-20": (Entity("Nišavski okrug", "RS-20", "DISTRICT", "sr", ""),),
        "RS-21": (Entity("Toplički okrug", "RS-21", "DISTRICT", "sr", ""),),
        "RS-22": (Entity("Pirotski okrug", "RS-22", "DISTRICT", "sr", ""),),
        "RS-23": (Entity("Jablanički okrug", "RS-23", "DISTRICT", "sr", ""),),
        "RS-24": (Entity("Pčinjski okrug", "RS-24", "DISTRICT", "sr", ""),),
        "RS-25": (Entity("Kosovski okrug", "RS-25", "DISTRICT", "sr", "RS-KM"),),
        "RS-26": (Entity("Pećki okrug", "RS-26", "DISTRICT", "sr", "RS-KM"),),
        "RS-27": (Entity("Prizrenski okrug", "RS-27", "DISTRICT", "sr", "RS-KM"),),
        "RS-28": (Entity("Kosovsko-Mitrovački okrug", "RS-28", "DISTRICT", "sr", "RS-KM"),),
        "RS-29": (Entity("Kosovsko-Pomoravski okrug", "RS-29", "DISTRICT", "sr", "RS-KM"),),
        "RS-KM": (Entity("Kosovo-Metohija", "RS-KM", "AUTONOMOUS PROVINCE", "sr", ""),),
        "RS-VO": (Entity("Vojvodina", "RS-VO", "AUTONOMOUS PROVINCE", "sr", ""),),
    }
