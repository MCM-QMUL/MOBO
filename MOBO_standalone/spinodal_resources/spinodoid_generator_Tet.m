% close all; clear all; clc

rng(123);
cMap       = gjet(5); 
patchColor = cMap(1,:);
markerSize = 25; 
cMap       = parula(250);
faceAlpha1 = 1;
faceAlpha2 = 0.5;
edgeColor1 = 'none';
edgeColor2 = 'none';
fontSize   = 15;
inputStruct.isocap     = true;                                              % option to cap the isosurface
inputStruct.domainSize = 1;                                                 % domain size
inputStruct.resolution = 100;                                               % resolution for sampling GRF
inputStruct.waveNumber = 15*pi;                                             % GRF wave number
inputStruct.numWaves   = 1000;                                              % number of waves in GRF
%%%The Four Main Controlling Parameters%%%%%%%%%%%%%
inputStruct.relativeDensity = Ro;                                           
inputStruct.thetas = [Theta_1, Theta_2, Theta_3];                           % 
% Create spinodoid
[F,V,C] = spinodoid(inputStruct);
% Using grouping to keep only largest group
groupOptStruct.outputType = 'label';
[G,~,groupSize]           = tesgroup(F,groupOptStruct);                     %Group connected faces
[~,indKeep]               = max(groupSize);                                 %Index of largest group
%Keep only largest group
F     = F(G==indKeep,:);                                                    %Trim faces
C     = C(G==indKeep,:);                                                    %Trim color data
[F,V] = patchCleanUnused(F,V);                                              %Remove unused nodes
%% Remove non-manifold faces
D = patchConnectivity(F,V,'ff');
logicManifold = sum(D.face.face>0,2)==3;
F     = F(logicManifold,:);
C     = C(logicManifold,:);
[F,V] = patchCleanUnused(F,V);
% Smoothen mesh using ggremesh
optionStruct.pointSpacing = 1/res;
[F,V] = ggremesh(F,V,optionStruct);
C     = zeros(size(F,1),1);
%%%%%%%%%%%%%%%%%%%%%%%Mesh using Tetgen%%%%%%%%%%%%%%%%%%%%%%%%
V_regions          = getInnerPoint(F,V);
V_holes            =[];                                                     %Define hole points
[regionTetVolumes] = tetVolMeanEst(F,V);                                    %Volume estimate for regular tets
stringOpt          = '-pq1.2AaY';                                           %Options for tetgen
%% export STL
% fileName_STL = fullfile(savePath,['Spinodoid', '_', num2str(Ro, '%.2f'), '_', num2str(res, '%.2f'), '_', num2str(Theta_1, '%.2f'), '_', num2str(Theta_2, '%.2f'), '_', num2str(Theta_3, '%.2f'), '.stl']);
% stlwrite(fileName_STL ,F,V)

%%
% Mesh using TetGen
%Create tetgen input structure
inputStruct.stringOpt=stringOpt;                                            %Tetgen options
inputStruct.Faces=F;                                                        %Boundary faces
inputStruct.Nodes=V;                                                        %Nodes of boundary
inputStruct.faceBoundaryMarker=C; 
inputStruct.regionPoints=V_regions;                                         %Interior points for regions
inputStruct.holePoints=V_holes;                                             %Interior points for holes
inputStruct.regionA=regionTetVolumes;                                       %Desired tetrahedral volume for each region
% Mesh model using tetrahedral elements using tetGen 
[meshOutput]=runTetGen(inputStruct);                                        %Run tetGen 
%% 
% Access mesh output structure
E=meshOutput.elements;                                                      %The elements
V=Cube_Length*meshOutput.nodes;                                             %The vertices or nodes
CE=meshOutput.elementMaterialID;                                            %Element material or region id
Fb=meshOutput.facesBoundary;                                                %The boundary faces
Cb=meshOutput.boundaryMarker;                                               %The boundary markers
% Node
nodeIds=(1:1:size(V,1))';
Nodes = [nodeIds, V];
% Element
elementIds=(1:1:size(E,1))';
Elements = [elementIds,E];
%%%%%%%%%%%%%%%%%%%%%%%% GENERATE ABAQUS IMPUT FILE %%%%%%%%%%%%%%%%%%%%%%%
fileID = fopen('Spinodoid_Tet.inp','w');
fprintf(fileID,'%s\r\n','*Part, name=SPINODAL');
fprintf(fileID,'%s\r\n','*Node');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Node Generating %%%%%%%%%%%%%%%%%%%%%%%%%%%%
for i = 1 : size(Nodes, 1)
    fprintf(fileID,'%7d%s %12.6f%s %12.6f%s %12.6f\r\n', Nodes(i, 1), ',', Nodes(i, 2), ',',Nodes(i, 3), ',', Nodes(i, 4));
end
%%%%%%%%%%%%%%%%%%%%%%%%%%% Element Generating %%%%%%%%%%%%%%%%%%%%%%%%%%%%
fprintf(fileID,'%s\r\n','*Element, type=C3D4');
for i =1 : size(Elements, 1)
    fprintf(fileID,'%7d%s %7d%s %7d%s %7d%s %7d\r\n', Elements(i, 1), ',', Elements(i, 2), ',',Elements(i, 3), ',',Elements(i, 4), ',',Elements(i, 5));
end
fprintf(fileID,'%s\r\n', '*Elset, elset=Set-1, generate');
fprintf(fileID,'%s\r\n', ['     1,', num2str(max(Elements(:, 1))), ',      1']);
fprintf(fileID,'%s\r\n', '*Orientation, name=Ori-1');
fprintf(fileID,'%s\r\n', '          1.,           0.,           0.,           0.,           1.,           0.');
fprintf(fileID,'%s\r\n', '3, 0.');
fprintf(fileID,'%s\r\n', '** Section: Section-1');
fprintf(fileID,'%s\r\n', '*Solid Section, elset=Set-1, orientation=Ori-1, controls=EC-1, material=Carbon_P');
fprintf(fileID,'%s\r\n', ',');
fprintf(fileID,'%s\r\n', '*End Part');
fprintf(fileID,'%s\r\n', '**');
fclose(fileID);
%% Calculating the equivalent length of the elements. This will be used for
% normalizing the failure parameter for FEA simulations.
L_elements = ones(size(Elements, 1), 1);
V_elements = ones(size(Elements, 1), 1);
A_elements = ones(size(Elements, 1), 1);
for i = 1 : size(Elements, 1)
    V_elements(i, 1) = dot(cross([Nodes(Elements(i, 3), 2:4) - Nodes(Elements(i, 2), 2:4)],  ...
                                 [Nodes(Elements(i, 4), 2:4) - Nodes(Elements(i, 2), 2:4)]), ...
                                 [Nodes(Elements(i, 5), 2:4) - Nodes(Elements(i, 2), 2:4)])/6;
    A_elements(i, 1) = norm(cross([Nodes(Elements(i, 3), 2:4) - Nodes(Elements(i, 2), 2:4)],  ...
                                  [Nodes(Elements(i, 4), 2:4) - Nodes(Elements(i, 2), 2:4)]))/2;
    L_elements(i, 1) =V_elements(i, 1)/A_elements(i, 1);
end
L_equivalent = mean(L_elements);