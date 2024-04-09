"""
a Netzvertrag is a contract between a supplier and a grid operator
"""

from enum import StrEnum
from uuid import UUID

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, RootModel

from tmdsclient.models.bo4e_stub import Menge


class Vertragsteil(BaseModel):
    """
    BO4E COM Vertragsteil
    """

    guid: UUID | None = None
    vertragsteilbeginn: AwareDatetime
    vertragsteilende: AwareDatetime | None = None
    lokation: str | None = None
    jahresverbrauchsprognose: Menge | None = None
    kundenwert: Menge | None = None


class Vertragsstatus(StrEnum):
    """
    Abbildung einer Statusinformation für Verträge.
    """

    # copied instead of imported from bo4e because: https://github.com/bo4e/BO4E-python/issues/724
    IN_ARBEIT = "IN_ARBEIT"  #: in Arbeit
    UEBERMITTELT = "UEBERMITTELT"  #: übermittelt
    ANGENOMMEN = "ANGENOMMEN"  #: angenommen
    AKTIV = "AKTIV"  #: aktiv
    ABGELEHNT = "ABGELEHNT"  #: abgelehnt
    WIDERRUFEN = "WIDERRUFEN"  #: widerrufen
    STORNIERT = "STORNIERT"  #: storniert
    GEKUENDIGT = "GEKUENDIGT"  #: gekündigt
    BEENDET = "BEENDET"  #: beendet


class Bo4eVertrag(BaseModel):
    """
    a bo4e vertrag (inside the Netzvertrag)
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    vertragsnummer: str
    vertragsbeginn: AwareDatetime
    vertragsende: AwareDatetime | None = None
    vertragstatus: Vertragsstatus
    # note that in TMDS / BO4E.net the property is called "vertragstatus" but in Python 'vertragsstatus'
    # https://github.com/Hochfrequenz/BO4E-dotnet/issues/417
    vertragsteile: list[Vertragsteil] | None = None


class TmdsMarktlokation(BaseModel):
    """tmds wrapper around a bo4e marktlokation"""

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: str  #: e.g. '32631452574'


class Netzvertrag(BaseModel):
    """
    a TMDS netzvertrag
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)
    id: UUID
    bo_model: Bo4eVertrag | None = Field(alias="boModel", default=None)
    marktlokation: TmdsMarktlokation | None = Field(alias="marktlokation", default=None)


class _ListOfNetzvertraege(RootModel[list[Netzvertrag]]):
    pass
