import os
from importer import length, radius, insulation, Tfluid, ambientTemp
from storage import Storage
import singlePhaseModel.arrays as arr
import exporter

rootDirectory = os.getcwd()
logDirectory = os.path.join(rootDirectory, r'logs')
if not os.path.exists(logDirectory):
    os.makedirs(logDirectory)

exportDirectory = exporter.getDirectoryName(logDirectory)
exportData = exporter.Export(exportDirectory, length, radius, insulation)
print(exportDirectory)

# storage = Storage([], exportData)
# charging = storage.process("Charging", arr.ChargingArray, Tfluid)
# storing = storage.process("Storing", arr.StoringArray, ambientTemp)
# discharging = storage.process("Discharging", arr.DischargingArray, ambientTemp)
