import numpy as np
import os
from package import export, initialize, mapping
from arrays import *
from properties import *

rootDir = os.getcwd()
logDir = os.path.join(rootDir, r'logs')
if not os.path.exists(logDir):
    os.makedirs(logDir)

exportable = export.Export(export.getFileName(logDir), length, radius, insulation)

class Storage:

    def __init__(self, temperatureList):
        self.temperatureList = temperatureList

    def outputCurrentTemperatures(self):
        return self.temperatureList

    # Tukaj je definicija procesa, lahko je polnjenje, hranjenje ali praznjenje
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
        initialCount = export.Count.endCount()

        # Zanka, ki se izvaja dokler ni razlika med točko v hranilniku in zunanjo točko manjša od 200°C
        while difference >= finalDifference:
            for array in self.temperatureList:
                constArray = processArray(
                    coefficients, constants).constArray(array)
                temperature = np.linalg.solve(coeffMatrix, constArray)
                temperature = temperature.tolist()
                currentTempList.append(temperature)

            match process:
                case ("Discharging"):
                    keepCount = export.Count.time(dt)
                    # Dont export every time, but when determined by exportDt
                    if (keepCount - initialCount) % exportDtCharging == 0:
                        exportable.allTemperatures(process, currentTempList, keepCount)

                case "Charging":
                    keepCount = export.Count.time(dt)
                    # Dont export every time, but when determined by exportDt
                    if (keepCount - initialCount) % exportDtCharging == 0:
                        exportable.allTemperatures(
                            process, currentTempList, keepCount)
                        exportable.heatStored(
                    currentTempList, ambientTemp, cp, keepCount)

                case "Storing":
                    keepCount = export.Count.time(dtStore)
                    if (keepCount - initialCount) % exportDtStoring == 0:
                        exportable.allStoringTemperatures(
                            currentTempList, rNodesIns, keepCount)
                        exportable.heatStoredStoring(currentTempList, ambientTemp, rNodesIns, cp, keepCount)

            self.temperatureList = list(currentTempList)
            currentTempList = []

            # Če je razlika manjša, se bo zanka končala
            match process:
                case "Charging":
                    difference = abs(outerTemperature - self.temperatureList[0][-1])
                case ("Storing"|"Discharging"):
                    difference = abs(outerTemperature - self.temperatureList[-1][0])

        if process == "Storing":
            self.temperatureList = initialize.delInsulation(self.temperatureList, rNodesIns)
        print(".")

        return self.temperatureList


# Tukaj kličemo metode znotraj Storage razreda
storage = Storage([])
charging = storage.process("Charging", ChargingArray, Tfluid)
storing = storage.process("Storing", StoringArray, ambientTemp)
discharging = storage.process("Discharging", DischargingArray, ambientTemp)
