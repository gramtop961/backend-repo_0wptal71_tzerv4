"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# CRM-specific schemas

class Automation(BaseModel):
    """
    Automations configured in the CRM
    Collection name: "automation"
    """
    name: str = Field(..., description="Automation name")
    description: Optional[str] = Field(None, description="What this automation does")
    status: Literal["active", "paused"] = Field("active", description="Whether automation is active")
    trigger: Literal["schedule", "webhook", "event"] = Field("schedule", description="How it is triggered")
    frequency: Optional[str] = Field(None, description="For schedule: e.g., hourly, daily 9am")

class AutomationRun(BaseModel):
    """
    Historical execution runs of automations
    Collection name: "automationrun"
    """
    automation_id: str = Field(..., description="Reference to Automation _id as string")
    status: Literal["success", "failed", "running"] = Field("running")
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    processed: int = 0
    errors: int = 0
    notes: Optional[str] = None

# Example schemas (kept for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
