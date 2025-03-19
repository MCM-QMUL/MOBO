import numpy as np
from pymoo.core.problem import ElementwiseProblem
import random
import shutil
import scipy.io as sio
import subprocess
import os
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination
import pandas as pd
from pymoo.core.evaluator import Evaluator
from pymoo.core.population import Population
from pymoo.problems.static import StaticProblem
from pymoo.core.callback import Callback
import dill
from pymoo.termination.max_gen import MaximumGenerationTermination
from pymoo.termination import get_termination
import logging

logging.basicConfig(filename='spinodoid_optimisation.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def output_transform(train_y):
    train_y[:, 0] = np.log(1/train_y[:, 0])
    train_y[:, 1] = train_y[:, 1]
    return train_y

class Spinodoid_problem(ElementwiseProblem):

    def __init__(self, path_to_spinodal_resources, output_directory, path_to_GIBBON, output_columns, algorithm):
        super().__init__(n_var= 4, 
                          n_obj= 2, 
                          n_constr= 0, 
                          xl= np.array([0.3, 0, 0, 0]), 
                          xu= np.array([0.6, 90, 90, 90]))
        self.path_to_spinodal_resources = path_to_spinodal_resources
        self.output_directory = output_directory
        self.path_to_GIBBON = path_to_GIBBON
        self.output_columns = output_columns
        self.data = {'inputs': [], 'outputs': []}
        self.dim = 4
        self.algorithm = algorithm

    def _evaluate(self, x, out, iteration_number=4, mode='cluster'):
        
        if mode == 'cluster':
            JOB_ID = os.environ.get("JOB_ID")
            SGE_TASK_ID = os.environ.get('SGE_TASK_ID')
        elif mode == 'local':
            JOB_ID = 1
            SGE_TASK_ID = 1
        
        work_directory = os.path.join(self.output_directory, f"iteration_{iteration_number}/job_{SGE_TASK_ID}")

        if not os.path.exists(work_directory):
            shutil.copytree(src=self.path_to_spinodal_resources, dst=work_directory)
        
        temp_directory = self.path_to_GIBBON+ f"/data/temp_{JOB_ID}_job_{SGE_TASK_ID}_iter_{iteration_number}"

        if not os.path.isdir(temp_directory):
            os.mkdir(temp_directory)

        sio.savemat(work_directory + '/temp_directory.mat', {'temp_directory': temp_directory})

        x_numpy = np.array(x)

        if x_numpy[1] <= 1e-5 and x_numpy[2] <= 1e-5 and x_numpy[3] <= 1e-5:
            logging.debug("Thetas are all zeros. Generating random design...")
            x = self.generate_random_input()
            x_numpy = np.array(x)
            logging.debug(f'Random Input: {x_numpy}')

        with open(os.path.join(work_directory, 'acquisition.txt'), 'w') as f:
            logging.debug(f'Acquisition values: {x_numpy}')
            f.write(' '.join(map(str, x_numpy)) + '\n')

        os.chdir(work_directory)
        
        matlab_process = subprocess.Popen(["matlab", "-nosplash", "-wait", "-nodesktop", "-r",  "Objective_Spinodoid_Tet; exit"])
        matlab_process.wait()

        output_file_path = os.path.join(work_directory, 'OBJECTIVE_output.txt')
        if os.path.exists(output_file_path):
            outputs = pd.read_csv(output_file_path, sep='\s+', names=['mass', 'EA', 'Peak_Force', 'CE', 'combined', 'EA_Mode'])
            selected_outputs = outputs[self.output_columns]
             
            ea_mode_data = outputs['EA_Mode']
                
            if ea_mode_data is not None and ea_mode_data.iloc[0] == 'progressive_failure':
                outputs = selected_outputs.to_numpy()
            else:
                outputs = np.array([[1, 1]])

            out['F'] = outputs[0][0], outputs[0][1]
            logging.debug(f'Outputs: {outputs}')
        else:
            logging.debug("Output file not found or empty. Generating and evaluating random design...")
            random_input = self.generate_random_input()
            random_output = self.evaluate_random_input(random_input, out, SGE_TASK_ID, iteration_number, mode)
            out['F'] = random_output[0][0], random_output[0][1]

        self.data['inputs'].append(x_numpy)
        self.data['outputs'].append(out['F'])

        df_inputs = pd.DataFrame(self.data['inputs'], columns=['Ro', 'Theta_1', 'Theta_2', 'Theta_3'])
        df_outputs = pd.DataFrame(self.data['outputs'], columns=['EA', 'Peak_Force'])
        df_combined = pd.concat([df_inputs, df_outputs], axis=1)
        df_combined.to_csv('inputs_outputs.csv', index=False)

        # Save checkpoint
        with open("checkpoint", "wb") as f:
            dill.dump(self.algorithm, f)
        logging.debug("Checkpoint saved after evaluation.")

    def __call__(self, x):
        return self.evaluate(x)
    
    def generate_random_input(self):
        random_input = np.empty((1, self.dim))
        while True:
            for i in range(self.dim):
                lower_bound = self.xl[i].copy()
                upper_bound = self.xu[i].copy()
                random_input[0, i] = random.uniform(lower_bound, upper_bound)

            if not np.isnan(random_input).any():
                break
        logging.debug(f'Generated random input: {random_input}')
        return random_input

    def evaluate_random_input(self, random_input, out, sge_jobid, iteration_number, mode):
        logging.debug(f'Evaluating random input: {random_input}')
        random_output = self.evaluate(random_input, sge_jobid, iteration_number, mode)
        
        if np.isnan(random_output).any() or (random_output == 0).any() or np.isinf(random_output).any():
            logging.debug("Generated design contains NaNs or zeros or inf. Regenerating...")
            random_input = self.generate_random_input()
            random_output = self.evaluate(random_input, sge_jobid, iteration_number, mode)

        out['F'] = random_output[0][0], random_output[0][1]
        logging.debug(f'Random output: {random_output}')

        return random_output

class SaveResultsCallback(Callback):

    def __init__(self, output_directory):
        super().__init__()
        self.data["obj"] = []
        self.data["inputs"] = []

    def notify(self, algorithm):
        self.data["obj"].append(algorithm.pop.get("F"))
        self.data["inputs"].append(algorithm.pop.get("X"))

input_columns = ['Ro','Theta_1', 'Theta_2', 'Theta_3']
output_columns = ['EA', 'Peak_Force']

callback = SaveResultsCallback('/data/home/exx687/MOO/NSGA_2/outputs/')

path_to_initial_data = os.path.join('/data/home/exx687/MOO/NSGA_2/inputs_outputs.csv')
df = pd.read_csv(path_to_initial_data)
df.columns = df.columns.str.strip()

X = df[input_columns].to_numpy()
Y = df[output_columns].to_numpy()
Y = output_transform(Y)

initial_population = Population.new('X', X)
initial_population.set("F", Y)

if os.path.exists("checkpoint"):
    with open("checkpoint", 'rb') as f:
        algorithm = dill.load(f)
    logging.info("Checkpoint loaded. Resuming optimization...")
    
    termination = MaximumGenerationTermination(algorithm.n_gen + 10)
else:
    logging.info("No checkpoint found. Starting new optimization...")
    algorithm = NSGA2(
        pop_size=30,
        n_offsprings=25,
        crossover=SBX(prob=0.9, eta=15),
        mutation=PM(eta=20),
        eliminate_duplicates=True
    )

    termination = get_termination("n_gen", 10)

problem = Spinodoid_problem(path_to_GIBBON='/data/home/exx687/MOO/GIBBON/',
                            path_to_spinodal_resources='/data/home/exx687/MOO/MOBO_standalone/spinodal_resources/',
                            output_directory='/data/home/exx687/MOO/NSGA_2/outputs/',
                            output_columns=output_columns,
                            algorithm=algorithm)

res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               callback=callback,
               save_history=True,
               verbose=True,
               copy_algorithm=False,
               initial_population=initial_population)

with open("checkpoint", "wb") as f:
    dill.dump(algorithm, f)

X = res.X
F = res.F

X_df = pd.DataFrame(X, columns=['Rho', 'Theta_1', 'Theta_2', 'Theta_3'])
F_df = pd.DataFrame(F, columns=['EA', 'Peak_Force'])

combined_df = pd.concat([X_df, F_df], axis=1)
combined_df.to_csv('NSGA_2_output.csv', index=False)

for i, (X, F) in enumerate(zip(callback.data["inputs"], callback.data["obj"])):
    X_df = pd.DataFrame(X, columns=['Rho', 'Theta_1', 'Theta_2', 'Theta_3'])
    F_df = pd.DataFrame(F, columns=['EA', 'Peak_Force'])
    combined_df = pd.concat([X_df, F_df], axis=1)
    combined_df.to_csv(f'generation_{i}.csv', index=False)
