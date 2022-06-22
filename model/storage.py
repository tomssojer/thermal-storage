import numpy as np
import initialize as init
from importer import *
from pandas import DataFrame

class Storage:

    counter = 0

    def __init__(self, arrayFile, mappingFile, exportFile, temperatureList, sizeOfMatrixCoeff=1):
        self.arrayFile = arrayFile
        self.mappingFile = mappingFile
        self.exportFile = exportFile
        self.temperatureList = temperatureList
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    def returnTemperatures(self):
        return self.temperatureList

    def time(self, deltaTime):
        self.counter += deltaTime
        self.counter = round(self.counter, 3)
        return self.counter

    def endCount(self):
        return self.counter

    def calculateTemperatures(self, process, newList, coeffMatrix):
        for array in self.temperatureList:
            constArray = process(self.sizeOfMatrixCoeff).constArray(array)
            temperature = np.linalg.solve(coeffMatrix, constArray)
            temperature = temperature.tolist()
            newList.append(temperature)

    def charge(self, outerTemperature, exportObj):
        self.temperatureList = init.temperatures(zNodes, rNodes, Tambient, self.sizeOfMatrixCoeff)
        exportObj.initialTemperatures(self.temperatureList)
        difference = abs(outerTemperature - self.temperatureList[0][-1])

        coeffMatrix = self.arrayFile.ChargingArray(self.sizeOfMatrixCoeff).coeffMatrix()
        initialCount = self.endCount()
        currentTempList = []

        while difference >= finalDifference:
            self.calculateTemperatures(self.arrayFile.ChargingArray, currentTempList, coeffMatrix)
            keepCount = self.time(dt)

            if (keepCount - initialCount) % exportDtCharging == 0:
                self.exportFile.allTemperatures("Charging", currentTempList, keepCount)
                # self.exportFile.heatStored(currentTempList, Tambient, cp, keepCount)

            self.temperatureList = list(currentTempList)
            currentTempList = []
            difference = abs(outerTemperature - self.temperatureList[0][-1])

        return self.temperatureList


    def store(self, outerTemperature):
        self.temperatureList = self.mappingFile.lengthToRadius(self.temperatureList)
        self.temperatureList = init.makeInsulation(self.temperatureList, Tambient, rNodesIns)
        difference = abs(outerTemperature - self.temperatureList[-1][0])

        coeffMatrix = self.arrayFile.StoringArray(self.sizeOfMatrixCoeff).coeffMatrix()
        initialCount = self.endCount()
        currentTempList = []

        # Zanka, ki se izvaja dokler ni razlika med točko v hranilniku in zunanjo točko manjša od 200°C
        while difference >= finalDifference:
            self.calculateTemperatures(self.arrayFile.StoringArray, currentTempList, coeffMatrix)
            keepCount = self.time(dtStore)

            if (keepCount - initialCount) % exportDtStoring == 0:
                self.exportFile.allStoringTemperatures(currentTempList, rNodesIns, keepCount)
                # self.exportFile.heatStoredStoring(currentTempList, Tambient, rNodesIns, cp, keepCount)

            self.temperatureList = list(currentTempList)
            currentTempList = []
            difference = abs(outerTemperature - self.temperatureList[-1][0])
        
        self.temperatureList = init.delInsulation(self.temperatureList, rNodesIns)
        self.temperatureList = self.mappingFile.radiusToLength(self.temperatureList)
        return self.temperatureList


    def discharge(self, outerTemperature):
        difference = abs(outerTemperature - self.temperatureList[-1][0])
        coeffMatrix = self.arrayFile.DischargingArray(self.sizeOfMatrixCoeff).coeffMatrix()
        currentTempList = []
        initialCount = self.endCount()

        while difference >= 50:
            self.calculateTemperatures(self.arrayFile.DischargingArray, currentTempList, coeffMatrix)
            keepCount = self.time(dt)

            if (keepCount - initialCount) % exportDtCharging == 0:
                self.exportFile.allTemperatures("Discharging", currentTempList, keepCount)

            self.temperatureList = list(currentTempList)
            currentTempList = []
            difference = abs(outerTemperature - self.temperatureList[-1][0])

        return self.temperatureList
