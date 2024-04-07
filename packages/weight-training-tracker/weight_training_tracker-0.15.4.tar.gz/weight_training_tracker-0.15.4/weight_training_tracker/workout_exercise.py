import pydantic

from typing import List, Optional

from .workout_set import WorkoutSet

class WorkoutExercise(pydantic.BaseModel):
    """The exercise model."""
    name: str
    sets: Optional[List[WorkoutSet]] = []
