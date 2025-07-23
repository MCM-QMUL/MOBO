clear; close all; clc;

%disp('File read start')
%load('temp_directory.mat')
addpath(fullfile(temp_directory)); 
addpath(fullfile('Path/to/Gibbon/','lib')); 
addpath(fullfile('Path/to/Gibbon/lib_ext','geogram'));
Count = 1; 
Cube_Length = 40;

if isfile('acquisition.txt') == 1
    fileID = fopen('acquisition.txt','r');
    A = textscan(fileID,'%f %f %f %f %f','delimiter','\t');
    fclose(fileID);

    fileID = fopen('OBJECTIVE_output.txt','w');
    fprintf(fileID,'%18.6f %18.6f %18.6f %18.6f %18.6f %18s\r\n', 0, 0, 0, 0, 0, 'Null');
    fclose(fileID);
    
    Input = cell2mat(A(1:4));
    clear A;
    Ro      = Input(1, 1);
    res     = 30; %Input(1, 2);
    Theta_1 = Input(1, 2);
    Theta_2 = Input(1, 3);
    Theta_3 = Input(1, 4);
    spinodoid_generator_Tet
    ASSEMBLY_writer_Hill_PETG;
    clear Elements
    clear Nodes
    disp('Simulation start')
    system(['abaqus job=MAIN double cpus=6 mp_mode=' ...		           
        'THREADS memory="90 %" parallel=domain interactive ask_delete=OFF'])         
                                                                          
    if isfile('MAIN.sta') == 1
        CHECKER = fileread('MAIN.sta');
        Check = strfind(CHECKER, 'SUCCESSFULLY');
        if isempty(Check) ~= 1
            Force_reader
            clear Elements
            clear Nodes
            DataSet.Count{Count}        = Count;
            DataSet.Combination{Count}  = [Ro, res, Theta_1, Theta_2, Theta_3];
            DataSet.Mass{Count}         = Mass;
            DataSet.Volume{Count}       = Volume;
            DataSet.Force{Count}        = Force;
            DataSet.Peak_Force{Count}   = P_max;
            DataSet.Min_Force{Count}    = P_min;
            DataSet.EA{Count}           = E_absorption;
            DataSet.CE{Count}           = CE;
            DataSet.combined{Count}     = combined;
            DataSet.Displacement{Count} = [0:20/200:20]';
            DataSet.EA_mode_name{Count} = EA_mode;
            Count = Count + 1;
            
            fileID = fopen('OBJECTIVE_output.txt','w');
            fprintf(fileID,'%18.6f %18.6f %18.6f %18.6f %18.6f %18s\r\n', cell2mat(DataSet.Mass), cell2mat(DataSet.EA), cell2mat(DataSet.Peak_Force), cell2mat(DataSet.CE), cell2mat(DataSet.combined),  cell2mat(DataSet.EA_mode_name));
            fclose(fileID);
            fileID_ss = fopen('force_displacement.txt','w');
            fprintf(fileID_ss,'%8s %15s\n', 'Force',  num2str(Force'));
            fclose(fileID_ss);
            
            clear Mass
            clear Volume
            clear Force
            clear P_max
            clear P_min
            clear E_absorption
            clear CE
            clear combined
            clear EA_mode
            
        else
            clear Elements
            clear Nodes
            DataSet.Count{Count}        = Count;
            DataSet.Combination{Count}  = [Ro, res, Theta_1, Theta_2, Theta_3];
            DataSet.Mass{Count}         = 0;
            DataSet.Volume{Count}       = 0;
            DataSet.Force{Count}        = 0;
            DataSet.Peak_Force{Count}   = 0;
            DataSet.Min_Force{Count}    = 0;
            DataSet.EA{Count}           = 0;
            DataSet.Displacement{Count} = 0;
            DataSet.CE{Count}           = 0;
            DataSet.combined{Count}     = 0;
            DataSet.EA_mode_name{Count} = 'NaN';
            Count = Count + 1;
            fileID = fopen('OBJECTIVE_output.txt','w');
            fprintf(fileID,'%18.6f %18.6f %18.6f %18.6f %18.6f %18s\r\n', cell2mat(DataSet.Mass), cell2mat(DataSet.EA), cell2mat(DataSet.Peak_Force), cell2mat(DataSet.CE), cell2mat(DataSet.combined), cell2mat(DataSet.EA_mode_name));
            fclose(fileID);
        end

            clear CHECKER
            clear Check
    else
        clear Elements
        clear Nodes
        DataSet.Count{Count}        = Count;
        DataSet.Combination{Count}  = [Ro, res, Theta_1, Theta_2, Theta_3];
        DataSet.Mass{Count}         = 0;
        DataSet.Volume{Count}       = 0;
        DataSet.Force{Count}        = 0;
        DataSet.Peak_Force{Count}   = 0;
        DataSet.Min_Force{Count}    = 0;
        DataSet.EA{Count}           = 0;
        DataSet.Displacement{Count} = 0;
        DataSet.CE{Count}           = 0;
        DataSet.combined{Count}     = 0;
        DataSet.EA_mode_name{Count} = 'NaN';
        Count = Count + 1;
        fileID = fopen('OBJECTIVE_output.txt','w');
        fprintf(fileID,'%18.6f %18.6f %18.6f %18.6f %18.6f %18s\r\n', cell2mat(DataSet.Mass), cell2mat(DataSet.EA), cell2mat(DataSet.Peak_Force), cell2mat(DataSet.CE), cell2mat(DataSet.combined), cell2mat(DataSet.EA_mode_name));
        fclose(fileID);

    end
    delete Spinodoid_Tet.inp
    delete ASSEMBLY.inp
    delete MAIN.abq
    delete MAIN.com
    delete MAIN.dat
    delete MAIN.mdl
    delete MAIN.msg
    delete MAIN.odb
    delete MAIN.pac
    delete MAIN.prt
    delete MAIN.res
    delete MAIN.sel
    delete MAIN.sta
    delete MAIN.stt
    delete F_Z.rpt
    delete Mass.txt
    % delete ASSEMBLY_writer_Hill_PETG.m
    % delete Force_Extractor.py
    % delete Force_reader.m
    % delete MAIN.inp
    % delete MASS_VOLUME_Extractor.py
    % delete PETG_plastic_compression.csv
    % delete Plate_01.inp
    % delete SETTING.inp
    % delete spinodoid_generator_Tet.m
    % delete temp_directory.mat

else
    DataSet.Mass{Count}         = 0;
    DataSet.Volume{Count}       = 0;
    DataSet.Force{Count}        = 0;
    DataSet.Peak_Force{Count}   = 0;
    DataSet.Min_Force{Count}    = 0;
    DataSet.EA{Count}           = 0;
    DataSet.Displacement{Count} = 0;
    DataSet.CE{Count}           = 0;
    DataSet.combined{Count}     = 0;
    DataSet.EA_mode_name{Count} = 'NaN';
    fileID = fopen('OBJECTIVE_output.txt','w');
    fprintf(fileID,'%18.6f %18.6f %18.6f %18.6f %18.6f %18s\r\n', cell2mat(DataSet.Mass), cell2mat(DataSet.EA), cell2mat(DataSet.Peak_Force), cell2mat(DataSet.CE), cell2mat(DataSet.combined), cell2mat(DataSet.EA_mode_name));
    fclose(fileID);
    save('DataSet.mat', 'DataSetUpdate')
end

exit;
