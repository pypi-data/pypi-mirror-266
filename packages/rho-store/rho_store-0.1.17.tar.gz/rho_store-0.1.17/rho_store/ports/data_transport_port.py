import abc

from ..types import TableDataResult


class DataTransportPort(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_table_data(self, table_id: str) -> TableDataResult:
        raise NotImplementedError


__all__ = ["DataTransportPort"]
