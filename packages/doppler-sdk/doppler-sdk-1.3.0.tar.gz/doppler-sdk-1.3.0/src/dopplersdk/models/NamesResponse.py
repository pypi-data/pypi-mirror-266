from .base import BaseModel
from typing import List


class NamesResponse(BaseModel):
    def __init__(self, names: List[str] = None, **kwargs):
        """
        Initialize NamesResponse
        Parameters:
        ----------
            names: list of NamesResponseNames
        """
        self.names = names
