"""ISO 3166-2 NG standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:NG
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "NG-AB": (Entity("Abia", "NG-AB", "STATE", "en", ""),),
        "NG-AD": (Entity("Adamawa", "NG-AD", "STATE", "en", ""),),
        "NG-AK": (Entity("Akwa Ibom", "NG-AK", "STATE", "en", ""),),
        "NG-AN": (Entity("Anambra", "NG-AN", "STATE", "en", ""),),
        "NG-BA": (Entity("Bauchi", "NG-BA", "STATE", "en", ""),),
        "NG-BE": (Entity("Benue", "NG-BE", "STATE", "en", ""),),
        "NG-BO": (Entity("Borno", "NG-BO", "STATE", "en", ""),),
        "NG-BY": (Entity("Bayelsa", "NG-BY", "STATE", "en", ""),),
        "NG-CR": (Entity("Cross River", "NG-CR", "STATE", "en", ""),),
        "NG-DE": (Entity("Delta", "NG-DE", "STATE", "en", ""),),
        "NG-EB": (Entity("Ebonyi", "NG-EB", "STATE", "en", ""),),
        "NG-ED": (Entity("Edo", "NG-ED", "STATE", "en", ""),),
        "NG-EK": (Entity("Ekiti", "NG-EK", "STATE", "en", ""),),
        "NG-EN": (Entity("Enugu", "NG-EN", "STATE", "en", ""),),
        "NG-FC": (
            Entity("Abuja Federal Capital Territory", "NG-FC", "CAPITAL TERRITORY", "en", ""),
        ),
        "NG-GO": (Entity("Gombe", "NG-GO", "STATE", "en", ""),),
        "NG-IM": (Entity("Imo", "NG-IM", "STATE", "en", ""),),
        "NG-JI": (Entity("Jigawa", "NG-JI", "STATE", "en", ""),),
        "NG-KD": (Entity("Kaduna", "NG-KD", "STATE", "en", ""),),
        "NG-KE": (Entity("Kebbi", "NG-KE", "STATE", "en", ""),),
        "NG-KN": (Entity("Kano", "NG-KN", "STATE", "en", ""),),
        "NG-KO": (Entity("Kogi", "NG-KO", "STATE", "en", ""),),
        "NG-KT": (Entity("Katsina", "NG-KT", "STATE", "en", ""),),
        "NG-KW": (Entity("Kwara", "NG-KW", "STATE", "en", ""),),
        "NG-LA": (Entity("Lagos", "NG-LA", "STATE", "en", ""),),
        "NG-NA": (Entity("Nasarawa", "NG-NA", "STATE", "en", ""),),
        "NG-NI": (Entity("Niger", "NG-NI", "STATE", "en", ""),),
        "NG-OG": (Entity("Ogun", "NG-OG", "STATE", "en", ""),),
        "NG-ON": (Entity("Ondo", "NG-ON", "STATE", "en", ""),),
        "NG-OS": (Entity("Osun", "NG-OS", "STATE", "en", ""),),
        "NG-OY": (Entity("Oyo", "NG-OY", "STATE", "en", ""),),
        "NG-PL": (Entity("Plateau", "NG-PL", "STATE", "en", ""),),
        "NG-RI": (Entity("Rivers", "NG-RI", "STATE", "en", ""),),
        "NG-SO": (Entity("Sokoto", "NG-SO", "STATE", "en", ""),),
        "NG-TA": (Entity("Taraba", "NG-TA", "STATE", "en", ""),),
        "NG-YO": (Entity("Yobe", "NG-YO", "STATE", "en", ""),),
        "NG-ZA": (Entity("Zamfara", "NG-ZA", "STATE", "en", ""),),
    }
