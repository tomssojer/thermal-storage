import os
import sys
import inspect

currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from properties import *

###############################################################################################
# V coeffMatrix metodi se definirajo koeficienti za v matriko, v constArray pa konstante
# To dvoje se potem rešuje v storage.py z numpy.linalg.solve
class ChargingArray():

    # We add empty lists when we call an object
    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    # Matrix of coefficients
    def coeffMatrix(self):
        # Coefficients at the boundaries
        self.coefficients[0][0] = 2*k*dt + 2*h*dz*dt + thermalMass*(dz**2)
        self.coefficients[0][1] = -2*k*dt + G*cGas*dz*dt
        self.coefficients[-1][-2] = -2*k*dt - G*cGas*dz*dt
        self.coefficients[-1][-1] = 2*k*dt + thermalMass*(dz**2) + G*cGas*dz*dt

        # Coefficients in the storage
        for i in range(1, len(self.coefficients) - 1):
            self.coefficients[i][i-1] = -2*k*dt - G*cGas*dz*dt
            self.coefficients[i][i] = 4*k*dt + 2*thermalMass*(dz**2)
            self.coefficients[i][i+1] = -2*k*dt + G*cGas*dz*dt

        return self.coefficients

    # Array of constants
    def constArray(self, previousTemperatures):
        # Constants at the boundaries
        self.constants[0] = thermalMass*(dz**2)*previousTemperatures[0] + (2*h*dz*dt + G*cGas*dz*dt)*Tfluid
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
        self.coefficients[0][0] = 4*k*dtStore + thermalMass*(dr**2)
        self.coefficients[0][1] = -4*k*dtStore

        # Coefficients in the storage
        for j in range(1, rNodes - 1):
            self.coefficients[j][j-1] = -k*dtStore - 2*k*dtStore*j
            self.coefficients[j][j] = 4*k*dtStore*j + 2*thermalMass*(dr**2)*j
            self.coefficients[j][j+1] = k*dtStore - 2*k*dtStore*j

        if drIns > 0: 
            # Coefficients at the storage/insulation boundary
            K = (rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns
            K1 = 2*(rNodes - 1)
            self.coefficients[rNodes-1][rNodes-2] = (-1 - K1)*k*dtStore
            self.coefficients[rNodes-1][rNodes-1] = k*dtStore - kIns*dtStore + K1*dtStore*k + K1*dtStore*kIns + K*(dr**2)
            self.coefficients[rNodes-1][rNodes] = (1 - K1)*kIns*dtStore

            # Coefficients in the insulation
            for j in range(rNodes, rNodes + rNodesIns - 1):
                self.coefficients[j][j-1] = -kIns*dtStore - 2*kIns*dtStore*j
                self.coefficients[j][j] = 4*kIns*dtStore*j + 2*rhoIns*cIns*(drIns**2)*j
                self.coefficients[j][j+1] = kIns*dtStore - 2*kIns*dtStore*j

            # Coefficients at the outer boundary
            K2 = rNodes+rNodesIns-1
            K3 = 2*ambienth*drIns*dtStore
            self.coefficients[-1][-2] = -2*kIns*dtStore*K2
            self.coefficients[-1][-1] = K3 + 2*kIns*dtStore*K2 + K3*K2 + rhoIns*cIns*(drIns**2)*K2

        elif drIns == 0:
            K2 = rNodes-1
            K3 = 2*ambienth*dr*dtStore
            self.coefficients[-1][-2] = -2*k*dtStore*K2
            self.coefficients[-1][-1] = K3 + 2*k*dtStore*K2 + K3*K2 + thermalMass*(dr**2)*K2

        return self.coefficients

    def constArray(self, previousTemperatures):
        # Constant at the inner boundary
        self.constants[0] = thermalMass*(dr**2)*previousTemperatures[0]

        # Constants in the storage
        for j in range(1, rNodes - 1):
            self.constants[j] = 2*thermalMass*(dr**2)*j*previousTemperatures[j]

        if drIns > 0:
            # Constants at the storage/insulation boundary
            K = (rNodes - 3/2)*thermalMass + (rNodes - 1/2)*rhoIns*cIns
            self.constants[rNodes-1] = K*(dr**2)*previousTemperatures[rNodes-1]

            # Constants in the insulation
            for j in range(rNodes, rNodes + rNodesIns - 1):
                self.constants[j] = 2*rhoIns*cIns * \
                    (drIns**2)*j*previousTemperatures[j]

            # Constants at the outer boundary
            K = 2*ambienth*drIns*dtStore
            K1 = rNodes+rNodesIns-1
            self.constants[-1] = (K*K1 + K)*ambientTemp + \
                rhoIns*cIns*(drIns**2)*K1*previousTemperatures[-1]
        
        elif drIns == 0:
            K = 2*ambienth*dr*dtStore
            K1 = rNodes-1
            self.constants[-1] = (K*K1 + K)*ambientTemp + thermalMass*(dr**2)*K1*previousTemperatures[-1]

        return self.constants


# Arrays to calculate the charging process
class DischargingArray():

    def __init__(self, coefficients, constants):
        self.coefficients = coefficients
        self.constants = constants

    # Matrix of coefficients
    def coeffMatrix(self):
        # Coefficients at the boundaries
        self.coefficients[0][0] = 2*k*dt + 2*G*cGas*dz*dt + thermalMass*(dz**2)
        self.coefficients[0][1] = -2*k*dt - 2*G*cGas*dz*dt
        self.coefficients[-1][-2] = -2*k*dt + G*cGas*dz*dt
        self.coefficients[-1][-1] = 2*k*dt + 2*h*dz*dt + thermalMass*(dz**2)

        # Coefficients in the storage
        for i in range(1, len(self.coefficients) - 1):
            self.coefficients[i][i-1] = -2*k*dt + G*cGas*dz*dt
            self.coefficients[i][i] = 4*k*dt + 2*thermalMass*(dz**2)
            self.coefficients[i][i+1] = -2*k*dt - G*cGas*dz*dt

        return self.coefficients

    # Array of constants
    def constArray(self, previousTemperatures):
        # Constants at the boundaries
        self.constants[0] = thermalMass*(dz**2)*previousTemperatures[0]
        self.constants[-1] = thermalMass*(dz**2)*previousTemperatures[-1] + (2*h*dz*dt + G*cGas*dz*dt)*ambientTemp

        for i in range(1, len(self.constants) - 1):
            self.constants[i] = 2*thermalMass*(dz**2)*previousTemperatures[i]

        return self.constants

