def lengthToRadius(oldList):

    newList = list(zip(*(oldList[::-1])))
    newList = [list(newList[subList]) for subList in range(len(newList))]

    return newList


def radiusToLength(oldList):

    newList = list(zip(*oldList))[::-1]
    newList = [list(newList[subList]) for subList in range(len(newList))]

    return newList
