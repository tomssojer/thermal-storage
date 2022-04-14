import numpy as np
import os
from package import export, initialize, mapping
from arrays import *
from properties import *
from pandas import DataFrame

rootDir = os.getcwd()
logDir = os.path.join(rootDir, r'logs')
if not os.path.exists(logDir):
    os.makedirs(logDir)

class Storage:

    # Methods follow this pattern:
    # 1. Initialize temperatures by using starting temperatures or mapping
    #    from the previous process
    # 2. Prepare an empty list for temperatures to put in
    # 3. Prepare arrays for solving
    # 4. Solve arrays one by one and append results to the empty array
    # 5. Export temperatures to a txt file
    # 6. Return the last calculated array of temperatures

    def __init__(self):
        pass

##########################################################################################
# Glej kodo tukaj

    def charge(self):

        # Tukaj se pripravi list iz začetnih temperatur
        previousTempList = initialize.temperatures(zNodes, rNodes, ambientTemp)
        currentTempList = []  

        # Pripravimo matrike za levo in desno stran
        coefficients, constants = initialize.prepareCharging(zNodes)
        coeffMatrix = ChargingArray(coefficients, constants).coeffMatrix()
        
        # 1000x poračunamo temperature v hranilniku
        # V tem primeru računamo samo temperature v prvem arrayu (zato pa previousTempList[0])
        # previousTempList je sicer sestavljen iz nested arrayov, ampak kličemo samo prvega
        for timeStep in range(int(dt*10000)):
            # Uporabimo constArray metodo iz arrays.py zato da dobimo matriko na desni strani
            constArray = ChargingArray(coefficients, constants).constArray(previousTempList[0])
            
            # Izračunamo temperature in dodamo v nov array
            temperature = np.linalg.solve(coeffMatrix, constArray)
            temperature = temperature.tolist()
            currentTempList.append(temperature)

            # Izpišemo temperature v terminalu, tukaj lahko filtriraš, koliko jih izpiše
            if timeStep % 100 == 0:
                print(DataFrame(currentTempList))

            previousTempList = currentTempList
            currentTempList = []

        return previousTempList

##################################################################################################

    # def store(self, tempFromCharging):

    #     previousTempList = mapping.lengthToRadius(tempFromCharging)
    #     previousTempList = initialize.makeInsulation(previousTempList, ambientTemp, rNodesIns)
    #     currentTempList = []

    #     coefficients, constants = initialize.prepareStoring(rNodes, rNodesIns)
    #     coeffMatrix = StoringArray(coefficients, constants).coeffMatrix()

    #     for timeStep in range(10):
    #         for array in previousTempList:
    #             constArray = StoringArray(coefficients, constants).constArray(array)
    #             temperature = np.linalg.solve(coeffMatrix, constArray)
    #             temperature = temperature.tolist()
    #             currentTempList.append(temperature)

    #         keepCount = export.Count.time(dt)
    #         # exportable.allStoringTemperatures(currentTempList, rNodesIns, keepCount)
    #         # Reassign temperatures
    #         previousTempList = list(currentTempList)
    #         currentTempList = []

    #     previousTempList = initialize.delInsulation(previousTempList, rNodesIns)
        
    #     return previousTempList


    # def discharge(self, tempFromStoring):
        
    #     previousTempList = mapping.radiusToLength(tempFromStoring)
    #     currentTempList = []

    #     coefficients, constants = initialize.prepareCharging(zNodes)
    #     coeffMatrix = DischargingArray(coefficients, constants).coeffMatrix()

    #     for timeStep in range(10):
    #         for array in previousTempList:
    #             constArray = DischargingArray(
    #                 coefficients, constants).constArray(array)
    #             temperature = np.linalg.solve(coeffMatrix, constArray)
    #             temperature = temperature.tolist()
    #             currentTempList.append(temperature)

    #         # Export the array of arrays
    #         keepCount = export.Count.time(dt)
    #         export.allTemperatures("Discharging", currentTempList, keepCount)

    #         # Assign new temperatures as previous, empty out the current temperature array
    #         previousTempList = list(currentTempList)
    #         currentTempList = []

    #     return previousTempList


z = Storage().charge()