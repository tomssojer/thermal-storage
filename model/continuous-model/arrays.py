import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from properties import *

class ChargingArray:

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    def coeffMatrix(self):

        arrLength = len(self.coefficients)
        halfLength = int(arrLength/2)

        self.coefficients[0][0] = voidFrac*rhoGas*cGas*2*dz**2 + 4*kf*dt + h*A*2*dt*dz**2
        self.coefficients[0][1] = voidFrac*rhoGas*cGas*flowVelocity*dt*dz - kf*2*dt
        self.coefficients[0][halfLength] = -h*A*2*dt*dz**2

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

        self.constants[0] = voidFrac*rhoGas*cGas*flowVelocity/(2*dz)*Tfluid + voidFrac*rhoGas*cGas/dt*previousTempList[0]

        for i in range(1, halfLength):
            self.constants[i] = voidFrac*rhoGas*cGas/dt*previousTempList[i]

        for i in range(halfLength, arrLength):
            self.constants[i] = (1 - voidFrac)*rhoGas*cGas/dt*previousTempList[i]

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
