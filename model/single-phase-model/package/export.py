import os
from . import mapping

class Count:
    counter = 0

    def time(dt):
        Count.counter += dt
        Count.counter = round(Count.counter, 2)
        
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

    def __init__(self, fileName, length, radius):
        self.fileName = fileName
        self.length = length
        self.radius = radius

    def initialTemperatures(self, tempList):

        # Open a file to append to:
        with open(f"{self.fileName}.txt", "a") as file:
            file.write("Initial temperatures\n")
            # Export the initial temperatures first
            file.write("t = 0.0 s\n")
            file.write("r(m)|z(m)\t")
            for dz in range(0, len(tempList[0])):
                file.write(f"{dz*self.length/(len(tempList[0])-1)}\t")
            file.write("\n")
            for array in range(len(tempList)):
                file.write(f"{round(array*self.radius/(len(tempList)-1), 2)}\t")
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")


    def allTemperatures(self, message, tempList, keepCount):

        # Open a file to append to:
        with open(f"{self.fileName}.txt", "a") as file:
            # Write into the file
            file.write("{}\n".format(message))
            file.write("t = {}s|{}h\n".format(keepCount, round(keepCount/3600, 2)))
            file.write("r(m)|z(m)\t")
            for dz in range(0, len(tempList[0])):
                file.write(f"{dz*self.length/(len(tempList[0])-1)}\t")
            file.write("\n")

            for array in range(len(tempList)):
                file.write(f"{round(array*self.radius/(len(tempList)-1), 2)}\t")
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")

    # Export during the storing process and exclude insulation temperatures
    def allStoringTemperatures(self, tempList, insulationNodes, keepCount):

        with open(f"{self.fileName}.txt", "a") as file:
            file.write("Storing\n")
            file.write("t = {}s|{}h\n".format(keepCount, round(keepCount/3600, 2)))

            mappedList = mapping.radiusToLength(tempList)
            file.write("r(m)|z(m)\t")
            for dz in range(0, len(mappedList[0])):
                file.write(f"{dz*self.length/(len(mappedList[0])-1)}\t")
            file.write("\n")
            for array in range(insulationNodes, len(mappedList)):
                file.write(f"{round((array-insulationNodes)*self.radius/(len(mappedList)-1-insulationNodes), 2)}\t")
                for number in mappedList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")
