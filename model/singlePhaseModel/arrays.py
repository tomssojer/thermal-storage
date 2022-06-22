import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from importer import *
import initialize as init

###############################################################################################
# V coeffMatrix metodi se definirajo koeficienti za v matriko, v constArray pa konstante
# To dvoje se potem rešuje v storage.py z numpy.linalg.solve
class ChargingArray():

    def __init__(self, sizeOfMatrixCoeff = 1):
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    # Matrix of coefficients
    def coeffMatrix(self):
        coefficients = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[0]

        # Coefficients at the boundaries
        coefficients[0][0] = 2*k*dt + 2*h*dz*dt + thermalMass*(dz**2)
        coefficients[0][1] = -2*k*dt + G*cGas*dz*dt
        coefficients[-1][-2] = -2*k*dt - G*cGas*dz*dt
        coefficients[-1][-1] = 2*k*dt + thermalMass*(dz**2) + G*cGas*dz*dt

        # Coefficients in the storage
        for i in range(1, len(coefficients) - 1):
            coefficients[i][i-1] = -2*k*dt - G*cGas*dz*dt
            coefficients[i][i] = 4*k*dt + 2*thermalMass*(dz**2)
            coefficients[i][i+1] = -2*k*dt + G*cGas*dz*dt

        return coefficients

    # Array of constants
    def constArray(self, previousTemperatures):
        constants = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[1]

        # Constants at the boundaries
        constants[0] = thermalMass*(dz**2)*previousTemperatures[0] + (2*h*dz*dt + G*cGas*dz*dt)*Tfluid
        constants[-1] = thermalMass*(dz**2)*previousTemperatures[-1]

        for i in range(1, len(constants) - 1):
            constants[i] = 2*thermalMass*(dz**2)*previousTemperatures[i]

        return constants
    
# Arrays to calculate the storing process
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


# Arrays to calculate the charging process
class DischargingArray():

    def __init__(self, sizeOfMatrixCoeff = 1):
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    # Matrix of coefficients
    def coeffMatrix(self):
        coefficients = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[0]

        # Coefficients at the boundaries
        coefficients[0][0] = 2*k*dt + 2*G*cGas*dz*dt + thermalMass*(dz**2)
        coefficients[0][1] = -2*k*dt - 2*G*cGas*dz*dt
        coefficients[-1][-2] = -2*k*dt + G*cGas*dz*dt
        coefficients[-1][-1] = 2*k*dt + 2*h*dz*dt + thermalMass*(dz**2)

        # Coefficients in the storage
        for i in range(1, len(coefficients) - 1):
            coefficients[i][i-1] = -2*k*dt + G*cGas*dz*dt
            coefficients[i][i] = 4*k*dt + 2*thermalMass*(dz**2)
            coefficients[i][i+1] = -2*k*dt - G*cGas*dz*dt

        return coefficients

    # Array of constants
    def constArray(self, previousTemperatures):
        constants = init.prepareCharging(zNodes, self.sizeOfMatrixCoeff)[1]

        # Constants at the boundaries
        constants[0] = thermalMass*(dz**2)*previousTemperatures[0]
        constants[-1] = thermalMass*(dz**2)*previousTemperatures[-1] + (2*h*dz*dt + G*cGas*dz*dt)*Tambient

        for i in range(1, len(constants) - 1):
            constants[i] = 2*thermalMass*(dz**2)*previousTemperatures[i]

        return constants
