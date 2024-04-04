from pydantic import BaseModel
from typing import Optional, List
from enum import IntEnum
from agricore_sp_models.common_models import OrganicProductionType, ProductGroupJsonDTO
from pydantic import confloat
    
class AgriculturalProduction(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    productGroupId: Optional[int] = None
    # Value of Sales (PLV - [€])
    valueSales: float
    # Quantity of Sold Production ([tons])
    quantitySold: float
    # Quantity of Used Production ([tons])
    quantityUsed: float
    # Value of total production (PLT - [€])
    cropProduction: float
    # Irrigated Area (IA - [ha])
    irrigatedArea: float
    # Cultivated Area (UAA - [ha])
    cultivatedArea: float
    organicProductionType: OrganicProductionType
    # Variable Costs per produced unit (CV - [€/ton])
    variableCosts: float
    # Land Value (PVF - [€])
    landValue: float
    # Unit selling price (PVU - [€/unit])
    sellingPrice: float
    
class AgriculturalProductionDTO(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    productGroupId: Optional[int] = None
    # Value of Sales (PLV - [€])
    valueSales: float
    # Quantity of Sold Production ([tons])
    quantitySold: float
    # Quantity of Used Production ([tons])
    quantityUsed: float
    # Value of total production (PLT - [€])
    cropProduction: float
    # Irrigated Area (IA - [ha])
    irrigatedArea: float
    # Cultivated Area (UAA - [ha])
    cultivatedArea: float
    organicProductionType: OrganicProductionType
    # Variable Costs per produced unit (CV - [€/ton])
    variableCosts: float
    # Land Value (PVF - [€])
    landValue: float
    # Unit selling price (PVU - [€/unit])
    sellingPrice: float
    
class LivestockProduction(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    productGroupId: Optional[int] = None
    # Number of Animals [units]
    numberOfAnimals: float
    # Number of Animals Sold [units]
    numberOfAnimalsSold: int
    # Value of Sold Animals ([€])
    valueSoldAnimals: float
    # Number of Animals for Slaughtering [units]
    numberAnimalsForSlaughtering: int
    # Value of Slaughtered Animals ([€])
    valueSlaughteredAnimals: float
    # Number of Animals for Rearing/Breading [units]
    numberAnimalsRearingBreading: float
    # Value of Animals Rearing/Breading ([€])
    valueAnimalsRearingBreading: float
    # Number of tons of milk produced [tons]
    milkTotalProduction: float
    # Number of tons of milk sold [tons]
    milkProductionSold: float
    # Value of Sold Milk ([€])
    milkTotalSales: float
    # Variable Costs per produced unit (CV - [€/ton])
    milkVariableCosts: float
    woolTotalProduction: float
    woolProductionSold: float
    eggsTotalSales: float
    eggsTotalProduction: float
    eggsProductionSold: float
    manureTotalSales: float
    # Number of dairy cows [UBA - [units]]
    dairyCows: int
    # Average variable cost per unit of product [€/ton]
    variableCosts: float

class Population(BaseModel):
    id: Optional[int] = None
    description: str

class SyntheticPopulation(BaseModel):
    id: Optional[int] = None
    populationId: int
    yearId: int
    description: str
    name: str
    
class Farm(BaseModel):
    id: Optional[int] = None
    populationId: Optional[int] = None
    lat: int
    long: int
    altitude: int
    regionLevel1: str
    regionLevel1Name: str
    regionLevel2: str
    regionLevel2Name: str
    regionLevel3: int
    regionLevel3Name: str
    farmCode: str
    technicalEconomicOrientation: int
    weight_ra: float
    weight_reg: float
        
class ProductGroup(BaseModel):
    id: Optional[int] = None
    populationId: Optional[int] = None
    name: str
    productType: int
    originalNameDatasource: str
    productsIncludedInOriginalDataset: str
    organic: OrganicProductionType
    modelSpecificCategories: List[str]
    
class FADNProductRelation(BaseModel):
    id: Optional[int] = None
    productGroupId: Optional[int] = None
    fadnProductId: Optional[int] = None
    populationId: Optional[int] = None

class ClosingValue(BaseModel):
    id: Optional[int] = None
    # Total Area of type Agricultural Land [ha]
    agriculturalLandArea: float
    # Total value of Agricultural Land [€]
    agriculturalLandValue: float
    # Acquired Agricultural Land [ha]
    plantationsValue: float
    # Investment in Land improvements [€]
    landImprovements: float
    # Total Area of type Forest Land [ha]
    forestLandArea: float
    # Total value of Forest Land [€]
    forestLandValue: float
    # Value of Buildings in the farm [€]
    farmBuildingsValue: float
    # Value of Machinery and Equipment in the farm [€]
    machineryAndEquipment: float
    # Value of intangible assets that are tradable [€]
    intangibleAssetsTradable: float
    # Value of intangible assets that are non-tradable [€]
    intangibleAssetsNonTradable: float
    # Value of other non-current assets [€]
    otherNonCurrentAssets: float
    # Total value of established long and medium term loans [€]
    longAndMediumTermLoans: float
    # Total value of current assets [€]
    totalCurrentAssets: float
    # Farm Net Income [€]
    farmNetIncome: float
    # Gross Farm Income [€]
    grossFarmIncome: float
    # Total value of subsidies on investments [€]
    subsidiesOnInvestments: float
    # Balance of Taxes on Investments [€]
    vatBalanceOnInvestments: float
    # Total value of Agricultural Production [€]
    totalOutputCropsAndCropProduction: float
    # Total value of Livestock Production [€]
    totalOutputLivestockAndLivestockProduction: float
    # Total value of other outputs [€]
    otherOutputs: float
    # Total value of intermediate consumption [€]
    totalIntermediateConsumption: float
    # Value of Taxes (>0 received , <0 paid) [€]
    taxes: float
    # Balance of VAT excluding investments [€]
    vatBalanceExcludingInvestments: float
    # Total value of Fixed Assets [€]
    fixedAssets: float
    # Yearly Depreciation [€]
    depreciation: float
    # Total value of External Factors [€]
    totalExternalFactors: float
    # Total value of Machinery [€]
    machinery: float
    farmId: int
    yearId: int
    
class Policy(BaseModel):
    id: Optional[int] = None
    policyIdentifier: str
    policyDescription: str
    isCoupled: bool
    
class PolicyProductGroupRelation(BaseModel):
    id: Optional[int] = None
    productGroupId: int
    policyId: int
    populationId: Optional[int] = None

class HolderFarmYearData(BaseModel):
    id: Optional[int] = None
    farmId: Optional[int] = None
    yearId: Optional[int] = None
    holderAge: int
    holderGender: int
    holderSuccessors: int
    holderSuccessorsAge: int
    holderFamilyMembers: int
    
class FarmYearSubsidy(BaseModel):
    id: Optional[int] = None
    farmId: int
    yearId: int
    policyId: int
    value: float

class FarmYearSubsidyDTO(BaseModel):
    yearNumber: int
    value: float
    policyIdentifier: str

class HolderInfoDTO(BaseModel):
    holderAge: int
    holderSuccessorsAge: int
    holderSuccessors: int
    holderFamilyMembers: int
    holderGender: str

class ValueToLPDTO(BaseModel):
    farmId: int
    yearId: int
    a_0: float
    # CurrentAssets in SP model [€]
    sE465: float
    # SE490 [€]
    sE490: float
    # Average ha price [€/ha]
    averageHAPrice: float
    # SE420 [€]
    sE420: float
    # SE410 [€]
    sE410: float
    # Aversion risk factor [TBD]
    aversionRiskFactor: float
    m_0: float
    agentHolder: Optional[HolderInfoDTO] = None
    agentSubsidies: Optional[List[FarmYearSubsidyDTO]] = None

class CropDataDTO(BaseModel):
    # Crop productive Area [ha]
    cropProductiveArea: float
    # Variable Costs per produced unit (CV - [€/ton])
    cropVariableCosts: float
    # Quantity of Sold Production ([tons])
    quantitySold: float
    # Quantity of Used Production ([tons])
    quantityUsed: float
    # Unit selling price (PVU - [€/unit])
    cropSellingPrice: float
    # Total value of coupled subsidy received [€]
    coupledSubsidy: float
    # Used Area [ha]
    uaa: float
    # Number (LSU) of rebreeding cows
    rebreedingCows: float
    # Number (LSU) of dairy cows
    dairyCows: float

class DecoupledSubsidiesDTO(BaseModel):
    # Amount received for the Green subsidy [€]
    pGreen: float
    # Amount received for the Basic subsidy [€]
    pBasic: float
    # Amount received for the Pension subsidy [€]
    pPension: float

class ValueFromSPDTO(BaseModel):
    farmId: int
    # Total Current Assets [€]
    totalCurrentAssets: float
    # Farm Net Income [€]
    farmNetIncome: float
    # Gross Farm Income [€]
    farmGrossIncome: float
    # Area of Agricultural Land [ha]
    agriculturalLand: float
    crops: dict[str,CropDataDTO]
    # Total Variable Costs [€]
    totalVariableCosts: float
    # Balance of the rented area (>0 if the farmer is renting in land) [ha]
    rentBalanceArea: float
    decoupledSubsidies: DecoupledSubsidiesDTO
    # Greening Surface [ha]
    greeningSurface: float

class LivestockDTO(BaseModel):
    # Number of animals [units]
    numberOfAnimals: float
    # Number of dairy cows [units]
    dairyCows: int
    # Number of rebreeding cows [units]
    rebreedingCows: float
    # Quantity of produced milk [tons]
    milkProduction: float
    # Unit value of sold milk [€/ton]
    milkSellingPrice: float
    # Variable costs per produced unit (CV - [€/ton])
    variableCosts: float



class AltitudeEnum(IntEnum):
    MOUNTAINS = 1
    HILLS = 2
    PLAINS = 3

class ValueToSPDTO(BaseModel):
    farmCode: int
    holderInfo: Optional[HolderInfoDTO] = None
    cod_RAGR: str
    cod_RAGR2: str
    cod_RAGR3: int
    technicalEconomicOrientation: int
    altitude: AltitudeEnum
    currentAssets: float
    decoupledSubsidies: Optional[DecoupledSubsidiesDTO] = None
    crops: dict[str,CropDataDTO]
    livestock: Optional[LivestockDTO] = None
    # Greening Surface [ha]
    greeningSurface: float

class DataToSPDTO(BaseModel):
    values: List[ValueToSPDTO]
    productGroups: List[ProductGroupJsonDTO]
    coupledSubsidiesProductGroupsDict: dict[str,List[str]]

class IntermediateValueFromLP(BaseModel):
    farmId: int
    averageHAPrice: float
    previousAgriculturalLand: float
    result: dict

class LandTransaction(BaseModel):
    productionId: int
    destinationFarmId: int
    yearId: int
    percentage: confloat(ge=0, le=1)
    salePrice: float

class AgroManagementDecisions(BaseModel):
    farmId: int
    yearId: int
    # Total Area of type Agricultural Land [ha]
    agriculturalLand: float
    # Amount of stablished loans at long and medium term [€]
    longAndMediumTermLoans: float
    # Total current assets [€]
    totalCurrentAssets: float
    # Average hectar price of the owned land [€/ha]
    averageLandValue: float
    # Total amount of land the farmer is willing to acquire [ha]
    targetedLandAquisitionArea: float
    # Price per hectar the farmer is willing to pay for the land [€/ha]
    targetedLandAquisitionHectarPrice: float
    # Boolean to indicate if the farmer is willing to retire and hand over the farm to its successors
    retireAndHandOver: bool

class AgroManagementDecisionFromLP(BaseModel):
    agroManagementDecisions: List[AgroManagementDecisions]
    landTransactions: List[LandTransaction]
    errorList: List[int]

class DataToLPDTO(BaseModel):
    values: List[ValueToLPDTO]
    agriculturalProductions: List[AgriculturalProductionDTO]
    ignoreLP: Optional[bool]
    ignoreLMM: Optional[bool]

