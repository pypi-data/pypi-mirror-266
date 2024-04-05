"""ISO 3166-2 KE standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:KE
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "KE-01": (Entity("Baringo", "KE-01", "COUNTY", "en", ""),),
        "KE-02": (Entity("Bomet", "KE-02", "COUNTY", "en", ""),),
        "KE-03": (Entity("Bungoma", "KE-03", "COUNTY", "en", ""),),
        "KE-04": (Entity("Busia", "KE-04", "COUNTY", "en", ""),),
        "KE-05": (Entity("Elgeyo/Marakwet", "KE-05", "COUNTY", "en", ""),),
        "KE-06": (Entity("Embu", "KE-06", "COUNTY", "en", ""),),
        "KE-07": (Entity("Garissa", "KE-07", "COUNTY", "en", ""),),
        "KE-08": (Entity("Homa Bay", "KE-08", "COUNTY", "en", ""),),
        "KE-09": (Entity("Isiolo", "KE-09", "COUNTY", "en", ""),),
        "KE-10": (Entity("Kajiado", "KE-10", "COUNTY", "en", ""),),
        "KE-11": (Entity("Kakamega", "KE-11", "COUNTY", "en", ""),),
        "KE-12": (Entity("Kericho", "KE-12", "COUNTY", "en", ""),),
        "KE-13": (Entity("Kiambu", "KE-13", "COUNTY", "en", ""),),
        "KE-14": (Entity("Kilifi", "KE-14", "COUNTY", "en", ""),),
        "KE-15": (Entity("Kirinyaga", "KE-15", "COUNTY", "en", ""),),
        "KE-16": (Entity("Kisii", "KE-16", "COUNTY", "en", ""),),
        "KE-17": (Entity("Kisumu", "KE-17", "COUNTY", "en", ""),),
        "KE-18": (Entity("Kitui", "KE-18", "COUNTY", "en", ""),),
        "KE-19": (Entity("Kwale", "KE-19", "COUNTY", "en", ""),),
        "KE-20": (Entity("Laikipia", "KE-20", "COUNTY", "en", ""),),
        "KE-21": (Entity("Lamu", "KE-21", "COUNTY", "en", ""),),
        "KE-22": (Entity("Machakos", "KE-22", "COUNTY", "en", ""),),
        "KE-23": (Entity("Makueni", "KE-23", "COUNTY", "en", ""),),
        "KE-24": (Entity("Mandera", "KE-24", "COUNTY", "en", ""),),
        "KE-25": (Entity("Marsabit", "KE-25", "COUNTY", "en", ""),),
        "KE-26": (Entity("Meru", "KE-26", "COUNTY", "en", ""),),
        "KE-27": (Entity("Migori", "KE-27", "COUNTY", "en", ""),),
        "KE-28": (Entity("Mombasa", "KE-28", "COUNTY", "en", ""),),
        "KE-29": (Entity("Murang'a", "KE-29", "COUNTY", "en", ""),),
        "KE-30": (Entity("Nairobi City", "KE-30", "COUNTY", "en", ""),),
        "KE-31": (Entity("Nakuru", "KE-31", "COUNTY", "en", ""),),
        "KE-32": (Entity("Nandi", "KE-32", "COUNTY", "en", ""),),
        "KE-33": (Entity("Narok", "KE-33", "COUNTY", "en", ""),),
        "KE-34": (Entity("Nyamira", "KE-34", "COUNTY", "en", ""),),
        "KE-35": (Entity("Nyandarua", "KE-35", "COUNTY", "en", ""),),
        "KE-36": (Entity("Nyeri", "KE-36", "COUNTY", "en", ""),),
        "KE-37": (Entity("Samburu", "KE-37", "COUNTY", "en", ""),),
        "KE-38": (Entity("Siaya", "KE-38", "COUNTY", "en", ""),),
        "KE-39": (Entity("Taita/Taveta", "KE-39", "COUNTY", "en", ""),),
        "KE-40": (Entity("Tana River", "KE-40", "COUNTY", "en", ""),),
        "KE-41": (Entity("Tharaka-Nithi", "KE-41", "COUNTY", "en", ""),),
        "KE-42": (Entity("Trans Nzoia", "KE-42", "COUNTY", "en", ""),),
        "KE-43": (Entity("Turkana", "KE-43", "COUNTY", "en", ""),),
        "KE-44": (Entity("Uasin Gishu", "KE-44", "COUNTY", "en", ""),),
        "KE-45": (Entity("Vihiga", "KE-45", "COUNTY", "en", ""),),
        "KE-46": (Entity("Wajir", "KE-46", "COUNTY", "en", ""),),
        "KE-47": (Entity("West Pokot", "KE-47", "COUNTY", "en", ""),),
    }
