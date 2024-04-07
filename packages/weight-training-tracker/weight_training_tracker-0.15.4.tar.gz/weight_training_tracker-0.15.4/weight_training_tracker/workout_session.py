import pydantic

from typing import List, Optional
from datetime import datetime

from .workout_exercise import WorkoutExercise

class WorkoutSession(pydantic.BaseModel):
    """The workout session model."""
    date: Optional[str]
    elapsed_time: Optional[str]
    end_timestamp: Optional[datetime]
    start_timestamp: Optional[datetime]
    exercises: Optional[List[WorkoutExercise]] = []
