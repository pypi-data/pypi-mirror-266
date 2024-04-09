"""
'models' contains the TMDS data model (or at least the part which we use in this client)
"""

from typing import Literal

from pydantic import BaseModel, Field, RootModel

_SupportedEntityType = Literal["Netzvertrag"]


class _IdPair(BaseModel):
    interne_id: str = Field(alias="interneId")
    externe_id: str | None = Field(alias="externeId", default=None)


class AllIdsResponse(RootModel[dict[_SupportedEntityType, list[_IdPair]]]):
    """
    response of any /allIds endpoint
    """
