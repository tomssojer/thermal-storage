import os
from importer import length, radius, insulation, Tfluid, Tambient
from storage import Storage
import singlePhaseModel.arrays, continuousModel.arrays
import singlePhaseModel.mapping, continuousModel.mapping
from exporter import getDirectoryName, Export

rootDirectory = os.getcwd()
logDirectory = os.path.join(rootDirectory, r'logs')
if not os.path.exists(logDirectory):
    os.makedirs(logDirectory)

exportDir = getDirectoryName(logDirectory)

# Kličemo storage class - objekt storageSinglePhase (povemo kateri arrayi so uporabljeni, katero datoteko izvozimo)
exportSinglePhase = Export(exportDir, "single-phase-model", singlePhaseModel.mapping, length, radius, insulation)
objectSinglePhase = Storage(singlePhaseModel.arrays, singlePhaseModel.mapping, exportSinglePhase, [])
objectSinglePhase.charge(Tfluid, exportSinglePhase)
objectSinglePhase.store(Tambient)
objectSinglePhase.discharge(Tambient)

exportContinuous = Export(exportDir, "continuous-model", continuousModel.mapping, length, radius, insulation, 2)
objectContinuous = Storage(continuousModel.arrays, continuousModel.mapping, exportContinuous, [], 2)
objectContinuous.charge(Tfluid, exportContinuous)
objectContinuous.store(Tambient)
objectContinuous.discharge(Tambient)
