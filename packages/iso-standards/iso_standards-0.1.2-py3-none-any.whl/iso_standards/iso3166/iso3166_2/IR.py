"""ISO 3166-2 IR standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:IR
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "IR-00": (Entity("Markazī", "IR-00", "PROVINCE", "fa", ""),),
        "IR-01": (Entity("Gīlān", "IR-01", "PROVINCE", "fa", ""),),
        "IR-02": (Entity("Māzandarān", "IR-02", "PROVINCE", "fa", ""),),
        "IR-03": (Entity("Āz̄ārbāyjān-e Shārqī", "IR-03", "PROVINCE", "fa", ""),),
        "IR-04": (Entity("Āz̄ārbāyjān-e Ghārbī", "IR-04", "PROVINCE", "fa", ""),),
        "IR-05": (Entity("Kermānshāh", "IR-05", "PROVINCE", "fa", ""),),
        "IR-06": (Entity("Khūzestān", "IR-06", "PROVINCE", "fa", ""),),
        "IR-07": (Entity("Fārs", "IR-07", "PROVINCE", "fa", ""),),
        "IR-08": (Entity("Kermān", "IR-08", "PROVINCE", "fa", ""),),
        "IR-09": (Entity("Khorāsān-e Raẕavī", "IR-09", "PROVINCE", "fa", ""),),
        "IR-10": (Entity("Eşfahān", "IR-10", "PROVINCE", "fa", ""),),
        "IR-11": (Entity("Sīstān va Balūchestān", "IR-11", "PROVINCE", "fa", ""),),
        "IR-12": (Entity("Kordestān", "IR-12", "PROVINCE", "fa", ""),),
        "IR-13": (Entity("Hamadān", "IR-13", "PROVINCE", "fa", ""),),
        "IR-14": (Entity("Chahār Maḩāl va Bakhtīārī", "IR-14", "PROVINCE", "fa", ""),),
        "IR-15": (Entity("Lorestān", "IR-15", "PROVINCE", "fa", ""),),
        "IR-16": (Entity("Īlām", "IR-16", "PROVINCE", "fa", ""),),
        "IR-17": (Entity("Kohgīlūyeh va Bowyer Aḩmad", "IR-17", "PROVINCE", "fa", ""),),
        "IR-18": (Entity("Būshehr", "IR-18", "PROVINCE", "fa", ""),),
        "IR-19": (Entity("Zanjān", "IR-19", "PROVINCE", "fa", ""),),
        "IR-20": (Entity("Semnān", "IR-20", "PROVINCE", "fa", ""),),
        "IR-21": (Entity("Yazd", "IR-21", "PROVINCE", "fa", ""),),
        "IR-22": (Entity("Hormozgān", "IR-22", "PROVINCE", "fa", ""),),
        "IR-23": (Entity("Tehrān", "IR-23", "PROVINCE", "fa", ""),),
        "IR-24": (Entity("Ardabīl", "IR-24", "PROVINCE", "fa", ""),),
        "IR-25": (Entity("Qom", "IR-25", "PROVINCE", "fa", ""),),
        "IR-26": (Entity("Qazvīn", "IR-26", "PROVINCE", "fa", ""),),
        "IR-27": (Entity("Golestān", "IR-27", "PROVINCE", "fa", ""),),
        "IR-28": (Entity("Khorāsān-e Shomālī", "IR-28", "PROVINCE", "fa", ""),),
        "IR-29": (Entity("Khorāsān-e Jonūbī", "IR-29", "PROVINCE", "fa", ""),),
        "IR-30": (Entity("Alborz", "IR-30", "PROVINCE", "fa", ""),),
    }
