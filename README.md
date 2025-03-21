# MOBO
**Open-source Code for Multi-objective Bayesian Optimisation of Spinodoid Cellular Materials**

This repository introduces a multi-objective Bayesian optimization (MOBO) framework for optimizing spinodoid structures—scalable, non-periodic topologies with efficient stress distribution—to enhance crush energy absorption under impact. The framework addresses the challenge of balancing conflicting objectives: maximizing energy absorption while minimizing peak forces, accounting for non-linear material behavior and plastic deformation. By integrating finite element analysis (FEA) with Bayesian optimization, it efficiently navigates the design space, reducing computational costs compared to conventional methods (e.g., NSGA-II). Key features include:

-Pareto-optimal solutions via scalarization and hypervolume techniques.

-Avoidance of structural densification to maintain integrity.

-Superior performance over NSGA-II in computational efficiency and solution quality.

Ideal for real-world structural/material optimization where complex trade-offs and non-linear dynamics are critical.

![varying_relative_density_wavenumber_page-0001](https://github.com/user-attachments/assets/1788a7de-42dc-4301-93fc-47a7db6a9a6b)

Figure 1: Visualisation of changes in two design parameters using graded spinodoids. Both structures were produced with $\theta_1 = 90^\circ, \theta_2 = 0^\circ, \theta_3 = 0^\circ$. (a) A linearly graded generated with an increasing relative density from left to right. The left side has the lowest relative density, starting at 0.3, the middle portion has a relative density of 0.45, and the right side reaches a relative density of 0.6. (b) A structure illustrating an increase in the wave number from left to right. The left side has the lowest wave number of $4\pi$, the right has the highest at $20\pi$, and the middle portion has an intermediate value of $12\pi$. It should be noted that these structures serve as a visualisation tool and do not represent the structures being optimised.

![MOBO_framework2 (1)_page-0001](https://github.com/user-attachments/assets/2e95605e-1955-4db3-a32e-aea2230ad332)

Figure 2: A schematic of the multi-objective Bayesian optimisation (MOBO) process for optimising the spinodoid cellular structure design space involves four steps of the data-driven process. (1) Initial Dataset Creation: Sampling 50 points from the design space using the Sobol' sequence and evaluate them with FEM simulations to build the initial dataset. (2) Surrogate Model Update: Updating the Gaussian Process model based on the dataset to predict structural properties. (3) Identifying samples to evaluate: Using an acquisition function to identify and evaluate the most promising design points. (4) FEM Simulations: Performing FEM analysis on generated structures and extracting objectives to then update the dataset.

MOBO is an open-source framework capable of carrying out Bayesian optimisation of spinodoid cellular materials.

First author: **Hirak Kansara**, Code contribution:Siamak Khosroshahi, Corresponding authors: **Dr Wei Tan (wei.tan@qmul.ac.uk)**


## 🛠 Installation

### **Prerequisites**
- Python 3.8+  
- [pip](https://pip.pypa.io/en/stable/installation/)  
- FEA software (Abaqus)
- Matlab

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
   - `gpflow`, `trieste`: Bayesian optimization.  
   - `pymoo`: Multi-objective optimization utilities.  

3. **(Optional) Set up FEA integration**:  
   - Configure paths to your FEA solver in `config.yaml`.  
   - Test with:  
     ```bash  
     python tests/test_fea.py  
     ```  

---

## 🚀 Running Jobs

### **Basic Usage**  
Run the optimization workflow with:  
```bash  
python main.py --config config.yaml  
```  

#### **Input Parameters** (edit `config.yaml`)  
- `material_model`: Elastoplastic parameters (e.g., yield stress).  
- `design_bounds`: Min/max values for spinodoid topology variables.  
- `objectives`: Set weights for `energy_absorption` and `peak_force`.  

### **Outputs**  
- **Pareto-optimal designs**: Saved to `results/pareto_front.csv`.  
- **Simulation logs**: Stored in `logs/optimization.log`.  
- **Visualizations**: Generate plots with:  
  ```bash  
  python scripts/plot_results.py --input results/pareto_front.csv  
  ```  

### **Example Workflow**  
1. Define objectives in `config.yaml`:  
   ```yaml  
   objectives:  
     energy_absorption: maximize  
     peak_force: minimize  
   ```  

2. Start optimization:  
   ```bash  
   python optimize.py --config config.yaml  
   ```  

3. Analyze results:  
   - View Pareto front: `results/pareto_front.csv`.  
   - Visualize top designs:  
     ```bash  
     python scripts/render_design.py --id 42  
     ```  

### **Advanced Options**  
- Parallel evaluation: Add `--workers 4` to use 4 CPU cores.  
- Resume optimization:  
  ```bash  
  python main.py --config config.yaml --resume_from results/checkpoint.pkl  
  ```  

---

## 💡 Notes  
- **Hardware**: Simulations are computationally intensive. Use HPC/cluster for large-scale runs.  
- **Troubleshooting**:  
  - If FEA fails, check `logs/simulation_errors.log`.  
  - Reduce mesh density in `config.yaml` for faster debugging.  

## Reference
If using this code for research or industrial purposes, please cite:

[1] Kansara, H., Khosroshahi, S.F., Guo, L., Bessa, M.A. and Tan, W., 2024. Multi-objective Bayesian Optimisation of Spinodoid Cellular Structures for Crush Energy Absorption. Computer Methods for Applied Mechanics and Engineering, 2025

## License
MIT
