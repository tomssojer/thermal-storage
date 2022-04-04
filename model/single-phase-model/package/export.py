import os

from pandas import DataFrame
from . import mapping
length = 3
radius = 0.5

class Count:
    counter = 0

    def time(dt):
        Count.counter += dt
        Count.counter = round(Count.counter, 2)
        print(Count.counter)
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
    print("Exporting temperatures...")

    return fileName

class Export:

    def __init__(self, fileName):
        self.fileName = fileName

    def initialTemperatures(self, tempList):

        # Open a file to append to:
        with open(f"{self.fileName}.txt", "a") as file:
            file.write("Initial temperatures\n")
            # Export the initial temperatures first
            file.write("t = 0.0 s\n")
            file.write("r(m)|z(m)\t")
            for dz in range(0, len(tempList[0])):
                file.write(f"{dz*length/(len(tempList[0])-1)}\t")
            file.write("\n")
            for array in range(len(tempList)):
                file.write(f"{round(array*radius/(len(tempList)-1), 2)}\t")
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")


    def allTemperatures(self, message, tempList, keepCount):

        # Open a file to append to:
        with open(f"{self.fileName}.txt", "a") as file:
            # Write into the file
            file.write("{}\n".format(message))
            file.write("t = {} s\n".format(keepCount))
            file.write("r(m)|z(m)\t")
            for dz in range(0, len(tempList[0])):
                file.write(f"{dz*length/(len(tempList[0])-1)}\t")
            file.write("\n")
            for array in range(len(tempList)):
                file.write(f"{round(array*radius/(len(tempList)-1), 2)}\t")
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")

    # Export during the storing process and exclude insulation temperatures
    def allStoringTemperatures(self, tempList, insulationNodes, keepCount):

        with open(f"{self.fileName}.txt", "a") as file:
            file.write("Storing\n")
            file.write("t = {} s\n".format(keepCount))

            mappedList = mapping.radiusToLength(tempList)
            file.write("r(m)|z(m)\t")
            for dz in range(0, len(mappedList[0])):
                file.write(f"{dz*length/(len(mappedList[0])-1)}\t")
            file.write("\n")
            for array in range(insulationNodes, len(mappedList)):
                file.write(f"{round((array-insulationNodes)*radius/(len(mappedList)-1-insulationNodes), 2)}\t")
                for number in mappedList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")
