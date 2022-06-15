def prepareCharging(zNodes, sizeCoefficient = 1):

    # Matrix of coefficients
    coefficients = [[0 for _ in range((zNodes)*sizeCoefficient)] for _ in range((zNodes)*sizeCoefficient)]
    # Matrix of constants
    constants = [0 for _ in range((zNodes))*sizeCoefficient]

    return coefficients, constants



def prepareStoring(rNodes, insulationNodes):

    numOfNodes = rNodes + insulationNodes

    # Matrix of coefficients for the storing process
    coefficients = [[0 for _ in range(
        numOfNodes)] for _ in range(numOfNodes)]
    # Array of constants for the storing process
    constants = [0 for _ in range(numOfNodes)]

    return coefficients, constants


def temperatures(zNodes, rNodes, temperature, sizeCoefficient = 1):

    # An array of all initial temperatures in the storage
    initTemperatures = [[temperature for _ in range(zNodes)*sizeCoefficient] for _ in range(rNodes)]

    return initTemperatures


def makeInsulation(innerTemperatures, temperature, insNodes):

    allTemperatures = list(innerTemperatures)
    # Appends insulation temperatures to arrays
    for subList in allTemperatures:
        for _ in range(insNodes):
            subList.append(temperature)

    return allTemperatures


def delInsulation(allTemperatures, insNodes):

    innerTemperatures = list(allTemperatures)
    # Deletes insulation temperatures from arrays
    for subList in innerTemperatures:
        for _ in range(insNodes):
            subList.pop(-1)

    return innerTemperatures
