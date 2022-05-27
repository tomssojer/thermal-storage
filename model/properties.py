import re

# Properties
length = radius = insulation = None
materialDiameter = None
voidFrac = None
kStorage = rhoStorage = cStorage = None
kGas = rhoGas = cGas = None
kIns = rhoIns = cIns = None 
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
# def getListFromImportedFile(material, property):
#     try:
#         with open(f"data/{material}/{property}.csv", "r", encoding='utf-8-sig') as openedFile:
#             lines = openedFile.readlines()
#             values = []
#             for line in lines:
#                 line = line.strip("\n")
#                 valuesArray = line.split(",")
#                 valuesArray[0] = float(valuesArray[0])
#                 valuesArray[1] = float(valuesArray[1])
#                 values.append(valuesArray)

#     except:
#         raise Exception("Incorrectly defined material or property in getListsFromFiles.")

#     return values


# kStorage = getListFromImportedFile("graphite", "k")
# cStorage = getListFromImportedFile("graphite", "cp")
# rhoStorage = getListFromImportedFile("graphite", "rho")
# kGas = getListFromImportedFile("helium", "k")
# cGas = getListFromImportedFile("helium", "cp")
# rhoGas = getListFromImportedFile("helium", "rho")

# def searchForProperty(previousTemperatureList, listFromFile):

#     propertyList = []

#     if len(listFromFile) == 1:
#         for temp in range(len(previousTemperatureList)):
#             propertyList.append(listFromFile[0][1])
#         return propertyList

#     for temp in range(len(previousTemperatureList)):

#         if previousTemperatureList[temp] < listFromFile[0][0]:
#             extrapolate = listFromFile[0][1] + (previousTemperatureList[temp]-listFromFile[0][0])/(listFromFile[1][0]-listFromFile[0][0])*(listFromFile[1][1]-listFromFile[0][1])
#             propertyList.append(extrapolate)

#         elif previousTemperatureList[temp] > listFromFile[-1][0]:
#             extrapolate = listFromFile[-2][1] + (previousTemperatureList[temp]-listFromFile[-1][0])/(
#                 listFromFile[-1][0]-listFromFile[-2][0])*(listFromFile[-1][1]-listFromFile[-2][1])
#             propertyList.append(extrapolate)

#         else:
#             firstIndex = 0
#             lastIndex = len(listFromFile) - 1

#             while lastIndex - firstIndex > 1:
#                 middleIndex = (firstIndex + lastIndex)//2

#                 if previousTemperatureList[temp] <= listFromFile[middleIndex][0]:
#                     lastIndex = middleIndex
#                 elif previousTemperatureList[temp] > listFromFile[middleIndex][0]:
#                     firstIndex = middleIndex

#             interpolate = listFromFile[firstIndex][1] + (previousTemperatureList[temp]-listFromFile[firstIndex][0])*(listFromFile[lastIndex][1]-listFromFile[firstIndex][1])/(listFromFile[lastIndex][0]-listFromFile[firstIndex][0])
#             propertyList.append(interpolate)

#     return propertyList

# previousList = [50, 200, 400, 340, 932, 1500]
# a = searchForProperty(previousList, cGas)
# print(a)

# Nekateri koeficienti, ki jih je potrebno izračunati
A = 6*(1 - voidFrac)/materialDiameter
cp = voidFrac*cStorage + (1 - voidFrac)*cGas
thermalMass = voidFrac*rhoGas*cGas + (1 - voidFrac)*rhoStorage*cStorage
reynoldsNum = rhoGas*flowVelocity*materialDiameter/dinamicViscosity
prandtlNum = cGas*dinamicViscosity/kGas
effConductivity = kGas*voidFrac*(1 + c1*(reynoldsNum*prandtlNum)**c2)
k = kStorage*(1 - voidFrac*(kStorage - effConductivity)/(effConductivity + voidFrac**(1/3)*(kStorage - effConductivity)))

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
