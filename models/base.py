from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Generic, TypeVar


@dataclass
class BaseParams:
    group_id: int                       # 组号
    
    material: str                       # 材料
    is_customized_material: bool        # 是否自定义材料

    magdir: int                         # 磁场方向
    automesh: int                       # 是否自动网格: 0:off, 1:on
    meshsize: float                     # 网格大小

T = TypeVar('T', bound='BaseParams')

class BaseModel(Generic[T]):
    def __init__(self, params: T):
        self._params: T = params
        self._group_id = params.group_id

    @property
    def get_params(self) -> Dict[str, Any]:
        return asdict(self._params)
    
    @property
    def get_group_id(self) -> int:
        return self._group_id
    
    def _build(self):
        raise NotImplementedError("Method 'build' must be implemented in subclass")