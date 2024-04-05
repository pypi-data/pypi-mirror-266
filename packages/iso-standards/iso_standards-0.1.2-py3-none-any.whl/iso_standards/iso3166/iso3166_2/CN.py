"""ISO 3166-2 CN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:CN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "CN-AH": (Entity("Anhui Sheng", "CN-AH", "PROVINCE", "zh", ""),),
        "CN-BJ": (Entity("Beijing Shi", "CN-BJ", "MUNICIPALITY", "zh", ""),),
        "CN-CQ": (Entity("Chongqing Shi", "CN-CQ", "MUNICIPALITY", "zh", ""),),
        "CN-FJ": (Entity("Fujian Sheng", "CN-FJ", "PROVINCE", "zh", ""),),
        "CN-GD": (Entity("Guangdong Sheng", "CN-GD", "PROVINCE", "zh", ""),),
        "CN-GS": (Entity("Gansu Sheng", "CN-GS", "PROVINCE", "zh", ""),),
        "CN-GX": (Entity("Guangxi Zhuangzu Zizhiqu", "CN-GX", "AUTONOMOUS REGION", "zh", ""),),
        "CN-GZ": (Entity("Guizhou Sheng", "CN-GZ", "PROVINCE", "zh", ""),),
        "CN-HA": (Entity("Henan Sheng", "CN-HA", "PROVINCE", "zh", ""),),
        "CN-HB": (Entity("Hubei Sheng", "CN-HB", "PROVINCE", "zh", ""),),
        "CN-HE": (Entity("Hebei Sheng", "CN-HE", "PROVINCE", "zh", ""),),
        "CN-HI": (Entity("Hainan Sheng", "CN-HI", "PROVINCE", "zh", ""),),
        "CN-HK": (
            Entity("Hong Kong SAR", "CN-HK", "SPECIAL ADMINISTRATIVE REGION", "en", ""),
            Entity(
                "Xianggang Tebiexingzhengqu", "CN-HK", "SPECIAL ADMINISTRATIVE REGION", "zh", ""
            ),
        ),
        "CN-HL": (Entity("Heilongjiang Sheng", "CN-HL", "PROVINCE", "zh", ""),),
        "CN-HN": (Entity("Hunan Sheng", "CN-HN", "PROVINCE", "zh", ""),),
        "CN-JL": (Entity("Jilin Sheng", "CN-JL", "PROVINCE", "zh", ""),),
        "CN-JS": (Entity("Jiangsu Sheng", "CN-JS", "PROVINCE", "zh", ""),),
        "CN-JX": (Entity("Jiangxi Sheng", "CN-JX", "PROVINCE", "zh", ""),),
        "CN-LN": (Entity("Liaoning Sheng", "CN-LN", "PROVINCE", "zh", ""),),
        "CN-MO": (
            Entity("Aomen Tebiexingzhengqu", "CN-MO", "SPECIAL ADMINISTRATIVE REGION", "zh", ""),
            Entity("Macao SAR", "CN-MO", "SPECIAL ADMINISTRATIVE REGION", "en", ""),
            Entity("Macau SAR", "CN-MO", "SPECIAL ADMINISTRATIVE REGION", "pt", ""),
        ),
        "CN-NM": (Entity("Nei Mongol Zizhiqu", "CN-NM", "AUTONOMOUS REGION", "zh", ""),),
        "CN-NX": (Entity("Ningxia Huizu Zizhiqu", "CN-NX", "AUTONOMOUS REGION", "zh", ""),),
        "CN-QH": (Entity("Qinghai Sheng", "CN-QH", "PROVINCE", "zh", ""),),
        "CN-SC": (Entity("Sichuan Sheng", "CN-SC", "PROVINCE", "zh", ""),),
        "CN-SD": (Entity("Shandong Sheng", "CN-SD", "PROVINCE", "zh", ""),),
        "CN-SH": (Entity("Shanghai Shi", "CN-SH", "MUNICIPALITY", "zh", ""),),
        "CN-SN": (Entity("Shaanxi Sheng", "CN-SN", "PROVINCE", "zh", ""),),
        "CN-SX": (Entity("Shanxi Sheng", "CN-SX", "PROVINCE", "zh", ""),),
        "CN-TJ": (Entity("Tianjin Shi", "CN-TJ", "MUNICIPALITY", "zh", ""),),
        "CN-TW": (Entity("Taiwan Sheng", "CN-TW", "PROVINCE", "zh", ""),),
        "CN-XJ": (Entity("Xinjiang Uygur Zizhiqu", "CN-XJ", "AUTONOMOUS REGION", "zh", ""),),
        "CN-XZ": (Entity("Xizang Zizhiqu", "CN-XZ", "AUTONOMOUS REGION", "zh", ""),),
        "CN-YN": (Entity("Yunnan Sheng", "CN-YN", "PROVINCE", "zh", ""),),
        "CN-ZJ": (Entity("Zhejiang Sheng", "CN-ZJ", "PROVINCE", "zh", ""),),
    }
