import os

def getDirectoryName(directory):
    # Change to specified directory
    os.chdir(directory)

    dirName = input("Directory to export: ")
    dirPath = os.path.join(directory, dirName)
    try:
        os.mkdir(dirPath)
    except OSError:
        print("Try a different one")
        getDirectoryName(directory)

    return dirPath

class Export:

    def __init__(self, directory, model, mappingFile, length, radius, insulation, sizeCoefficient=1):
        self.directory = directory
        self.model = model
        self.mappingFile = mappingFile
        self.length = length
        self.radius = radius
        self.insulation = insulation
        self.sizeCoefficient = sizeCoefficient

    def initialTemperatures(self, tempList):

        # Open a file to append to:
        with open(f"{self.directory}/{self.model}.csv", "a") as file:
            file.write("Initial temperatures\n")
            # Export the initial temperatures first
            file.write("t = 0s|0h\nr(m)|z(m),")
            
            # Values for storage length
            for dz in range(0, round(len(tempList[0])/self.sizeCoefficient)):
                file.write(f"{dz*self.length/(len(tempList[0])/self.sizeCoefficient-1)},")
            file.write("\n")

            # Temperature values and radius length
            for array in range(len(tempList)):
                file.write(f"{round(array*self.radius/(len(tempList)-1), 2)},")
                for i in range(round(len(tempList[array])/self.sizeCoefficient)):
                    file.write("{:.2f},".format(tempList[array][i]))
                file.write("\n")
            file.write("\n")

    def allTemperatures(self, message, tempList, keepCount):

        # Open a file to append to:
        with open(f"{self.directory}/{self.model}.csv", "a") as file:
            # Write into the file
            file.write(f"{message}\n")
            file.write("t = {}s|{}h\n".format(keepCount, round(keepCount/3600, 2)))
            file.write("r(m)|z(m),")

            for dz in range(round(len(tempList[0])/self.sizeCoefficient)):
                file.write(f"{round(dz*self.length/(len(tempList[0])/self.sizeCoefficient-1), 3)},")
            file.write("\n")

            for array in range(len(tempList)):
                dimension = self.radius - self.radius*array/(len(tempList)-1)
                file.write(f"{round(dimension, 2)},")
                for i in range(round(len(tempList[array])/self.sizeCoefficient)):
                    file.write("{:.2f},".format(tempList[array][i]))
                file.write("\n")
            file.write("\n")

    # Export during the storing process and exclude insulation temperatures
    def allStoringTemperatures(self, tempList, insulationNodes, keepCount):

        with open(f"{self.directory}/{self.model}.csv", "a") as file:
            file.write("Storing\n")
            file.write("t = {}s|{}h\n".format(keepCount, round(keepCount/3600, 2)))

            mappedList = self.mappingFile.radiusToLength(tempList)
            # file.write("r(m)|z(m),")
            # for dz in range(0, len(mappedList[0])):
            #     file.write(f"{dz*self.length/(len(mappedList[0])-1)},")
            # file.write("\n")
            # for array in range(0, len(mappedList)):
            #     dimension = (self.radius + self.insulation)*(1-(array)/(len(mappedList)-1))
            #     file.write(f"{round(dimension, 2)},")
            #     for number in mappedList[array]:
            #         file.write("{:.2f},".format(number))
            #     file.write("\n")
            # file.write("\n")
            file.write("r(m)|z(m),")
            for dz in range(round(len(mappedList[0])/self.sizeCoefficient)):
                file.write(f"{round(dz*self.length/(len(mappedList[0])/self.sizeCoefficient-1), 3)},")
            file.write("\n")

            for array in range(insulationNodes, len(mappedList)):
                dimension = self.radius*(1-(array-insulationNodes)/(len(mappedList)-1-insulationNodes))
                file.write(f"{round(dimension, 2)},")
                for i in range(round(len(mappedList[array])/self.sizeCoefficient)):
                    file.write("{:.2f},".format(mappedList[array][i]))
                file.write("\n")
            file.write("\n")

    # Izvozimo shranjeno toploto med polnjenjem
    def heatStored(self, tempList, tempInitial, cp, keepCount):

        tempDifferenceList = []
        for list in tempList:
            for temperature in list:
                tempAppend = temperature - tempInitial
                tempDifferenceList.append(tempAppend)

        heatPerKilo = cp*sum(tempDifferenceList)/len(tempDifferenceList)

        with open(f"{self.directory}/heat-charging.csv", "a+") as file:
            file.write("{:.2f},{:.2f}\n".format(keepCount/3600, heatPerKilo/1000))

    # Shranjena toplota med hranjenjem
    def heatStoredStoring(self, tempList, tempInitial, insulationNodes, cp, keepCount):

        tempDifferenceList = []
        mappedList = self.mappingFile.radiusToLength(tempList)

        for index in range(len(mappedList)):
            for temperature in mappedList[index]:
                tempAppend = temperature - tempInitial
                tempDifferenceList.append(tempAppend)

        heatPerKilo = cp*sum(tempDifferenceList)/len(tempDifferenceList)

        with open(f"{self.directory}/heat-storing.csv", "a+") as file:
            file.write("{:.2f},{:.2f}\n".format(keepCount/3600, heatPerKilo/1000))

        # tempDifferenceList = []
        # mappedList = mapping.radiusToLength(tempList)

        # for index in range(insulationNodes, len(mappedList)):
        #     for temperature in mappedList[index]:
        #         tempAppend = temperature - tempInitial
        #         tempDifferenceList.append(tempAppend)

        # heatPerKilo = cp*sum(tempDifferenceList)/len(tempDifferenceList)

        # with open(f"{self.fileName}-heat-storing.csv", "a+") as file:
        #     file.write("{:.2f},{:.2f}\n".format(
        #         keepCount/3600, heatPerKilo/1000))
