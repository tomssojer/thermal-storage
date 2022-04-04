import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from properties import *

#####--------------- class ChargingArray -----------------#####
###
##### Arrays used to calculate the charging process 

class ChargingArray():

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants


    def coeffMatrix(self):
        # Coefficients at the boundaries
        self.coefficients[0][0] = h/dz + k/dz**2 + thermalMass / \
            (2*dt) + G*cGas/dz  # Zadnji člen negativen
        self.coefficients[0][1] = -k/dz**2 - G*cGas/dz  # Zadnji člen pozitiven
        self.coefficients[-1][-2] = -k/dz**2 - G*cGas/dz
        self.coefficients[-1][-1] = k/dz**2 + thermalMass/(2*dt) + G*cGas/dz

        # Coefficients in the storage
        for i in range(1, len(self.coefficients) - 1):
            self.coefficients[i][i-1] = -k/dz**2 - G*cGas/(2*dz)
            self.coefficients[i][i] = 2*k/dz**2 + thermalMass/dt
            self.coefficients[i][i+1] = -k/dz**2 + G*cGas/(2*dz)

        return self.coefficients


    def constArray(self, previousTemperatures):
        # Constants at the boundaries
        self.constants[0] = thermalMass/(2*dt)*previousTemperatures[0] + h/dz*Tfluid
        self.constants[-1] = thermalMass/(2*dt)*previousTemperatures[-1]

        # Constants in the storage
        for i in range(1, len(self.constants) - 1):
            self.constants[i] = thermalMass/dt*previousTemperatures[i]

        return self.constants

#####--------------- class ChargingArray -----------------#####
###
#####--------------- class StoringArray -----------------#####
###
##### Arrays used to calculate the storing process

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
        K = ((rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns)/(2*(rNodes - 1)*dt)
        Khr = k/(2*dr**2*(rNodes - 1)) + k/dr**2
        Kins = kIns/(2*drIns**2*(rNodesIns - 1)) + kIns/drIns**2
        self.coefficients[rNodes-1][rNodes-2] = -Khr
        self.coefficients[rNodes-1][rNodes-1] = Kins - k/(2*dr**2*(rNodes - 1)) + k/dr**2 - K
        self.coefficients[rNodes-1][rNodes] = -Kins

        # Coefficients in the insulation
        for j in range(rNodes, rNodes + rNodesIns - 1):
            self.coefficients[j][j-1] = (1/(2*j) - 1)*kIns/drIns**2
            self.coefficients[j][j] = 2*kIns/drIns**2 + rhoIns*cIns/dt
            self.coefficients[j][j+1] = -(1/(2*j) - 1)*kIns/drIns**2

        # Coefficients at the outer boundary
        Kambient = ambienth/(drIns*(rNodes+rNodesIns-1)) + ambienth/drIns
        self.coefficients[-1][-2] = -kIns/drIns**2
        self.coefficients[-1][-1] = Kambient + kIns/drIns**2 + rhoIns*cIns/(2*dt)

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
        Kambient = (ambienth/(drIns*(rNodes+rNodesIns-1)) + ambienth/drIns)*ambientTemp
        self.constants[-1] = rhoIns*cIns/(2*dt)*previousTemperatures[-1] + Kambient

        return self.constants

#####--------------- class StoringArray -----------------#####

#####--------------- class DischargingArray -----------------#####


class DischargingArray():

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    def coeffMatrix(self):
        # Coefficients at the boundaries
        self.coefficients[0][0] = -k/dz**2 - G*cGas/dz
        self.coefficients[0][1] = k/dz**2 + thermalMass/(2*dt) + G*cGas/dz
        self.coefficients[-1][-2] = h/dz + k/dz**2 + thermalMass / \
            (2*dt) + G*cGas/dz
        self.coefficients[-1][-1] = -k/dz**2 - G*cGas/dz

        # Coefficients in the storage
        for i in range(1, len(self.coefficients) - 1):
            self.coefficients[i][i-1] = -k/dz**2 - G*cGas/(2*dz)
            self.coefficients[i][i] = 2*k/dz**2 + thermalMass/dt
            self.coefficients[i][i+1] = -k/dz**2 + G*cGas/(2*dz)

        return self.coefficients

    def constArray(self, previousTemperatures):
        # Constants at the boundaries
        self.constants[0] = thermalMass/(2*dt)*previousTemperatures[0]
        self.constants[-1] = thermalMass / \
            (2*dt)*previousTemperatures[-1] + h/dz*Tfluid

        # Constants in the storage
        for i in range(1, len(self.constants) - 1):
            self.constants[i] = thermalMass/dt*previousTemperatures[i]

        return self.constants
