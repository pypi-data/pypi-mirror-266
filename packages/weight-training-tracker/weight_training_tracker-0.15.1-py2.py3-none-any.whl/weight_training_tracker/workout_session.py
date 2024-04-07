import pydantic

from typing import List, Optional

from .workout_exercise import WorkoutExercise

class WorkoutSession(pydantic.BaseModel):
    """The workout session model."""
    date: str
    elapsed_time: str
    end_timestamp: str
    start_timestamp: str
    exercises: Optional[List[WorkoutExercise]]
