import pydantic


from typing import Optional


class WorkoutSet(pydantic.BaseModel):
    """The set model."""
    set_number: Optional[int]
    leftside_weight: Optional[int]
    rightside_weight: Optional[int]
    leftside_reps: Optional[int]
    rightside_reps: Optional[int]
    weight: Optional[int]
    reps: Optional[int]
