"""ISO 3166-2 TN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TN-11": (Entity("Tunis", "TN-11", "GOVERNORATE", "ar", ""),),
        "TN-12": (Entity("L'Ariana", "TN-12", "GOVERNORATE", "ar", ""),),
        "TN-13": (Entity("Ben Arous", "TN-13", "GOVERNORATE", "ar", ""),),
        "TN-14": (Entity("La Manouba", "TN-14", "GOVERNORATE", "ar", ""),),
        "TN-21": (Entity("Nabeul", "TN-21", "GOVERNORATE", "ar", ""),),
        "TN-22": (Entity("Zaghouan", "TN-22", "GOVERNORATE", "ar", ""),),
        "TN-23": (Entity("Bizerte", "TN-23", "GOVERNORATE", "ar", ""),),
        "TN-31": (Entity("Béja", "TN-31", "GOVERNORATE", "ar", ""),),
        "TN-32": (Entity("Jendouba", "TN-32", "GOVERNORATE", "ar", ""),),
        "TN-33": (Entity("Le Kef", "TN-33", "GOVERNORATE", "ar", ""),),
        "TN-34": (Entity("Siliana", "TN-34", "GOVERNORATE", "ar", ""),),
        "TN-41": (Entity("Kairouan", "TN-41", "GOVERNORATE", "ar", ""),),
        "TN-42": (Entity("Kasserine", "TN-42", "GOVERNORATE", "ar", ""),),
        "TN-43": (Entity("Sidi Bouzid", "TN-43", "GOVERNORATE", "ar", ""),),
        "TN-51": (Entity("Sousse", "TN-51", "GOVERNORATE", "ar", ""),),
        "TN-52": (Entity("Monastir", "TN-52", "GOVERNORATE", "ar", ""),),
        "TN-53": (Entity("Mahdia", "TN-53", "GOVERNORATE", "ar", ""),),
        "TN-61": (Entity("Sfax", "TN-61", "GOVERNORATE", "ar", ""),),
        "TN-71": (Entity("Gafsa", "TN-71", "GOVERNORATE", "ar", ""),),
        "TN-72": (Entity("Tozeur", "TN-72", "GOVERNORATE", "ar", ""),),
        "TN-73": (Entity("Kébili", "TN-73", "GOVERNORATE", "ar", ""),),
        "TN-81": (Entity("Gabès", "TN-81", "GOVERNORATE", "ar", ""),),
        "TN-82": (Entity("Médenine", "TN-82", "GOVERNORATE", "ar", ""),),
        "TN-83": (Entity("Tataouine", "TN-83", "GOVERNORATE", "ar", ""),),
    }
