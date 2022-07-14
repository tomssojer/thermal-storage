from importer import Properties
from modules import mapContinuous, mapSinglePhase
from matrix import singlePhaseCharging, singlePhaseDischarging
from matrix import continuousCharging, continuousDischarging
from matrix import storingHeat
from exporter import Export
from storage import Storage
import modules.makeDirectory
import time
import multiprocessing

def prepareSimulations(model, props, directoryPath):

    props.getProperties()
    props.discretization()
    props.calculatedCoefficients()

    if model == "single-phase":
        exportSinglePhase = Export(props, directoryPath, "single-phase", mapSinglePhase)
        objectSinglePhase = Storage(props, mapSinglePhase, exportSinglePhase, [])
        objectSinglePhase.charge(singlePhaseCharging, props.Tfluid, exportSinglePhase)
        objectSinglePhase.store(storingHeat, props.Tambient, exportSinglePhase)
        objectSinglePhase.discharge(singlePhaseDischarging, props.Tambient)

    
    elif model == "continuous-solid":
        exportContinuous = Export(props, directoryPath, "continuous-solid-phase", mapContinuous, 2)
        objectContinuous = Storage(props, mapContinuous, exportContinuous, [], 2)
        objectContinuous.charge(continuousCharging, props.Tfluid, exportContinuous)
        objectContinuous.store(storingHeat, props.Tambient, exportContinuous)
        objectContinuous.discharge(continuousDischarging, props.Tambient)

if __name__ == "__main__":

    startTime = time.time()

    directoryPath = modules.makeDirectory.makeDir()
    copyProperties = modules.makeDirectory.copyPropertiesFile(directoryPath)
    props = Properties()

    while props.simulationId:

        idDirectory = props.makeDirectoryForId(directoryPath)

        p1 = multiprocessing.Process(target=prepareSimulations, args=("single-phase", props, idDirectory))
        p2 = multiprocessing.Process(target=prepareSimulations, args=("continuous-solid", props, idDirectory))

        p1.start()
        p2.start()
        p1.join()
        props.progressOfSimulations()
        p2.join()
        props.progressOfSimulations()

        props.getNextId()

    endTime = time.time()
    props.simulationTime(startTime, endTime)
