% clear all; close all; clc

%%%%%%%%%%%%%%%%%%%%%%%%%% Reading Force %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
force_peak_cube = 80475.8856371; 
EA_cube = 1747052.65623; 

system('abaqus cae noGUI=Force_Extractor');

fileID = fopen(['F_Z.rpt'],'r');
A = textscan(fileID,'%f %f %f','delimiter','\t', 'headerLines', 3);
fclose(fileID);

Force = cell2mat(A(3));

Displacement = cell2mat(A(2))*-1;

displacement_start = 0;
displacement_end = 0.2*Cube_Length; 

indices = find(Displacement >= displacement_start & Displacement <= displacement_end);

Force_range = Force(indices);

P_max_unnorm = max(Force_range);

Strain = Displacement/Cube_Length;
Stress = Force/Cube_Length/Cube_Length;

E_absorption_S = trapz(Strain, Stress);

E_absorption_unnorm   = trapz(Displacement, Force);
E_absorption = E_absorption_unnorm / EA_cube;

P_max = P_max_unnorm / force_peak_cube;
% P_max = log(1 ./ P_max);

CE = E_absorption_unnorm / (0.5 * P_max_unnorm * Cube_Length);
combined = sqrt(E_absorption^2 + CE^2);

P_min = min(Force);

[second_order_grad_02_05, p2] = calculate_second_order_gradient(Displacement, Force, [0.2*Cube_Length, 0.5*Cube_Length]);

if second_order_grad_02_05 > 350
    EA_mode = 'densification';
else
    EA_mode = 'progressive_failure';
end

% plot(Displacement, Force);
clear A;
%plot(Strain, Stress);
delete abaqus.rpy
%%%%%%%%%%%%%%%%%%%% Reading Mass & Volume %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
system('abaqus cae noGUI=MASS_VOLUME_Extractor');
fileID = fopen(['Mass.txt'],'r');
A = textscan(fileID,'%f','delimiter','\t');
fclose(fileID);
MASS = cell2mat(A);
Mass   = MASS(1);
Volume = MASS(2);
clear MASS
delete abaqus.rpy

function [second_order_gradient, p] = calculate_second_order_gradient(displacement, force, range)
    index_range = find(displacement >= range(1) & displacement <= range(2));
    displacement_subset = displacement(index_range);
    force_subset = force(index_range);
    
    p = polyfit(displacement_subset, force_subset, 2);
    second_order_gradient = p(1) * 2; % Second derivative of a*x^2 + b*x + c is 2*a
end