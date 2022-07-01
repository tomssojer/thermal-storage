import os
from importer import Properties
from storage import Storage
from exporter import getDirectoryName, Export
from modules import mapContinuous, mapSinglePhase
from matrix import singlePhaseCharging, singlePhaseDischarging
from matrix import continuousCharging, continuousDischarging
from matrix import storing

# Create a log directory and directory in which we will export data
rootDirectory = os.getcwd()
logDirectory = os.path.join(rootDirectory, r'logs')
if not os.path.exists(logDirectory):
    os.makedirs(logDirectory)

exportDir = getDirectoryName(logDirectory)

props = Properties()

while props.simulationId:
    props.getProperties()
    props.discretization()
    props.calculatedCoefficients()

    exportSinglePhase = Export(props, exportDir, f"{props.simulationId}-single-phase-model", mapSinglePhase)
    objectSinglePhase = Storage(props, mapSinglePhase, exportSinglePhase, [])
    objectSinglePhase.charge(singlePhaseCharging, props.Tfluid, exportSinglePhase)
    objectSinglePhase.store(storing, props.Tambient)
    objectSinglePhase.discharge(singlePhaseDischarging, props.Tambient)

    exportContinuous = Export(props, exportDir, f"{props.simulationId}-continuous-model", mapContinuous, 2)
    objectContinuous = Storage(props, mapContinuous, exportContinuous, [], 2)
    objectContinuous.charge(continuousCharging, props.Tfluid, exportContinuous)
    objectContinuous.store(storing, props.Tambient)
    objectContinuous.discharge(continuousDischarging, props.Tambient)

    props.getNextId()
