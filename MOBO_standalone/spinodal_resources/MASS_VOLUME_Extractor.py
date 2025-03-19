from abaqus import *
from abaqusConstants import *
import numpy as np
import __main__
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
mdb.ModelFromInputFile(name='MAIN', inputFileName='MAIN.inp')
a = mdb.models['MAIN'].rootAssembly
session.viewports['Viewport: 1'].setValues(displayedObject=a)
MASS = mdb.models['MAIN'].parts['SPINODAL'].getMassProperties()['mass']
VOLUME = mdb.models['MAIN'].parts['SPINODAL'].getMassProperties()['volume']
with open('Mass.txt','w') as f:
	f.write(str(MASS)+"\n")
	f.write(str(VOLUME)+"\n")