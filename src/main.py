import os
import constants
from importer import Properties
from storage import Storage
from exporter import getDirectoryName, Export
from modules import mapContinuous, mapSinglePhase
from matrix import singlePhaseCharging, singlePhaseDischarging
from matrix import continuousCharging, continuousDischarging
from matrix import storing

if not os.path.exists(constants.LOG_DIRECTORY_PATH):
    os.makedirs(constants.LOG_DIRECTORY_PATH)
exportDir = getDirectoryName(constants.LOG_DIRECTORY_PATH)

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
    props.progressOfSimulations()

    exportContinuous = Export(props, exportDir, f"{props.simulationId}-continuous-model", mapContinuous, 2)
    objectContinuous = Storage(props, mapContinuous, exportContinuous, [], 2)
    objectContinuous.charge(continuousCharging, props.Tfluid, exportContinuous)
    objectContinuous.store(storing, props.Tambient)
    objectContinuous.discharge(continuousDischarging, props.Tambient)
    props.progressOfSimulations()

    props.getNextId()
