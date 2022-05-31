import os
from turtle import pen
from . import mapping

class Count:
    counter = 0

    def time(deltaTime):
        Count.counter += deltaTime
        Count.counter = round(Count.counter, 3)
        
        return Count.counter

    def endCount():
        return Count.counter


def getFileName(directory):

    # Change to specified directory
    os.chdir(directory)

    fileName = input("Specify name for the single phase model: ")
    filePath = os.path.join(directory, "{}.txt".format(fileName))
    while os.path.exists(filePath) == True:
        fileName = input(
            "A file with this name already exists. Specify a new one: ")
        filePath = os.path.join(directory, "{}.txt".format(fileName))
    print("Exporting...")

    return fileName

class Export:

    def __init__(self, fileName, length, radius, insulation):
        self.fileName = fileName
        self.length = length
        self.radius = radius
        self.insulation = insulation

    def initialTemperatures(self, tempList):

        # Open a file to append to:
        with open(f"{self.fileName}.csv", "a") as file:
            file.write("Initial temperatures\n")
            # Export the initial temperatures first
            file.write("t = 0.0 s\n")
            file.write("r(m)|z(m),")
            for dz in range(0, len(tempList[0])):
                file.write(f"{dz*self.length/(len(tempList[0])-1)},")
            file.write("\n")
            for array in range(len(tempList)):
                file.write(f"{round(array*self.radius/(len(tempList)-1), 2)},")
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + ",")
                file.write("\n")
            file.write("\n")


    def allTemperatures(self, message, tempList, keepCount):

        # Open a file to append to:
        with open(f"{self.fileName}.csv", "a") as file:
            # Write into the file
            file.write("{}\n".format(message))
            file.write("t = {}s|{}h\n".format(keepCount, round(keepCount/3600, 2)))
            file.write("r(m)|z(m),")
            for dz in range(0, len(tempList[0])):
                file.write(f"{dz*self.length/(len(tempList[0])-1)},")
            file.write("\n")

            for array in range(len(tempList)):
                dimension = self.radius - self.radius*array/(len(tempList)-1)
                file.write(f"{round(dimension, 2)},")
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + ",")
                file.write("\n")
            file.write("\n")

    # Export during the storing process and exclude insulation temperatures
    def allStoringTemperatures(self, tempList, insulationNodes, keepCount):

        with open(f"{self.fileName}.csv", "a") as file:
            file.write("Storing\n")
            file.write("t = {}s|{}h\n".format(keepCount, round(keepCount/3600, 2)))

            mappedList = mapping.radiusToLength(tempList)
            file.write("r(m)|z(m),")
            for dz in range(0, len(mappedList[0])):
                file.write(f"{dz*self.length/(len(mappedList[0])-1)},")
            file.write("\n")
            for array in range(0, len(mappedList)):
                dimension = (self.radius+self.insulation)*(1-(array)/(len(mappedList)-1))
                file.write(f"{round(dimension, 2)},")
                for number in mappedList[array]:
                    file.write("{:.2f}".format(number) + ",")
                file.write("\n")
            file.write("\n")
            # file.write("r(m)|z(m),")
            # for dz in range(0, len(mappedList[0])):
            #     file.write(f"{dz*self.length/(len(mappedList[0])-1)},")
            # file.write("\n")
            # for array in range(insulationNodes, len(mappedList)):
            #     dimension = self.radius*(1-(array-insulationNodes)/(len(mappedList)-1-insulationNodes))
            #     file.write(f"{round(dimension, 2)},")
            #     for number in mappedList[array]:
            #         file.write("{:.2f}".format(number) + ",")
            #     file.write("\n")
            # file.write("\n")

    # Izvozimo shranjeno toploto med polnjenjem
    def heatStored(self, tempList, tempInitial, cp, keepCount):

        tempDifferenceList = []
        for list in tempList:
            for temperature in list:
                tempAppend = temperature - tempInitial
                tempDifferenceList.append(tempAppend)

        heatPerKilo =  cp*sum(tempDifferenceList)/len(tempDifferenceList)

        with open(f"{self.fileName}-heat-charging.csv", "a+") as file:
            file.write("{:.2f},{:.2f}\n".format(keepCount/3600, heatPerKilo/1000))

    # Shranjena toplota med hranjenjem
    def heatStoredStoring(self, tempList, tempInitial, insulationNodes, cp, keepCount):

        tempDifferenceList = []
        mappedList = mapping.radiusToLength(tempList)

        for index in range(insulationNodes, len(mappedList)):
            for temperature in mappedList[index]:
                tempAppend = temperature - tempInitial
                tempDifferenceList.append(tempAppend)

        heatPerKilo = cp*sum(tempDifferenceList)/len(tempDifferenceList)

        with open(f"{self.fileName}-heat-storing.csv", "a+") as file:
            file.write("{:.2f},{:.2f}\n".format(
                keepCount/3600, heatPerKilo/1000))
            

