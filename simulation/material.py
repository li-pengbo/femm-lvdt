# femm_simulator/core/materials.py
from typing import Dict, Any
import femm
class MaterialHandler:
    """Material handler"""
    
    _CUSTOM_MATERIALS: Dict[str, Dict[str, Any]] = {
        '100um': {
            'mu_x': 1,          # relative permeability in x direction
            'mu_y': 1,          # relative permeability in y direction
            'H_c': 0,           # coercivity
            'J': 0,             # current density
            'Cduct': 58,        # conductivity
            'Lam_d': 0,         # lamination thickness
            'Phi_hmax': 0,      # maximum hysteresis phase shift
            'Lam_fill': 1,      # lamination fill factor
            'LamType': 3,       # lamination type
            'Phi_hx': 0,        # hysteresis phase shift in x direction 
            'Phi_hy': 0,        # hysteresis phase shift in y direction
            'NStrands': 1,      # number of strands
            'WireD': 0.1        # wire diameter
        },
        'RS wire': {
            'mu_x': 1,
            'mu_y': 1,
            'H_c': 0,
            'J': 0,
            'Cduct': 58,
            'Lam_d': 0,
            'Phi_hmax': 0,
            'Lam_fill': 1,
            'LamType': 3,
            'Phi_hx': 0,
            'Phi_hy': 0,
            'NStrands': 1,
            'WireD': 0.2
        }
    }
    @classmethod
    def get_material(cls, name: str, customized: bool) -> None:
        if customized:
            cls.get_custom_material(name)
        else:
            cls.get_builtin_material(name)

    @staticmethod
    def get_builtin_material(name: str) -> None:
        """获取FEMM内置材料
        
        Args:
            name: 内置材料名称
            
        Raises:
            ValueError: 材料不存在或获取失败
        """
        try:
            femm.mi_getmaterial(name)
        except Exception as e:
            raise ValueError(
                f"无法获取内置材料 '{name}'. 请检查：\n"
                "1. 材料名称是否正确\n"
                "2. FEMM是否处于磁学模式"
            ) from e

    @classmethod
    def get_custom_material(cls, name: str) -> None:
        """获取预定义自定义材料
        
        Args:
            name: 预定义的自定义材料名称
            
        Raises:
            KeyError: 材料未预定义
            RuntimeError: FEMM操作失败
        """
        try:
            params = cls._CUSTOM_MATERIALS[name]
        except KeyError:
            available = list(cls._CUSTOM_MATERIALS.keys())
            raise KeyError(
                f"自定义材料 '{name}' 未预定义。可用材料: {available}"
            ) from None

        try:
            femm.mi_addmaterial(
                name,
                params['mu_x'],
                params['mu_y'],
                params['H_c'],
                params['J'],
                params['Cduct'],
                params['Lam_d'],
                params['Phi_hmax'],
                params['Lam_fill'],
                params['LamType'],
                params['Phi_hx'],
                params['Phi_hy'],
                params['NStrands'],
                params['WireD']
            )
        except Exception as e:
            raise RuntimeError(
                f"创建材料 '{name}' 失败，参数: {params}"
            ) from e

    @classmethod
    def add_custom_material(cls, name: str, **kwargs) -> None:
        """动态添加新自定义材料
        
        Args:
            name: 材料唯一名称
            **kwargs: 材料参数
            
        Raises:
            ValueError: 材料已存在
        """
        if name in cls._CUSTOM_MATERIALS:
            raise ValueError(f"材料 '{name}' 已存在")
        cls._CUSTOM_MATERIALS[name] = kwargs