from abaqus import *
from abaqusConstants import *
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
session.mdbData.summary()
o1 = session.openOdb(name='MAIN.odb')
session.viewports['Viewport: 1'].setValues(displayedObject=o1)
odb = session.odbs['MAIN.odb']
xy1 = xyPlot.XYDataFromHistory(odb=odb,
    outputVariableName='Reaction force: RF3 PI: ANVIL Node 2602 in NSET SET-2',
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
xy2 = xyPlot.XYDataFromHistory(odb=odb,
    outputVariableName='Spatial displacement: U3 PI: LOADER Node 2602 in NSET SET-3',
    steps=('Step-1', ), suppressQuery=True, __linkedVpName__='Viewport: 1')
session.writeXYReport(fileName='F_Z.rpt', xyData=(xy2, xy1))