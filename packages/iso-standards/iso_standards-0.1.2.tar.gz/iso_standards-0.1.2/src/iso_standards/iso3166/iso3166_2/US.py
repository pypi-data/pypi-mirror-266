"""ISO 3166-2 US standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:US
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "US-AK": (Entity("Alaska", "US-AK", "STATE", "en", ""),),
        "US-AL": (Entity("Alabama", "US-AL", "STATE", "en", ""),),
        "US-AR": (Entity("Arkansas", "US-AR", "STATE", "en", ""),),
        "US-AS": (Entity("American Samoa", "US-AS", "OUTLYING AREA", "en", ""),),
        "US-AZ": (Entity("Arizona", "US-AZ", "STATE", "en", ""),),
        "US-CA": (Entity("California", "US-CA", "STATE", "en", ""),),
        "US-CO": (Entity("Colorado", "US-CO", "STATE", "en", ""),),
        "US-CT": (Entity("Connecticut", "US-CT", "STATE", "en", ""),),
        "US-DC": (Entity("District of Columbia", "US-DC", "DISTRICT", "en", ""),),
        "US-DE": (Entity("Delaware", "US-DE", "STATE", "en", ""),),
        "US-FL": (Entity("Florida", "US-FL", "STATE", "en", ""),),
        "US-GA": (Entity("Georgia", "US-GA", "STATE", "en", ""),),
        "US-GU": (Entity("Guam", "US-GU", "OUTLYING AREA", "en", ""),),
        "US-HI": (Entity("Hawaii", "US-HI", "STATE", "en", ""),),
        "US-IA": (Entity("Iowa", "US-IA", "STATE", "en", ""),),
        "US-ID": (Entity("Idaho", "US-ID", "STATE", "en", ""),),
        "US-IL": (Entity("Illinois", "US-IL", "STATE", "en", ""),),
        "US-IN": (Entity("Indiana", "US-IN", "STATE", "en", ""),),
        "US-KS": (Entity("Kansas", "US-KS", "STATE", "en", ""),),
        "US-KY": (Entity("Kentucky", "US-KY", "STATE", "en", ""),),
        "US-LA": (Entity("Louisiana", "US-LA", "STATE", "en", ""),),
        "US-MA": (Entity("Massachusetts", "US-MA", "STATE", "en", ""),),
        "US-MD": (Entity("Maryland", "US-MD", "STATE", "en", ""),),
        "US-ME": (Entity("Maine", "US-ME", "STATE", "en", ""),),
        "US-MI": (Entity("Michigan", "US-MI", "STATE", "en", ""),),
        "US-MN": (Entity("Minnesota", "US-MN", "STATE", "en", ""),),
        "US-MO": (Entity("Missouri", "US-MO", "STATE", "en", ""),),
        "US-MP": (Entity("Northern Mariana Islands", "US-MP", "OUTLYING AREA", "en", ""),),
        "US-MS": (Entity("Mississippi", "US-MS", "STATE", "en", ""),),
        "US-MT": (Entity("Montana", "US-MT", "STATE", "en", ""),),
        "US-NC": (Entity("North Carolina", "US-NC", "STATE", "en", ""),),
        "US-ND": (Entity("North Dakota", "US-ND", "STATE", "en", ""),),
        "US-NE": (Entity("Nebraska", "US-NE", "STATE", "en", ""),),
        "US-NH": (Entity("New Hampshire", "US-NH", "STATE", "en", ""),),
        "US-NJ": (Entity("New Jersey", "US-NJ", "STATE", "en", ""),),
        "US-NM": (Entity("New Mexico", "US-NM", "STATE", "en", ""),),
        "US-NV": (Entity("Nevada", "US-NV", "STATE", "en", ""),),
        "US-NY": (Entity("New York", "US-NY", "STATE", "en", ""),),
        "US-OH": (Entity("Ohio", "US-OH", "STATE", "en", ""),),
        "US-OK": (Entity("Oklahoma", "US-OK", "STATE", "en", ""),),
        "US-OR": (Entity("Oregon", "US-OR", "STATE", "en", ""),),
        "US-PA": (Entity("Pennsylvania", "US-PA", "STATE", "en", ""),),
        "US-PR": (Entity("Puerto Rico", "US-PR", "OUTLYING AREA", "en", ""),),
        "US-RI": (Entity("Rhode Island", "US-RI", "STATE", "en", ""),),
        "US-SC": (Entity("South Carolina", "US-SC", "STATE", "en", ""),),
        "US-SD": (Entity("South Dakota", "US-SD", "STATE", "en", ""),),
        "US-TN": (Entity("Tennessee", "US-TN", "STATE", "en", ""),),
        "US-TX": (Entity("Texas", "US-TX", "STATE", "en", ""),),
        "US-UM": (
            Entity("United States Minor Outlying Islands", "US-UM", "OUTLYING AREA", "en", ""),
        ),
        "US-UT": (Entity("Utah", "US-UT", "STATE", "en", ""),),
        "US-VA": (Entity("Virginia", "US-VA", "STATE", "en", ""),),
        "US-VI": (Entity("Virgin Islands", "US-VI", "OUTLYING AREA", "en", ""),),
        "US-VT": (Entity("Vermont", "US-VT", "STATE", "en", ""),),
        "US-WA": (Entity("Washington", "US-WA", "STATE", "en", ""),),
        "US-WI": (Entity("Wisconsin", "US-WI", "STATE", "en", ""),),
        "US-WV": (Entity("West Virginia", "US-WV", "STATE", "en", ""),),
        "US-WY": (Entity("Wyoming", "US-WY", "STATE", "en", ""),),
    }
