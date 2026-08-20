from typing import TypedDict
from pydantic import BaseModel, Field


class FarmInput(BaseModel):
    land_acres: float = Field(gt=0, le=10000)
    available_water_liters: float = Field(ge=0)
    capital: float = Field(ge=0)

    soil_n: float = Field(ge=0)
    soil_p: float = Field(ge=0)
    soil_k: float = Field(ge=0)
    soil_ph: float = Field(ge=0, le=14)
    soil_moisture: float = Field(ge=0, le=100)

    temperature: float
    rainfall_forecast_mm: float = Field(ge=0)

    current_crop: str = ""
    crop_growth_stage: str = ""
    planting_date: str = ""

    livestock_type: str
    livestock_count: int = Field(ge=0)

    available_workers: int = Field(ge=0)

    decisions: dict = {}


class FarmState(TypedDict):
    land_acres: float
    available_water_liters: float
    capital: float

    soil_n: float
    soil_p: float
    soil_k: float
    soil_ph: float
    soil_moisture: float

    temperature: float
    rainfall_forecast_mm: float

    current_crop: str
    crop_growth_stage: str
    planting_date: str

    livestock_type: str
    livestock_count: int

    available_workers: int

    decisions: dict