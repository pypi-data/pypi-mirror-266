"""ISO 3166-2 JP standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:JP
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "JP-01": (
            Entity("Hokkaido", "JP-01", "PREFECTURE", "en", ""),
            Entity("Hokkaidô", "JP-01", "PREFECTURE", "ja", ""),
        ),
        "JP-02": (Entity("Aomori", "JP-02", "PREFECTURE", "ja", ""),),
        "JP-03": (Entity("Iwate", "JP-03", "PREFECTURE", "ja", ""),),
        "JP-04": (Entity("Miyagi", "JP-04", "PREFECTURE", "ja", ""),),
        "JP-05": (Entity("Akita", "JP-05", "PREFECTURE", "ja", ""),),
        "JP-06": (Entity("Yamagata", "JP-06", "PREFECTURE", "ja", ""),),
        "JP-07": (
            Entity("Fukushima", "JP-07", "PREFECTURE", "en", ""),
            Entity("Hukusima", "JP-07", "PREFECTURE", "ja", ""),
        ),
        "JP-08": (Entity("Ibaraki", "JP-08", "PREFECTURE", "ja", ""),),
        "JP-09": (
            Entity("Tochigi", "JP-09", "PREFECTURE", "en", ""),
            Entity("Totigi", "JP-09", "PREFECTURE", "ja", ""),
        ),
        "JP-10": (Entity("Gunma", "JP-10", "PREFECTURE", "ja", ""),),
        "JP-11": (Entity("Saitama", "JP-11", "PREFECTURE", "ja", ""),),
        "JP-12": (
            Entity("Chiba", "JP-12", "PREFECTURE", "en", ""),
            Entity("Tiba", "JP-12", "PREFECTURE", "ja", ""),
        ),
        "JP-13": (
            Entity("Tokyo", "JP-13", "PREFECTURE", "en", ""),
            Entity("Tôkyô", "JP-13", "PREFECTURE", "ja", ""),
        ),
        "JP-14": (Entity("Kanagawa", "JP-14", "PREFECTURE", "ja", ""),),
        "JP-15": (Entity("Niigata", "JP-15", "PREFECTURE", "ja", ""),),
        "JP-16": (Entity("Toyama", "JP-16", "PREFECTURE", "ja", ""),),
        "JP-17": (
            Entity("Ishikawa", "JP-17", "PREFECTURE", "en", ""),
            Entity("Isikawa", "JP-17", "PREFECTURE", "ja", ""),
        ),
        "JP-18": (
            Entity("Fukui", "JP-18", "PREFECTURE", "en", ""),
            Entity("Hukui", "JP-18", "PREFECTURE", "ja", ""),
        ),
        "JP-19": (
            Entity("Yamanashi", "JP-19", "PREFECTURE", "en", ""),
            Entity("Yamanasi", "JP-19", "PREFECTURE", "ja", ""),
        ),
        "JP-20": (Entity("Nagano", "JP-20", "PREFECTURE", "ja", ""),),
        "JP-21": (
            Entity("Gifu", "JP-21", "PREFECTURE", "en", ""),
            Entity("Gihu", "JP-21", "PREFECTURE", "ja", ""),
        ),
        "JP-22": (
            Entity("Shizuoka", "JP-22", "PREFECTURE", "en", ""),
            Entity("Sizuoka", "JP-22", "PREFECTURE", "ja", ""),
        ),
        "JP-23": (
            Entity("Aichi", "JP-23", "PREFECTURE", "en", ""),
            Entity("Aiti", "JP-23", "PREFECTURE", "ja", ""),
        ),
        "JP-24": (Entity("Mie", "JP-24", "PREFECTURE", "ja", ""),),
        "JP-25": (
            Entity("Shiga", "JP-25", "PREFECTURE", "en", ""),
            Entity("Siga", "JP-25", "PREFECTURE", "ja", ""),
        ),
        "JP-26": (
            Entity("Kyoto", "JP-26", "PREFECTURE", "en", ""),
            Entity("Kyôto", "JP-26", "PREFECTURE", "ja", ""),
        ),
        "JP-27": (
            Entity("Osaka", "JP-27", "PREFECTURE", "en", ""),
            Entity("Ôsaka", "JP-27", "PREFECTURE", "ja", ""),
        ),
        "JP-28": (
            Entity("Hyogo", "JP-28", "PREFECTURE", "en", ""),
            Entity("Hyôgo", "JP-28", "PREFECTURE", "ja", ""),
        ),
        "JP-29": (Entity("Nara", "JP-29", "PREFECTURE", "ja", ""),),
        "JP-30": (Entity("Wakayama", "JP-30", "PREFECTURE", "ja", ""),),
        "JP-31": (Entity("Tottori", "JP-31", "PREFECTURE", "ja", ""),),
        "JP-32": (
            Entity("Shimane", "JP-32", "PREFECTURE", "en", ""),
            Entity("Simane", "JP-32", "PREFECTURE", "ja", ""),
        ),
        "JP-33": (Entity("Okayama", "JP-33", "PREFECTURE", "ja", ""),),
        "JP-34": (
            Entity("Hiroshima", "JP-34", "PREFECTURE", "en", ""),
            Entity("Hirosima", "JP-34", "PREFECTURE", "ja", ""),
        ),
        "JP-35": (
            Entity("Yamaguchi", "JP-35", "PREFECTURE", "en", ""),
            Entity("Yamaguti", "JP-35", "PREFECTURE", "ja", ""),
        ),
        "JP-36": (
            Entity("Tokushima", "JP-36", "PREFECTURE", "en", ""),
            Entity("Tokusima", "JP-36", "PREFECTURE", "ja", ""),
        ),
        "JP-37": (Entity("Kagawa", "JP-37", "PREFECTURE", "ja", ""),),
        "JP-38": (Entity("Ehime", "JP-38", "PREFECTURE", "ja", ""),),
        "JP-39": (
            Entity("Kochi", "JP-39", "PREFECTURE", "en", ""),
            Entity("Kôti", "JP-39", "PREFECTURE", "ja", ""),
        ),
        "JP-40": (
            Entity("Fukuoka", "JP-40", "PREFECTURE", "en", ""),
            Entity("Hukuoka", "JP-40", "PREFECTURE", "ja", ""),
        ),
        "JP-41": (Entity("Saga", "JP-41", "PREFECTURE", "ja", ""),),
        "JP-42": (Entity("Nagasaki", "JP-42", "PREFECTURE", "ja", ""),),
        "JP-43": (Entity("Kumamoto", "JP-43", "PREFECTURE", "ja", ""),),
        "JP-44": (
            Entity("Oita", "JP-44", "PREFECTURE", "en", ""),
            Entity("Ôita", "JP-44", "PREFECTURE", "ja", ""),
        ),
        "JP-45": (Entity("Miyazaki", "JP-45", "PREFECTURE", "ja", ""),),
        "JP-46": (
            Entity("Kagoshima", "JP-46", "PREFECTURE", "en", ""),
            Entity("Kagosima", "JP-46", "PREFECTURE", "ja", ""),
        ),
        "JP-47": (Entity("Okinawa", "JP-47", "PREFECTURE", "ja", ""),),
    }
