"""ISO 3166-2 VN standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:VN
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "VN-01": (Entity("Lai Châu", "VN-01", "PROVINCE", "vi", ""),),
        "VN-02": (Entity("Lào Cai", "VN-02", "PROVINCE", "vi", ""),),
        "VN-03": (Entity("Hà Giang", "VN-03", "PROVINCE", "vi", ""),),
        "VN-04": (Entity("Cao Bằng", "VN-04", "PROVINCE", "vi", ""),),
        "VN-05": (Entity("Sơn La", "VN-05", "PROVINCE", "vi", ""),),
        "VN-06": (Entity("Yên Bái", "VN-06", "PROVINCE", "vi", ""),),
        "VN-07": (Entity("Tuyên Quang", "VN-07", "PROVINCE", "vi", ""),),
        "VN-09": (Entity("Lạng Sơn", "VN-09", "PROVINCE", "vi", ""),),
        "VN-13": (Entity("Quảng Ninh", "VN-13", "PROVINCE", "vi", ""),),
        "VN-14": (Entity("Hòa Bình", "VN-14", "PROVINCE", "vi", ""),),
        "VN-18": (Entity("Ninh Bình", "VN-18", "PROVINCE", "vi", ""),),
        "VN-20": (Entity("Thái Bình", "VN-20", "PROVINCE", "vi", ""),),
        "VN-21": (Entity("Thanh Hóa", "VN-21", "PROVINCE", "vi", ""),),
        "VN-22": (Entity("Nghệ An", "VN-22", "PROVINCE", "vi", ""),),
        "VN-23": (Entity("Hà Tĩnh", "VN-23", "PROVINCE", "vi", ""),),
        "VN-24": (Entity("Quảng Bình", "VN-24", "PROVINCE", "vi", ""),),
        "VN-25": (Entity("Quảng Trị", "VN-25", "PROVINCE", "vi", ""),),
        "VN-26": (Entity("Thừa Thiên-Huế", "VN-26", "PROVINCE", "vi", ""),),
        "VN-27": (Entity("Quảng Nam", "VN-27", "PROVINCE", "vi", ""),),
        "VN-28": (Entity("Kon Tum", "VN-28", "PROVINCE", "vi", ""),),
        "VN-29": (Entity("Quảng Ngãi", "VN-29", "PROVINCE", "vi", ""),),
        "VN-30": (Entity("Gia Lai", "VN-30", "PROVINCE", "vi", ""),),
        "VN-31": (Entity("Bình Định", "VN-31", "PROVINCE", "vi", ""),),
        "VN-32": (Entity("Phú Yên", "VN-32", "PROVINCE", "vi", ""),),
        "VN-33": (Entity("Đắk Lắk", "VN-33", "PROVINCE", "vi", ""),),
        "VN-34": (Entity("Khánh Hòa", "VN-34", "PROVINCE", "vi", ""),),
        "VN-35": (Entity("Lâm Đồng", "VN-35", "PROVINCE", "vi", ""),),
        "VN-36": (Entity("Ninh Thuận", "VN-36", "PROVINCE", "vi", ""),),
        "VN-37": (Entity("Tây Ninh", "VN-37", "PROVINCE", "vi", ""),),
        "VN-39": (Entity("Đồng Nai", "VN-39", "PROVINCE", "vi", ""),),
        "VN-40": (Entity("Bình Thuận", "VN-40", "PROVINCE", "vi", ""),),
        "VN-41": (Entity("Long An", "VN-41", "PROVINCE", "vi", ""),),
        "VN-43": (Entity("Bà Rịa - Vũng Tàu", "VN-43", "PROVINCE", "vi", ""),),
        "VN-44": (Entity("An Giang", "VN-44", "PROVINCE", "vi", ""),),
        "VN-45": (Entity("Đồng Tháp", "VN-45", "PROVINCE", "vi", ""),),
        "VN-46": (Entity("Tiền Giang", "VN-46", "PROVINCE", "vi", ""),),
        "VN-47": (Entity("Kiến Giang", "VN-47", "PROVINCE", "vi", ""),),
        "VN-49": (Entity("Vĩnh Long", "VN-49", "PROVINCE", "vi", ""),),
        "VN-50": (Entity("Bến Tre", "VN-50", "PROVINCE", "vi", ""),),
        "VN-51": (Entity("Trà Vinh", "VN-51", "PROVINCE", "vi", ""),),
        "VN-52": (Entity("Sóc Trăng", "VN-52", "PROVINCE", "vi", ""),),
        "VN-53": (Entity("Bắc Kạn", "VN-53", "PROVINCE", "vi", ""),),
        "VN-54": (Entity("Bắc Giang", "VN-54", "PROVINCE", "vi", ""),),
        "VN-55": (Entity("Bạc Liêu", "VN-55", "PROVINCE", "vi", ""),),
        "VN-56": (Entity("Bắc Ninh", "VN-56", "PROVINCE", "vi", ""),),
        "VN-57": (Entity("Bình Dương", "VN-57", "PROVINCE", "vi", ""),),
        "VN-58": (Entity("Bình Phước", "VN-58", "PROVINCE", "vi", ""),),
        "VN-59": (Entity("Cà Mau", "VN-59", "PROVINCE", "vi", ""),),
        "VN-61": (Entity("Hải Dương", "VN-61", "PROVINCE", "vi", ""),),
        "VN-63": (Entity("Hà Nam", "VN-63", "PROVINCE", "vi", ""),),
        "VN-66": (Entity("Hưng Yên", "VN-66", "PROVINCE", "vi", ""),),
        "VN-67": (Entity("Nam Định", "VN-67", "PROVINCE", "vi", ""),),
        "VN-68": (Entity("Phú Thọ", "VN-68", "PROVINCE", "vi", ""),),
        "VN-69": (Entity("Thái Nguyên", "VN-69", "PROVINCE", "vi", ""),),
        "VN-70": (Entity("Vĩnh Phúc", "VN-70", "PROVINCE", "vi", ""),),
        "VN-71": (Entity("Điện Biên", "VN-71", "PROVINCE", "vi", ""),),
        "VN-72": (Entity("Đắk Nông", "VN-72", "PROVINCE", "vi", ""),),
        "VN-73": (Entity("Hậu Giang", "VN-73", "PROVINCE", "vi", ""),),
        "VN-CT": (Entity("Cần Thơ", "VN-CT", "MUNICIPALITY", "vi", ""),),
        "VN-DN": (Entity("Đà Nẵng", "VN-DN", "MUNICIPALITY", "vi", ""),),
        "VN-HN": (Entity("Hà Nội", "VN-HN", "MUNICIPALITY", "vi", ""),),
        "VN-HP": (Entity("Hải Phòng", "VN-HP", "MUNICIPALITY", "vi", ""),),
        "VN-SG": (Entity("Hồ Chí Minh", "VN-SG", "MUNICIPALITY", "vi", ""),),
    }
