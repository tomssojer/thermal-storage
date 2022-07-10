import sys
sys.path.append('..')
from getData import Node
import modules.initialize as init

class GetArrays:

    def __init__(self, subList, sizeOfMatrixCoeff=1):
        self.subList = subList
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    # Matrix of coefficients
    def coeffMatrix(self, props):
        coefficients = init.prepareCharging(props.zNodes, self.sizeOfMatrixCoeff)[0]
        k = Node(self.subList, props).kList()
        thermalMass = Node(self.subList, props).thermalMassList()
        cGas = Node(self.subList, props).cGasList()

        # Coefficients at the boundaries
        coefficients[0][0] = 2*k[0]*props.dt + 2*props.h*props.dz*props.dt + thermalMass[0]*(props.dz**2)
        coefficients[0][1] = -2*k[1]*props.dt + props.G*cGas[1]*props.dz*props.dt
        coefficients[-1][-2] = -2*k[-2]*props.dt - props.G*cGas[-2]*props.dz*props.dt
        coefficients[-1][-1] = 2*k[-1]*props.dt + thermalMass[-1]*(props.dz**2) + props.G*cGas[-1]*props.dz*props.dt

        # Coefficients in the storage
        for i in range(1, len(coefficients) - 1):
            coefficients[i][i-1] = -2*k[i-1]*props.dt - props.G*cGas[i-1]*props.dz*props.dt
            coefficients[i][i] = 4*k[i]*props.dt + 2*thermalMass[i]*(props.dz**2)
            coefficients[i][i+1] = -2*k[i+1]*props.dt + props.G*cGas[i+1]*props.dz*props.dt

        return coefficients

    # Array of constants
    def constArray(self, props, previousTemperatures):
        constants = init.prepareCharging(props.zNodes, self.sizeOfMatrixCoeff)[1]
        thermalMass = Node(self.subList, props).thermalMassList()
        cGas = Node(self.subList, props).cGasList()

        # Constants at the boundaries
        constants[0] = thermalMass[0]*(props.dz**2)*previousTemperatures[0] + (2*props.h*props.dz*props.dt + props.G*cGas[0]*props.dz*props.dt)*props.Tfluid
        constants[-1] = thermalMass[-1]*(props.dz**2)*previousTemperatures[-1]

        for i in range(1, len(constants) - 1):
            constants[i] = 2*thermalMass[i]*(props.dz**2)*previousTemperatures[i]

        return constants