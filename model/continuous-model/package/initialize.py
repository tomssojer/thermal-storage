def prepareCharging(zNodes):

    # Matrix of coefficients
    coefficients = [[0 for zTemp in range((zNodes-1)*2)] for zTemp in range((zNodes-1)*2)]

    # Matrix of constants
    constants = [0 for zTemp in range((zNodes-1)*2)]

    return coefficients, constants


def prepareStoring(rNodes, insulationNodes):

    numOfNodes = rNodes + insulationNodes

    # Matrix of coefficients for the storing process
    coefficients = [[0 for rTemp in range(
        numOfNodes)] for rTemp in range(numOfNodes)]
    # Array of constants for the storing process
    constants = [0 for rTemp in range(numOfNodes)]

    return coefficients, constants


def temperatures(zNodes, rNodes, temperature):

    # An array of all initial temperatures in the storage
    initTemperatures = [
        [temperature for zTemp in range((zNodes-1)*2)] for rTemp in range(rNodes)]
    print(initTemperatures)

    return initTemperatures


def makeInsulation(innerTemperatures, temperature, insNodes):

    allTemperatures = list(innerTemperatures)
    # Appends insulation temperatures to arrays
    for subList in allTemperatures:
        for insulationNode in range(insNodes):
            subList.append(temperature)

    return allTemperatures


def delInsulation(allTemperatures, insNodes):

    innerTemperatures = list(allTemperatures)
    # Deletes insulation temperatures from arrays
    for subList in innerTemperatures:
        for insulationNode in range(insNodes):
            subList.pop(-1)

    return innerTemperatures
