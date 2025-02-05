# femm_simulator/core/AirModel.py
import sys
sys.path.append("../")
import femm
from dataclasses import dataclass, asdict
from models.base import BaseParams, BaseModel
from simulation.material import MaterialHandler as mat_handler
@dataclass
class AirParams(BaseParams):
    boundary_id: int = 10                   # 边界号
    boundary_name: str = "Outside"          # 边界名称

    inner_radius: float = 100.0             # 内径 (mm)
    outer_radius: float = 300.0             # 外径 (mm)

class AirModel(BaseModel[AirParams]):
    def __init__(self, **params):
        super().__init__(AirParams(**params))
        
    def _build(self):
            ri, ro = self._params.inner_radius, self._params.outer_radius
            try:
                self._make_airspace(ri, ro)
                self._set_properties(ri, ro)
                
            except Exception as e:
                error_info = f"airspace build failed: {self._params}"
                raise RuntimeError(error_info) from e


    def _make_airspace(self, ri, ro):
        femm.mi_drawline(0, -ri, 0, ri)
        femm.mi_drawarc(0, -ri,0, ri, 180, 2)
        mat_handler.get_material(self._params.material, self._params.is_customized_material)
        femm.mi_clearselected()

        femm.mi_drawline(0, -ro, 0, ro)
        femm.mi_drawarc(0, -ro,0, ro, 180, 2)
        mat_handler.get_material(self._params.material, self._params.is_customized_material)
        femm.mi_clearselected()

    def _set_properties(self, ri, ro):
        inner_label_pos = ri/4, ri/2
        outer_label_pos = ro/4, ro/2

        femm.mi_addblocklabel(*inner_label_pos)
        femm.mi_selectlabel(*inner_label_pos)
        femm.mi_setblockprop(
            self._params.material,       # materialname
            1,                          # automesh: 0:off, 1:on
            0.1,                        # meshsize
            '',                         # circuit
            0,                          # magdir
            self._params.group_id,       # group
            0                           # turns
        )
        femm.mi_clearselected()
        
        femm.mi_addblocklabel(*outer_label_pos)
        femm.mi_selectlabel(*outer_label_pos)
        femm.mi_setblockprop(
            self._params.material,       # materialname
            self._params.automesh,       # automesh: 0:off, 1:on
            self._params.meshsize,       # meshsize
            '',                         # circuit
            self._params.magdir,         # magdir
            self._params.group_id,       # group
            0                           # turns
        )
        femm.mi_addboundprop(self._params.boundary_name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        femm.mi_selectarcsegment(0, ro)
        femm.mi_setarcsegmentprop(2, self._params.boundary_name, 0, self._params.boundary_id)
        femm.mi_clearselected()