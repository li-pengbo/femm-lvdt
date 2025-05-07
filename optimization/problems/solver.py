import sys
sys.path.append('../../')
import pickle
import multiprocessing
from pymoo.optimize import minimize
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.mutation.pm import PM
from pymoo.operators.crossover.sbx import SBX
from pymoo.core.problem import StarmapParallelization
from pymoo.operators.repair.rounding import RoundingRepair
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from optimization.problems import myProblem, Problem_alucoil

version = 1
n_var = 7
n_obj = 4
n_constr = 5
n_pop = 50
n_gen = 50
n_processes = 25

opt_result_filename = f'../solutions/lvdt_vc_nvar{n_var}_nobj{n_obj}_nconstr{n_constr}_npop{n_pop}_ngen{n_gen}_v{version}.pkl'

PSalgorithm = NSGA2(pop_size=n_pop, 
                  sampling=IntegerRandomSampling(),
                  crossover=SBX(prob=0.9, eta=25, vtype = float, repair = RoundingRepair()),
                  mutation=PM(prob = 0.3,eta=50, vtype = float, repair = RoundingRepair()),
                  eliminate_duplicates=True)



if __name__ == "__main__":
    
    pool = multiprocessing.Pool(processes=n_processes)
    runner = StarmapParallelization(starmap=pool.starmap)
    problem = myProblem.SenActProblem(elementwise_runner = runner)
    try:
        res = minimize(problem, 
                    PSalgorithm, 
                    ('n_gen', n_gen), 
                    seed=1, 
                    verbose=True,
                    save_history=True)
        print(f"Execution time: {res.exec_time}")
        pool.close()
        with open(opt_result_filename, "wb") as f:
            pickle.dump(res, f)

    except KeyboardInterrupt:
        print("Process interrupted by user.")
        pool.close()


"""    
# from pymoo.core.problem import JoblibParallelization
# from joblib import Parallel, delayed

# n_jobs = 25
# parallel = Parallel(n_jobs=n_jobs)
# runner = JoblibParallelization(parallel, delayed)
"""