# MOBO
**Open-source Code for Multi-objective Bayesian Optimisation of Spinodoid Cellular Materials**

This repository introduces a multi-objective Bayesian optimisation (MOBO) framework for optimising spinodoid structures—scalable, non-periodic topologies with efficient stress distribution—to enhance crush energy absorption under impact. The framework addresses the challenge of balancing conflicting objectives: maximising energy absorption while minimising peak forces, accounting for non-linear material behavior and plastic deformation. By integrating finite element analysis (FEA) with Bayesian optimisation, it efficiently navigates the design space, reducing computational costs compared to conventional methods (e.g., NSGA-II). Key features include:

- Pareto-optimal solutions via scalarisation and hypervolume techniques.

- Avoidance of structural densification to maintain integrity.

- Superior performance over NSGA-II in computational efficiency and solution quality.

Ideal for real-world structural/material optimisation where complex trade-offs and non-linear dynamics are critical.

![varying_relative_density_wavenumber_page-0001](https://github.com/user-attachments/assets/1788a7de-42dc-4301-93fc-47a7db6a9a6b)

Figure 1: Visualisation of changes in two design parameters using graded spinodoids. Both structures were produced with $\theta_1 = 90^\circ, \theta_2 = 0^\circ, \theta_3 = 0^\circ$. (a) A linearly graded generated with an increasing relative density from left to right. The left side has the lowest relative density, starting at 0.3, the middle portion has a relative density of 0.45, and the right side reaches a relative density of 0.6. (b) A structure illustrating an increase in the wave number from left to right. The left side has the lowest wave number of $4\pi$, the right has the highest at $20\pi$, and the middle portion has an intermediate value of $12\pi$. It should be noted that these structures serve as a visualisation tool and do not represent the structures being optimised.

![MOBO_framework2 (1)_page-0001](https://github.com/user-attachments/assets/2e95605e-1955-4db3-a32e-aea2230ad332)

Figure 2: A schematic of the multi-objective Bayesian optimisation (MOBO) process for optimising the spinodoid cellular structure design space involves four steps of the data-driven process. (1) Initial Dataset Creation: Sampling 50 points from the design space using the Sobol' sequence and evaluate them with FEM simulations to build the initial dataset. (2) Surrogate Model Update: Updating the Gaussian Process model based on the dataset to predict structural properties. (3) Identifying samples to evaluate: Using an acquisition function to identify and evaluate the most promising design points. (4) FEM Simulations: Performing FEM analysis on generated structures and extracting objectives to then update the dataset.


![optimisation_History_and_Hypervolume](https://github.com/user-attachments/assets/fcac0a0f-6272-4403-8e59-8c4c61d35768)

Figure 3: Optimisation history: peak force verus energy absorption. Insert figure: the hypervolume evoluation against iterations. 

![Geometry_Changes_with_Pareto_Front_Sorted](https://github.com/user-attachments/assets/34c5bf71-10ed-4da3-aaf2-febcc4ea2524)

Figure 4: Topologies changes with the changing pareto front. 

MOBO is an open-source framework capable of carrying out Bayesian optimisation of spinodoid cellular materials.

First author: **Hirak Kansara**, Code contribution: Siamak Khosroshahi, Corresponding author: **Dr Wei Tan (wei.tan@qmul.ac.uk)**


## 🛠 Installation

### **Prerequisites**
- Python 3.8+  
- [pip](https://pip.pypa.io/en/stable/installation/)  
- FEA software (Abaqus)
- MATLAB (Requires the GIBBON library https://github.com/gibbonCode/GIBBON.git and ImageProcessingToolBox)

### **Steps**  
1. **Clone the repository**:  
   ```bash  
   git clone https://github.com/MCM-QMUL/MOBO.git
   cd MOBO 
   ```  

2. **Install dependencies**:  
   ```bash  
   pip install -r requirements.txt  
   ```  
   Key packages include:  
   - `numpy`, `scipy`: Numerical operations.  
   - `botorch`, `gpytorch`: Bayesian optimisation.  
   - `pymoo`: Multi-objective optimisation utilities.  

3. **Change directories in**:  
   - config.yaml to define path to MOBO folder, path to spinodal resources, and path to GIBBON folder
   - MOBO_standalone\spinodal_resources\spinodoid_scripy.py to allow subprocess to call MATLAB.exe file
   - Add path to GIBBON folder in Objective_Spinodoid_Tet.m lines 6 & 7
---

## 🚀 Running Jobs

### **Basic Usage**  
Run the optimisation workflow with:  
```bash  
python main.py
```  

#### **Input Parameters** (edit `config.yaml`)  
- `input_columns`: Design parameters.
- `n_iterations`: Number of MOBO iterations used as stopping criteria
- `kernel`: Type of kernel used for covariance calculation
- `MOBO_type`: MOBO methods as described in the article
- `apply_transform`: If True, scales the objectives for them to be maximised.
  
#### **Output Parameters** (edit `config.yaml`)  
- `output_columns`: Parameters to output, maximised by default
- **Pareto-optimal designs**: Saved to `hydra_output_dir/pareto_front.csv`.
- **Optimisation History**: Saved to `hydra_output_dir/optimisation_history.csv`.  
- **Simulation logs**: Stored in `hydra_output_dir/main.log`.  

### **Example Workflow**  
1. Define objectives in `config.yaml`:  
   ```yaml  
   objectives:  
     EA 
     Peak_Force
   ```  

2. Start optimisation:  # change mode in main.py if running framework either locally or on cluster
   ```bash  
   python main.py  
   ```  

3. Analyse results:  
   - View Pareto front: `hydra_output_dir/pareto_front.csv`.  
---

## 💡 Notes  
- **Hardware**: Simulations are computationally intensive. Use HPC/cluster for large-scale runs.  
- **Troubleshooting**:  
  - If FEA fails, check `<job_name>.o<job_id>`.  
  - Mesh density can be changed in /MOBO_standalone/spinodal_resources/Objective_Spinodoid_Tet.m by changing the res variable for faster debugging.

## Reference
If using this code for research or industrial purposes, please cite:

[1] Kansara, H., Khosroshahi, S.F., Guo, L., Bessa, M.A. and Tan, W., Multi-objective Bayesian Optimisation of Spinodoid Cellular Structures for Crush Energy Absorption. Computer Methods for Applied Mechanics and Engineering, 2025. https://doi.org/10.1016/j.cma.2025.117890

## License
MIT
