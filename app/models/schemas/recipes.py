from typing import List, Optional, ClassVar
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema


class Ingredient(BaseModel):
    name: str = Field(..., description="Ingredient name")
    quantity: Optional[str] = Field(default=None, description="Ingredient quantity")
    unit: Optional[str] = Field(default=None, description="Unit of measurement")


class CookingStep(BaseModel):
    step_number: int = Field(..., description="Step order number")
    instruction: str = Field(..., description="Cooking instruction")
    duration: Optional[str] = Field(
        default=None, description="Time required for this step"
    )


class RecipeExtraction(BaseExtractionSchema):
    title: str = Field(..., description="Recipe title")
    description: Optional[str] = Field(default=None, description="Recipe description")
    prep_time: Optional[str] = Field(default=None, description="Preparation time")
    cook_time: Optional[str] = Field(default=None, description="Cooking time")
    servings: Optional[int] = Field(default=None, description="Number of servings")

    ingredients: List[Ingredient] = Field(..., description="List of ingredients")
    instructions: List[CookingStep] = Field(..., description="Cooking instructions")

    # Class attributes - use ClassVar to tell Pydantic these are NOT fields
    extraction_type: ClassVar[str] = "recipes"
    description: ClassVar[str] = (
        "Extracts recipe information including ingredients and instructions"
    )
    prompt: ClassVar[str] = (
        "Extract recipe information from the given content. Focus on ingredients with quantities and step-by-step instructions."
    )
