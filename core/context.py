# LVDT_simulation/simulation/context.py
import femm
import logging
from typing import Generator

class FEMMError(Exception):
    """Base exception for FEMM operations"""
    def __init__(self, msg: str):
        super().__init__(f"FEMM Error: {msg}")

class FEMMSession:
    """Context manager for FEMM session"""
    def __init__(self, signal_frequency: float, problem_type: str = 'axi', gui: bool = False):
        self.signal_frequency = signal_frequency
        self.problem_type = problem_type
        self._is_open = False
        self._gui = gui

    def __enter__(self):
        self.open()
        return self

    def __exit__(self):
        if self._is_open:
            logging.warning("Warning: FEMM session is not closed")

    def open(self):
        """Open FEMM session"""
        if not self._is_open:
            try:
                if self._gui:
                    femm.openfemm()
                else:
                    femm.openfemm(1) 
                femm.newdocument(0)
                femm.mi_probdef(
                    self.signal_frequency,
                    'millimeters',
                    self.problem_type,
                    1e-10, 30, 30  # precision, depth, minangle
                )
                self._is_open = True
                logging.info("FEMM session opened")
            except Exception as e:
                raise FEMMError(f"FEMM session open failed: {str(e)}") from e

    def close(self):
        """Close FEMM session"""
        if self._is_open:
            try:
                femm.mi_close()  # Close the current document
                femm.closefemm() # Close FEMM application
                self._is_open = False
                logging.info("FEMM session closed")
            except Exception as e:
                raise FEMMError(f"FEMM session close failed: {str(e)}") from e