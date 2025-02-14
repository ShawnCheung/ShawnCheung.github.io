__all__ = [
    "ModelDBO",
]


from base_dbo import BaseDBO
from models import (
    Table
)


class ModelDBO(BaseDBO[Table]):
    _table = Table
