import sys
sys.path.append('..')
from getData import Node
import modules.initialize as init

class GetArrays:

    def __init__(self, subList, sizeOfMatrixCoeff=1):
        self.subList = subList
        self.sizeOfMatrixCoeff = sizeOfMatrixCoeff

    def coeffMatrix(self, props):
        coefficients = init.prepareStoring(props.rNodes, props.rNodesIns)[0]
        k = Node(self.subList, props).kStoringList()
        thermalMass = Node(self.subList, props).thermalMassList()

        # Coefficients at the inner boundary
        coefficients[0][0] = 4*k[0]*props.dtStore + thermalMass[0]*(props.dr**2)
        coefficients[0][1] = -4*k[1]*props.dtStore

        # Coefficients in the storage
        for j in range(1, props.rNodes - 1):
            coefficients[j][j-1] = -k[j-1]*props.dtStore - 2*k[j-1]*props.dtStore*j
            coefficients[j][j] = 4*k[j]*props.dtStore*j + 2*thermalMass[j]*(props.dr**2)*j
            coefficients[j][j+1] = k[j+1]*props.dtStore - 2*k[j+1]*props.dtStore*j

        if props.drIns > 0:
            # Coefficients at the storage/insulation boundary
            # K = (props.rNodes - 3/2)*thermalMass + (props.rNodes - 1/2)*props.rhoIns*props.cIns
            K = thermalMass[props.rNodes-1]*(props.rNodes-1)*2
            K1 = 2*(props.rNodes - 1)
            kBoth = k[props.rNodes-1]*props.kIns/(k[props.rNodes-1]+props.kIns)
            coefficients[props.rNodes-1][props.rNodes-2] = (-1 - K1)*k[props.rNodes-2]*props.kIns/(k[props.rNodes-2]+props.kIns)*props.dtStore
            coefficients[props.rNodes-1][props.rNodes-1] = kBoth*props.dtStore - kBoth*props.dtStore + K1*props.dtStore*kBoth + K1*props.dtStore*kBoth + K*(props.dr**2)
            coefficients[props.rNodes-1][props.rNodes] = (1 - K1)*k[props.rNodes]*props.kIns/(k[props.rNodes]+props.kIns)*props.dtStore

            # Coefficients in the insulation
            for j in range(props.rNodes, props.rNodes + props.rNodesIns - 1):
                coefficients[j][j-1] = -props.kIns*props.dtStore - 2*props.kIns*props.dtStore*j
                coefficients[j][j] = 4*props.kIns*props.dtStore*j + 2*props.rhoIns*props.cIns*(props.drIns**2)*j
                coefficients[j][j+1] = props.kIns*props.dtStore - 2*props.kIns*props.dtStore*j

            # Coefficients at the outer boundary
            K2 = props.rNodes+props.rNodesIns-1
            K3 = 2*props.hAmbient*props.drIns*props.dtStore
            coefficients[-1][-2] = -2*props.kIns*props.dtStore*K2
            coefficients[-1][-1] = K3 + 2*props.kIns*props.dtStore*K2 + K3*K2 + props.rhoIns*props.cIns*(props.drIns**2)*K2

        elif props.drIns == 0:
            K2 = props.rNodes-1
            K3 = 2*props.hAmbient*props.dr*props.dtStore
            coefficients[-1][-2] = -2*k[-2]*props.dtStore*K2
            coefficients[-1][-1] = K3 + 2*k[-1]*props.dtStore*K2 + K3*K2 + thermalMass[-1]*(props.dr**2)*K2

        return coefficients

    def constArray(self, props, previousTemperatures):
        constants = init.prepareStoring(props.rNodes, props.rNodesIns)[1]
        thermalMass = Node(self.subList, props).thermalMassList()

        # Constant at the inner boundary
        constants[0] = thermalMass[0]*(props.dr**2)*previousTemperatures[0]

        # Constants in the storage
        for j in range(1, props.rNodes - 1):
            constants[j] = 2*thermalMass[j]*(props.dr**2)*j*previousTemperatures[j]

        if props.drIns > 0:
            # Constants at the storage/insulation boundary
            # K = (props.rNodes - 3/2)*thermalMass + (props.rNodes - 1/2)*props.rhoIns*props.cIns
            K = thermalMass[props.rNodes-1]*(props.rNodes-1)*2
            constants[props.rNodes-1] = K*(props.dr**2)*previousTemperatures[props.rNodes-1]

            # Constants in the insulation
            for j in range(props.rNodes, props.rNodes + props.rNodesIns - 1):
                constants[j] = 2*props.rhoIns*props.cIns*(props.drIns**2)*j*previousTemperatures[j]

            # Constants at the outer boundary
            K = 2*props.hAmbient*props.drIns*props.dtStore
            K1 = props.rNodes+props.rNodesIns-1
            constants[-1] = (K*K1 + K)*props.Tambient + props.rhoIns*props.cIns*(props.drIns**2)*K1*previousTemperatures[-1]

        elif props.drIns == 0:
            K = 2*props.hAmbient*props.dr*props.dtStore
            K1 = props.rNodes-1
            constants[-1] = (K*K1 + K)*props.Tambient + thermalMass[-1]*(props.dr**2)*K1*previousTemperatures[-1]

        return constants