def lengthToRadius(oldList):

    # Uses the second half of temperatures, turns the array by 90 degrees to the right
    newList = [oldList[array][:round(len(oldList[0])/2)] for array in range(len(oldList))]
    newList = list(zip(*(newList[::-1])))
    newList = [list(newList[subList]) for subList in range(len(newList))]

    return newList
    

def radiusToLength(oldList):

    # Turns the array by -90 degrees and appends temperatures to calculate fluid T
    newList = list(zip(*oldList))[::-1]
    newList = [list(newList[subList]) for subList in range(len(newList))]

    for array in range(len(newList)):
        for number in range(len(newList[array])):
            newList[array].append(newList[array][number])

    return newList