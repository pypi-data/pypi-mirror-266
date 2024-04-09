from dataclasses import dataclass


@dataclass(frozen=True)
class TableDataResult:
    table_id: str
    columns: list[str]
    rows: list

    def to_list(self) -> list[dict]:
        columns = self.columns
        rows = self.rows
        return [dict(zip(columns, row)) for row in rows]


__all__ = ["TableDataResult"]
