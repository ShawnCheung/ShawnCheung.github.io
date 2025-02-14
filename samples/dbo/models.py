from typing import Any, Dict, List

from sqlalchemy import Column, Integer, Text, DateTime, Boolean, BigInteger, func
from sqlalchemy.ext.declarative import declarative_base


__all__ = [
    "Table"
]

Base = declarative_base()


class ToDictMixin:
    _default_select_columns: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = {}
        for col in self._default_select_columns:
            obj = getattr(self, col)
            if isinstance(obj, DateTime):
                obj = obj.isoformat()
            d[col] = obj
        return d

class Table(Base, ToDictMixin):
    __tablename__ = 'table'
    _default_select_columns = ["model_id", "model_name", "model_version", "model_description", "service_id", "publish_time", "deploy_time", "deploy_status", "test_status"]
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    model_id = Column(Text(), comment="模型的id")
    model_name = Column(Text(), comment="模型的名称")
    model_version = Column(Text(), comment="模型的版本")
    model_description = Column(Text(), comment="模型的描述")
    service_id = Column(Text(), comment="模型服务的id")
    publish_time = Column(Text(), comment="模型发布时间")
    deploy_time = Column(Text(), comment="模型部署时间")
    deploy_status = Column(Text(), comment="模型部署状态")
    test_status = Column(Text(), comment="模型测试状态")
