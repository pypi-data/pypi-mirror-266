from .base import BaseModel
from typing import List
from enum import Enum


class Type_(Enum):
    WORKPLACE_USER = "workplace_user"
    GROUP = "group"
    INVITE = "invite"
    SERVICE_ACCOUNT = "service_account"

    def list():
        return list(map(lambda x: x.value, Type_._member_map_.values()))


class AddRequest(BaseModel):
    def __init__(
        self,
        type_: Type_,
        slug: str,
        role: str = None,
        environments: List[str] = None,
        **kwargs,
    ):
        """
        Initialize AddRequest
        Parameters:
        ----------
            type_: str
            slug: str
                Member's slug
            role: str
                Identifier of the project role
            environments: list of AddRequestEnvironments
                Environment slugs to grant the member access to
        """
        self.type_ = self._enum_matching(type_, Type_.list(), "type_")
        self.slug = slug
        self.role = role
        self.environments = environments
