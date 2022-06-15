import os
import mapping

class Count():
    counter = 0

    def time(dt):
        Count.counter += dt
        Count.counter = round(Count.counter, 2)
        print(Count.counter)
        return Count.counter

def getFileName(directory):

    # Change to specified directory
    os.chdir(directory)

    fileName = input("Specify name for the continuous model: ")
    filePath = os.path.join(directory, "{}.txt".format(fileName))
    while os.path.exists(filePath) == True:
        fileName = input(
            "A file with this name already exists. Specify a new one: ")
        filePath = os.path.join(directory, "{}.txt".format(fileName))
    print("Exporting temperatures...")

    return fileName

class Export:

    def __init__(self, fileName, counter):
        self.fileName = fileName
        self.counter = counter

    def initialTemperatures(self, tempList):

        # Open a file to append to:
        with open(f"{self.fileName}.txt", "a") as file:
            file.write("Initial temperatures\n")
            # Export the initial temperatures first
            file.write(f"t = {self.counter} s\n")
            for array in range(int(len(tempList)/2)-1, len(tempList)):
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")


    def allTemperatures(self, message, tempList):

        # Open a file to append to:
        with open(f"{self.fileName}.txt", "a") as file:
            # Write into the file
            file.write("{}\n".format(message))
            file.write("t = {} s\n".format(self.counter))

            for array in range(int(len(tempList)/2)-1, len(tempList)):
                for number in tempList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")


    def allStoringTemperatures(self, tempList, insulationNodes):

        with open(f"{self.fileName}.txt", "a") as file:
            file.write("Storing\n")
            file.write("t = {} s\n".format(self.counter))

            mappedList = mapping.radiusToLength(tempList)
            for array in range(insulationNodes, len(mappedList)):
                for number in mappedList[array]:
                    file.write("{:.2f}".format(number) + "\t")
                file.write("\n")
            file.write("\n")
