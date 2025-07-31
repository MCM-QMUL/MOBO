fileID = fopen('ASSEMBLY.inp','w');
fprintf(fileID,'%s\r\n','** ASSEMBLY');
fprintf(fileID,'%s\r\n','*Assembly, name=Assembly');
fprintf(fileID,'%s\r\n','*Instance, name=SPINODAL, part=SPINODAL');
fprintf(fileID,'%s\r\n','*End Instance');
fprintf(fileID,'%s\r\n','*Instance, name=Anvil, part=Plate');
fprintf(fileID,'%s\r\n','          0.,           0.,         0.');
fprintf(fileID,'%s\r\n','*End Instance');
fprintf(fileID,'%s\r\n','*Instance, name=Loader, part=Plate');
fprintf(fileID,'%s\r\n','          0.,           0.,         40.');
fprintf(fileID,'%s\r\n','*End Instance');
fprintf(fileID,'%s\r\n','*Nset, nset=Set-2, instance=Anvil');
fprintf(fileID,'%s\r\n',' 2602,');
fprintf(fileID,'%s\r\n','*Nset, nset=Set-3, instance=Loader');
fprintf(fileID,'%s\r\n',' 2602,');
fprintf(fileID,'%s\r\n','*Nset, nset=Set-4, instance=Loader');
fprintf(fileID,'%s\r\n',' 2602,');
fprintf(fileID,'%s\r\n','*Nset, nset=s_Set-1, internal, instance=SPINODAL, generate');
fprintf(fileID,'%s\r\n',['      1,  ', num2str(max(Nodes(:, 1))), ',       1']);
fprintf(fileID,'%s\r\n','*Elset, elset=_m_Surf-1_SPOS, internal, instance=Anvil, generate');
fprintf(fileID,'%s\r\n','    1,  2500,     1');
fprintf(fileID,'%s\r\n','*Surface, type=ELEMENT, name=m_Surf-1');
fprintf(fileID,'%s\r\n','_m_Surf-1_SPOS, SPOS');
fprintf(fileID,'%s\r\n','*Elset, elset=_m_Surf-2_SNEG, internal, instance=Loader, generate');
fprintf(fileID,'%s\r\n','    1,  2500,     1');
fprintf(fileID,'%s\r\n','*Surface, type=ELEMENT, name=m_Surf-2');
fprintf(fileID,'%s\r\n','_m_Surf-2_SNEG, SNEG');
fprintf(fileID,'%s\r\n','*Surface, type=NODE, name=s_Set-1_CNS_, internal');
fprintf(fileID,'%s\r\n','s_Set-1, 1.');
fprintf(fileID,'%s\r\n','*Rigid Body, ref node=Anvil.Plate-RefPt_, elset=Anvil.Plate');
fprintf(fileID,'%s\r\n','*Rigid Body, ref node=Loader.Plate-RefPt_, elset=Loader.Plate');
fprintf(fileID,'%s\r\n','*End Assembly');
fprintf(fileID,'%s\r\n','**');

%%%%%%%%%%%%%%% Material Constitutive model & Properties%%%%%%%%%%%%%%%%%%%

fprintf(fileID,'%s\r\n','** MATERIALS');
fprintf(fileID,'%s\r\n','**');
fprintf(fileID,'%s\r\n','*Material, name=Carbon_P');

fprintf(fileID,'%s\r\n','*Density');                                                                            
fprintf(fileID,'%s\r\n',' 1.27e-09,');
fprintf(fileID,'%s\r\n','*Elastic, type=ENGINEERING CONSTANTS');

if (Theta_1 >= 0 && Theta_1 <= 5) && (Theta_2 >= 0 && Theta_2 <= 5) && (Theta_3 >= 0 && Theta_3 <= 45)
    % 60% E

    fprintf(fileID,'%s\r\n','623.5281555,  580.9961058,  580.9961058,    0.3,    0.3,    0.3, 239.818521346, 223.460040692');
    fprintf(fileID,'%s\r\n',' 163.360845738,');
else
    % 20% E

    fprintf(fileID,'%s\r\n','207.8427185,  193.6653686,  193.6653686,    0.3,    0.3,    0.3, 79.93950712, 74.48668025');
    fprintf(fileID,'%s\r\n',' 54.45361525,');
end

fprintf(fileID,'%s\r\n','*Plastic');
fileID_Hill = readtable('PETG_plastic_compression.csv');
A_Hill = table2array(fileID_Hill);

for jik = 1:size(A_Hill(:, 1))
	fprintf(fileID,'%f, %f\r\n', A_Hill(jik,2), A_Hill(jik,1));
end
fprintf(fileID,'%s\r\n','*Potential');

fprintf(fileID,'%s\r\n','0.8713, 1.0399 ,  0.7577,  0.8660,   1.,   1.');

fprintf(fileID,'%s\r\n','**');

fclose(fileID);
