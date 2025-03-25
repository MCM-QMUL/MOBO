# Open-source Code for Multi-objective Bayesian Optimisation of Spinodoid Cellular Materials
# 
# If using this code for research or industrial purposes, please cite:
# Kansara, H., Khosroshahi, S.F., Guo, L., Bessa, M.A. and Tan, W., 2025. 
# Multi-objective Bayesian Optimisation of Spinodoid Cellular Structures for Crush Energy Absorption
# Computer Methods for Applied Mechanics and Engineering, 117890
# DOI: https://doi.org/10.1016/j.cma.2025.117890
# Preprint: https://arxiv.org/abs/2411.14508
#
# Author: Wei Tan (wei.tan@qmul.ac.uk)
# Queen Mary University of London
#

import torch
from botorch.utils.transforms import normalize, unnormalize
from botorch.utils.multi_objective.box_decompositions.non_dominated import FastNondominatedPartitioning
from botorch.acquisition.multi_objective.monte_carlo import (
    qExpectedHypervolumeImprovement,
    qNoisyExpectedHypervolumeImprovement,
)
from botorch.sampling.normal import SobolQMCNormalSampler
from botorch.acquisition.objective import ScalarizedPosteriorTransform
from botorch.acquisition.analytic import LogExpectedImprovement
from botorch.utils.multi_objective.scalarization import get_chebyshev_scalarization
from botorch.utils.sampling import sample_simplex
from botorch.optim.optimize import optimize_acqf, optimize_acqf_list
from botorch.acquisition.objective import GenericMCObjective
from botorch.acquisition.monte_carlo import qNoisyExpectedImprovement, qExpectedImprovement
from botorch.acquisition.logei import qLogExpectedImprovement, qLogNoisyExpectedImprovement
from botorch.utils.sampling import draw_sobol_samples

from utility import utility_functions

tkwargs = {"dtype": torch.double, "device": torch.device("cuda" if torch.cuda.is_available() else "cpu")}

class MOBO_methods:
    def __init__(self, MOBO_type, problem, model, train_x, train_y, batch_size, **kwargs):

        self.MOBO_type = MOBO_type
        self.problem = problem
        self.model = model
        self.train_x = train_x
        self.train_y = train_y
        self.normalised_acq_fun_bounds = torch.zeros(2, self.problem.dim, **tkwargs)
        self.normalised_acq_fun_bounds[1] = 1
        self.batch_size = batch_size
        self.num_restarts : int = 10
        self.raw_samples : int = 512
        self.sampler = SobolQMCNormalSampler(sample_shape=torch.Size([256])) # 256 MC samples
        
        for key, value in kwargs.items():
            setattr(self, key, value)

    def run_optimisation(self):
        if self.MOBO_type == "random_sobol_sampling":
            return self._random_sobol_sampling()
        elif self.MOBO_type == "qEHVI":
            return self._optimise_qEHVI()
        elif self.MOBO_type == "qNEHVI":
            return self._optimise_qNEHVI()
        elif self.MOBO_type == "weighted_sum":
            return self._optimise_weighted_sum()
        elif self.MOBO_type == "scalarise_chebyshev":
            return self._optimise_qNParEGO()
        elif self.MOBO_type == "single_obj_optimise":
            return self._single_obj_optimise()
        else:
            raise ValueError(f"Invalid MOBO type: {self.MOBO_type}")

    def _random_sobol_sampling(self):
        scaled_samples = draw_sobol_samples(bounds=self.problem.bounds, n=1, q=self.batch_size).squeeze(1) # seed here not required as we want to randommly sample the sequence

        new_x = scaled_samples
        return new_x

    def _optimise_qEHVI(self):
        train_x = normalize(self.train_x, self.problem.bounds)
        with torch.no_grad():
            pred = self.model.posterior(normalize(train_x, self.problem.bounds)).mean
        partitioning = FastNondominatedPartitioning(ref_point=self.problem.ref_point, Y=pred)
        acq_func = qExpectedHypervolumeImprovement(model=self.model, ref_point=self.problem.ref_point, partitioning=partitioning, 
                                                   sampler=self.sampler)
        candidates, _ = optimize_acqf(acq_function=acq_func, bounds=self.normalised_acq_fun_bounds,
                                      q=self.batch_size, num_restarts=self.num_restarts,
                                      raw_samples=self.raw_samples, options={"batch_limit": 10, "maxiter": 200},
                                      sequential=True, return_best_only=True)
        new_x = unnormalize(candidates.detach(), bounds=self.problem.bounds)
        new_x = utility_functions.adjust_boundary(new_x=new_x, problem=self.problem)
        return new_x
        
    def _optimise_qNEHVI(self):
        train_x = normalize(self.train_x, self.problem.bounds)
        acq_func = qNoisyExpectedHypervolumeImprovement(model=self.model, ref_point=self.problem.ref_point,
                                                         X_baseline=train_x, prune_baseline=True, sampler=self.sampler)
        candidates, _ = optimize_acqf(acq_function=acq_func, bounds=self.normalised_acq_fun_bounds,
                                      q=self.batch_size, num_restarts=self.num_restarts,
                                      raw_samples=self.raw_samples, options={"batch_limit": 10, "maxiter": 200},
                                      sequential=True, return_best_only=True)
        new_x = unnormalize(candidates.detach(), bounds=self.problem.bounds)
        new_x = utility_functions.adjust_boundary(new_x=new_x, problem=self.problem)
        return new_x
        
    def _optimise_weighted_sum(self):
        
        train_x = normalize(self.train_x, self.problem.bounds)
        with torch.no_grad():
            pred = self.model.posterior(train_x).mean

        acq_func_list = []
        for _ in range(self.batch_size):
            weights = sample_simplex(self.problem.num_objectives, **tkwargs).squeeze()

            objective = GenericMCObjective(utility_functions.get_weighted_sum_scalarisation(Y=pred, weights=weights))
            acq_func = qLogNoisyExpectedImprovement(model=self.model, 
                                                objective=objective,
                                                # best_f=best_f, 
                                                X_baseline=train_x,
                                                prune_baseline=True,
                                                sampler=self.sampler
                                                )
            acq_func_list.append(acq_func)
            candidates, _ = optimize_acqf_list(acq_function_list=acq_func_list,
                                            bounds=self.normalised_acq_fun_bounds,
                                            num_restarts=self.num_restarts, raw_samples=self.raw_samples,
                                            options={"batch_limit": 10, "maxiter": 200})
            
        new_x = unnormalize(candidates.detach(), bounds=self.problem.bounds)
        new_x = utility_functions.adjust_boundary(new_x=new_x, problem=self.problem)
        return new_x
        
    def _optimise_qNParEGO(self):
        train_x = normalize(self.train_x, self.problem.bounds)
        with torch.no_grad():
            pred = self.model.posterior(train_x).mean
        acq_func_list = []
        for _ in range(self.batch_size):
            weights = sample_simplex(self.problem.num_objectives, **tkwargs).squeeze()
            objective = GenericMCObjective(get_chebyshev_scalarization(weights=weights, Y=pred))
            acq_func = qLogNoisyExpectedImprovement(model=self.model, 
                                                objective=objective,
                                                #   best_f=torch.max(self.train_y), 
                                                X_baseline=train_x,
                                                prune_baseline=True,
                                                sampler=self.sampler
                                                )
            acq_func_list.append(acq_func)
            candidates, _ = optimize_acqf_list(acq_function_list=acq_func_list,
                                            bounds=self.normalised_acq_fun_bounds,
                                            num_restarts=self.num_restarts, raw_samples=self.raw_samples,
                                            options={"batch_limit": 10, "maxiter": 200})

        new_x = unnormalize(candidates.detach(), bounds=self.problem.bounds)
        new_x = utility_functions.adjust_boundary(new_x=new_x, problem=self.problem)
        return new_x

    def _single_obj_optimise(self):
        train_x = normalize(self.train_x, self.problem.bounds)

        acq_func_list = []
        for _ in range(self.batch_size):

            acq_func = qLogNoisyExpectedImprovement(model=self.model, 
                                                # best_f=best_f, 
                                                X_baseline=train_x,
                                                prune_baseline=True,
                                                sampler=self.sampler
                                                )
            acq_func_list.append(acq_func)
            candidates, _ = optimize_acqf_list(acq_function_list=acq_func_list,
                                            bounds=self.normalised_acq_fun_bounds,
                                            num_restarts=self.num_restarts, raw_samples=self.raw_samples,
                                            options={"batch_limit": 10, "maxiter": 200})
            
        new_x = unnormalize(candidates.detach(), bounds=self.problem.bounds)
        new_x = utility_functions.adjust_boundary(new_x=new_x, problem=self.problem)
        return new_x
