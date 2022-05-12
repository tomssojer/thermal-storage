# Properties
length = radius = insulation = None
materialDiameter = None
voidFrac = None
kStorage = rhoStorage = cStorage = None
kGas = rhoGas = cGas = None
kIns = rhoIns = cIns = None 
kf = ks = None 
ambientTemp = Tfluid = finalDifference = None
h =  ambienth = None
G = None
flowVelocity = None
dinamicViscosity = None
c1 = c2 = None
# Discretization
dzDefined = drDefined = dt = dtStore = None
exportDtCharging = exportDtStoring = None

with open("./data/properties.txt", "r") as file:
    exec(file.read())

A = 6*(1 - voidFrac)/materialDiameter
thermalMass = voidFrac*rhoGas*cGas + (1 - voidFrac)*rhoStorage*cStorage
reynoldsNum = rhoGas*flowVelocity*materialDiameter/dinamicViscosity
prandtlNum = cGas*dinamicViscosity/kStorage
effConductivity = kStorage*voidFrac*(1 + c1*(reynoldsNum*prandtlNum)**c2)
k = kStorage*(1 - voidFrac*(kStorage - effConductivity)/(effConductivity + voidFrac**(1/3)*(kStorage - effConductivity)))


############ Discretization ###############
# z-direction discretization
zNodes = round(length/dzDefined) + 1  # ------- /
dz = length/(zNodes - 1)  # ------------------- m
# Storage r-direction discretization
rNodes = round(radius/drDefined) + 1  # ------- /
dr = radius/(rNodes - 1)  # ------------------- m
# Insulation r-direction
if insulation == 0:
    rNodesIns = 0
    drIns = 0
else:
    rNodesIns = round(insulation/drDefined)
    drIns = insulation/rNodesIns
