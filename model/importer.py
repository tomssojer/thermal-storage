import re

# Properties
length = radius = insulation = None
materialDiameter = None
voidFrac = None
# kStorage = rhoStorage = cStorage = None
# kGas = rhoGas = cGas = None
# kIns = rhoIns = cIns = None 
kf = ks = None 
ambientTemp = Tfluid = finalDifference = None
h =  ambienth = None
G = None
flowVelocity = None
dinamicViscosity = None
c1 = c2 = None
# Discretization
dzDefined = drDefined = dt = dtStore = None
exportDtCharging = exportDtStoring = None

# Open and execute the properties file
with open("./data/properties.txt", "r") as file:
    exec(file.read())

# Extract data from materials files and return a list of lists
def getListFromImportedFile(material, property):
    try:
        with open(f"data/{material}/{property}.csv", "r", encoding='utf-8-sig') as openedFile:
            lines = openedFile.readlines()
            values = []
            for line in lines:
                line = line.strip("\n")
                valuesArray = line.split(",")
                valuesArray[0] = float(valuesArray[0])
                valuesArray[1] = float(valuesArray[1])
                values.append(valuesArray)
    except:
        raise Exception("Incorrectly defined material or property in getListsFromFiles.")

    return values

# Binary search to search for properties from files with data
def searchForProperty(previousTemperatureList, listFromFile):

    # Create a list to append values according to temperatures
    propertyList = []

    # Edge case if we want to have a constant value
    if len(listFromFile) == 1:
        for temp in range(len(previousTemperatureList[0])):
            propertyList.append(listFromFile[0][1])
        return propertyList

    # Enter the loop to iterate through temperatures from previous list
    for temp in range(len(previousTemperatureList[0])):

        # Case where temperature is smaller than the smallest temperature from data file
        if previousTemperatureList[0][temp] < listFromFile[0][0]:
            # Extrapolation equation
            extrapolate = listFromFile[0][1] + (previousTemperatureList[0][temp]-listFromFile[0][0])/(listFromFile[1][0]-listFromFile[0][0])*(listFromFile[1][1]-listFromFile[0][1])
            propertyList.append(extrapolate)

        # Case where temperature is higher
        elif previousTemperatureList[0][temp] > listFromFile[-1][0]:
            extrapolate = listFromFile[-2][1] + (previousTemperatureList[0][temp]-listFromFile[-1][0])/(
                listFromFile[-1][0]-listFromFile[-2][0])*(listFromFile[-1][1]-listFromFile[-2][1])
            propertyList.append(extrapolate)

        # For all middle cases
        else:
            firstIndex = 0
            lastIndex = len(listFromFile) - 1

            # We go through the list of data and search for the value, closest to the temperature
            while lastIndex - firstIndex > 1:
                middleIndex = (firstIndex + lastIndex)//2

                if previousTemperatureList[0][temp] <= listFromFile[middleIndex][0]:
                    lastIndex = middleIndex
                elif previousTemperatureList[0][temp] > listFromFile[middleIndex][0]:
                    firstIndex = middleIndex

            # Interpolation equation
            interpolate = listFromFile[firstIndex][1] + (previousTemperatureList[0][temp]-listFromFile[firstIndex][0])*(listFromFile[lastIndex][1]-listFromFile[firstIndex][1])/(listFromFile[lastIndex][0]-listFromFile[firstIndex][0])
            propertyList.append(interpolate)

    return propertyList


kStorage = getListFromImportedFile("graphite", "k")
cStorage = getListFromImportedFile("graphite", "cp")
rhoStorage = getListFromImportedFile("graphite", "rho")
kGas = getListFromImportedFile("helium", "k")
cGas = getListFromImportedFile("helium", "cp")
rhoGas = getListFromImportedFile("helium", "rho")


# We now get a list of properies for each list 


# Nekateri koeficienti, ki jih je potrebno izračunati
A = 6*(1 - voidFrac)/materialDiameter

# def calculateProperties(list):

#     kStorageList = searchForProperty(list, kStorage)
#     cStorageList = searchForProperty(list, cStorage)
#     rhoStorageList = searchForProperty(list, rhoStorage)
#     kGasList = searchForProperty(list, kGas)
#     cGasList = searchForProperty(list, cStorage)
#     rhoGasList = searchForProperty(list, rhoStorage)
    
#     for _ in list:
#         cp = voidFrac*cStorage + (1 - voidFrac)*cGas
#         thermalMass = voidFrac*rhoGas*cGas + (1 - voidFrac)*rhoStorage*cStorage
#         reynoldsNum = rhoGas*flowVelocity*materialDiameter/dinamicViscosity
#         prandtlNum = cGas*dinamicViscosity/kGas
#         effConductivity = kGas*voidFrac*(1 + c1*(reynoldsNum*prandtlNum)**c2)
#         k = kStorage*(1 - voidFrac*(kStorage - effConductivity)/(effConductivity + voidFrac**(1/3)*(kStorage - effConductivity)))

#     return k, cp, thermalMass

class Node:

    def __init__(self, listOfTemperatures, kStorageMapped, rhoStorageMapped, cStorageMapped, kGasMapped, rhoGasMapped, cGasMapped):
        self.listOfTemperatures = listOfTemperatures
        self.kStorageMapped = kStorageMapped
        self.rhoStorageMapped = rhoStorageMapped
        self.cStorageMapped = cStorageMapped
        self.kGasMapped = kGasMapped
        self.rhoGasMapped = rhoGasMapped
        self.cGasMapped = cGasMapped

    def capacity(self):

        cpList = []
        for i in range(len(self.listOfTemperatures[0])):
            cpList.append(voidFrac*self.cStorageMapped[i] + (1 - voidFrac)*self.cGasMapped[i])

        return cpList

    def thermalMass(self):

        thermalMassList = []
        for i in range(len(self.listOfTemperatures[0])):
            thermalMassList.append(voidFrac*self.rhoGasMapped[i]*self.cGasMapped[i] + (1 - voidFrac)*self.rhoStorageMapped[i]*self.cStorageMapped[i])

        return thermalMassList

    def conductivity(self, reynoldsNum, prandtlNum, effConductivity):

        conductivityList = []
        for _ in range(len(self.listOfTemperatures[0])):
            reynoldsNum = self.rhoGasMapped*flowVelocity*materialDiameter/dinamicViscosity
            prandtlNum = self.cGasMapped*dinamicViscosity/self.kGasMapped
            effConductivity = self.kGasMapped*voidFrac*(1 + c1*(reynoldsNum*prandtlNum)**c2)
            conductivityList.append(self.kStorageMapped*(1 - voidFrac*(self.kStorageMapped - effConductivity)/(effConductivity + voidFrac**(1/3)*(self.kStorageMapped - effConductivity))))

        return conductivityList

# We have a previousTemperaturesList
# Data is fetched from files and coverted to lists with getListsFromFile - k, cp, rho for storage, gas
# Everytime, before 

############ Discretization ###############
# z-direction discretization
zNodes = round(length/dzDefined) + 1  # ------- /
dz = length/(zNodes - 1)  # ------------------- m
# Storage r-direction discretization
rNodes = round(radius/drDefined) + 1  # ------- /
dr = radius/(rNodes - 1)  # ------------------- m
# Insulation r-direction
# If there is no insulation
if insulation == 0:
    rNodesIns = 0
    drIns = 0
else:
    rNodesIns = round(insulation/drDefined)
    drIns = insulation/rNodesIns
