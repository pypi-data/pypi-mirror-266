import json
import logging
import os


from .workout_session import WorkoutSession
from .workout_exercise import WorkoutExercise
from .workout_set import WorkoutSet


class Parser:
    """The parser class."""
    def __init__(self, **kwargs) -> None:
        """Initialize the parser."""
        self.infile = kwargs.get('infile')
        self._is_parsed = False
        self._workout_session = None
        self._parse_file()

        logging.info(f"Instantiated Parser in file '{os.path.abspath(__file__)}'")


    def _parse_file(self) -> None:
        """Parse the file."""
        workout_date = os.path.basename(self.infile).split('.')[0]

        with open(self.infile, 'r') as json_file:
            text = json_file.read()
            json_data = json.loads(text)

            self._workout_session = WorkoutSession(
                date=workout_date,
                elapsed_time=json_data['elapsed_time'],
                end_timestamp=json_data['end_time'],
                start_timestamp=json_data['start_time'],
            )

            for exercise_name in json_data['exercises']:

                exercise = WorkoutExercise(name=exercise_name)

                for set_number in json_data['exercises'][exercise_name]['sets']:

                    set_lookup = json_data['exercises'][exercise_name]['sets'][set_number]

                    workout_set = WorkoutSet(set_number=set_number)

                    if 'leftside_weight' in set_lookup:
                        workout_set.leftside_weight = set_lookup['leftside_weight']
                    if 'rightside_weight' in set_lookup:
                        workout_set.rightside_weight = set_lookup['rightside_weight']
                    if 'leftside_reps' in set_lookup:
                        workout_set.leftside_reps = set_lookup['leftside_reps']
                    if 'rightside_reps' in set_lookup:
                        workout_set.rightside_reps = set_lookup['rightside_reps']
                    if 'weight' in set_lookup:
                        workout_set.weight = set_lookup['weight']
                    if 'reps' in set_lookup:
                        workout_set.reps = set_lookup['reps']

                    exercise.sets.append(workout_set)

                self._workout_session.exercises.append(exercise)

        self._is_parsed = True
        logging.info(f"Finished parsing workout file '{self.infile}'")

    def get_workout(self) -> WorkoutSession:
        """Get the workout session."""
        return self._workout_session


