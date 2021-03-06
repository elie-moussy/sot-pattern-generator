import sys
sys.path.append('../../sot-dyninv/python')

from dynamic_graph import plug
from dynamic_graph.sot.core import *
from dynamic_graph.sot.core.math_small_entities import Derivator_of_Matrix
from dynamic_graph.sot.dynamics import *
import dynamic_graph.script_shortcuts
from dynamic_graph.script_shortcuts import optionalparentheses
from dynamic_graph.matlab import matlab
from dynamic_graph.sot.core.meta_task_6d import MetaTask6d,toFlags

from robotSpecific import pkgDataRootDir,modelName,robotDimension,initialConfig,gearRatio,inertiaRotor
robotName = 'hrp10small'

from numpy import *
def totuple( a ):
    al=a.tolist()
    res=[]
    for i in range(a.shape[0]):
        res.append( tuple(al[i]) )
    return tuple(res)

initialConfig.clear()
initialConfig['hrp10small'] = (0,0,0.648697398115,0,0,0)+(0, 0, -0.4538, 0.8727, -0.4189, 0, 0, 0, -0.4538, 0.8727, -0.4189, 0, 0, 0, 0, 0, 0.2618, -0.1745, 0, -0.5236, 0, 0, 0, 0, 0.2618, 0.1745, 0, -0.5236, 0, 0, 0, 0 )

# --- ROBOT SIMU ---------------------------------------------------------------
# --- ROBOT SIMU ---------------------------------------------------------------
# --- ROBOT SIMU ---------------------------------------------------------------

robotDim=robotDimension[robotName]
robot = RobotSimu("robot")
robot.resize(robotDim)

robot.set( initialConfig[robotName] )
dt=5e-3

# --- VIEWER -------------------------------------------------------------------
# --- VIEWER -------------------------------------------------------------------
# --- VIEWER -------------------------------------------------------------------
try:
   import robotviewer

   def stateFullSize(robot):
       if 'dyn' in globals():
           return [float(val) for val in dyn.ffposition.value+robot.state.value[6:]]+10*[0.0]
       else:
           return [float(val) for val in robot.state.value]+10*[0.0]
   RobotSimu.stateFullSize = stateFullSize
   robot.viewer = robotviewer.client('XML-RPC')
   # Check the connection
   robot.viewer.updateElementConfig('hrp',robot.stateFullSize())

   def refreshView( robot ):
       robot.viewer.updateElementConfig('hrp',robot.stateFullSize())
   RobotSimu.refresh = refreshView
   def incrementView( robot,dt ):
       robot.incrementNoView(dt)
       robot.refresh()
   RobotSimu.incrementNoView = RobotSimu.increment
   RobotSimu.increment = incrementView
   def setView( robot,*args ):
       robot.setNoView(*args)
       robot.refresh()
   RobotSimu.setNoView = RobotSimu.set
   RobotSimu.set = setView

   robot.refresh()
except:
    print "No robot viewer, sorry."
    robot.viewer = None


# --- MAIN LOOP ------------------------------------------

qs=[]
def inc():
    robot.increment(dt)
    qs.append(robot.state.value)

from ThreadInterruptibleLoop import *
@loopInThread
def loop():
    inc()
runner=loop()

@optionalparentheses
def go(): runner.play()
@optionalparentheses
def stop(): runner.pause()
@optionalparentheses
def next(): inc() #runner.once()

@optionalparentheses
def n():
    inc()
    qdot()
@optionalparentheses
def n5():
    for loopIdx in range(5): inc()
@optionalparentheses
def n10():
    for loopIdx in range(10): inc()
@optionalparentheses
def q():
    if 'dyn' in globals(): print dyn.ffposition.__repr__()
    print robot.state.__repr__()
@optionalparentheses
def qdot(): print robot.control.__repr__()
@optionalparentheses
def t(): print robot.state.time-1


# --- DYN ----------------------------------------------------------------------
# --- DYN ----------------------------------------------------------------------
# --- DYN ----------------------------------------------------------------------

modelDir = pkgDataRootDir[robotName]
xmlDir = pkgDataRootDir[robotName]
specificitiesPath = xmlDir + '/HRP2SpecificitiesSmall.xml'
jointRankPath = xmlDir + '/HRP2LinkJointRankSmall.xml'

dyn = Dynamic("dyn")
dyn.setFiles(modelDir, modelName[robotName],specificitiesPath,jointRankPath)
dyn.parse()

dyn.inertiaRotor.value = inertiaRotor[robotName]
dyn.gearRatio.value = gearRatio[robotName]

plug(robot.state,dyn.position)
dyn.velocity.value = robotDim*(0.,)
dyn.acceleration.value = robotDim*(0.,)

dyn.ffposition.unplug()
dyn.ffvelocity.unplug()
dyn.ffacceleration.unplug()

robot.control.unplug()

# --- Task 6D ------------------------------------------
# Task right hand
taskRH=MetaTask6d('rh',dyn,'rh','right-wrist')
taskLH=MetaTask6d('lh',dyn,'lh','left-wrist')
taskRF=MetaTask6d('rf',dyn,'rf','right-ankle')
taskLF=MetaTask6d('lf',dyn,'lf','left-ankle')

taskRH.ref = ((0,0,-1,0.22),(0,1,0,-0.37),(1,0,0,.74),(0,0,0,1))

# --- TASK COM ------------------------------------------------------
dyn.setProperty('ComputeCoM','true')

featureCom    = FeatureGeneric('featureCom')
featureComDes = FeatureGeneric('featureComDes')
plug(dyn.com,featureCom.errorIN)
plug(dyn.Jcom,featureCom.jacobianIN)
featureCom.sdes.value = 'featureComDes'
featureComDes.errorIN.value = (0.0478408688115,-0.0620357207995,0.684865189311)

taskCom = Task('taskCom')
taskCom.add('featureCom')

gCom = GainAdaptive('gCom')
plug(taskCom.error,gCom.error)
plug(gCom.gain,taskCom.controlGain)
gCom.set(1,1,1)

# --- shortcuts -------------------------------------------------
comref=featureComDes.errorIN

@optionalparentheses
def iter():         print 'iter = ',robot.state.time
@optionalparentheses
def status():       print runner.isPlay

# --- PG ---------------------------------------------------------
from dynamic_graph.sot.pattern_generator import *

pg = PatternGenerator('pg')
pg.setVrmlDir(modelDir+'/')
pg.setVrml(modelName[robotName])
pg.setXmlSpec(specificitiesPath)
pg.setXmlRank(jointRankPath)
pg.buildModel()

# Standard initialization
pg.parseCmd(":samplingperiod 0.005")
pg.parseCmd(":previewcontroltime 1.6")
pg.parseCmd(":comheight 0.814")
pg.parseCmd(":omega 0.0")
pg.parseCmd(":stepheight 0.05")
pg.parseCmd(":singlesupporttime 0.780")
pg.parseCmd(":doublesupporttime 0.020")
pg.parseCmd(":armparameters 0.5")
pg.parseCmd(":LimitsFeasibility 0.0")
pg.parseCmd(":ZMPShiftParameters 0.015 0.015 0.015 0.015")
pg.parseCmd(":TimeDistributeParameters 2.0 3.5 1.0 3.0")
pg.parseCmd(":UpperBodyMotionParameters 0.0 -0.5 0.0")
pg.parseCmd(":comheight 0.814")
pg.parseCmd(":SetAlgoForZmpTrajectory Morisawa")

plug(dyn.position,pg.position)
plug(dyn.com,pg.com)
pg.motorcontrol.value = robotDim*(0,)
pg.zmppreviouscontroller.value = (0,0,0)

pg.initState()

# --- PG INIT FRAMES ---
geom = Dynamic("geom")
geom.setFiles(modelDir, modelName[robotName],specificitiesPath,jointRankPath)
geom.parse()
geom.createOpPoint('rf','right-ankle')
geom.createOpPoint('lf','left-ankle')
plug(dyn.position,geom.position)
geom.ffposition.value = 6*(0,)
geom.velocity.value = robotDim*(0,)
geom.acceleration.value = robotDim*(0,)

#from dynamic_graph.sot.pattern_generator.meta_selector import SelectorPy
#import dynamic_graph.sot.pattern_generator.meta_selector
# --- Selector of the foot on the ground
SelectorPy=Selector
selecSupportFoot = Selector('selecSupportFoot'
                            ,['matrixHomo','pg_H_sf',pg.rightfootref,pg.leftfootref]
                            ,['matrixHomo','wa_H_sf',geom.rf,geom.lf]
                            )

plug(pg.SupportFoot,selecSupportFoot.selec)
sf_H_wa = Inverse_of_matrixHomo('sf_H_wa')
plug(selecSupportFoot.wa_H_sf,sf_H_wa.sin)
pg_H_wa = Multiply_of_matrixHomo('pg_H_wa')
plug(selecSupportFoot.pg_H_sf,pg_H_wa.sin1)
plug(sf_H_wa.sout,pg_H_wa.sin2)

# --- Compute the ZMP ref in the Waist reference frame.
wa_H_pg = Inverse_of_matrixHomo('wa_H_pg')
plug(pg_H_wa.sout,wa_H_pg.sin)
wa_zmp = Multiply_matrixHomo_vector('wa_zmp')
plug(wa_H_pg.sout,wa_zmp.sin1)
plug(pg.zmpref,wa_zmp.sin2)


# --- PLUGS PG --------------------------------------------------------
# --- Pass the dyn from ref left_foot to ref pg.
ffpos_from_pg = MatrixHomoToPoseRollPitchYaw('ffpos_from_pg')
plug(pg_H_wa.sout,ffpos_from_pg.sin)
plug(ffpos_from_pg.sout,dyn.ffposition)

# --- Connect the ZMPref to OpenHRP in the waist reference frame.
pg.parseCmd(':SetZMPFrame world')
plug(wa_zmp.sout,robot.zmp)

# --- Extract pose and attitude from ffpos
ffattitude_from_pg = Selec_of_vector('ffattitude_from_pg')
plug(ffpos_from_pg.sout,ffattitude_from_pg.sin)
ffattitude_from_pg.selec(3,6)
plug(ffattitude_from_pg.sout,robot.attitudeIN)

# --- REFERENCES ---------------------------------------------------------------
# --- Selector of Com Ref: when pg is stopped, pg.inprocess becomes 0
pgSelec = SelectorPy('pgSelec'
                     ,['vector','scomref',dyn.com,pg.comref])
plug(pg.inprocess,pgSelec.selec)


footSelection = SelectorPy('refFootSelection'
                              ,[ 'matrixHomo','desFoot',pg.rightfootref,pg.leftfootref] # Ref of the flying foot
                              ,[ 'matrixHomo','desRefFoot',pg.leftfootref,pg.rightfootref] # Ref of the support foot
                              ,[ 'matrixHomo','foot',dyn.rf,dyn.lf]  # actual pos of the flying foot
                              ,[ 'matrixHomo','refFoot',dyn.lf,dyn.rf] # actual pos of the support foot
                              ,['matrix','Jfoot',dyn.Jrf,dyn.Jlf] # jacobian of .foot
                              ,['matrix','JrefFoot',dyn.Jlf,dyn.Jrf] # jacobian of .refFoot
                              )
plug(pg.SupportFoot,footSelection.selec)

# ---- TASKS -------------------------------------------------------------------

# ---- WAIST TASK ---
taskWaist=MetaTask6d('waist',dyn,'waist','waist')

# Build the reference waist pos homo-matrix from PG.
waistReferenceVector = Stack_of_vector('waistReferenceVector')
plug(pg.initwaistposref,waistReferenceVector.sin1)
plug(pg.initwaistattref,waistReferenceVector.sin2)
waistReferenceVector.selec1(0,3)
waistReferenceVector.selec2(0,3)
waistReference=PoseRollPitchYawToMatrixHomo('waistReference')
plug(waistReferenceVector.sout,waistReference.sin)
plug(waistReference.sout,taskWaist.featureDes.position)

taskWaist.feature.selec.value = '011100'
taskWaist.task.controlGain.value = 5

# --- TASK 2 FEET ---
featureTwoFeet = FeaturePoint6dRelative('featureTwoFeet')
plug(footSelection.foot,featureTwoFeet.position)
plug(footSelection.refFoot,featureTwoFeet.positionRef)
plug(footSelection.Jfoot,featureTwoFeet.Jq)
plug(footSelection.JrefFoot,featureTwoFeet.JqRef)
featureTwoFeetDes = FeaturePoint6dRelative('featureTwoFeetDes')
#featureTwoFeet.initSdes('featureTwoFeetDes')
featureTwoFeetDes.sdes.value = 'featureTwoFeetDes'
featureTwoFeet.sdes.value = 'featureTwoFeetDes'
plug(footSelection.desFoot,featureTwoFeetDes.position)
plug(footSelection.desRefFoot,featureTwoFeetDes.positionRef)

taskTwoFeet = Task('taskTwoFeet')
taskTwoFeet.add('featureTwoFeet')
taskTwoFeet.controlGain.value = 40

# --- TASK COM ---
featureCom = FeatureGeneric('featureCom')
plug(dyn.com,featureCom.errorIN)
plug(dyn.Jcom,featureCom.jacobianIN)
featureComDes = FeatureGeneric('featureComDes')
featureCom.sdes.value = 'featureComDes'
plug(pgSelec.scomref,featureComDes.errorIN)
featureCom.selec.value = '011'

taskComPD = TaskPD('taskComPD')
taskComPD.add('featureCom')
plug(pg.dcomref,featureComDes.errordotIN)
plug(featureCom.errordot,taskComPD.errorDot)
taskComPD.controlGain.value = 40
taskComPD.setBeta(-1)

# --- CONSTRAINT SUPPORT FOOT
featureSupport = FeatureGeneric('featureSupport')
featureSupport.errorIN.value = 6*(0,)
plug(footSelection.Jfoot,featureSupport.jacobianIN)
constraintSupport = Task('constraintSupport')
constraintSupport.add(featureSupport.name)
constraintSupport.task.value = 6*(0,)

# ---- SOT ---------------------------------------------------------------------
# The solver SOTH of dyninv is used, but normally, the SOT solver should be sufficient
from dynamic_graph.sot.dyninv import SolverKine
sot = SolverKine('sot')
sot.setSize(robotDim)
sot.push(constraintSupport.name)
sot.push(taskTwoFeet.name)
sot.push(taskWaist.task.name)
sot.push(taskComPD.name)

plug(sot.control,robot.control)

# --- HERDT PG AND START -------------------------------------------------------
# Set the algorithm generating the ZMP reference trajectory to Herdt's one.
pg.parseCmd(':SetAlgoForZmpTrajectory Herdt')
pg.parseCmd(':doublesupporttime 0.1')
pg.parseCmd(':singlesupporttime 0.7')
# When velocity reference is at zero, the robot stops all motion after n steps
pg.parseCmd(':numberstepsbeforestop 4')
# Set constraints on XY
pg.parseCmd(':setfeetconstraint XY 0.09 0.06')

# The next command must be runned after a OpenHRP.inc ... ???
# Start the robot with a speed of 0.1 m/0.8 s.
pg.parseCmd(':HerdtOnline 0.1 0.0 0.0')

# You can now modifiy the speed of the robot using set pg.velocitydes [3]( x, y, yaw)
pg.velocitydes.value =(0.1,0.0,0.0)

