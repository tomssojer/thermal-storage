import os
import sys
import inspect

from numpy import void

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from importer import *

class ChargingArray:

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    def coeffMatrix(self):

        wholeArray = 2*len(self.coefficients)
        halfArray = len(self.coefficients)

        # Solid - 1. robni pogoj
        self.coefficients[0][0] = (1-voidFrac)*rhoStorage*cStorage*dz** + ks*dt + h*A*dt*dz**2
        self.coefficients[0][1] = -ks*dt
        self.coefficients[0][halfArray] = -2*h*A*dt*dz**2

        # Solid - vmesne enačbe
        for i in range(1, halfArray-1):
            self.coefficients[i][i-1] = -ks*dt
            self.coefficients[i][i] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + 2*ks*dt + h*A*dt*dz**2
            self.coefficients[i][i+1] = -ks*dt
            self.coefficients[i][halfArray+1] = h*A*dt*dz**2

        # Solid - 2. robni pogoj
        self.coefficients[halfArray-1][halfArray-2] = -ks*dt
        self.coefficients[halfArray-1][halfArray-1] = (1-voidFrac)*rhoStorage*cStorage*dz**2 + 2*ks*dt + h*A*dt*dz**2
        self.coefficients[halfArray-1][halfArray] = -ks*dt
        self.coefficients[halfArray-1][0] = -h*A*dt*dz**2

        # Fluid - 1. robni pogoj
        self.coefficients[halfArray][0] = 2*h*A*dt*dz**2
        self.coefficients[halfArray][halfArray] = 2*voidFrac*rhoGas*cGas*dz**2 + 4*kf*dt + 2*h*A*dt*dz**2
        self.coefficients[halfArray][halfArray+1] = -voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            self.coefficients[i][i-halfArray+1] = -2*h*A*dt*dz**2
            self.coefficients[i][i-1] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt
            self.coefficients[i][i] = 2*voidFrac*rhoGas*cGas*dz**2 + 4*kf*dt + 2*h*A*dt*dz**2
            self.coefficients[i][i+1] = -voidFrac*rhoGas*cGas*flowVelocity*dt*dz - 2*kf*dt

        # Fluid - 2. robni pogoj
        self.coefficients[wholeArray-1][halfArray-1] = -h*A*dt*dz**2
        self.coefficients[wholeArray-1][wholeArray-2] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz - kf*dt
        self.coefficients[wholeArray-1][wholeArray-1] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz + kf*dt + h*A*dt*dz**2

        return self.coefficients

    def constArray(self, solidPreviousTempList, fluidPreviousTempList):

        wholeArray = 2*len(self.coefficients)
        halfArray = len(self.coefficients)

        # Solid - 1. robni pogoj
        self.constants[0] = (1-voidFrac)*rhoStorage*cStorage*dz**2*solidPreviousTempList[0]

        # Solid - vmesne enačbe
        for i in range(1, halfArray-1):
            self.constants[i] = (1-voidFrac)*rhoStorage*cStorage*dz**2*solidPreviousTempList[i]

        # Solid - 2. robni pogoj
        self.constants[halfArray-1] = (1-voidFrac)*rhoStorage*cStorage*dz**2*solidPreviousTempList[halfArray-1]

        # Fluid - 1. robni pogoj
        self.constants[halfArray] = (-voidFrac*rhoGas*cGas*flowVelocity*dt*dz+2*kf*dt)*Tfluid + 2*voidFrac*rhoGas*cGas*dz**2*fluidPreviousTempList[0]

        # Fluid - vmesne enačbe
        for i in range(halfArray+1, wholeArray-1):
            self.constants[i] = 2*voidFrac*rhoGas*cGas*dz**2*fluidPreviousTempList[i]

        # Fluid - 2. robni pogoj
        self.constants[wholeArray-1] = voidFrac*rhoGas*cGas*dz**2*fluidPreviousTempList[wholeArray-1]

        return self.constants


class StoringArray():

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    def coeffMatrix(self):
        # Coefficients at the inner boundary
        self.coefficients[0][0] = 4*k/dr**2 + thermalMass/dt
        self.coefficients[0][1] = -4*k/dr**2

        # Coefficients in the storage
        for j in range(1, rNodes - 1):
            self.coefficients[j][j-1] = (1/(2*j) - 1)*k/dr**2
            self.coefficients[j][j] = 2*k/dr**2 + thermalMass/dt
            self.coefficients[j][j+1] = -(1/(2*j) - 1)*k/dr**2

        # Coefficients at the storage/insulation boundary
        # Lets define coefficients so the lines won't be too long
        K = ((rNodes - 3/2)*thermalMass + (rNodes - 1/2)
            * rhoIns*cIns)/(2*(rNodes - 1)*dt)
        Khr = k/(2*dr**2*(rNodes - 1)) + k/dr**2
        Kins = kIns/(2*drIns**2*(rNodesIns - 1)) + kIns/drIns**2
        self.coefficients[rNodes-1][rNodes-2] = -Khr
        self.coefficients[rNodes-1][rNodes-1] = Kins - \
            k/(2*dr**2*(rNodes - 1)) + k/dr**2 - K
        self.coefficients[rNodes-1][rNodes] = -Kins

        # Coefficients in the insulation
        for j in range(rNodes, rNodes + rNodesIns - 1):
            self.coefficients[j][j-1] = (1/(2*j) - 1)*kIns/drIns**2
            self.coefficients[j][j] = 2*kIns/drIns**2 + rhoIns*cIns/dt
            self.coefficients[j][j+1] = -(1/(2*j) - 1)*kIns/drIns**2

        # Coefficients at the outer boundary
        Kambient = ambienth/(drIns*(rNodes+rNodesIns-1)) + ambienth/drIns
        self.coefficients[-1][-2] = -kIns/drIns**2
        self.coefficients[-1][-1] = Kambient + \
            kIns/drIns**2 + rhoIns*cIns/(2*dt)

        return self.coefficients

    def constArray(self, previousTemperatures):
        # Constant at the inner boundary
        self.constants[0] = thermalMass/dt*previousTemperatures[0]

        # Constants in the storage
        for j in range(1, rNodes - 1):
            self.constants[j] = thermalMass/dt*previousTemperatures[j]

        # Constants at the storage/insulation boundary
        K = ((rNodes - 3/2)*thermalMass + (rNodes - 1/2)
            * rhoIns*cIns)/(2*(rNodes - 1)*dt)
        self.constants[rNodes-1] = K*previousTemperatures[rNodes-1]

        # Constants in the insulation
        for j in range(rNodes, rNodes + rNodesIns - 1):
            self.constants[j] = thermalMass/dr*previousTemperatures[j]

        # Constants at the outer boundary
        Kambient = (ambienth/(drIns*(rNodes+rNodesIns-1)) +
                    ambienth/drIns)*ambientTemp
        self.constants[-1] = rhoIns*cIns / \
            (2*dt)*previousTemperatures[-1] + Kambient

        return self.constants


class DischargingArray:

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    def coeffMatrix(self):

        arrLength = len(self.coefficients)
        halfLength = int(arrLength/2)

        self.coefficients[0][0] = voidFrac*rhoGas*cGas/dt + h*A
        self.coefficients[0][1] = voidFrac*rhoGas*cGas*flowVelocity/(2*dz)
        self.coefficients[0][halfLength] = -h*A

        for i in range(1, halfLength-1):
            self.coefficients[i][i-1] = -voidFrac*rhoGas*cGas*flowVelocity/(2*dz)
            self.coefficients[i][i] = voidFrac*rhoGas*cGas/dt + h*A
            self.coefficients[i][i+1] = voidFrac*rhoGas*cGas*flowVelocity/(2*dz)
            self.coefficients[i][halfLength+i] = -h*A

        self.coefficients[halfLength-1][halfLength-2] = - voidFrac*rhoGas*cGas*flowVelocity/dz
        self.coefficients[halfLength-1][halfLength-1] = voidFrac*rhoGas*cGas/dt + voidFrac*rhoGas*cGas*flowVelocity/dz + h*A
        self.coefficients[halfLength-1][arrLength-1] = -h*A

        for i in range(halfLength, arrLength):
            self.coefficients[i][i] = (1-voidFrac)*rhoGas*cGas/dt + h*A
        for i in range(1, halfLength+1):
            self.coefficients[halfLength-1+i][i-1] = -h*A

        return self.coefficients

    def constArray(self, previousTempList):

        arrLength = len(self.coefficients)
        halfLength = int(arrLength/2)

        self.constants[2] = voidFrac*rhoGas*cGas*flowVelocity/(2*dz)*Tfluid + voidFrac*rhoGas*cGas/dt*previousTempList[1]

        for i in range(1, halfLength):
            self.constants[i] = voidFrac*rhoGas*cGas/dt*previousTempList[i]

        for i in range(halfLength, arrLength):
            self.constants[i] = (1 - voidFrac)*rhoGas*cGas/dt*previousTempList[i]

        return self.constants

# coefficients = [[0 for i in range(10)] for i in range(10)]
# constants = [0 for i in range(10)]
# from pandas import DataFrame
# a = ChargingArray(coefficients, constants).coeffMatrix()
# print(DataFrame(a))
