from importer import Properties
from modules import mapContinuous, mapSinglePhase
from matrix import singlePhaseCharging, singlePhaseDischarging
from matrix import continuousCharging, continuousDischarging
from matrix import storingHeat
from exporter import Export
from storage import Storage
from modules.makeDirectory import makeDir
import time
import multiprocessing


def prepareSimulations(model, props, exportDirectory):

    props.getProperties()
    props.discretization()
    props.calculatedCoefficients()

    if model == "single-phase":
        exportSinglePhase = Export(props, exportDirectory, f"{props.simulationId}-single-phase-model", mapSinglePhase)
        objectSinglePhase = Storage(props, mapSinglePhase, exportSinglePhase, [])
        objectSinglePhase.charge(singlePhaseCharging, props.Tfluid, exportSinglePhase)
        objectSinglePhase.store(storingHeat, props.Tambient)
        objectSinglePhase.discharge(singlePhaseDischarging, props.Tambient)

    
    elif model == "continuous":
        exportContinuous = Export(props, exportDirectory, f"{props.simulationId}-continuous-model", mapContinuous, 2)
        objectContinuous = Storage(props, mapContinuous, exportContinuous, [], 2)
        objectContinuous.charge(continuousCharging, props.Tfluid, exportContinuous)
        objectContinuous.store(storingHeat, props.Tambient)
        objectContinuous.discharge(continuousDischarging, props.Tambient)

if __name__ == "__main__":

    startTime = time.time()

    exportDirectory = makeDir()
    props = Properties()


    while props.simulationId:

        p1 = multiprocessing.Process(target=prepareSimulations, args=("single-phase", props, exportDirectory))

        p2 = multiprocessing.Process(target=prepareSimulations, args=("continuous", props, exportDirectory))

        p1.start()
        p2.start()
        p1.join()
        props.progressOfSimulations()
        p2.join()
        props.progressOfSimulations()

        props.getNextId()

    endTime = time.time()
    props.simulationTime(startTime, endTime)
