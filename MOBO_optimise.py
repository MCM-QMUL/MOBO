import torch
from botorch import fit_gpytorch_mll
import gpytorch.kernels
import os
import sys
import logging
from hydra.core.hydra_config import HydraConfig
import pandas as pd

tkwargs = {"dtype": torch.double, "device": torch.device("cuda" if torch.cuda.is_available() else "cpu")}

def MOBO_optimise(config, mode):

    logger = logging.getLogger(__name__)

    path_to_spinodal_resources = config.path_to_spinodal_resources

    hydra_cfg = HydraConfig.get()

    hydra_output_directory = hydra_cfg['runtime']['output_dir']    

    MOBO_type = config.MOBO_type 
    n_iterations = config.n_iterations
    input_columns = config.input_columns    
    output_columns = config.output_columns
    kernel = config.kernel
    path_to_MOBO = config.path_to_MOBO_folder
    batch_size = config.batch_size
    path_to_GIBBON = config.path_to_GIBBON
    initial_data_filename = config.initial_data_filename
    apply_transform = config.apply_transform

    sys.path.insert(0, os.path.abspath(path_to_MOBO+'/MOBO_standalone'))
    sys.path.insert(0, os.path.abspath(path_to_MOBO+'/src'))

    from MOBO_methods import MOBO_methods
    from spinodoid_script import Spinodoid_function
    from initialise_GP import initialise_model
    from utility import utility_functions

    if kernel == 'RBF':
        kernel = gpytorch.kernels.RBFKernel()

    elif kernel == 'Matern':
        kernel = gpytorch.kernels.MaternKernel()

    train_x, train_y = utility_functions.initial_data_to_csv(
        path_to_spinodal_resources=path_to_spinodal_resources, 
        path_to_MOBO=path_to_MOBO,
        hydra_output_directory=hydra_output_directory, 
        input_columns=input_columns, 
        output_columns=output_columns, 
        initial_data_file_name=initial_data_filename,
        tkwargs=tkwargs,
        apply_transform=apply_transform
    )

    ## In the event that EA_Mode is not None, i.e. densification filter is required, must prep the data accordingly.

    # if ea_mode_data is not None:
    #     train_x, train_y = utility_functions.densification_filtering(train_x_unfiltered, train_y_unfiltered, ea_mode_data)

    optimisation_file_path = os.path.join(hydra_output_directory, 'optimisation_history.csv')
    pareto_front_file_path = os.path.join(hydra_output_directory, 'pareto_front.csv')

    problem = Spinodoid_function(train_x=train_x, 
                                 train_y=train_y, 
                                 path_to_spinodal_resources=path_to_spinodal_resources,
                                 hydra_output_directory=hydra_output_directory,
                                 path_to_GIBBON=path_to_GIBBON,
                                 output_columns=output_columns,
                                 batch_size=batch_size,
                                 apply_transform=apply_transform,
                                 tkwargs=tkwargs)

    mll, model = initialise_model(problem=problem, train_x=train_x, train_y=train_y, kernel=kernel, NOISE_SE=None)
    
    optimisation_history = pd.read_csv(optimisation_file_path)

    ## calculating the hypervolume for the initial data
        
    output_columns = [col for col in output_columns if col != 'EA_Mode']

    if MOBO_type != 'single_obj_optimise':
        hypervolume_values = []
        for i in range(optimisation_history.shape[0]):
            
            train_y_iter = optimisation_history.loc[0:i, output_columns].reset_index(drop=True).to_numpy()
            train_y_iter = torch.from_numpy(train_y_iter).to(**tkwargs)

            volume = utility_functions.get_hypervolume(ref_point=problem.ref_point, output_data=train_y_iter)
            hypervolume_values.append(volume)

        optimisation_history['volume'] = hypervolume_values

        optimisation_history.to_csv(optimisation_file_path, index=False)

        for i in range(n_iterations):
            fit_gpytorch_mll(mll)

            MOBO_output = MOBO_methods(MOBO_type=MOBO_type, problem=problem, model=model, train_x=train_x, train_y=train_y, batch_size=batch_size)
            
            new_x = MOBO_output.run_optimisation()
            
            logger.info(f'Iteration {i}: Next point to evaluate = {new_x.cpu().detach().numpy()}')

            current_x, new_obj, ea_mode_data = problem.evaluate(new_x, mode=mode, batch_id=0, iteration_number=i) 
            
            logger.info(f'Iteration {i}: Objective value = {new_obj.cpu().detach().numpy()}')

            new_x = current_x 

            utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'new_x', new_x, input_columns, output_columns)

            utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'new_obj', new_obj, input_columns, output_columns)
            
            if ea_mode_data is not None:
                utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'EA_Mode', ea_mode_data, input_columns, output_columns)

            train_x = torch.cat([train_x, new_x])
            train_y = torch.cat([train_y, new_obj])
            
            mll, model = initialise_model(problem=problem, train_x=train_x, train_y=train_y, kernel=kernel, NOISE_SE=None)

            volume = utility_functions.get_hypervolume(ref_point=problem.ref_point, output_data=train_y)

            utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'volume', volume, input_columns, output_columns)

        utility_functions.get_pareto(train_x, train_y, input_columns, output_columns, pareto_front_file_path)

    else: # for single objective optimisation

        optimisation_history.to_csv(optimisation_file_path, index=False)

        for i in range(n_iterations):
            fit_gpytorch_mll(mll)

            MOBO_output = MOBO_methods(MOBO_type=MOBO_type, problem=problem, model=model, train_x=train_x, train_y=train_y, batch_size=batch_size)
            
            new_x = MOBO_output.run_optimisation()
            
            logger.info(f'Iteration {i}: Next point to evaluate = {new_x.cpu().detach().numpy()}')

            current_x, new_obj, ea_mode_data = problem.evaluate(new_x, mode=mode, batch_id=0, iteration_number=i) 
            
            logger.info(f'Iteration {i}: Objective value = {new_obj.cpu().detach().numpy()}')

            new_x = current_x # in the event that random input is required

            utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'new_x', new_x, input_columns, output_columns)

            utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'new_obj', new_obj, input_columns, output_columns)
            
            if ea_mode_data is not None:
                utility_functions.append_to_optimisation_history_csv(optimisation_file_path, 'EA_Mode', ea_mode_data, input_columns, output_columns)

            train_x = torch.cat([train_x, new_x])
            train_y = torch.cat([train_y, new_obj])
            
            mll, model = initialise_model(problem=problem, train_x=train_x, train_y=train_y, kernel=kernel, NOISE_SE=None)
