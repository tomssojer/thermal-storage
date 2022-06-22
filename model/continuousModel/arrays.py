from importer import *
import initialize as init
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

class ChargingArray:

    def __init__(self, sizeOfMatrixCoeff):
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    def coeffMatrix(self):
        coefficients = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[0]

        wholeArray = len(coefficients)
        halfArray = round(wholeArray/2)

        # Solid - 1. robni pogoj
        coefficients[0][0] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + ks*dt + h*A*dt*dz**2
        coefficients[0][1] = -ks*dt
        coefficients[0][halfArray] = -h*A*dt*dz**2

        # Solid - vmesne enačbe
        for i in range(1, halfArray-1):
            coefficients[i][i-1] = -ks*dt
            coefficients[i][i] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + 2*ks*dt + h*A*dt*dz**2
            coefficients[i][i+1] = -ks*dt
            coefficients[i][halfArray+i] = -h*A*dt*dz**2

        # Solid - 2. robni pogoj
        coefficients[halfArray-1][halfArray-2] = -ks*dt
        coefficients[halfArray-1][halfArray-1] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + ks*dt + h*A*dt*dz**2
        coefficients[halfArray-1][wholeArray-1] = -h*A*dt*dz**2

        # Fluid - 1. robni pogoj
        coefficients[halfArray][0] = -2*h*A*dt*dz**2
        coefficients[halfArray][halfArray] = 2*voidFrac*rhoGas*cGas*dz**2 + 4*kf*dt + 2*h*A*dt*dz**2
        coefficients[halfArray][halfArray+1] = +voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt # -

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            coefficients[i][i-halfArray] = -2*h*A*dt*dz**2
            coefficients[i][i-1] = -voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt # +
            coefficients[i][i] = 2*voidFrac*rhoGas*cGas*dz**2 + 4*kf*dt + 2*h*A*dt*dz**2
            coefficients[i][i+1] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt # -

        # Fluid - 2. robni pogoj
        coefficients[wholeArray-1][halfArray-1] = -h*A*dt*dz**2
        coefficients[wholeArray-1][wholeArray-2] = -voidFrac*rhoGas*cGas*flowVelocity*dt*dz - kf*dt # +
        coefficients[wholeArray-1][wholeArray-1] = voidFrac*rhoGas*cGas*dz**2 + voidFrac*rhoGas*cGas*flowVelocity*dt*dz + kf*dt + h*A*dt*dz**2 # -

        return coefficients

    def constArray(self, temperatureList):
        constants = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[1]

        wholeArray = len(constants)
        halfArray = round(wholeArray/2)

        # Solid - vmesne enačbe in oba robna pogoja
        for i in range(0, halfArray):
            constants[i] = (1-voidFrac)*rhoStorage*cStorage*dz**2*temperatureList[i]

        # Fluid - 1. robni pogoj
        constants[halfArray] = (voidFrac*rhoGas*cGas*flowVelocity*dt*dz + 2*kf*dt)*Tfluid + 2*voidFrac*rhoGas*cGas*dz**2*temperatureList[halfArray] # -

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            constants[i] = 2*voidFrac*rhoGas*cGas*dz**2*temperatureList[i]

        # Fluid - 2. robni pogoj
        constants[wholeArray-1] = voidFrac*rhoGas*cGas*dz**2*temperatureList[wholeArray-1]

        return constants


class StoringArray():

    def __init__(self, sizeOfMatrixCoeff = 1):
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    def coeffMatrix(self):
        coefficients = init.prepareStoring(rNodes, rNodesIns)[0]

        # Coefficients at the inner boundary
        coefficients[0][0] = 4*k*dtStore + thermalMass*(dr**2)
        coefficients[0][1] = -4*k*dtStore

        # Coefficients in the storage
        for j in range(1, rNodes - 1):
            coefficients[j][j-1] = -k*dtStore - 2*k*dtStore*j
            coefficients[j][j] = 4*k*dtStore*j + 2*thermalMass*(dr**2)*j
            coefficients[j][j+1] = k*dtStore - 2*k*dtStore*j

        if drIns > 0:
            # Coefficients at the storage/insulation boundary
            # K = (rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns
            K = thermalMass*(rNodes-1)*2
            K1 = 2*(rNodes - 1)
            kBoth = k*kIns/(k+kIns)
            coefficients[rNodes-1][rNodes-2] = (-1 - K1)*kBoth*dtStore
            coefficients[rNodes-1][rNodes-1] = kBoth*dtStore - kBoth*dtStore + K1*dtStore*kBoth + K1*dtStore*kBoth + K*(dr**2)
            coefficients[rNodes-1][rNodes] = (1 - K1)*kBoth*dtStore

            # Coefficients in the insulation
            for j in range(rNodes, rNodes + rNodesIns - 1):
                coefficients[j][j-1] = -kIns*dtStore - 2*kIns*dtStore*j
                coefficients[j][j] = 4*kIns*dtStore*j + 2*rhoIns*cIns*(drIns**2)*j
                coefficients[j][j+1] = kIns*dtStore - 2*kIns*dtStore*j

            # Coefficients at the outer boundary
            K2 = rNodes+rNodesIns-1
            K3 = 2*hAmbient*drIns*dtStore
            coefficients[-1][-2] = -2*kIns*dtStore*K2
            coefficients[-1][-1] = K3 + 2*kIns*dtStore*K2 + K3*K2 + rhoIns*cIns*(drIns**2)*K2

        elif drIns == 0:
            K2 = rNodes-1
            K3 = 2*hAmbient*dr*dtStore
            coefficients[-1][-2] = -2*k*dtStore*K2
            coefficients[-1][-1] = K3 + 2*k*dtStore*K2 + K3*K2 + thermalMass*(dr**2)*K2

        return coefficients

    def constArray(self, previousTemperatures):
        constants = init.prepareStoring(rNodes, rNodesIns)[1]

        # Constant at the inner boundary
        constants[0] = thermalMass*(dr**2)*previousTemperatures[0]

        # Constants in the storage
        for j in range(1, rNodes - 1):
            constants[j] = 2*thermalMass*(dr**2)*j*previousTemperatures[j]

        if drIns > 0:
            # Constants at the storage/insulation boundary
            # K = (rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns
            K = thermalMass*(rNodes-1)*2
            constants[rNodes-1] = K*(dr**2)*previousTemperatures[rNodes-1]

            # Constants in the insulation
            for j in range(rNodes, rNodes + rNodesIns - 1):
                constants[j] = 2*rhoIns*cIns*(drIns**2)*j*previousTemperatures[j]

            # Constants at the outer boundary
            K = 2*hAmbient*drIns*dtStore
            K1 = rNodes+rNodesIns-1
            constants[-1] = (K*K1 + K)*Tambient + rhoIns*cIns*(drIns**2)*K1*previousTemperatures[-1]

        elif drIns == 0:
            K = 2*hAmbient*dr*dtStore
            K1 = rNodes-1
            constants[-1] = (K*K1 + K)*Tambient + thermalMass*(dr**2)*K1*previousTemperatures[-1]

        return constants


class DischargingArray:

    def __init__(self, sizeOfMatrixCoeff):
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    def coeffMatrix(self):
        coefficients = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[0]

        wholeArray = len(coefficients)
        halfArray = round(wholeArray/2)

        # Solid - 1. robni pogoj
        coefficients[0][0] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + ks*dt - h*A*dt*dz**2
        coefficients[0][1] = -ks*dt
        coefficients[0][halfArray] = h*A*dt*dz**2

        # Solid - vmesne enačbe
        for i in range(1, halfArray-1):
            coefficients[i][i-1] = -ks*dt
            coefficients[i][i] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + 2*ks*dt - h*A*dt*dz**2
            coefficients[i][i+1] = -ks*dt
            coefficients[i][halfArray+i] = h*A*dt*dz**2

        # Solid - 2. robni pogoj
        coefficients[halfArray-1][halfArray-2] = -ks*dt
        coefficients[halfArray-1][halfArray-1] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + ks*dt - h*A*dt*dz**2
        coefficients[halfArray-1][wholeArray-1] = h*A*dt*dz**2

        # Fluid - 1. robni pogoj
        coefficients[halfArray][0] = 2*h*A*dt*dz**2
        coefficients[halfArray][halfArray] = 2*voidFrac*rhoGas*cGas*dz**2 + 4*kf*dt - 2*h*A*dt*dz**2
        coefficients[halfArray][halfArray+1] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            coefficients[i][i-halfArray] = 2*h*A*dt*dz**2
            coefficients[i][i-1] = -voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt
            coefficients[i][i] = 2*voidFrac*rhoGas*cGas*dz**2 + 4*kf*dt - 2*h*A*dt*dz**2
            coefficients[i][i+1] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt

        # Fluid - 2. robni pogoj
        coefficients[wholeArray-1][halfArray-1] = h*A*dt*dz**2
        coefficients[wholeArray-1][wholeArray-2] = -voidFrac*rhoGas*cGas*flowVelocity*dt*dz - kf*dt
        coefficients[wholeArray-1][wholeArray-1] = voidFrac*rhoGas*cGas*dz**2 + voidFrac*rhoGas*cGas*flowVelocity*dt*dz + kf*dt - h*A*dt*dz**2

        return coefficients

    def constArray(self, temperatureList):
        constants = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[1]

        wholeArray = len(constants)
        halfArray = round(wholeArray/2)

        # Solid - vmesne enačbe in oba robna pogoja
        for i in range(0, halfArray):
            constants[i] = (1-voidFrac)*rhoStorage*cStorage*dz**2*temperatureList[i]

        # Fluid - 1. robni pogoj
        constants[halfArray] = (voidFrac*rhoGas*cGas*flowVelocity*dt*dz + 2*kf*dt)*Tambient + 2*voidFrac*rhoGas*cGas*dz**2*temperatureList[halfArray]

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            constants[i] = 2*voidFrac*rhoGas*cGas*dz**2*temperatureList[i]

        # Fluid - 2. robni pogoj
        constants[wholeArray-1] = voidFrac*rhoGas*cGas*dz**2*temperatureList[wholeArray-1]

        return constants
