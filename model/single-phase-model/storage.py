##### Main python file for simulations #####

import numpy as np
import os
from package import export, initialize, mapping
from arrays import ChargingArray, StoringArray, DischargingArray
from properties import *
from pandas import DataFrame
import time
from multiprocessing import Pool

rootDir = os.getcwd()
logDir = os.path.join(rootDir, r'logs')
if not os.path.exists(logDir):
    os.makedirs(logDir)

exportable = export.Export(export.getFileName(logDir))

class Storage:

    # Methods look like this:
    # 1. Initialize temperatures by using starting temperatures or mapping
    #    from the previous process
    # 2. Prepare an empty list for temperatures to put in
    # 3. Prepare arrays for solving
    # 4. Solve arrays one by one and append results to the empty array
    # 5. Export temperatures to a txt file
    # 6. Return the last calculated array of temperatures

    def __init__(self):
        pass

    def charge(self):

        ##### Initialize temperatures #####
        previousTempList = initialize.temperatures(zNodes, rNodes, ambientTemp)
        currentTempList = []  

        exportable.initialTemperatures(previousTempList)   

        ##### Call functions #####
        coefficients, constants = initialize.prepareCharging(zNodes)
        coeffMatrix = ChargingArray(coefficients, constants).coeffMatrix()

        # Calculate temperatures for every time step
        start = time.time()
        for timeStep in range(10):
            def calcList():
                for array in previousTempList:
                    constArray = ChargingArray(coefficients, constants).constArray(array)
                    temperature = np.linalg.solve(coeffMatrix, constArray)
                    temperature = temperature.tolist()
                    currentTempList.append(temperature)

                # Export the array of arrays
                keepCount = export.Count.time(dt)
                exportable.allTemperatures("Charging", currentTempList, keepCount)
                # Assign new temperatures as previous, empty out the current temperature array
                previousTempList = list(currentTempList)
                currentTempList = []
            
            
        end = time.time()
        print(end-start)

        return previousTempList



    def store(self, tempFromCharging):

        ##### Mapping temperatures #####
        previousTempList = mapping.lengthToRadius(tempFromCharging)
        previousTempList = initialize.makeInsulation(previousTempList, ambientTemp, rNodesIns)
        currentTempList = []

        ##### Calling arrays from other classes #####
        coefficients, constants = initialize.prepareStoring(rNodes, rNodesIns)
        coeffMatrix = StoringArray(coefficients, constants).coeffMatrix()

        ##### Solve the equations #####
        for timeStep in range(10):
            for array in previousTempList:
                constArray = StoringArray(coefficients, constants).constArray(array)
                temperature = np.linalg.solve(coeffMatrix, constArray)
                temperature = temperature.tolist()
                currentTempList.append(temperature)

            ##### Export every time step #####
            keepCount = export.Count.time(dt)
            exportable.allStoringTemperatures(currentTempList, rNodesIns, keepCount)
            ##### Reassign temperatures #####
            previousTempList = list(currentTempList)
            currentTempList = []

        previousTempList = initialize.delInsulation(previousTempList, rNodesIns)
        
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
            keepCount = export.Count.time(dt)
            export.allTemperatures("Discharging", currentTempList, keepCount)

            # Assign new temperatures as previous, empty out the current temperature array
            previousTempList = list(currentTempList)
            currentTempList = []

        return previousTempList


# During discharging, we should use the same matrix/ similar matrix to make it easier. 
# The only thing that should change is the direction in which the HTF flows. 

# storage = Storage(export.getFileName(logDir), export.Count().time())
# z = Storage().charge()
# r = Storage().store(z)
# zz = Storage().discharge(r)

# def function(x):
#     return x*x

# start = time.time()
# if __name__ == '__main__':
#     with Pool as p:
#         p.map(function, [1, 2, 3])

# end = time.time()

# print(end-start)


# def func(num):
#     return [num, num**2, num**3]


# start = time.time()
# list = []
# for i in range(800):
#     list.append(func(i))

# print(list)
# end = time.time()
# print(end-start)



# start = time.time()
# if __name__ == '__main__':
    
#     p = Pool(processes=4)



#     result = p.map(func, range(800))
#     print(result)

# end = time.time()
# print(end-start)
