from typing import List
from ...interface import IData
from ...packer.market.fin_persist_save_param_data_packer import FinPersistSaveParamDataPacker
from .fin_persist_filed_data import FinPersistFiledData


class FinPersistSaveParamData(IData):
    def __init__(self, table_name: str = '', range: str = '',
                 append: bool = False, basepath: str = ''):
        super().__init__(FinPersistSaveParamDataPacker(self))
        self._TableName: str = table_name
        self._Range: str = range
        self._Fileds: List[FinPersistFiledData] = []
        self._Append: bool = append
        self._BasePath: str = basepath

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
    def Fileds(self):
        return self._Fileds

    @Fileds.setter
    def Fileds(self, value: List[FinPersistFiledData]):
        self._Fileds = value

    @property
    def Append(self):
        return self._Append

    @Append.setter
    def Append(self, value: bool):
        self._Append = value

    @property
    def BasePath(self):
        return self._BasePath

    @BasePath.setter
    def BasePath(self, value: str):
        self._BasePath = value
