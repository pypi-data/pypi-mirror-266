"""ISO 3166-2 SD standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:SD
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "SD-DC": (
            Entity("Central Darfur", "SD-DC", "STATE", "en", ""),
            Entity("Wasaţ Dārfūr", "SD-DC", "STATE", "ar", ""),
        ),
        "SD-DE": (
            Entity("East Darfur", "SD-DE", "STATE", "en", ""),
            Entity("Sharq Dārfūr", "SD-DE", "STATE", "ar", ""),
        ),
        "SD-DN": (
            Entity("North Darfur", "SD-DN", "STATE", "en", ""),
            Entity("Shamāl Dārfūr", "SD-DN", "STATE", "ar", ""),
        ),
        "SD-DS": (
            Entity("Janūb Dārfūr", "SD-DS", "STATE", "ar", ""),
            Entity("South Darfur", "SD-DS", "STATE", "en", ""),
        ),
        "SD-DW": (
            Entity("Gharb Dārfūr", "SD-DW", "STATE", "ar", ""),
            Entity("West Darfur", "SD-DW", "STATE", "en", ""),
        ),
        "SD-GD": (
            Entity("Al Qaḑārif", "SD-GD", "STATE", "ar", ""),
            Entity("Gedaref", "SD-GD", "STATE", "en", ""),
        ),
        "SD-GK": (
            Entity("Gharb Kurdufān", "SD-GK", "STATE", "ar", ""),
            Entity("West Kordofan", "SD-GK", "STATE", "en", ""),
        ),
        "SD-GZ": (
            Entity("Al Jazīrah", "SD-GZ", "STATE", "ar", ""),
            Entity("Gezira", "SD-GZ", "STATE", "en", ""),
        ),
        "SD-KA": (
            Entity("Kassala", "SD-KA", "STATE", "en", ""),
            Entity("Kassalā", "SD-KA", "STATE", "ar", ""),
        ),
        "SD-KH": (
            Entity("Al Kharţūm", "SD-KH", "STATE", "ar", ""),
            Entity("Khartoum", "SD-KH", "STATE", "en", ""),
        ),
        "SD-KN": (
            Entity("North Kordofan", "SD-KN", "STATE", "en", ""),
            Entity("Shamāl Kurdufān", "SD-KN", "STATE", "ar", ""),
        ),
        "SD-KS": (
            Entity("Janūb Kurdufān", "SD-KS", "STATE", "ar", ""),
            Entity("South Kordofan", "SD-KS", "STATE", "en", ""),
        ),
        "SD-NB": (
            Entity("An Nīl al Azraq", "SD-NB", "STATE", "ar", ""),
            Entity("Blue Nile", "SD-NB", "STATE", "en", ""),
        ),
        "SD-NO": (
            Entity("Ash Shamālīyah", "SD-NO", "STATE", "ar", ""),
            Entity("Northern", "SD-NO", "STATE", "en", ""),
        ),
        "SD-NR": (
            Entity("Nahr an Nīl", "SD-NR", "STATE", "ar", ""),
            Entity("River Nile", "SD-NR", "STATE", "en", ""),
        ),
        "SD-NW": (
            Entity("An Nīl al Abyaḑ", "SD-NW", "STATE", "ar", ""),
            Entity("White Nile", "SD-NW", "STATE", "en", ""),
        ),
        "SD-RS": (
            Entity("Al Baḩr al Aḩmar", "SD-RS", "STATE", "ar", ""),
            Entity("Red Sea", "SD-RS", "STATE", "en", ""),
        ),
        "SD-SI": (
            Entity("Sennar", "SD-SI", "STATE", "en", ""),
            Entity("Sinnār", "SD-SI", "STATE", "ar", ""),
        ),
    }
