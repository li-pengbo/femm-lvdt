import sys
sys.path.append('../../')
import uuid
import numpy as np
from datetime import datetime
from pymoo.core.problem import ElementwiseProblem
from core.evaluator import lvdt_evaluator, vc_evaluator

"""
constraints:
LVDT:
    1. total length of the bobbin should be 60mm: 50mm<= L <= 70mm.
    2. distance between the inner and outer layer of the coil should be 10mm.
    3. non-linearirty should be below 5%
    4. half the length of the inner coil should be smaller than the distance between middle coil and outer coil.
VC:
    1. resistance of two outer coils should be smaller than 90 ohm.
    2. voice coil force should be at least 1.2N.
    3. the force variation index should be below 10%.
"""

class SenActProblem(ElementwiseProblem):
    
    def __init__(self, **kwargs):
        # manually optimal params = [6, 14, 20, 7, 34, 25, 17.5]

        x_min = np.zeros(7)
        x_max = np.zeros(7)

        x_min[0], x_max[0] = 4 ,  8     # NLI
        x_min[1], x_max[1] = 10, 20     # DI
        x_min[2], x_max[2] = 5 , 25     # LI

        x_min[3], x_max[3] = 5 ,  9     # NLO
        x_min[4], x_max[4] = 30, 40     # DO
        x_min[5], x_max[5] = 10, 30     # LO
        
        x_min[6], x_max[6] = 10, 25     # DIO

        super().__init__(n_var=7, n_obj=4, n_constr=5, xl=x_min, xu=x_max, **kwargs)
    
       
    def _evaluate(self, x, out, *args, **kwargs):
        iter_datetime = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:12]}"
        
        lvdt_json_filename      = f"../iteration/config/config_init/v0_typeG_lvdt.json"
        lvdt_iter_filename      = f"../iteration/config/config_iter/iteration_lvdt_{iter_datetime}.json"
        lvdt_output_dir         = f"../iteration/data/lvdt"
        lvdt_output_filename    = f"typeG_LVDT_{iter_datetime}.h5"

        vc_json_filename        = f"../iteration/config/config_init/v0_typeG_vc.json"
        vc_iter_filename        = f"../iteration/config/config_iter/iteration_vc_{iter_datetime}.json"
        vc_output_dir           = f"../iteration/data/voicecoil"
        vc_output_filename      = f"typeG_VC_{iter_datetime}.h5"

        f1, f2 = lvdt_evaluator(x, 
                                lvdt_json_filename, 
                                lvdt_iter_filename, 
                                lvdt_output_dir, 
                                lvdt_output_filename,)
        
        f3, f4, f5 = vc_evaluator(x,
                              vc_json_filename, 
                              vc_iter_filename, 
                              vc_output_dir, 
                              vc_output_filename)
        
        g1 = x[6]*2 + x[5] - 70  # length of the bobbin smaller than 70mm
        g2 = 50 - x[6]*2 - x[5]  # length of the bobbin larger  than 50mm
        g3 = 20- (x[4] - x[1])     # distance between the inner and outer layer of the coil larger than 10mm
        g4 = x[2] -2*x[6]        # length of the inner coil smaller than the distance between middle coil and outer coil
        g5 = f5 - 90             # resistance of two outer coils smaller than 90 ohm

        out["F"] = np.column_stack([-f1, f2, -f3, f4]) 
        out["G"] = np.column_stack([g1, g2, g3, g4, g5])

class SenProblem(ElementwiseProblem):
    
    def __init__(self, **kwargs):
        # manually optimal params = [6, 14, 20, 7, 34, 25, 17.5]

        x_min = np.zeros(7)
        x_max = np.zeros(7)

        x_min[0], x_max[0] = 4 , 6     # NLI
        x_min[1], x_max[1] = 10, 18     # DI
        x_min[2], x_max[2] = 15, 25     # LI

        x_min[3], x_max[3] = 5 ,  7     # NLO
        x_min[4], x_max[4] = 25, 40     # DO
        x_min[5], x_max[5] = 10, 30     # LO
        
        x_min[6], x_max[6] = 15 , 20     # DIO

        super().__init__(n_var=7,n_obj=2, n_constr=3, xl=x_min, xu=x_max, **kwargs)
    
       
    def _evaluate(self, x, out, *args, **kwargs):
        iter_datetime = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:12]}"
        
        lvdt_json_filename      = f"../iteration/config/config_init/v0_typeG_lvdt.json"
        lvdt_iter_filename      = f"../iteration/config/config_iter/iteration_lvdt_{iter_datetime}.json"
        lvdt_output_dir         = f"../iteration/data/lvdt"
        lvdt_output_filename    = f"typeG_LVDT_{iter_datetime}.h5"

        f1, f2 = lvdt_evaluator(x, 
                                lvdt_json_filename, 
                                lvdt_iter_filename, 
                                lvdt_output_dir, 
                                lvdt_output_filename,)

        
        g1 = x[6]*2 + x[5] - 70 # length of the bobbin smaller than 70mm
        g2 = 50 - x[6]*2 - x[5] # length of the bobbin larger  than 50mm
        g3 = x[4] - x[1] -20    # distance between the inner and outer layer of the coil larger than 10mm


        out["F"] = np.column_stack([-f1, f2]) 
        out["G"] = np.column_stack([g1, g2, g3])