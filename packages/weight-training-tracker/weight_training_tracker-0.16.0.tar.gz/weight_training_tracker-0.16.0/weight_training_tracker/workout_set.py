import pydantic

from typing import Optional


class WorkoutSet(pydantic.BaseModel):
    """The set model."""
    set_number: Optional[int] = None
    leftside_weight: Optional[int] = None
    rightside_weight: Optional[int] = None
    leftside_reps: Optional[int] = None
    rightside_reps: Optional[int] = None
    weight: Optional[int] = None
    reps: Optional[int] = None
