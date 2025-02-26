# LVDT_simulation/simulation/material.py
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
        },
        "31 AWG": {
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
            'WireD': 0.2261
        },
    }
    @classmethod
    def get_material(cls, name: str, customized: bool) -> None:
        if customized:
            cls.get_custom_material(name)
        else:
            cls.get_builtin_material(name)

    @staticmethod
    def get_builtin_material(name: str) -> None:
        """Get built-in material
        
        Args:
            name: Built-in material name
            
        Raises:
            ValueError: Material not found
        """
        try:
            femm.mi_getmaterial(name)
        except Exception as e:
            raise ValueError(
                f"Material '{name}' not found. Please check:\n"
                "1. Material name is correct\n"
                "2. FEMM is in magnetostatic mode"
            ) from e

    @classmethod
    def get_custom_material(cls, name: str) -> None:
        """Get custom material
        
        Args:
            name: Pre-defined custom material name
            
        Raises:
            KeyError: Material not defined
            RuntimeError: FEMM operation failed
        """
        try:
            params = cls._CUSTOM_MATERIALS[name]
        except KeyError:
            available = list(cls._CUSTOM_MATERIALS.keys())
            raise KeyError(
                f"Custom material '{name}' not defined. Available materials: {available}"
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
                f"Failed to create material '{name}', parameters: {params}"
            ) from e

    @classmethod
    def add_custom_material(cls, name: str, **kwargs) -> None:
        """Add custom material
        
        Args:
            name: Custom material name
            **kwargs: Material parameters
            
        Raises:
            ValueError: Material already exists
        """
        if name in cls._CUSTOM_MATERIALS:
            raise ValueError(f"Material '{name}' already exists")
        cls._CUSTOM_MATERIALS[name] = kwargs