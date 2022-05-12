import numpy as np
import os
from package import export, initialize, mapping
from arrays import *
from properties import *

rootDir = os.getcwd()
logDir = os.path.join(rootDir, r'logs')
if not os.path.exists(logDir):
    os.makedirs(logDir)

exportable = export.Export(export.getFileName(logDir), length, radius)

class Storage:

    def __init__(self, temperatureList = None):
        self.temperatureList = temperatureList

    def process(self, process, processArray, outerTemperature):

        match process:
            case "Charging":
                self.temperatureList = initialize.temperatures(zNodes, rNodes, ambientTemp)
                coefficients, constants = initialize.prepareCharging(zNodes)
                difference = abs(outerTemperature - self.temperatureList[0][-1])

            case "Storing":
                self.temperatureList = mapping.lengthToRadius(self.temperatureList)
                self.temperatureList = initialize.makeInsulation(self.temperatureList, ambientTemp, rNodesIns)
                coefficients, constants = initialize.prepareStoring(
                    rNodes, rNodesIns)
                difference = abs(outerTemperature - self.temperatureList[-1][0])

            case "Discharging":
                self.temperatureList = mapping.radiusToLength(self.temperatureList)
                coefficients, constants = initialize.prepareCharging(zNodes)
                difference = abs(outerTemperature - self.temperatureList[-1][0])

            case _:
                raise Exception("This is not a valid process, check the syntax.")

        currentTempList = []
        coeffMatrix = processArray(coefficients, constants).coeffMatrix()

        while difference >= finalDifference:
            for array in self.temperatureList:
                constArray = processArray(
                    coefficients, constants).constArray(array)
                temperature = np.linalg.solve(coeffMatrix, constArray)
                temperature = temperature.tolist()
                currentTempList.append(temperature)

            match process:
                case ("Charging"|"Discharging"):
                    keepCount = export.Count.time(dt)
                    if keepCount % exportDtCharging == 0:
                        exportable.allTemperatures(process, currentTempList, keepCount)

                case "Storing":
                    keepCount = export.Count.time(dtStore)
                    if keepCount % exportDtStoring == 0:
                        exportable.allStoringTemperatures(
                            currentTempList, rNodesIns, keepCount)

            self.temperatureList = list(currentTempList)
            currentTempList = []

            match process:
                case "Charging":
                    difference = abs(outerTemperature - self.temperatureList[0][-1])
                case ("Storing"|"Discharging"):
                    difference = abs(outerTemperature - self.temperatureList[-1][0])

        if process == "Storing":
            self.temperatureList = initialize.delInsulation(self.temperatureList, rNodesIns)

        return self.temperatureList

    def currentTemperatures(self):
        return self.temperatureList

a = Storage().process("Charging", ChargingArray, Tfluid)
b = Storage(a).process("Storing", StoringArray, ambientTemp)
c = Storage(b).process("Discharging", DischargingArray, ambientTemp)
