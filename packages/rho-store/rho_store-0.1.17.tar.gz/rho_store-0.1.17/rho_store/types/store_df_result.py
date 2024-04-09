from dataclasses import dataclass


@dataclass(frozen=True)
class StoreDfResult:
    table_id: str
    client_url: str


__all__ = ["StoreDfResult"]
