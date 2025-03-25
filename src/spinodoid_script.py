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
import numpy as np
import pandas as pd
import random
import os
import subprocess
import logging
import scipy.io as sio
import shutil
logger = logging.getLogger(__name__)

from utility import utility_functions

class Spinodoid_function:
    def __init__(self, train_x, train_y, path_to_spinodal_resources, path_to_GIBBON, hydra_output_directory, output_columns, batch_size, tkwargs, apply_transform):
        self.dim = train_x.size(dim=1)
        self.bounds = torch.tensor([[0.3, 0, 0, 0], [0.6, 90, 90, 90]]).to(**tkwargs) 
        self.ref_point = torch.tensor([-10, -3]).to(**tkwargs)
        self.num_objectives = train_y.size(dim=1)
        self.path_to_spinodal_resources = path_to_spinodal_resources
        self.tkwargs = tkwargs
        self.hydra_output_directory = hydra_output_directory
        self.path_to_GIBBON = path_to_GIBBON
        self.output_columns = output_columns
        self.batch_size = batch_size
        self.apply_transform = apply_transform
    def evaluate(self, x, batch_id, iteration_number, mode):
        global JOB_ID, SGE_TASK_ID
        if mode == 'cluster':
            JOB_ID = os.environ.get("JOB_ID")
            SGE_TASK_ID = batch_id 
        elif mode == 'local':
            JOB_ID = 0
            SGE_TASK_ID = 0
        
        work_directory = os.path.join(self.hydra_output_directory, f"iteration_{iteration_number}/batch_{SGE_TASK_ID}")
        
        if not os.path.exists(work_directory):
            shutil.copytree(src=self.path_to_spinodal_resources, dst=work_directory)
        
        temp_directory = self.path_to_GIBBON+ f"/data/temp_{JOB_ID}_batch_{SGE_TASK_ID}_iter_{iteration_number}"

        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)

        sio.savemat(work_directory + '/temp_directory.mat',
                    {'temp_directory': temp_directory})
        
        x_numpy = x.cpu().detach().numpy()
        
        if self.batch_size > 1:
            x_numpy = x_numpy.tolist()
            x_numpy = np.array([x_numpy])

        if np.all(x_numpy[:, 1:4] <= 1e-5):
            logger.info("Thetas are all zeros. Null objective. Objective assumed to be a dominated point")
            objectives = torch.tensor([[-4, -0.2]]) 
            if 'EA_Mode' in self.output_columns:
                ea_mode_data = pd.DataFrame([['Null']], columns=['EA_Mode'])

            else:
                ea_mode_data = None
            return x, objectives, ea_mode_data
        
        else:
            with open(os.path.join(work_directory, 'acquisition.txt'), 'w') as f:
                for row in x_numpy:
                    f.write(' '.join(map(str, row)) + '\n')

            os.chdir(work_directory)

            matlab_process = subprocess.Popen(["C:/Program Files/MATLAB/R2020b/bin/matlab.exe", "-nosplash", "-wait", "-nodesktop", "-r",  "Objective_Spinodoid_Tet; exit"])
            matlab_process.wait()

            output_file_path = os.path.join(work_directory, 'OBJECTIVE_output.txt')

            if os.path.exists(output_file_path):

                outputs = pd.read_csv(output_file_path, sep='\s+', names=['mass', 'EA', 'Peak_Force', 'CE', 'combined', 'EA_Mode'])

                selected_outputs = outputs[self.output_columns]

                if 'EA_Mode' in self.output_columns:
                    ea_mode_data = selected_outputs.pop('EA_Mode')
                else:
                    ea_mode_data = None
                
                if ea_mode_data is not None:
                
                    if ea_mode_data.iloc[0] == 'progressive_failure':
                    
                        output_array_numeric = selected_outputs.to_numpy()
                        objectives = torch.tensor(output_array_numeric)

                    else:

                        objectives = torch.tensor([[-4, -0.2]])

                else:

                    output_array_numeric = selected_outputs.to_numpy()
                    objectives = torch.tensor(output_array_numeric)                

                ### Output scaling ###

                objectives = utility_functions.output_transform(objectives, self.apply_transform).to(**self.tkwargs)

                ######################

                if torch.isnan(objectives).any() or (objectives == 0).any() or torch.isinf(objectives).any():
                    logger.info("Random input required. Objective is either NaN, zero or inf. Generating and evaluating random design...")
                    x = self.generate_random_input()
                    logger.info(f'Random Input: {x.cpu().detach().numpy()}')

                    x, objectives, ea_mode_data = self.evaluate(x, batch_id, iteration_number, mode)
                    logger.info(f'Random Output: {objectives.cpu().detach().numpy()}')

                return x, objectives, ea_mode_data
                
    def __call__(self, x):
        return self.evaluate(x)
    
    def generate_random_input(self):
        random_input = torch.empty((1, self.dim), **self.tkwargs)
        while True:
            for i in range(self.dim):
                lower_bound = self.bounds[0, i].clone().detach()
                upper_bound = self.bounds[1, i].clone().detach()
                random_input[0, i] = random.uniform(lower_bound, upper_bound).clone().detach()

            if not torch.isnan(random_input).any():
                break
        return random_input

    def evaluate_random_input(self, random_input, batch_id, iteration_number, mode):
        max_attempts = 1  # Maximum number of attempts to generate a valid random input
        for _ in range(max_attempts):
            random_output = self.evaluate(random_input, batch_id, iteration_number, mode)
            if not (torch.isnan(random_output).any() or (random_output == 0).any() or torch.isinf(random_output).any()):
                return random_output

            logger.info("Generated design contains NaNs or zeros or inf. Regenerating...")
            random_input = self.generate_random_input()

        logger.error(f"Failed to evaluate a valid random output after {max_attempts} attempts.")

        return None
