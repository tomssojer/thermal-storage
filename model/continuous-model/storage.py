##### Main python file for simulations #####

import numpy as np
import os
from package import export, initialize, mapping
from arrays import ChargingArray, StoringArray, DischargingArray
from properties import *
from pandas import DataFrame

rootDir = os.getcwd()
logDir = os.path.join(rootDir, r'logs')
if not os.path.exists(logDir):
    os.makedirs(logDir)

getFileName = export.getFileName(logDir)
export = export.Export(getFileName, export.Count().time(dt))

class Storage:

    # Methods look like this:
    # 1. Initialize temperatures by using starting temperatures or mapping
    #    from the previous process
    # 2. Prepare an empty list for temperatures to put in
    # 3. Prepare arrays for solving
    # 4. Solve arrays one by one and append results to the empty array
    # 5. Export temperatures to a txt file
    # 6. Return the last calculated array of temperatures

    # getFileName = export.getFileName(logDir)
    # keepCount = export.Count().time()
    # export = export.Export(getFileName, keepCount)

    def __init__(self):
        pass

    def charge(self):

        ##### Initialize temperatures #####
        previousTempList = initialize.temperatures(zNodes, rNodes, ambientTemp)
        currentTempList = []

        ##### Call functions #####
        coefficients, constants = initialize.prepareCharging(zNodes)
        coeffMatrix = ChargingArray(coefficients, constants).coeffMatrix()

        

        # currentDifference = abs(Tfluid - ambientTemp)
        # while finalDifference <= currentDifference:

        #     for array in previousTempList:
        #         constArray = ChargingArray(
        #             coefficients, constants).constArray(array)
        #         temperature = np.linalg.solve(coeffMatrix, constArray)
        #         temperature = temperature.tolist()
        #         temperature.insert(0, Tfluid)
        #         temperature.insert(int(len(temperature)/2+1), Tfluid)
        #         currentTempList.append(temperature)

        #     Storage.export.allTemperatures("Charging", currentTempList)

        #     previousTempList = list(currentTempList)
        #     currentTempList = []

        #     currentDifference = abs(Tfluid - temperature[-1])

        return previousTempList

    def store(self, tempFromCharging):

        ##### Mapping temperatures #####
        previousTempList = mapping.lengthToRadius(tempFromCharging)
        previousTempList = initialize.makeInsulation(
            previousTempList, ambientTemp, rNodesIns)
        currentTempList = []

        ##### Calling arrays from other classes #####
        coefficients, constants = initialize.prepareStoring(rNodes, rNodesIns)
        coeffMatrix = StoringArray(coefficients, constants).coeffMatrix()

        ##### Solve the equations #####
        for timeStep in range(10):
            for array in previousTempList:
                constArray = StoringArray(
                    coefficients, constants).constArray(array)
                temperature = np.linalg.solve(coeffMatrix, constArray)
                temperature = temperature.tolist()
                temperature.insert(0, 293)
                temperature.insert(int(len(temperature)/2+1), 293)
                currentTempList.append(temperature)

            ##### Export every time step #####
            Storage.export.allStoringTemperatures(currentTempList, timeStep, rNodesIns)
            ##### Reassign temperatures #####
            previousTempList = list(currentTempList)
            currentTempList = []

        previousTempList = initialize.delInsulation(
            previousTempList, rNodesIns)

        ##### Returns the last list returned from calculations #####
        return previousTempList

    def discharge(self, tempFromStoring):

        # Mapping temperatures
        previousTempList = mapping.radiusToLength(tempFromStoring)
        currentTempList = []

        ##### Call functions #####
        coefficients, constants = initialize.prepareCharging(zNodes)
        coeffMatrix = DischargingArray(coefficients, constants).coeffMatrix()

        # Calculate temperatures for every time step
        for timeStep in range(10):
            for array in previousTempList:
                constArray = DischargingArray(
                    coefficients, constants).constArray(array)
                temperature = np.linalg.solve(coeffMatrix, constArray)
                temperature = temperature.tolist()
                currentTempList.append(temperature)

            # Export the array of arrays
            Storage.export.allTemperatures("Discharging", currentTempList, timeStep)

            # Assign new temperatures as previous, empty out the current temperature array
            previousTempList = list(currentTempList)
            currentTempList = []

        return previousTempList


z = Storage().charge()
# r = Storage().store(z)
# zz = Storage().discharge(r)
