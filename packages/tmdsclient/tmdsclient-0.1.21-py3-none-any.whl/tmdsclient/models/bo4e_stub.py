"""
Classes copied directly from BO4E-python.
We cannot add bo4e-python as a dependency, because there is no version published yet that has
https://github.com/bo4e/BO4E-python/issues/724 fixed.
"""

from decimal import Decimal
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel


class Mengeneinheit(StrEnum):
    """
    Einheit: Messgrößen, die per Messung oder Vorgabe ermittelt werden können.
    """

    W = "W"  #: Watt
    WH = "WH"  #: Wattstunde
    KW = "KW"  #: Kilowatt
    KWH = "KWH"  #: Kilowattstunde
    KVARH = "KVARH"  #: Kilovarstunde
    MW = "MW"  #: Megawatt
    MWH = "MWH"  #: Megawattstunde
    STUECK = "STUECK"  #: Stückzahl
    KUBIKMETER = "KUBIKMETER"  #: Kubikmeter (Gas)
    SEKUNDE = "SEKUNDE"  #: Sekunde
    MINUTE = "MINUTE"  #: Minute
    STUNDE = "STUNDE"  #: Stunde
    VIERTEL_STUNDE = "VIERTEL_STUNDE"  #: Viertelstunde
    TAG = "TAG"  #: Tag
    WOCHE = "WOCHE"  #: Woche
    MONAT = "MONAT"  #: Monat
    QUARTAL = "QUARTAL"  #: Quartal
    HALBJAHR = "HALBJAHR"  #: Halbjahr
    JAHR = "JAHR"  #: Jahr
    PROZENT = "PROZENT"  #: Prozent
    KVAR = "KVAR"  #: Kilovar
    ANZAHL = "ANZAHL"  # e.g. keine Einheit. not included in bo4e-python
    VAR = "VAR"  # https://github.com/bo4e/BO4E-python/issues/755
    VARH = "VAR"  # https://github.com/bo4e/BO4E-python/issues/756
    KWHK = "KWHK"  # https://github.com/bo4e/BO4E-python/issues/757


class Menge(BaseModel):
    """
    Abbildung einer Menge mit Wert und Einheit.
    """

    #: Gibt den absoluten Wert der Menge an
    wert: Optional[Decimal] = None
    #: Gibt die Einheit zum jeweiligen Wert an
    einheit: Optional[Mengeneinheit] = None
