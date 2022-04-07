import os
import sys
import inspect
from properties import *

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Arrays to calculate the charging process 
class ChargingArray():

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants


    def coeffMatrix(self):
        # Coefficients at the boundaries
        self.coefficients[0][0] = 2*k*dt + 2*h*dz*dt + thermalMass*(dz**2) - 2*G*cGas*dz*dt
        self.coefficients[0][1] = -2*k*dt + 2*G*cGas*dz*dt
        self.coefficients[-1][-2] = -2*k*dt - 2*G*cGas*dz*dt
        self.coefficients[-1][-1] = 2*k*dt + thermalMass*(dz**2) + 2*G*cGas*dz*dt

        # Coefficients in the storage
        for i in range(1, len(self.coefficients) - 1):
            self.coefficients[i][i-1] = -2*k*dt - G*cGas*dz*dt
            self.coefficients[i][i] = 4*k*dt + 2*thermalMass*(dz**2)
            self.coefficients[i][i+1] = -2*k*dt + G*cGas*dz*dt

        return self.coefficients


    def constArray(self, previousTemperatures):
        # Constants at the boundaries
        self.constants[0] = thermalMass*(dz**2)*previousTemperatures[0] + 2*h*dz*dt*Tfluid
        self.constants[-1] = thermalMass*(dz**2)*previousTemperatures[-1]

        for i in range(1, len(self.constants) - 1):
            self.constants[i] = 2*thermalMass*(dz**2)*previousTemperatures[i]

        return self.constants


# Arrays to calculate the storing process
class StoringArray():

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants


    def coeffMatrix(self):
        # Coefficients at the inner boundary
        self.coefficients[0][0] = 4*k*dt + thermalMass*(dr**2)
        self.coefficients[0][1] = -4*k*dt

        # Coefficients in the storage
        for j in range(1, rNodes - 1):
            self.coefficients[j][j-1] = k*dt - 2*k*dt*j
            self.coefficients[j][j] = 4*k*dt*j + 2*thermalMass*(dr**2)*j
            self.coefficients[j][j+1] = k*dt + 2*k*dt*j

        # Coefficients at the storage/insulation boundary
        # Lets define coefficients so the lines won't be too long
        K = (rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns
        K1 = kIns*dt - k*dt + 2*(rNodes - 1)*dt*kIns + 2*(rNodes - 1)*dt*k + K*(dr**2)
        self.coefficients[rNodes-1][rNodes-2] = (1 - 2*(rNodes - 1))*k*dt
        self.coefficients[rNodes-1][rNodes-1] = K1
        self.coefficients[rNodes-1][rNodes] = (-1 - 2*(rNodes - 1))*kIns*dt

        # Coefficients in the insulation
        for j in range(rNodes, rNodes + rNodesIns - 1):
            self.coefficients[j][j-1] = kIns*dt - 2*kIns*dt*j
            self.coefficients[j][j] = 4*kIns*dt*j + 2*thermalMass*(drIns**2)*j
            self.coefficients[j][j+1] = kIns*dt + 2*kIns*dt*j

        # Coefficients at the outer boundary
        K2 = 2*ambienth*drIns*dt*(rNodes+rNodesIns-1)
        K3 = 2*kIns*dt*(rNodes+rNodesIns-1)
        self.coefficients[-1][-2] = -K3
        self.coefficients[-1][-1] = 2*ambienth*drIns*dt + K2 + K3 + rhoIns*cIns*(drIns**2)*(rNodes+rNodesIns-1)

        return self.coefficients


    def constArray(self, previousTemperatures):
        # Constant at the inner boundary
        self.constants[0] = thermalMass*(dr**2)*previousTemperatures[0]

        # Constants in the storage
        for j in range(1, rNodes - 1):
            self.constants[j] = 2*thermalMass*(dr**2)*j*previousTemperatures[j]

        # Constants at the storage/insulation boundary
        K = (rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns
        self.constants[rNodes-1] = K*(dr**2)*previousTemperatures[rNodes-1]

        # Constants in the insulation
        for j in range(rNodes, rNodes + rNodesIns - 1):
            self.constants[j] = 2*rhoIns*cIns*(drIns**2)*j*previousTemperatures[j]

        # Constants at the outer boundary
        K1 = 2*ambienth*drIns*dt*(rNodes+rNodesIns-1)
        self.constants[-1] = rhoIns*cIns*(drIns**2)*(rNodes+rNodesIns-1) + (2*ambienth*drIns*dt + K1)

        return self.constants


# Arrays to calculate the charging process
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
