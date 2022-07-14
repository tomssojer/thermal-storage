import numpy as np
from modules import initialize as init
from importer import *

class Storage:

    counter = 0

    def __init__(self, propsObj, mappingFile, exportFile, temperatureList, sizeOfMatrixCoeff=1):
        self.propsObj = propsObj
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

    def calculateTemperatures(self, process):

        newList = []

        for subList in self.temperatureList:
            coeffMatrix = process.GetArrays(subList, self.sizeOfMatrixCoeff).coeffMatrix(self.propsObj)
            constArray = process.GetArrays(subList, self.sizeOfMatrixCoeff).constArray(self.propsObj, subList)
            temperature = np.linalg.solve(coeffMatrix, constArray)
            temperature = temperature.tolist()
            newList.append(temperature)
        
        return newList

    def charge(self, arrayFile, outerTemperature, exportObj):
        self.temperatureList = init.temperatures(self.propsObj.zNodes, self.propsObj.rNodes, self.propsObj.Tambient, self.sizeOfMatrixCoeff)
        exportObj.initialTemperatures(self.temperatureList)
        exportObj.openFileForHeatStored("Charging process")

        difference = abs(outerTemperature - self.temperatureList[0][-1])
        initialCount = self.endCount()

        while difference >= self.propsObj.finalDifference:
            self.temperatureList = self.calculateTemperatures(arrayFile)
            countTime = self.time(self.propsObj.dt)

            if (countTime - initialCount) % self.propsObj.exportDtCharging == 0:
                self.exportFile.allTemperatures("Charging process", self.temperatureList, countTime)
                self.exportFile.heatStored(self.temperatureList, self.propsObj.Tambient, countTime)

            difference = abs(outerTemperature - self.temperatureList[0][-1])


    def store(self, arrayFile, outerTemperature, exportObj):
        self.temperatureList = self.mappingFile.lengthToRadius(self.temperatureList)
        self.temperatureList = init.makeInsulation(self.temperatureList, self.propsObj.Tambient, self.propsObj.rNodesIns)
        exportObj.openFileForHeatStored("Storing process")

        difference = abs(outerTemperature - self.temperatureList[-1][0])
        initialCount = self.endCount()

        # Zanka, ki se izvaja dokler ni razlika med točko v hranilniku in zunanjo točko manjša od 200°C
        while difference >= self.propsObj.finalDifference:
            self.temperatureList = self.calculateTemperatures(arrayFile)
            countTime = self.time(self.propsObj.dtStore)

            if (countTime - initialCount) % self.propsObj.exportDtStoring == 0:
                self.exportFile.allStoringTemperatures(self.temperatureList, self.propsObj.rNodesIns, countTime)
                self.exportFile.heatStoredStoring(self.temperatureList, self.propsObj.Tambient, self.propsObj.rNodesIns, countTime)

            difference = abs(outerTemperature - self.temperatureList[-1][0])
        
        self.temperatureList = init.delInsulation(self.temperatureList, self.propsObj.rNodesIns)
        self.temperatureList = self.mappingFile.radiusToLength(self.temperatureList)


    def discharge(self, arrayFile, outerTemperature):
        difference = abs(outerTemperature - self.temperatureList[-1][0])
        initialCount = self.endCount()

        while difference >= 50:
            self.temperatureList = self.calculateTemperatures(arrayFile)
            countTime = self.time(self.propsObj.dt)

            if (countTime - initialCount) % self.propsObj.exportDtCharging == 0:
                self.exportFile.allTemperatures("Discharging process", self.temperatureList, countTime)

            difference = abs(outerTemperature - self.temperatureList[-1][0])
