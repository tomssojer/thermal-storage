from getData import Node

class Export:

    def __init__(self, propertiesObject, directory, model, mappingFile, sizeCoefficient=1):
        self.propertiesObject = propertiesObject
        self.directory = directory
        self.model = model
        self.mappingFile = mappingFile
        self.sizeCoefficient = sizeCoefficient

    def initialTemperatures(self, tempList):

        # Open a file to append to:
        with open(f"{self.directory}/{self.model}.csv", "a") as file:
            file.write("Initial temperatures\n")
            # Export the initial temperatures first
            file.write("t = 0s|0h\nr(m)|z(m),")
            
            # Values for storage length
            for dz in range(0, round(len(tempList[0])/self.sizeCoefficient)):
                file.write(f"{dz*self.propertiesObject.length/(len(tempList[0])/self.sizeCoefficient-1)},")
            file.write("\n")

            # Temperature values and radius length
            for array in range(len(tempList)):
                file.write(f"{round(array*self.propertiesObject.radius/(len(tempList)-1), 2)},")
                for i in range(round(len(tempList[array])/self.sizeCoefficient)):
                    file.write("{:.2f},".format(tempList[array][i]))
                file.write("\n")
            file.write("\n")

    def allTemperatures(self, message, tempList, countTime):

        # Open a file to append to:
        with open(f"{self.directory}/{self.model}.csv", "a") as file:
            # Write into the file
            file.write(f"{message}\n")
            file.write("t = {}s|{}h\n".format(countTime, round(countTime/3600, 2)))
            file.write("r(m)|z(m),")

            for dz in range(round(len(tempList[0])/self.sizeCoefficient)):
                file.write(f"{round(dz*self.propertiesObject.length/(len(tempList[0])/self.sizeCoefficient-1), 3)},")
            file.write("\n")

            for array in range(len(tempList)):
                dimension = self.propertiesObject.radius - self.propertiesObject.radius*array/(len(tempList)-1)
                file.write(f"{round(dimension, 2)},")
                for i in range(round(len(tempList[array])/self.sizeCoefficient)):
                    file.write("{:.2f},".format(tempList[array][i]))
                file.write("\n")
            file.write("\n")

    # Export during the storing process and exclude insulation temperatures
    def allStoringTemperatures(self, tempList, insulationNodes, countTime):

        with open(f"{self.directory}/{self.model}.csv", "a") as file:
            file.write("Storing process\n")
            file.write("t = {}s|{}h\n".format(countTime, round(countTime/3600, 2)))

            mappedList = self.mappingFile.radiusToLength(tempList)
            # file.write("r(m)|z(m),")
            # for dz in range(0, len(mappedList[0])):
            #     file.write(f"{dz*self.propertiesObject.length/(len(mappedList[0])-1)},")
            # file.write("\n")
            # for array in range(0, len(mappedList)):
            #     dimension = (self.propertiesObject.radius + self.propertiesObject.insulation)*(1-(array)/(len(mappedList)-1))
            #     file.write(f"{round(dimension, 2)},")
            #     for number in mappedList[array]:
            #         file.write("{:.2f},".format(number))
            #     file.write("\n")
            # file.write("\n")
            file.write("r(m)|z(m),")
            for dz in range(round(len(mappedList[0])/self.sizeCoefficient)):
                file.write(f"{round(dz*self.propertiesObject.length/(len(mappedList[0])/self.sizeCoefficient-1), 3)},")
            file.write("\n")

            for array in range(insulationNodes, len(mappedList)):
                dimension = self.propertiesObject.radius*(1-(array-insulationNodes)/(len(mappedList)-1-insulationNodes))
                file.write(f"{round(dimension, 2)},")
                for i in range(round(len(mappedList[array])/self.sizeCoefficient)):
                    file.write("{:.2f},".format(mappedList[array][i]))
                file.write("\n")
            file.write("\n")

    def openFileForHeatStored(self, message):

        with open(f"{self.directory}/{self.model}-heat-stored.csv", "a") as file:
            file.write(f"\n{message},t(h)|Q/m(kJ/kg)\n\n")

    # Izvozimo shranjeno toploto med polnjenjem
    def heatStored(self, temperatureList, temperatureInitial, countTime):

        cpList = []
        for subList in temperatureList:
            fetchedCpList = Node(subList, self.propertiesObject).cpList()
            for i in range(len(fetchedCpList)):
                cpList.append(fetchedCpList[i])
        cp = sum(cpList)/len(cpList)

        tempDifferenceList = []
        for subList in temperatureList:
            for temperature in subList:
                tempDifferenceList.append(temperature - temperatureInitial)
        dT = sum(tempDifferenceList)/len(tempDifferenceList)

        heatPerKilo = cp*dT

        with open(f"{self.directory}/{self.model}-heat-stored.csv", "a") as file:
            file.write("{:.2f},{:.2f}\n".format(countTime/3600, heatPerKilo/1000))

    # Shranjena toplota med hranjenjem
    def heatStoredStoring(self, tempList, tempInitial, insulationNodes, countTime):

        mappedList = self.mappingFile.radiusToLength(tempList)

        cpList = []
        for subList in mappedList:
            fetchedCpList = Node(subList, self.propertiesObject).cpList()
            for i in range(len(fetchedCpList)):
                cpList.append(fetchedCpList[i])
        cp = sum(cpList)/len(cpList)

        tempDifferenceList = []
        for subList in mappedList:
            for temperature in subList:
                tempDifferenceList.append(temperature - tempInitial)
        dT = sum(tempDifferenceList)/len(tempDifferenceList)

        heatPerKilo = cp*dT

        with open(f"{self.directory}/{self.model}-heat-stored.csv", "a") as file:
            file.write("{:.2f},{:.2f}\n".format(countTime/3600, heatPerKilo/1000))

        # tempDifferenceList = []
        # mappedList = mapping.radiusToLength(tempList)

        # for index in range(insulationNodes, len(mappedList)):
        #     for temperature in mappedList[index]:
        #         tempAppend = temperature - tempInitial
        #         tempDifferenceList.append(tempAppend)

        # heatPerKilo = cp*sum(tempDifferenceList)/len(tempDifferenceList)

        # with open(f"{self.fileName}-heat-storing.csv", "a+") as file:
        #     file.write("{:.2f},{:.2f}\n".format(
        #         countTime/3600, heatPerKilo/1000))