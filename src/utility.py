import torch
from botorch.utils.multi_objective.pareto import is_non_dominated
import os
import pandas as pd
import numpy as np
from botorch.utils.multi_objective.box_decompositions.dominated import DominatedPartitioning
from botorch.exceptions.errors import BotorchTensorDimensionError, UnsupportedError
from botorch.utils.transforms import normalize
from torch import Tensor            
from typing import Callable, Optional

class utility_functions:
    @staticmethod
    def adjust_boundary(new_x, problem, delta=1e-7):
        '''
        Function reads the new_x to evaluate and adds/subtracts delta from them if they're close to the bounds.

        RETURNS:
        - Adjusted new_x
        
        '''
        for i in range(problem.dim):
            if torch.isclose(new_x[0, i], problem.bounds[1, i], atol=delta):
                new_x[0, i] = problem.bounds[1, i]
            elif torch.isclose(new_x[0, i], problem.bounds[0, i], atol=delta):
                new_x[0, i] = problem.bounds[0, i]
        return new_x
    

    def output_transform(train_y, apply_transform):

        '''
        Function used to transform the output to ensure a maximising problem is being solved.

        Assuming two objectives in the order of EA and Peak_Force

        RETURNS:
        - Transformed output
        
        '''
        if apply_transform == True:
            train_y[:, 0] = -torch.log(1/train_y[:, 0])
            train_y[:, 1] = -train_y[:, 1]
        
        else:
            train_y[:, 0] = train_y[:, 0]
   
        return train_y

    def densification_filtering(train_x, train_y, ea_mode):
        '''
        Function filters the train_y values based on ea_mode label.
        If the label is 'densification', it sets that particular train_y array to torch.tensor([[-4, -0.2]]).

        RETURNS:
        - Filtered train_x and train_y tensors.
        '''
        
        if ea_mode is not None:

            for idx, mode in enumerate(ea_mode):
                if mode == 'densification':
                    train_y[idx] = torch.tensor([[-4, -0.2]])

        return train_x, train_y
 
    def initial_data_to_csv(path_to_spinodal_resources, hydra_output_directory, input_columns, output_columns, path_to_MOBO, initial_data_file_name, tkwargs, apply_transform):
        '''
        Function reads data from initial csv file and creates a new csv file containing the selected inputs and outputs.
        
        OUTPUTS:
        - New csv file named 'optimisation_history.csv' in hydra output directory.

        RETURNS:
        - The selected inputs and outputs are converted to GPU tensors if CUDA is available.
        - A separate variable for 'EA_Mode' if present in output_columns.
        '''
        os.chdir(path_to_spinodal_resources)

        filename = os.path.join(path_to_MOBO, initial_data_file_name + '.csv')

        if initial_data_file_name == 'initial_doe_cleaned' or initial_data_file_name == 'initial_doe_cleaned_failure_type':
            df = pd.read_csv(filename, skiprows=[0])
        else:
            df = pd.read_csv(filename)

        if 'EA_Mode' in output_columns:
            ea_mode_data = df['EA_Mode']
            output_columns = [col for col in output_columns if col != 'EA_Mode']
        else:
            ea_mode_data = None

        output_array = df[output_columns].to_numpy()
        output_array = torch.from_numpy(output_array)
        transformed_output = utility_functions.output_transform(output_array, apply_transform).detach().numpy()
        transformed_df = pd.DataFrame(transformed_output, columns=output_columns)

        df = pd.concat([df.drop(output_columns, axis=1), transformed_df], axis=1)
        if ea_mode_data is not None:
            df['EA_Mode'] = ea_mode_data

        selected_columns = input_columns + output_columns
        if ea_mode_data is not None:
            selected_columns.append('EA_Mode')

            densification_mask = ea_mode_data == 'densification'
            df.loc[densification_mask, output_columns] = [-4, -0.2]
            
        selected_df = df[selected_columns]

        input_data = selected_df[input_columns].to_numpy()
        output_data = selected_df[output_columns].to_numpy()

        train_x = torch.tensor(input_data).to(**tkwargs)
        train_y = torch.tensor(output_data).to(**tkwargs)

        if ea_mode_data is not None:
            
            train_x, train_y = utility_functions.densification_filtering(train_x, train_y, ea_mode_data)

        

        selected_df.to_csv(os.path.join(hydra_output_directory, 'optimisation_history.csv'), index=False)

        return train_x, train_y

    def get_pareto(train_x, train_y, input_columns, output_columns, pareto_data_file_path):
        '''

        This function should be used at the end of the optimisation to get the pareto optimal points.

        RETURNS:
        Set of pareto optimal inputs and their corresponding outputs.

        '''

        pareto_mask = is_non_dominated(train_y)

        pareto_x = train_x[pareto_mask].cpu().numpy()
        pareto_y = train_y[pareto_mask].cpu().numpy()

        input_dict = {col: pareto_x[:, i] for i, col in enumerate(input_columns)}
        output_dict = {col: pareto_y[:, i] for i, col in enumerate(output_columns)}

        combined_dict = {**input_dict, **output_dict}

        df = pd.DataFrame(combined_dict)
        df.to_csv(pareto_data_file_path, index=False)
    
    def append_to_optimisation_history_csv(optimisation_file_path, data, input_data, input_columns, output_columns):
        '''
        Function that adds the new input and new output in each iteration to the optimisation history.

        RETURNS:
        csv file that is updated with data from each iteration.
        
        '''
        # data_np = input_data.cpu().numpy().reshape(1, -1)
            
        if data == 'new_x':
            data_np = input_data.cpu().numpy().reshape(1, -1)
            df = pd.read_csv(optimisation_file_path)
            new_row = pd.DataFrame(data_np, columns=input_columns)
            df = pd.concat([df, new_row[input_columns]], ignore_index=False)
            df.to_csv(optimisation_file_path, index=False)

        elif data == 'new_obj':
            data_np = input_data.cpu().numpy().reshape(1, -1)
            df = pd.read_csv(optimisation_file_path)
            new_row = pd.DataFrame(data_np, columns=output_columns)
            df.loc[df.index[-1], output_columns] = data_np # df = pd.concat([df, new_row[output_columns]], ignore_index=True)
            df.to_csv(optimisation_file_path, index=False)

        elif data == 'new_obj_true':
            data_np = input_data.cpu().numpy().reshape(1, -1)
            df = pd.read_csv(optimisation_file_path)
            new_row = pd.DataFrame(data_np, columns=output_columns)
            df.loc[df.index[-1], output_columns] = data_np 
            df.to_csv(optimisation_file_path, index=False)

        elif data =='volume':
            data_np = input_data
            df = pd.read_csv(optimisation_file_path)
            new_row = pd.DataFrame([data_np], columns=['volume'])
            df.loc[df.index[-1], ['volume']] = data_np 
            df.to_csv(optimisation_file_path, index=False)

        elif data =='EA_Mode':
            data_np = input_data.iloc[0]
            df = pd.read_csv(optimisation_file_path)
            new_row = pd.DataFrame([data_np], columns=['EA_Mode'])
            df.loc[df.index[-1], ['EA_Mode']] = data_np 
            df.to_csv(optimisation_file_path, index=False)

    def get_hypervolume(ref_point, output_data):

        '''
        Gives the encompassed hypervolume that is dominated by the pareto front.

        RETURNS:
        A value for the volume for each iteration.
        '''
        volume_partition = DominatedPartitioning(ref_point=ref_point, Y=output_data)
        volume = volume_partition.compute_hypervolume().item()

        return volume
    
    def get_weighted_sum_scalarisation(weights: Tensor, Y: Tensor):
        
        def weighted_sum(Y: Tensor) -> Tensor:
            product = weights * Y
            return product.sum(dim=-1)

        if Y.shape[-2] == 1:

            Y_bounds = torch.cat([Y, Y + 1], dim=0)
        else:
            # Set the bounds to be [min(Y_m), max(Y_m)], for each objective m
            Y_bounds = torch.stack([Y.min(dim=-2).values, Y.max(dim=-2).values])

        def obj(Y: Tensor, X: Optional[Tensor] = None) -> Tensor:
            # scale to [0,1]
            Y_normalized = normalize(Y, bounds=Y_bounds)

            return weighted_sum(Y=Y_normalized)

        return obj
