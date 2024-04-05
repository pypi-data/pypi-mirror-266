"""ISO 3166-2 TW standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:TW
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "TW-CHA": (Entity("Changhua", "TW-CHA", "COUNTY", "zh", ""),),
        "TW-CYI": (Entity("Chiayi", "TW-CYI", "CITY", "zh", ""),),
        "TW-CYQ": (Entity("Chiayi", "TW-CYQ", "COUNTY", "zh", ""),),
        "TW-HSQ": (Entity("Hsinchu", "TW-HSQ", "COUNTY", "zh", ""),),
        "TW-HSZ": (Entity("Hsinchu", "TW-HSZ", "CITY", "zh", ""),),
        "TW-HUA": (Entity("Hualien", "TW-HUA", "COUNTY", "zh", ""),),
        "TW-ILA": (Entity("Yilan", "TW-ILA", "COUNTY", "zh", ""),),
        "TW-KEE": (Entity("Keelung", "TW-KEE", "CITY", "zh", ""),),
        "TW-KHH": (Entity("Kaohsiung", "TW-KHH", "SPECIAL MUNICIPALITY", "zh", ""),),
        "TW-KIN": (Entity("Kinmen", "TW-KIN", "COUNTY", "zh", ""),),
        "TW-LIE": (Entity("Lienchiang", "TW-LIE", "COUNTY", "zh", ""),),
        "TW-MIA": (Entity("Miaoli", "TW-MIA", "COUNTY", "zh", ""),),
        "TW-NAN": (Entity("Nantou", "TW-NAN", "COUNTY", "zh", ""),),
        "TW-NWT": (Entity("New Taipei", "TW-NWT", "SPECIAL MUNICIPALITY", "zh", ""),),
        "TW-PEN": (Entity("Penghu", "TW-PEN", "COUNTY", "zh", ""),),
        "TW-PIF": (Entity("Pingtung", "TW-PIF", "COUNTY", "zh", ""),),
        "TW-TAO": (Entity("Taoyuan", "TW-TAO", "SPECIAL MUNICIPALITY", "zh", ""),),
        "TW-TNN": (Entity("Tainan", "TW-TNN", "SPECIAL MUNICIPALITY", "zh", ""),),
        "TW-TPE": (Entity("Taipei", "TW-TPE", "SPECIAL MUNICIPALITY", "zh", ""),),
        "TW-TTT": (Entity("Taitung", "TW-TTT", "COUNTY", "zh", ""),),
        "TW-TXG": (Entity("Taichung", "TW-TXG", "SPECIAL MUNICIPALITY", "zh", ""),),
        "TW-YUN": (Entity("Yunlin", "TW-YUN", "COUNTY", "zh", ""),),
    }
