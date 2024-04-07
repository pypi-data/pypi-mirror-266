from typing import List
from ...interface import IData
from ...packer.market.fin_persist_read_param_data_packer import FinPersistReadParamDataPacker
from .fin_persist_filed_data import FinPersistFiledData


class FinPersistReadParamData(IData):
    def __init__(self, table_name: str = '', range: str = '', start_date: int = 0, end_date: int = 99999999, base_path: str = ''):
        super().__init__(FinPersistReadParamDataPacker(self))
        self._TableName: str = table_name
        self._Range: str = range
        self._StartDate: int = start_date
        self._EndDate: int = end_date
        self._DataFileds: List[FinPersistFiledData] = []
        self._BasePath: str = base_path

    @property
    def TableName(self):
        return self._TableName

    @TableName.setter
    def TableName(self, value: str):
        self._TableName = value

    @property
    def Range(self):
        return self._Range

    @Range.setter
    def Range(self, value: str):
        self._Range = value

    @property
    def StartDate(self):
        return self._StartDate

    @StartDate.setter
    def StartDate(self, value: int):
        self._StartDate = value

    @property
    def EndDate(self):
        return self._EndDate

    @EndDate.setter
    def EndDate(self, value: int):
        self._EndDate = value

    @property
    def DataFileds(self):
        return self._DataFileds

    @DataFileds.setter
    def DataFileds(self, value: List[FinPersistFiledData]):
        self._DataFileds = value

    @property
    def BasePath(self):
        return self._BasePath

    @BasePath.setter
    def BasePath(self, value: str):
        self._BasePath = value
