import numpy as np
import initialize as init
import singlePhaseModel.mapping as mapp
from importer import *
from exporter import Count

class Storage:

    def __init__(self, temperatureList, exportFile):
        self.temperatureList = temperatureList
        self.exportFile = exportFile

    def outputCurrentTemperatures(self):
        return self.temperatureList

    # Tukaj je definicija procesa, lahko je polnjenje, hranjenje ali praznjenje
    def process(self, process, processArray, outerTemperature):

        match process:
            case "Charging":
                self.temperatureList = init.temperatures(zNodes, rNodes, ambientTemp)
                coefficients, constants = init.prepareCharging(zNodes)
                difference = abs(outerTemperature - self.temperatureList[0][-1])

            case "Storing":
                self.temperatureList = mapp.lengthToRadius(self.temperatureList)
                self.temperatureList = init.makeInsulation(self.temperatureList, ambientTemp, rNodesIns)
                coefficients, constants = init.prepareStoring(rNodes, rNodesIns)
                difference = abs(outerTemperature - self.temperatureList[-1][0])

            case "Discharging":
                self.temperatureList = mapp.radiusToLength(self.temperatureList)
                coefficients, constants = init.prepareCharging(zNodes)
                difference = abs(outerTemperature - self.temperatureList[-1][0])

            case _:
                raise Exception("This is not a valid process, check the syntax.")

        currentTempList = []
        coeffMatrix = processArray(coefficients, constants).coeffMatrix()
        initialCount = Count.endCount()

        # Zanka, ki se izvaja dokler ni razlika med točko v hranilniku in zunanjo točko manjša od 200°C
        while difference >= finalDifference:
            for array in self.temperatureList:
                constArray = processArray(coefficients, constants).constArray(array)
                temperature = np.linalg.solve(coeffMatrix, constArray)
                temperature = temperature.tolist()
                currentTempList.append(temperature)

            match process:
                case ("Discharging"):
                    keepCount = Count.time(dt)
                    # Dont export every time, but when determined by exportDt
                    if (keepCount - initialCount) % exportDtCharging == 0:
                        self.exportFile.allTemperatures(process, currentTempList, keepCount)

                case "Charging":
                    keepCount = Count.time(dt)
                    # Dont export every time, but when determined by exportDt
                    if (keepCount - initialCount) % exportDtCharging == 0:
                        self.exportFile.allTemperatures(process, currentTempList, keepCount)
                        self.exportFile.heatStored(currentTempList, ambientTemp, cp, keepCount)

                case "Storing":
                    keepCount = Count.time(dtStore)
                    if (keepCount - initialCount) % exportDtStoring == 0:
                        self.exportFile.allStoringTemperatures(currentTempList, rNodesIns, keepCount)
                        self.exportFile.heatStoredStoring(currentTempList, ambientTemp, rNodesIns, cp, keepCount)

            self.temperatureList = list(currentTempList)
            currentTempList = []

            # Če je razlika manjša, se bo zanka končala
            match process:
                case "Charging":
                    difference = abs(outerTemperature - self.temperatureList[0][-1])
                case ("Storing" | "Discharging"):
                    difference = abs(outerTemperature - self.temperatureList[-1][0])

        if process == "Storing":
            self.temperatureList = init.delInsulation(self.temperatureList, rNodesIns)
        print(".")

        return self.temperatureList
