# LVDT_simulation/models/base.py
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Generic, TypeVar


@dataclass
class BaseParams:
    group_id: int                       # Group ID
    
    material: str                       # Material Name
    is_customized_material: bool        # Whether the material is customized

    magdir: int                         # Magnetic direction
    automesh: int                       # Auto mesh, on/off: 0:off, 1:on
    meshsize: float                     # Mesh size

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