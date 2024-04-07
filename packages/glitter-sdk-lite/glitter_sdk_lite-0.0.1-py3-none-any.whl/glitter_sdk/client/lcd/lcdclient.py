from __future__ import annotations
from .db import DB


class LCDClient:
    """An object representing a connection to a node running the DB LCD server."""

    url: str
    """URL endpoint of LCD server."""

    def __init__(
            self,
            url: str,
    ):
        self.url = url

    def db(self) -> DB:  # type: ignore
        """Creates a :class:`DB` object from a url.

        """
        return DB(self.url)
