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


import hydra
import sys
import os
# sys.path.insert(0, os.path.abspath('C:\\Temp\\MOO'))
sys.path.insert(0, os.path.abspath('C:\\Temp\MOO\\benchmark'))
# from MOBO_optimise import MOBO_optimise

#from ZDT1_benchmark import MOBO_optimise

from BraninCurrin_benchmark import MOBO_optimise
@hydra.main(config_path=".", config_name="config")

def main(config):

    if config.hpc.jobid == 1:
        MOBO_optimise(config, mode = 'local') # mode = 'local' or 'cluster'
    else:
        pass

if __name__ == "__main__":
    main()

'''
TO DO:
- break down the process into multiple different stages with different files.
- before optimisation begins, must create a csv file containing the initial data in the same folder as the output folder created by hydra
- then in each step of optimisation when batch_size > 1, all the inputs should be stored in the csv file containing the initial data.
- then when the jobid is greater than 1, the main_local() file should then call the spinodoid script to evaluate the inputs with different nodes, 
each running a different simulation.
- this data should then be stored within the initial csv file.

NEED TO FIGURE OUT:
- how to call different nodes based on jobids.
'''
