from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GenderEnum(str, Enum):
    male = "male"
    female = "female"
    other = "other"

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[GenderEnum] = None
    weight_kg: Optional[float] = Field(None, gt=0)
    height_cm: Optional[float] = Field(None, gt=0)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[GenderEnum] = None
    weight_kg: Optional[float] = Field(None, gt=0)
    height_cm: Optional[float] = Field(None, gt=0)

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    sets: Optional[int] = Field(None, ge=1)
    reps: Optional[int] = Field(None, ge=1)
    weight_kg: Optional[float] = Field(None, ge=0)
    duration_seconds: Optional[int] = Field(None, ge=1)
    distance_km: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseResponse(ExerciseBase):
    id: int
    workout_id: int

    class Config:
        from_attributes = True

class WorkoutBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    calories_burned: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    workout_date: Optional[datetime] = None

class WorkoutCreate(WorkoutBase):
    exercises: Optional[List[ExerciseCreate]] = []

class WorkoutUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    workout_type: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1)
    calories_burned: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None
    workout_date: Optional[datetime] = None

class WorkoutResponse(WorkoutBase):
    id: int
    user_id: int
    created_at: datetime
    exercises: List[ExerciseResponse] = []

    class Config:
        from_attributes = True

class NutritionLogCreate(BaseModel):
    meal_type: Optional[str] = None
    log_date: Optional[datetime] = None
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    water_ml: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

class NutritionLogUpdate(BaseModel):
    meal_type: Optional[str] = None
    log_date: Optional[datetime] = None
    calories: Optional[float] = Field(None, ge=0)
    protein_g: Optional[float] = Field(None, ge=0)
    carbs_g: Optional[float] = Field(None, ge=0)
    fat_g: Optional[float] = Field(None, ge=0)
    water_ml: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

class NutritionLogResponse(BaseModel):
    id: int
    user_id: int
    meal_type: Optional[str] = None
    log_date: Optional[datetime] = None
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    water_ml: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class ProgressEntryCreate(BaseModel):
    weight_kg: Optional[float] = Field(None, gt=0)
    body_fat_pct: Optional[float] = Field(None, ge=0, le=100)
    muscle_mass_kg: Optional[float] = Field(None, ge=0)
    chest_cm: Optional[float] = Field(None, ge=0)
    waist_cm: Optional[float] = Field(None, ge=0)
    hips_cm: Optional[float] = Field(None, ge=0)
    notes: Optional[str] = None

class ProgressEntryResponse(BaseModel):
    id: int
    user_id: int
    weight_kg: Optional[float] = None
    body_fat_pct: Optional[float] = None
    muscle_mass_kg: Optional[float] = None
    chest_cm: Optional[float] = None
    waist_cm: Optional[float] = None
    hips_cm: Optional[float] = None
    notes: Optional[str] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None
    is_achieved: Optional[bool] = None

class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None
    is_achieved: bool
    created_at: datetime

    class Config:
        from_attributes = True
