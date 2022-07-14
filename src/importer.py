import sys, os
import csv
import modules.makeDirectory as makeDirectory

class Properties:

    def __init__(self, simulationId = 1, simulationCount = 1):
        self.simulationId = simulationId
        self.simulationCount = simulationCount
    
    def getNextId(self):
        with open(f"{makeDirectory.ROOT_DIRECTORY_PATH}/data/properties.csv", "r", encoding="utf-8-sig") as csvFile:
            allRows = csv.DictReader(csvFile)

            # Do this until row doesn't return anything, check the next row if it exists
            for row in allRows:
                if int(row["id"]) == self.simulationId + 1:
                    self.simulationId += 1
                    return self.simulationId

        self.simulationId = None

    def progressOfSimulations(self):
        with open(f"{makeDirectory.ROOT_DIRECTORY_PATH}/data/properties.csv", "r", encoding="utf-8-sig") as csvFile:
            allRows = csv.reader(csvFile)
            allSimulations = 2*(sum(1 for _ in allRows) - 1)

            print(f"{self.simulationCount}/{allSimulations} done")
            self.simulationCount += 1
            return self.simulationCount

    def makeDirectoryForId(self, exportDirectory):
        idDirectoryPath = f"{exportDirectory}/id-{self.simulationId}"
        os.makedirs(idDirectoryPath)

        return idDirectoryPath

    def simulationTime(self, startTime, endTime):
        difference = endTime - startTime
        if difference >= 60 and difference < 3600:
            print(f"Done in {round(difference/60, 1)} min")
        elif difference < 60:
            print(f"Done in {difference} s")
        else:
            print(f"Done in {round(difference/3600, 1)} h")

    def getProperties(self):
        with open(f"{makeDirectory.ROOT_DIRECTORY_PATH}/data/properties.csv", "r", encoding="utf-8-sig") as csvFile:
            allRows = csv.DictReader(csvFile)

            for row in allRows:
                if self.simulationId == int(row["id"]):
                    try:
                        self.length = float(row["length"])
                        self.radius = float(row["radius"])
                        self.insulation = float(row["insulation"])
                        self.materialDiameter = float(row["materialDiameter"])
                        self.voidFrac = float(row["voidFrac"])
                        self.kIns = float(row["kIns"])
                        self.rhoIns = float(row["rhoIns"])
                        self.cIns = float(row["cIns"])
                        self.kf = float(row["kf"])
                        self.ks = float(row["ks"])
                        self.Tambient = float(row["Tambient"])
                        self.Tfluid = float(row["Tfluid"])
                        self.finalDifference = float(row["finalDifference"])
                        self.h = float(row["h"])
                        self.hAmbient = float(row["hAmbient"])
                        self.G = float(row["G"])
                        self.flowVelocity = float(row["flowVelocity"])
                        self.dynamicViscosity = float(row["dynamicViscosity"])
                        self.c1 = float(row["c1"])
                        self.c2 = float(row["c2"])
                        self.dzDefined = float(row["dzDefined"])
                        self.drDefined = float(row["drDefined"])
                        self.dt = float(row["dt"])
                        self.dtStore = float(row["dtStore"])
                        self.exportDtCharging = float(row["exportDtCharging"])
                        self.exportDtStoring = float(row["exportDtStoring"])

                    except (TypeError, ValueError):
                        print("Not all properties are defined")
                        sys.exit()


    def discretization(self):
        # z-direction discretization
        self.zNodes = round(self.length/self.dzDefined) + 1  # /
        self.dz = self.length/(self.zNodes - 1)  # m
        # Storage r-direction discretization
        self.rNodes = round(self.radius/self.drDefined) + 1  # /
        self.dr = self.radius/(self.rNodes - 1)  # m
        # Insulation r-direction
        # If there is no insulation
        if self.insulation == 0:
            self.rNodesIns = 0
            self.drIns = 0
        else:
            self.rNodesIns = round(self.insulation/self.drDefined)
            try:
                self.drIns = self.insulation/self.rNodesIns
            except ZeroDivisionError:
                print("Redefine insulation or drDefined")
                sys.exit()

    def calculatedCoefficients(self):
        self.A = 6*(1 - self.voidFrac)/self.materialDiameter
