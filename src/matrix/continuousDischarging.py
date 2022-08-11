import sys
sys.path.append('..')
from getData import Node
import modules.initialize as init

class GetArrays:

    def __init__(self, subList, sizeOfMatrixCoeff):
        self.subList = subList
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    def coeffMatrix(self, props):
        coefficients = init.prepareCharging(props.zNodes, self.sizeOfMatrixCoeff)[0]
        kSolid = Node(self.subList, props).kContinuousSolidList()
        kFluid = Node(self.subList, props).kContinuousFluidList()
        rhoStorage = Node(self.subList, props).rhoStorageList()
        cStorage = Node(self.subList, props).cStorageList()
        rhoGas = Node(self.subList, props).rhoGasList()
        cGas = Node(self.subList, props).cGasList()
        A = 6*(1 - props.voidFrac)/props.materialDiameter

        wholeArray = len(coefficients)
        halfArray = round(wholeArray/2)

        # Solid - 1. robni pogoj
        coefficients[0][0] = (1-props.voidFrac)*rhoStorage[0]*cStorage[0]*props.dz**2 + 2*kSolid[0]*kSolid[1]/(kSolid[0]+kSolid[1])*props.dt - props.h*A*props.dt*props.dz**2
        coefficients[0][1] = -2*kSolid[0]*kSolid[1]/(kSolid[0]+kSolid[1])*props.dt
        coefficients[0][halfArray] = props.h*A*props.dt*props.dz**2

        # Solid - vmesne enačbe
        for i in range(1, halfArray-1):
            coefficients[i][i-1] = -2*kSolid[i-1]*kSolid[i]/(kSolid[i-1]+kSolid[i])*props.dt
            coefficients[i][i] = (1-props.voidFrac)*rhoStorage[i]*cStorage[i]*props.dz**2 + 2*(kSolid[i-1]*kSolid[i]/(kSolid[i-1]+kSolid[i]) + kSolid[i+1]*kSolid[i]/(kSolid[i+1]+kSolid[i]))*props.dt - props.h*A*props.dt*props.dz**2
            coefficients[i][i+1] = -2*kSolid[i+1]*kSolid[i]/(kSolid[i+1]+kSolid[i])*props.dt
            coefficients[i][halfArray+i] = props.h*A*props.dt*props.dz**2

        # Solid - 2. robni pogoj
        coefficients[halfArray-1][halfArray-2] = -2*kSolid[halfArray-2]*kSolid[halfArray-1]/(kSolid[halfArray-2]+kSolid[halfArray-1])*props.dt
        coefficients[halfArray-1][halfArray-1] = (1-props.voidFrac)*rhoStorage[halfArray-1]*cStorage[halfArray-1]*props.dz**2 + 2*kSolid[halfArray-2]*kSolid[halfArray-1]/(kSolid[halfArray-2]+kSolid[halfArray-1])*props.dt - props.h*A*props.dt*props.dz**2
        coefficients[halfArray-1][wholeArray-1] = props.h*A*props.dt*props.dz**2

        # Fluid - 1. robni pogoj
        coefficients[halfArray][0] = 2*props.h*A*props.dt*props.dz**2
        coefficients[halfArray][halfArray] = 2*props.voidFrac*rhoGas[halfArray]*cGas[halfArray]*props.dz**2 + 4*(kFluid[halfArray]/2 + kFluid[halfArray]*kFluid[halfArray+1]/(kFluid[halfArray]+kFluid[halfArray+1]))*props.dt - 2*props.h*A*props.dt*props.dz**2
        coefficients[halfArray][halfArray+1] = -props.voidFrac*rhoGas[halfArray+1]*cGas[halfArray+1]*props.flowVelocity*props.dt*props.dz - 4*kFluid[halfArray]*kFluid[halfArray+1]/(kFluid[halfArray]+kFluid[halfArray+1])*props.dt

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            coefficients[i][i-halfArray] = 2*props.h*A*props.dt*props.dz**2
            coefficients[i][i-1] = props.voidFrac*rhoGas[i-1]*cGas[i-1]*props.flowVelocity*props.dt*props.dz - 4*kFluid[i]*kFluid[i-1]/(kFluid[i]+kFluid[i-1])*props.dt
            coefficients[i][i] = 2*props.voidFrac*rhoGas[i]*cGas[i]*props.dz**2 + 4*(kFluid[i]*kFluid[i-1]/(kFluid[i]+kFluid[i-1]) + kFluid[i]*kFluid[i+1]/(kFluid[i]+kFluid[i+1]))*props.dt - 2*props.h*A*props.dt*props.dz**2
            coefficients[i][i+1] = -props.voidFrac*rhoGas[i+1]*cGas[i+1]*props.flowVelocity*props.dt*props.dz - 4*kFluid[i]*kFluid[i+1]/(kFluid[i]+kFluid[i+1])*props.dt

        # Fluid - 2. robni pogoj
        coefficients[wholeArray-1][halfArray-1] = props.h*A*props.dt*props.dz**2
        coefficients[wholeArray-1][wholeArray-2] = props.voidFrac*rhoGas[wholeArray-2]*cGas[wholeArray-2]*props.flowVelocity*props.dt*props.dz - 2*kFluid[wholeArray-2]*kFluid[wholeArray-1]/(kFluid[wholeArray-2]+kFluid[wholeArray-1])*props.dt
        coefficients[wholeArray-1][wholeArray-1] = props.voidFrac*rhoGas[wholeArray-1]*cGas[wholeArray-1]*props.dz**2 - props.voidFrac*rhoGas[wholeArray-1]*cGas[wholeArray-1]*props.flowVelocity*props.dt*props.dz + 2*kFluid[wholeArray-2]*kFluid[wholeArray-1]/(kFluid[wholeArray-2]+kFluid[wholeArray-1])*props.dt - props.h*A*props.dt*props.dz**2

        return coefficients

    def constArray(self, props, temperatureList):
        constants = init.prepareCharging(props.zNodes, self.sizeOfMatrixCoeff)[1]
        kFluid = Node(self.subList, props).kContinuousFluidList()
        rhoStorage = Node(self.subList, props).rhoStorageList()
        cStorage = Node(self.subList, props).cStorageList()
        rhoGas = Node(self.subList, props).rhoGasList()
        cGas = Node(self.subList, props).cGasList()

        wholeArray = len(constants)
        halfArray = round(wholeArray/2)

        # Solid - vmesne enačbe in oba robna pogoja
        for i in range(0, halfArray):
            constants[i] = (1-props.voidFrac)*rhoStorage[i]*cStorage[i]*props.dz**2*temperatureList[i]

        # Fluid - 1. robni pogoj
        constants[halfArray] = (-props.voidFrac*rhoGas[halfArray]*cGas[halfArray]*props.flowVelocity*props.dt*props.dz + 2*kFluid[halfArray]*props.dt)*props.Tambient + 2*props.voidFrac*rhoGas[halfArray]*cGas[halfArray]*props.dz**2*temperatureList[halfArray]

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            constants[i] = 2*props.voidFrac*rhoGas[i]*cGas[i]*props.dz**2*temperatureList[i]

        # Fluid - 2. robni pogoj
        constants[wholeArray-1] = props.voidFrac*rhoGas[wholeArray-1]*cGas[wholeArray-1]*props.dz**2*temperatureList[wholeArray-1]

        return constants