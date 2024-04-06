from agricore_sp_models.common_models import OrganicProductionType, PolicyJsonDTO, ProductGroupJsonDTO
from pydantic import BaseModel, Field
from typing import List

class AgriculturalProductionJsonDTO(BaseModel):
    yearNumber: int
    productName: str 
    organicProductionType: OrganicProductionType
    # Utilized Agricultural Area (UAA - [ha])
    cultivatedArea: float
    # Irrigated Area (IA - [ha])
    irrigatedArea: float 
    # Value of total production (PLT - [€])
    cropProduction: float
    # Quantity of Sold Production ([tons])
    quantitySold: float
    # Quantity of Used Production ([tons])
    quantityUsed: float
    # Value of Sales (PLV - [€])
    valueSales: float 
    # Variable Costs per produced unit (CV - [€/ton])
    variableCosts: float 
    # Land Value (PVF - [€])
    landValue: float 
    # Unit selling price (PVU - [€/unit])
    sellingPrice: float

class LivestockProductionJsonDTO(BaseModel):
    yearNumber: int
    productName: str
    # Number of Animals [units]
    numberOfAnimals: float
    # Number of dairy cows [UBA - [units]]
    dairyCows: int
    # Number of Animals Sold [units]
    numberOfAnimalsSold: int
    # Value of Sold Animals ([€])
    valueSoldAnimals: float
    # Number of Animals for Slaughtering [units]
    numberAnimalsForSlaughtering: int
    # Value of Slaughtered Animals ([€])
    valueSlaughteredAnimals: float
    # Number of Animals for Rearing/Breeding [units]
    numberAnimalsRearingBreading: float
    # Value of Animals for Rearing/Breeding ([€])
    valueAnimalsRearingBreading: float
    # Number of tons of milk produced [tons]
    milkTotalProduction: float
    # Number of tons of milk sold [tons]
    milkProductionSold: float
    # Value of milk sold ([€])
    milkTotalSales: float
    # Variable Costs per produced unit (CV - [€/ton])
    milkVariableCosts: float
    woolTotalProduction: float
    woolProductionSold: float
    eggsTotalSales: float
    eggsTotalProduction: float
    eggsProductionSold: float
    manureTotalSales: float
    # Average variable cost per unit of product[€/ ton]
    variableCosts: float
    # Average sell price per unit of product[€/ ton]
    sellingPrice: float
    
class HolderFarmYearDataJsonDTO(BaseModel):
    yearNumber: int
    holderAge: int
    holderFamilyMembers: int
    holderSuccessorsAge: int
    holderGender: str
    holderSuccessors: int
    
class ClosingValFarmValueDTO(BaseModel):
    # Total Area of type Agricultural Land [ha]
    agriculturalLandArea: float
    # Total value of Agricultural Land [€]
    agriculturalLandValue: float
    # Acquired Agricultural Land [ha]
    agriculturalLandHectaresAdquisition: float
    # Invesment in Land improvements [€]
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
    yearNumber: int
    # Balance (>0 received , <0 paid) of rent operations [€]
    rentBalance: float

class FarmYearSubsidyDTO(BaseModel):
    yearNumber: int
    value: float
    policyIdentifier: str
    
class LandTransactionJsonDTO(BaseModel):
    yearNumber: int
    productGroupName: str
    destinationFarmCode: str
    originFarmCode: str
    # Percentage of the land transferred from the origin farm to the destination farm in [0,1] range
    percentage: float = Field(..., ge=0, le=1)
    # Sale price of the land transferred from the origin farm to the destination farm [€]
    salePrice: float
    
class LandRentJsonDTO(BaseModel):
    yearNumber: int
    originFarmCode: str
    destinationFarmCode: str
    # Total Rent Price [€]
    rentValue: float
    # Total Rent Area [ha]
    rentArea: float
    
class GreeningFarmYearDataJsonDTO(BaseModel):
    yearNumber: int
    # Greening Surface [ha]
    greeningSurface: float
    
class FarmJsonDTO(BaseModel):
    farmCode: str
    lat: int
    long: int
    altitude: str = ""
    regionLevel1: str
    regionLevel1Name: str = ""
    regionLevel2: str
    regionLevel2Name: str = ""
    regionLevel3: str
    regionLevel3Name: str = ""
    technicalEconomicOrientation: int
    agriculturalProductions: List[AgriculturalProductionJsonDTO]
    livestockProductions: List[LivestockProductionJsonDTO]
    holderFarmYearsData: List[HolderFarmYearDataJsonDTO]
    closingValFarmValues: List[ClosingValFarmValueDTO]
    farmYearSubsidies: List[FarmYearSubsidyDTO]
    greeningFarmYearData: List[GreeningFarmYearDataJsonDTO]
    
class PopulationJsonDTO(BaseModel):
    description: str = ""
    farms: List[FarmJsonDTO]
    productGroups: List[ProductGroupJsonDTO]
    uncoupledPolicies: List[PolicyJsonDTO]
    landTransactions: List[LandTransactionJsonDTO]
    landRents: List[LandRentJsonDTO]

class SyntheticPopulationJsonDTO(BaseModel):
    description: str = ""
    name: str = ""
    yearNumber: int
    population: PopulationJsonDTO