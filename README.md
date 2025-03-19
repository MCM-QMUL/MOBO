# MOBO
**Open-source Code for Multi-objective Bayesian Optimisation of Spinodoid Cellular Materials**

![varying_relative_density_wavenumber_page-0001](https://github.com/user-attachments/assets/dfe81601-d499-4ae4-8248-8e51f4ca32f0)
Figure 1: Visualisation of changes in two design parameters using graded spinodoids. Both structures were produced with $\theta_1 = 90^\circ, \theta_2 = 0^\circ, \theta_3 = 0^\circ$. (a) A linearly graded generated with an increasing relative density from left to right. The left side has the lowest relative density, starting at 0.3, the middle portion has a relative density of 0.45, and the right side reaches a relative density of 0.6. (b) A structure illustrating an increase in the wave number from left to right. The left side has the lowest wave number of $4\pi$, the right has the highest at $20\pi$, and the middle portion has an intermediate value of $12\pi$. It should be noted that these structures serve as a visualisation tool and do not represent the structures being optimised.

![MOBO_framework2 (1)_page-0001](https://github.com/user-attachments/assets/4a394a24-e756-48e3-8a4c-6df62c4beadb)
Figure 2: A schematic of the multi-objective Bayesian optimisation (MOBO) process for optimising the spinodoid cellular structure design space involves four steps of the data-driven process. (1) Initial Dataset Creation: Sampling 50 points from the design space using the Sobol' sequence and evaluate them with FEM simulations to build the initial dataset. (2) Surrogate Model Update: Updating the Gaussian Process model based on the dataset to predict structural properties. (3) Identifying samples to evaluate: Using an acquisition function to identify and evaluate the most promising design points. (4) FEM Simulations: Performing FEM analysis on generated structures and extracting objectives to then update the dataset.

MOBO is an open-source framework capable of carrying out Bayesian optimisation of spinodoid cellular materials.

First author: **Hirak Kansara**, Code contribution:Siamak Khosroshahi, Corresponding authors: **Dr Wei Tan (wei.tan@qmul.ac.uk)**


## Reference
If using this code for research or industrial purposes, please cite:

[1] Kansara, H., Khosroshahi, S.F., Guo, L., Bessa, M.A. and Tan, W., 2024. Multi-objective Bayesian Optimisation of Spinodoid Cellular Structures for Crush Energy Absorption. Computer Methods for Applied Mechanics and Engineering, 2025

## License
MIT
