from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date
from typing import List, Optional
from datetime import datetime, timezone
from datetime import timedelta
from db import get_db
import models, schemas, auth

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = auth.get_password_hash(user_in.password)
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pw,
        full_name=user_in.full_name,
        age=user_in.age,
        gender=user_in.gender,
        weight_kg=user_in.weight_kg,
        height_cm=user_in.height_cm,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@auth_router.post("/token", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and receive a JWT access token."""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """Get the currently authenticated user's profile."""
    return current_user

@auth_router.put("/me", response_model=schemas.UserResponse)
async def update_me(
    updates: schemas.UserUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update the currently authenticated user's profile."""
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


workouts = APIRouter(prefix="/workouts", tags=["Workouts"])

@workouts.post("/", response_model=schemas.WorkoutResponse, status_code=status.HTTP_201_CREATED)
async def create_workout(
    workout_in: schemas.WorkoutCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log a new workout."""
    data = workout_in.model_dump(exclude={"exercises"})
    workout = models.Workout(user_id=current_user.id, **data)
    db.add(workout)
    db.flush()
    for ex in workout_in.exercises or []:
        exercise = models.Exercise(workout_id=workout.id, **ex.model_dump())
        db.add(exercise)
    db.commit()
    db.refresh(workout)
    return workout

@workouts.get("/", response_model=List[schemas.WorkoutResponse])
async def list_workouts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all workouts for the authenticated user."""
    return (
        db.query(models.Workout)
        .filter(models.Workout.user_id == current_user.id)
        .order_by(models.Workout.workout_date.desc())
        .offset(skip).limit(limit).all()
    )

@workouts.get("/{workout_id}", response_model=schemas.WorkoutResponse)
async def get_workout(
    workout_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific workout by ID."""
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    return workout

@workouts.put("/{workout_id}", response_model=schemas.WorkoutResponse)
async def update_workout(
    workout_id: int,
    updates: schemas.WorkoutUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a workout entry."""
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(workout, field, value)
    db.commit()
    db.refresh(workout)
    return workout

@workouts.delete("/{workout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workout(
    workout_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a workout."""
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id
    ).first()
    if not workout:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workout not found")
    db.delete(workout)
    db.commit()


nutrition = APIRouter(prefix="/nutrition", tags=["Nutrition"])

@nutrition.post("/", response_model=schemas.NutritionLogResponse, status_code=status.HTTP_201_CREATED)
async def log_meal(
    log_in: schemas.NutritionLogCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Log a meal and its nutritional information."""
    entry = models.NutritionLog(user_id=current_user.id, **log_in.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@nutrition.get("/", response_model=List[schemas.NutritionLogResponse])
async def list_nutrition_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    meal_type: Optional[str] = Query(None),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all nutrition logs for the authenticated user."""
    query = db.query(models.NutritionLog).filter(models.NutritionLog.user_id == current_user.id)
    if meal_type:
        query = query.filter(models.NutritionLog.meal_type == meal_type)
    return query.order_by(models.NutritionLog.log_date.desc()).offset(skip).limit(limit).all()

@nutrition.get("/summary", response_model=dict)
async def daily_nutrition_summary(
    date: Optional[datetime] = Query(None, description="Date in ISO format; defaults to today"),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get total calories, protein, carbs, and fat for a given day."""
    target_date = date.date() if date else datetime.now(timezone.utc).date()
    logs = db.query(models.NutritionLog).filter(
        models.NutritionLog.user_id == current_user.id,
        cast(models.NutritionLog.log_date, Date) == target_date
    ).all()
    return {
        "date": str(target_date),
        "total_calories": round(sum(l.calories or 0 for l in logs), 2),
        "total_protein_g": round(sum(l.protein_g or 0 for l in logs), 2),
        "total_carbs_g": round(sum(l.carbs_g or 0 for l in logs), 2),
        "total_fat_g": round(sum(l.fat_g or 0 for l in logs), 2),
        "total_water_ml": round(sum(l.water_ml or 0 for l in logs), 2),
        "meals_logged": len(logs),
    }

@nutrition.get("/{log_id}", response_model=schemas.NutritionLogResponse)
async def get_nutrition_log(
    log_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific nutrition log by ID."""
    log = db.query(models.NutritionLog).filter(
        models.NutritionLog.id == log_id,
        models.NutritionLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition log not found")
    return log

@nutrition.put("/{log_id}", response_model=schemas.NutritionLogResponse)
async def update_nutrition_log(
    log_id: int,
    updates: schemas.NutritionLogUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a nutrition log entry."""
    log = db.query(models.NutritionLog).filter(
        models.NutritionLog.id == log_id,
        models.NutritionLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition log not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(log, field, value)
    db.commit()
    db.refresh(log)
    return log

@nutrition.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_nutrition_log(
    log_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a nutrition log entry."""
    log = db.query(models.NutritionLog).filter(
        models.NutritionLog.id == log_id,
        models.NutritionLog.user_id == current_user.id
    ).first()
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nutrition log not found")
    db.delete(log)
    db.commit()


progress = APIRouter(prefix="/progress", tags=["Progress Tracking"])

@progress.post("/", response_model=schemas.ProgressEntryResponse, status_code=status.HTTP_201_CREATED)
async def record_progress(
    entry_in: schemas.ProgressEntryCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Record a new body measurement / progress entry."""
    entry = models.ProgressEntry(user_id=current_user.id, **entry_in.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@progress.get("/", response_model=List[schemas.ProgressEntryResponse])
async def list_progress(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all progress entries for the authenticated user, newest first."""
    return (
        db.query(models.ProgressEntry)
        .filter(models.ProgressEntry.user_id == current_user.id)
        .order_by(models.ProgressEntry.recorded_at.desc())
        .offset(skip).limit(limit).all()
    )

@progress.get("/latest", response_model=schemas.ProgressEntryResponse)
async def get_latest_progress(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the most recent progress entry."""
    entry = (
        db.query(models.ProgressEntry)
        .filter(models.ProgressEntry.user_id == current_user.id)
        .order_by(models.ProgressEntry.recorded_at.desc())
        .first()
    )
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No progress entries found")
    return entry

@progress.get("/{entry_id}", response_model=schemas.ProgressEntryResponse)
async def get_progress_entry(
    entry_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific progress entry by ID."""
    entry = db.query(models.ProgressEntry).filter(
        models.ProgressEntry.id == entry_id,
        models.ProgressEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress entry not found")
    return entry

@progress.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_progress_entry(
    entry_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a progress entry."""
    entry = db.query(models.ProgressEntry).filter(
        models.ProgressEntry.id == entry_id,
        models.ProgressEntry.user_id == current_user.id
    ).first()
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress entry not found")
    db.delete(entry)
    db.commit()

goals = APIRouter(prefix="/goals", tags=["Goals"])

@goals.post("/", response_model=schemas.GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    goal_in: schemas.GoalCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new fitness goal."""
    goal = models.Goal(user_id=current_user.id, **goal_in.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal

@goals.get("/", response_model=List[schemas.GoalResponse])
async def list_goals(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_achieved: Optional[bool] = Query(None),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all goals for the authenticated user."""
    query = db.query(models.Goal).filter(models.Goal.user_id == current_user.id)
    if is_achieved is not None:
        query = query.filter(models.Goal.is_achieved == is_achieved)
    return query.order_by(models.Goal.created_at.desc()).offset(skip).limit(limit).all()

@goals.get("/{goal_id}", response_model=schemas.GoalResponse)
async def get_goal(
    goal_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal by ID."""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal

@goals.put("/{goal_id}", response_model=schemas.GoalResponse)
async def update_goal(
    goal_id: int,
    updates: schemas.GoalUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a fitness goal."""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal

@goals.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a fitness goal."""
    goal = db.query(models.Goal).filter(
        models.Goal.id == goal_id,
        models.Goal.user_id == current_user.id
    ).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    db.delete(goal)
    db.commit()

admin = APIRouter(prefix="/admin", tags=["Admin"])

@admin.get("/users", response_model=List[schemas.UserResponse])
async def list_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    """[Admin] List all registered users."""
    return db.query(models.User).offset(skip).limit(limit).all()

@admin.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    admin_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    """[Admin] Delete a user account."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()

@admin.patch("/users/{user_id}/deactivate", response_model=schemas.UserResponse)
async def deactivate_user(
    user_id: int,
    admin_user: models.User = Depends(auth.get_admin_user),
    db: Session = Depends(get_db)
):
    """[Admin] Deactivate a user account."""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
