from typing import List, Optional
from pydantic import BaseModel, Field
from ..base import BaseExtractionSchema

class Salary(BaseModel):
    min_amount: Optional[float] = Field(default=None, description="Minimum salary")
    max_amount: Optional[float] = Field(default=None, description="Maximum salary")
    currency: str = Field(default="USD", description="Currency code")
    period: str = Field(..., description="Salary period", enum=["hourly", "monthly", "yearly"])

class Requirement(BaseModel):
    category: str = Field(..., description="Requirement category", enum=["required", "preferred", "nice_to_have"])
    skill: str = Field(..., description="Required skill or qualification")
    years_experience: Optional[int] = Field(default=None, description="Years of experience needed")

class JobPostingExtraction(BaseExtractionSchema):
    # Schema definition
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location")
    remote_options: List[str] = Field(..., description="Remote work options", enum=["on-site", "remote", "hybrid"])
    job_type: str = Field(..., description="Employment type", enum=["full-time", "part-time", "contract", "internship"])
    department: Optional[str] = Field(default=None, description="Department or team")
    
    description: str = Field(..., description="Job description")
    responsibilities: List[str] = Field(..., description="Key responsibilities")
    requirements: List[Requirement] = Field(..., description="Job requirements")
    
    salary: Optional[Salary] = Field(default=None, description="Salary information")
    benefits: List[str] = Field(default_factory=list, description="Benefits offered")
    
    application_deadline: Optional[str] = Field(default=None, description="Application deadline")
    contact_email: Optional[str] = Field(default=None, description="Contact email")
    
    # Class configuration for auto-discovery
    extraction_type: str = "job_postings"
    schema_description: str = "Extracts detailed job posting information including requirements, responsibilities, and compensation"
    prompt: str = """You are an HR specialist and job posting analyzer. Extract comprehensive job posting information from the given content.
    
    Focus on:
    - Identifying complete job details and requirements
    - Categorizing requirements by importance level
    - Extracting salary and benefits information
    - Determining remote work options
    - Capturing application instructions and deadlines
    - Organizing responsibilities clearly
    
    Be precise and comprehensive in extracting all job-related information."""