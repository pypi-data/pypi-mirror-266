"""ISO 3166-2 PH standard representation.

References:
  - https://en.wikipedia.org/wiki/ISO_3166-2
  - https://www.iso.org/obp/ui/#iso:code:3166:PH
"""

from iso_standards.base import EntityCollection
from iso_standards.iso3166.types import Iso3166_2 as Entity


class Iso3166_2(EntityCollection):
    __slots__ = ()

    entities = {
        "PH-00": (
            Entity("National Capital Region", "PH-00", "REGION", "en", ""),
            Entity("Pambansang Punong Rehiyon", "PH-00", "REGION", "tl", ""),
        ),
        "PH-01": (
            Entity("Ilocos", "PH-01", "REGION", "en", ""),
            Entity("Rehiyon ng Iloko", "PH-01", "REGION", "tl", ""),
        ),
        "PH-02": (
            Entity("Cagayan Valley", "PH-02", "REGION", "en", ""),
            Entity("Rehiyon ng Lambak ng Kagayan", "PH-02", "REGION", "tl", ""),
        ),
        "PH-03": (
            Entity("Central Luzon", "PH-03", "REGION", "en", ""),
            Entity("Rehiyon ng Gitnang Luson", "PH-03", "REGION", "tl", ""),
        ),
        "PH-05": (
            Entity("Bicol", "PH-05", "REGION", "en", ""),
            Entity("Rehiyon ng Bikol", "PH-05", "REGION", "tl", ""),
        ),
        "PH-06": (
            Entity("Rehiyon ng Kanlurang Bisaya", "PH-06", "REGION", "tl", ""),
            Entity("Western Visayas", "PH-06", "REGION", "en", ""),
        ),
        "PH-07": (
            Entity("Central Visayas", "PH-07", "REGION", "en", ""),
            Entity("Rehiyon ng Gitnang Bisaya", "PH-07", "REGION", "tl", ""),
        ),
        "PH-08": (
            Entity("Eastern Visayas", "PH-08", "REGION", "en", ""),
            Entity("Rehiyon ng Silangang Bisaya", "PH-08", "REGION", "tl", ""),
        ),
        "PH-09": (
            Entity("Rehiyon ng Tangway ng Sambuwangga", "PH-09", "REGION", "tl", ""),
            Entity("Zamboanga Peninsula", "PH-09", "REGION", "en", ""),
        ),
        "PH-10": (
            Entity("Northern Mindanao", "PH-10", "REGION", "en", ""),
            Entity("Rehiyon ng Hilagang Mindanaw", "PH-10", "REGION", "tl", ""),
        ),
        "PH-11": (
            Entity("Davao", "PH-11", "REGION", "en", ""),
            Entity("Rehiyon ng Dabaw", "PH-11", "REGION", "tl", ""),
        ),
        "PH-12": (
            Entity("Rehiyon ng Soccsksargen", "PH-12", "REGION", "tl", ""),
            Entity("Soccsksargen", "PH-12", "REGION", "en", ""),
        ),
        "PH-13": (
            Entity("Caraga", "PH-13", "REGION", "en", ""),
            Entity("Rehiyon ng Karaga", "PH-13", "REGION", "tl", ""),
        ),
        "PH-14": (
            Entity("Autonomous Region in Muslim Mindanao", "PH-14", "REGION", "en", ""),
            Entity("Nagsasariling Rehiyon ng Muslim sa Mindanaw", "PH-14", "REGION", "tl", ""),
        ),
        "PH-15": (
            Entity("Cordillera Administrative Region", "PH-15", "REGION", "en", ""),
            Entity("Rehiyon ng Administratibo ng Kordilyera", "PH-15", "REGION", "tl", ""),
        ),
        "PH-40": (
            Entity("Calabarzon", "PH-40", "REGION", "en", ""),
            Entity("Rehiyon ng Calabarzon", "PH-40", "REGION", "tl", ""),
        ),
        "PH-41": (
            Entity("Mimaropa", "PH-41", "REGION", "en", ""),
            Entity("Rehiyon ng Mimaropa", "PH-41", "REGION", "tl", ""),
        ),
        "PH-ABR": (
            Entity("Abra", "PH-ABR", "PROVINCE", "en", "PH-15"),
            Entity("Abra", "PH-ABR", "PROVINCE", "tl", "PH-15"),
        ),
        "PH-AGN": (
            Entity("Agusan del Norte", "PH-AGN", "PROVINCE", "en", "PH-13"),
            Entity("Hilagang Agusan", "PH-AGN", "PROVINCE", "tl", "PH-13"),
        ),
        "PH-AGS": (
            Entity("Agusan del Sur", "PH-AGS", "PROVINCE", "en", "PH-13"),
            Entity("Timog Agusan", "PH-AGS", "PROVINCE", "tl", "PH-13"),
        ),
        "PH-AKL": (
            Entity("Aklan", "PH-AKL", "PROVINCE", "en", "PH-06"),
            Entity("Aklan", "PH-AKL", "PROVINCE", "tl", "PH-06"),
        ),
        "PH-ALB": (
            Entity("Albay", "PH-ALB", "PROVINCE", "en", "PH-05"),
            Entity("Albay", "PH-ALB", "PROVINCE", "tl", "PH-05"),
        ),
        "PH-ANT": (
            Entity("Antike", "PH-ANT", "PROVINCE", "tl", "PH-06"),
            Entity("Antique", "PH-ANT", "PROVINCE", "en", "PH-06"),
        ),
        "PH-APA": (
            Entity("Apayao", "PH-APA", "PROVINCE", "en", "PH-15"),
            Entity("Apayaw", "PH-APA", "PROVINCE", "tl", "PH-15"),
        ),
        "PH-AUR": (
            Entity("Aurora", "PH-AUR", "PROVINCE", "en", "PH-03"),
            Entity("Aurora", "PH-AUR", "PROVINCE", "tl", "PH-03"),
        ),
        "PH-BAN": (
            Entity("Bataan", "PH-BAN", "PROVINCE", "en", "PH-03"),
            Entity("Bataan", "PH-BAN", "PROVINCE", "tl", "PH-03"),
        ),
        "PH-BAS": (
            Entity("Basilan", "PH-BAS", "PROVINCE", "en", "PH-09"),
            Entity("Basilan", "PH-BAS", "PROVINCE", "tl", "PH-09"),
        ),
        "PH-BEN": (
            Entity("Benget", "PH-BEN", "PROVINCE", "tl", "PH-15"),
            Entity("Benguet", "PH-BEN", "PROVINCE", "en", "PH-15"),
        ),
        "PH-BIL": (
            Entity("Biliran", "PH-BIL", "PROVINCE", "en", "PH-08"),
            Entity("Biliran", "PH-BIL", "PROVINCE", "tl", "PH-08"),
        ),
        "PH-BOH": (
            Entity("Bohol", "PH-BOH", "PROVINCE", "en", "PH-07"),
            Entity("Bohol", "PH-BOH", "PROVINCE", "tl", "PH-07"),
        ),
        "PH-BTG": (
            Entity("Batangas", "PH-BTG", "PROVINCE", "en", "PH-40"),
            Entity("Batangas", "PH-BTG", "PROVINCE", "tl", "PH-40"),
        ),
        "PH-BTN": (
            Entity("Batanes", "PH-BTN", "PROVINCE", "en", "PH-02"),
            Entity("Batanes", "PH-BTN", "PROVINCE", "tl", "PH-02"),
        ),
        "PH-BUK": (
            Entity("Bukidnon", "PH-BUK", "PROVINCE", "en", "PH-10"),
            Entity("Bukidnon", "PH-BUK", "PROVINCE", "tl", "PH-10"),
        ),
        "PH-BUL": (
            Entity("Bulacan", "PH-BUL", "PROVINCE", "en", "PH-03"),
            Entity("Bulakan", "PH-BUL", "PROVINCE", "tl", "PH-03"),
        ),
        "PH-CAG": (
            Entity("Cagayan", "PH-CAG", "PROVINCE", "en", "PH-02"),
            Entity("Kagayan", "PH-CAG", "PROVINCE", "tl", "PH-02"),
        ),
        "PH-CAM": (
            Entity("Camiguin", "PH-CAM", "PROVINCE", "en", "PH-10"),
            Entity("Kamigin", "PH-CAM", "PROVINCE", "tl", "PH-10"),
        ),
        "PH-CAN": (
            Entity("Camarines Norte", "PH-CAN", "PROVINCE", "en", "PH-05"),
            Entity("Hilagang Kamarines", "PH-CAN", "PROVINCE", "tl", "PH-05"),
        ),
        "PH-CAP": (
            Entity("Capiz", "PH-CAP", "PROVINCE", "en", "PH-06"),
            Entity("Kapis", "PH-CAP", "PROVINCE", "tl", "PH-06"),
        ),
        "PH-CAS": (
            Entity("Camarines Sur", "PH-CAS", "PROVINCE", "en", "PH-05"),
            Entity("Timog Kamarines", "PH-CAS", "PROVINCE", "tl", "PH-05"),
        ),
        "PH-CAT": (
            Entity("Catanduanes", "PH-CAT", "PROVINCE", "en", "PH-05"),
            Entity("Katanduwanes", "PH-CAT", "PROVINCE", "tl", "PH-05"),
        ),
        "PH-CAV": (
            Entity("Cavite", "PH-CAV", "PROVINCE", "en", "PH-40"),
            Entity("Kabite", "PH-CAV", "PROVINCE", "tl", "PH-40"),
        ),
        "PH-CEB": (
            Entity("Cebu", "PH-CEB", "PROVINCE", "en", "PH-07"),
            Entity("Sebu", "PH-CEB", "PROVINCE", "tl", "PH-07"),
        ),
        "PH-COM": (Entity("Davao de Oro", "PH-COM", "PROVINCE", "en", "PH-11"),),
        "PH-DAO": (
            Entity("Davao Oriental", "PH-DAO", "PROVINCE", "en", "PH-11"),
            Entity("Silangang Dabaw", "PH-DAO", "PROVINCE", "tl", "PH-11"),
        ),
        "PH-DAS": (
            Entity("Davao del Sur", "PH-DAS", "PROVINCE", "en", "PH-11"),
            Entity("Timog Dabaw", "PH-DAS", "PROVINCE", "tl", "PH-11"),
        ),
        "PH-DAV": (
            Entity("Davao del Norte", "PH-DAV", "PROVINCE", "en", "PH-11"),
            Entity("Hilagang Dabaw", "PH-DAV", "PROVINCE", "tl", "PH-11"),
        ),
        "PH-DIN": (
            Entity("Dinagat Islands", "PH-DIN", "PROVINCE", "en", "PH-13"),
            Entity("Pulo ng Dinagat", "PH-DIN", "PROVINCE", "tl", "PH-13"),
        ),
        "PH-DVO": (
            Entity("Davao Occidental", "PH-DVO", "PROVINCE", "en", "PH-11"),
            Entity("Kanlurang Dabaw", "PH-DVO", "PROVINCE", "tl", "PH-11"),
        ),
        "PH-EAS": (
            Entity("Eastern Samar", "PH-EAS", "PROVINCE", "en", "PH-08"),
            Entity("Silangang Samar", "PH-EAS", "PROVINCE", "tl", "PH-08"),
        ),
        "PH-GUI": (
            Entity("Gimaras", "PH-GUI", "PROVINCE", "tl", "PH-06"),
            Entity("Guimaras", "PH-GUI", "PROVINCE", "en", "PH-06"),
        ),
        "PH-IFU": (
            Entity("Ifugao", "PH-IFU", "PROVINCE", "en", "PH-15"),
            Entity("Ipugaw", "PH-IFU", "PROVINCE", "tl", "PH-15"),
        ),
        "PH-ILI": (
            Entity("Iloilo", "PH-ILI", "PROVINCE", "en", "PH-06"),
            Entity("Iloilo", "PH-ILI", "PROVINCE", "tl", "PH-06"),
        ),
        "PH-ILN": (
            Entity("Hilagang Iloko", "PH-ILN", "PROVINCE", "tl", "PH-01"),
            Entity("Ilocos Norte", "PH-ILN", "PROVINCE", "en", "PH-01"),
        ),
        "PH-ILS": (
            Entity("Ilocos Sur", "PH-ILS", "PROVINCE", "en", "PH-01"),
            Entity("Timog Iloko", "PH-ILS", "PROVINCE", "tl", "PH-01"),
        ),
        "PH-ISA": (
            Entity("Isabela", "PH-ISA", "PROVINCE", "en", "PH-02"),
            Entity("Isabela", "PH-ISA", "PROVINCE", "tl", "PH-02"),
        ),
        "PH-KAL": (
            Entity("Kalinga", "PH-KAL", "PROVINCE", "en", "PH-15"),
            Entity("Kalinga", "PH-KAL", "PROVINCE", "tl", "PH-15"),
        ),
        "PH-LAG": (
            Entity("Laguna", "PH-LAG", "PROVINCE", "en", "PH-40"),
            Entity("Laguna", "PH-LAG", "PROVINCE", "tl", "PH-40"),
        ),
        "PH-LAN": (
            Entity("Hilagang Lanaw", "PH-LAN", "PROVINCE", "tl", "PH-12"),
            Entity("Lanao del Norte", "PH-LAN", "PROVINCE", "en", "PH-12"),
        ),
        "PH-LAS": (
            Entity("Lanao del Sur", "PH-LAS", "PROVINCE", "en", "PH-14"),
            Entity("Timog Lanaw", "PH-LAS", "PROVINCE", "tl", "PH-14"),
        ),
        "PH-LEY": (
            Entity("Leyte", "PH-LEY", "PROVINCE", "en", "PH-08"),
            Entity("Leyte", "PH-LEY", "PROVINCE", "tl", "PH-08"),
        ),
        "PH-LUN": (
            Entity("La Union", "PH-LUN", "PROVINCE", "en", "PH-01"),
            Entity("La Unyon", "PH-LUN", "PROVINCE", "tl", "PH-01"),
        ),
        "PH-MAD": (
            Entity("Marinduke", "PH-MAD", "PROVINCE", "tl", "PH-41"),
            Entity("Marinduque", "PH-MAD", "PROVINCE", "en", "PH-41"),
        ),
        "PH-MAS": (
            Entity("Masbate", "PH-MAS", "PROVINCE", "en", "PH-05"),
            Entity("Masbate", "PH-MAS", "PROVINCE", "tl", "PH-05"),
        ),
        "PH-MDC": (
            Entity("Kanlurang Mindoro", "PH-MDC", "PROVINCE", "tl", "PH-41"),
            Entity("Mindoro Occidental", "PH-MDC", "PROVINCE", "en", "PH-41"),
        ),
        "PH-MDR": (
            Entity("Mindoro Oriental", "PH-MDR", "PROVINCE", "en", "PH-41"),
            Entity("Silangang Mindoro", "PH-MDR", "PROVINCE", "tl", "PH-41"),
        ),
        "PH-MGN": (
            Entity("Hilagang Magindanaw", "PH-MGN", "PROVINCE", "tl", "PH-14"),
            Entity("Maguindanao del Norte", "PH-MGN", "PROVINCE", "en", "PH-14"),
        ),
        "PH-MGS": (
            Entity("Maguindanao del Sur", "PH-MGS", "PROVINCE", "en", "PH-14"),
            Entity("Timog Magindanaw", "PH-MGS", "PROVINCE", "tl", "PH-14"),
        ),
        "PH-MOU": (
            Entity("Lalawigang Bulubundukin", "PH-MOU", "PROVINCE", "tl", "PH-15"),
            Entity("Mountain Province", "PH-MOU", "PROVINCE", "en", "PH-15"),
        ),
        "PH-MSC": (
            Entity("Kanlurang Misamis", "PH-MSC", "PROVINCE", "tl", "PH-10"),
            Entity("Misamis Occidental", "PH-MSC", "PROVINCE", "en", "PH-10"),
        ),
        "PH-MSR": (
            Entity("Misamis Oriental", "PH-MSR", "PROVINCE", "en", "PH-10"),
            Entity("Silangang Misamis", "PH-MSR", "PROVINCE", "tl", "PH-10"),
        ),
        "PH-NCO": (
            Entity("Cotabato", "PH-NCO", "PROVINCE", "en", "PH-12"),
            Entity("Kotabato", "PH-NCO", "PROVINCE", "tl", "PH-12"),
        ),
        "PH-NEC": (
            Entity("Kanlurang Negros", "PH-NEC", "PROVINCE", "tl", "PH-06"),
            Entity("Negros Occidental", "PH-NEC", "PROVINCE", "en", "PH-06"),
        ),
        "PH-NER": (
            Entity("Negros Oriental", "PH-NER", "PROVINCE", "en", "PH-07"),
            Entity("Silangang Negros", "PH-NER", "PROVINCE", "tl", "PH-07"),
        ),
        "PH-NSA": (
            Entity("Hilagang Samar", "PH-NSA", "PROVINCE", "tl", "PH-08"),
            Entity("Northern Samar", "PH-NSA", "PROVINCE", "en", "PH-08"),
        ),
        "PH-NUE": (
            Entity("Nueva Ecija", "PH-NUE", "PROVINCE", "en", "PH-03"),
            Entity("Nuweva Esiha", "PH-NUE", "PROVINCE", "tl", "PH-03"),
        ),
        "PH-NUV": (
            Entity("Nueva Vizcaya", "PH-NUV", "PROVINCE", "en", "PH-02"),
            Entity("Nuweva Biskaya", "PH-NUV", "PROVINCE", "tl", "PH-02"),
        ),
        "PH-PAM": (
            Entity("Pampanga", "PH-PAM", "PROVINCE", "en", "PH-03"),
            Entity("Pampanga", "PH-PAM", "PROVINCE", "tl", "PH-03"),
        ),
        "PH-PAN": (
            Entity("Pangasinan", "PH-PAN", "PROVINCE", "en", "PH-01"),
            Entity("Pangasinan", "PH-PAN", "PROVINCE", "tl", "PH-01"),
        ),
        "PH-PLW": (
            Entity("Palawan", "PH-PLW", "PROVINCE", "en", "PH-41"),
            Entity("Palawan", "PH-PLW", "PROVINCE", "tl", "PH-41"),
        ),
        "PH-QUE": (
            Entity("Keson", "PH-QUE", "PROVINCE", "tl", "PH-40"),
            Entity("Quezon", "PH-QUE", "PROVINCE", "en", "PH-40"),
        ),
        "PH-QUI": (
            Entity("Kirino", "PH-QUI", "PROVINCE", "tl", "PH-02"),
            Entity("Quirino", "PH-QUI", "PROVINCE", "en", "PH-02"),
        ),
        "PH-RIZ": (
            Entity("Risal", "PH-RIZ", "PROVINCE", "tl", "PH-40"),
            Entity("Rizal", "PH-RIZ", "PROVINCE", "en", "PH-40"),
        ),
        "PH-ROM": (
            Entity("Romblon", "PH-ROM", "PROVINCE", "en", "PH-41"),
            Entity("Romblon", "PH-ROM", "PROVINCE", "tl", "PH-41"),
        ),
        "PH-SAR": (
            Entity("Sarangani", "PH-SAR", "PROVINCE", "en", "PH-11"),
            Entity("Sarangani", "PH-SAR", "PROVINCE", "tl", "PH-11"),
        ),
        "PH-SCO": (
            Entity("South Cotabato", "PH-SCO", "PROVINCE", "en", "PH-11"),
            Entity("Timog Kotabato", "PH-SCO", "PROVINCE", "tl", "PH-11"),
        ),
        "PH-SIG": (
            Entity("Sikihor", "PH-SIG", "PROVINCE", "tl", "PH-07"),
            Entity("Siquijor", "PH-SIG", "PROVINCE", "en", "PH-07"),
        ),
        "PH-SLE": (
            Entity("Katimogang Leyte", "PH-SLE", "PROVINCE", "tl", "PH-08"),
            Entity("Southern Leyte", "PH-SLE", "PROVINCE", "en", "PH-08"),
        ),
        "PH-SLU": (
            Entity("Sulu", "PH-SLU", "PROVINCE", "en", "PH-14"),
            Entity("Sulu", "PH-SLU", "PROVINCE", "tl", "PH-14"),
        ),
        "PH-SOR": (
            Entity("Sorsogon", "PH-SOR", "PROVINCE", "en", "PH-05"),
            Entity("Sorsogon", "PH-SOR", "PROVINCE", "tl", "PH-05"),
        ),
        "PH-SUK": (
            Entity("Sultan Kudarat", "PH-SUK", "PROVINCE", "en", "PH-12"),
            Entity("Sultan Kudarat", "PH-SUK", "PROVINCE", "tl", "PH-12"),
        ),
        "PH-SUN": (
            Entity("Hilagang Surigaw", "PH-SUN", "PROVINCE", "tl", "PH-13"),
            Entity("Surigao del Norte", "PH-SUN", "PROVINCE", "en", "PH-13"),
        ),
        "PH-SUR": (
            Entity("Surigao del Sur", "PH-SUR", "PROVINCE", "en", "PH-13"),
            Entity("Timog Surigaw", "PH-SUR", "PROVINCE", "tl", "PH-13"),
        ),
        "PH-TAR": (
            Entity("Tarlac", "PH-TAR", "PROVINCE", "en", "PH-03"),
            Entity("Tarlak", "PH-TAR", "PROVINCE", "tl", "PH-03"),
        ),
        "PH-TAW": (
            Entity("Tawi-Tawi", "PH-TAW", "PROVINCE", "en", "PH-14"),
            Entity("Tawi-Tawi", "PH-TAW", "PROVINCE", "tl", "PH-14"),
        ),
        "PH-WSA": (
            Entity("Samar", "PH-WSA", "PROVINCE", "en", "PH-08"),
            Entity("Samar", "PH-WSA", "PROVINCE", "tl", "PH-08"),
        ),
        "PH-ZAN": (
            Entity("Hilagang Sambuwangga", "PH-ZAN", "PROVINCE", "tl", "PH-09"),
            Entity("Zamboanga del Norte", "PH-ZAN", "PROVINCE", "en", "PH-09"),
        ),
        "PH-ZAS": (
            Entity("Timog Sambuwangga", "PH-ZAS", "PROVINCE", "tl", "PH-09"),
            Entity("Zamboanga del Sur", "PH-ZAS", "PROVINCE", "en", "PH-09"),
        ),
        "PH-ZMB": (
            Entity("Sambales", "PH-ZMB", "PROVINCE", "tl", "PH-03"),
            Entity("Zambales", "PH-ZMB", "PROVINCE", "en", "PH-03"),
        ),
        "PH-ZSI": (
            Entity("Sambuwangga Sibugay", "PH-ZSI", "PROVINCE", "tl", "PH-09"),
            Entity("Zamboanga Sibugay", "PH-ZSI", "PROVINCE", "en", "PH-09"),
        ),
    }
