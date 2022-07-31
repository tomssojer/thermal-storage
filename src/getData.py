from math import log10
import modules.makeDirectory as makeDirectory

# Extract data from materials files and return a list of lists
def getListFromImportedFile(material, property):
    path = f"{makeDirectory.ROOT_DIRECTORY_PATH}/data/{material}/{property}.csv"
    with open(path, "r", encoding='utf-8-sig') as openedFile:
        lines = openedFile.readlines()
        values = []
        for line in lines:
            line = line.strip("\n")
            valuesArray = line.split(",")
            valuesArray[0] = float(valuesArray[0])
            valuesArray[1] = float(valuesArray[1])
            values.append(valuesArray)

    return values

# Binary search to search for properties from files with data
def searchForProperty(previousTemperatureList, listFromFile):

    # Create a list to append values according to temperatures
    propertyList = []

    # Edge case if we want to have a constant value
    if len(listFromFile) == 1:
        for temp in range(len(previousTemperatureList)):
            propertyList.append(listFromFile[0][1])
        return propertyList

    # Enter the loop to iterate through temperatures from previous list
    for temp in range(len(previousTemperatureList)):

        # Case where temperature is smaller than the smallest temperature from data file
        if previousTemperatureList[temp] < listFromFile[0][0]:
            # Extrapolation equation
            extrapolate = listFromFile[0][1] + (previousTemperatureList[temp]-listFromFile[0][0])/(
                listFromFile[1][0]-listFromFile[0][0])*(listFromFile[1][1]-listFromFile[0][1])
            propertyList.append(extrapolate)

        # Case where temperature is higher
        elif previousTemperatureList[temp] > listFromFile[-1][0]:
            extrapolate = listFromFile[-2][1] + (previousTemperatureList[temp]-listFromFile[-1][0])/(
                listFromFile[-1][0]-listFromFile[-2][0])*(listFromFile[-1][1]-listFromFile[-2][1])
            propertyList.append(extrapolate)

        # For all middle cases
        else:
            firstIndex = 0
            lastIndex = len(listFromFile) - 1

            # We go through the list of data and search for the value, closest to the temperature
            while lastIndex - firstIndex > 1:
                middleIndex = (firstIndex + lastIndex)//2

                if previousTemperatureList[temp] <= listFromFile[middleIndex][0]:
                    lastIndex = middleIndex
                elif previousTemperatureList[temp] > listFromFile[middleIndex][0]:
                    firstIndex = middleIndex

            # Interpolation equation
            interpolate = listFromFile[firstIndex][1] + (previousTemperatureList[temp]-listFromFile[firstIndex][0])*(
                listFromFile[lastIndex][1]-listFromFile[firstIndex][1])/(listFromFile[lastIndex][0]-listFromFile[firstIndex][0])
            propertyList.append(interpolate)

    return propertyList


class Node():

    kStorage = getListFromImportedFile("graphite", "k")
    cStorage = getListFromImportedFile("graphite", "cp")
    rhoStorage = getListFromImportedFile("graphite", "rho")
    kGas = getListFromImportedFile("helium", "k")
    cGas = getListFromImportedFile("helium", "cp")
    rhoGas = getListFromImportedFile("helium", "rho")

    def __init__(self, subList, propertiesObject):
        self.subList = subList
        self.props = propertiesObject

    def rhoGasList(self):
        return searchForProperty(self.subList, self.rhoGas)

    def cGasList(self):
        return searchForProperty(self.subList, self.cGas)

    def kGasList(self):
        return searchForProperty(self.subList, self.kGas)

    def kStorageList(self):
        return searchForProperty(self.subList, self.kStorage)

    def rhoStorageList(self):
        return searchForProperty(self.subList, self.rhoStorage)

    def cStorageList(self):
        return searchForProperty(self.subList, self.cStorage)

    def thermalMassList(self):
        thermalMassList = []
        for i in range(len(self.subList)):
            thermalMassList.append(self.props.voidFrac*self.rhoGasList()[i]*self.cGasList()[i] + (1 - self.props.voidFrac)*self.rhoStorageList()[i]*self.cStorageList()[i])
        return thermalMassList

    def cpList(self):
        cpList = []
        for i in range(len(self.subList)):
            cpList.append(self.props.voidFrac*self.cGasList()[i] + (1 - self.props.voidFrac)*self.cStorageList()[i])
        return cpList

    def reynoldsNumList(self):
        reynoldsNum = []
        for i in range(len(self.subList)):
            reynoldsNum.append(self.rhoGasList()[i]*self.props.flowVelocity*self.props.materialDiameter/self.props.dynamicViscosity)
        return reynoldsNum

    def prandtlNumList(self):
        prandtlNum = []
        for i in range(len(self.subList)):
            prandtlNum.append(self.cGasList()[i]*self.props.dynamicViscosity/self.kGasList()[i])
        return prandtlNum

    def kStoringList(self):
        kList = []
        for i in range(len(self.subList)):
            kList.append(self.props.voidFrac*self.kGasList()[i] + (1 - self.props.voidFrac)*self.kStorageList()[i])
        return kList

    def kSinglePhaseList(self):
        kEff = []; kList = []
        for i in range(len(self.subList)):
            kEff.append(self.kGasList()[i]*self.props.voidFrac*(1 + self.props.c1*(self.reynoldsNumList()[i]*self.prandtlNumList()[i])**self.props.c2))
            kList.append(self.kStorageList()[i]*(1 - self.props.voidFrac*(self.kStorageList()[i] - kEff[i])/(kEff[i] + self.props.voidFrac**(1/3)*(self.kStorageList()[i] - kEff[i]))))
        return kList

    def kContinuousFluidList(self):
        kList = []
        for i in range(len(self.subList)):
            if self.reynoldsNumList()[i] <= 0.8:
                kList.append(0.7*self.props.voidFrac*self.kGasList()[i])
            else:
                kList.append(0.5*self.prandtlNumList()[i]*self.reynoldsNumList()[i]*self.kGasList()[i])
        return kList

    def kContinuousSolidList(self):
        kList = []; kEff = []; kStagnation = []; m = []
        for i in range(len(self.subList)):
            m.append(0.28 - 0.757*log10(self.props.voidFrac) - 0.057*log10(self.kStorageList()[i]/self.kGasList()[i]))
            kStagnation.append(self.kGasList()[i]*(self.kStorageList()[i]/self.kGasList()[i])**m[i])
            kEff.append(kStagnation[i] + self.kGasList()[i]*0.5*self.prandtlNumList()[i]*self.reynoldsNumList()[i])
            kList.append(kEff[i] - self.kContinuousFluidList()[i])
        return kList
