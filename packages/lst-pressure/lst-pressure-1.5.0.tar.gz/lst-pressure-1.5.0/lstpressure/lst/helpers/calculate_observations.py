from ...observation import Observation
from ...lstindex import LSTIntervalType as I
import math
from typing import Tuple
from perf import track_total_runtime


def convert_to_hours(x):
    try:
        result = round(
            (int(x.split(":")[0]) * 3600 + int(x.split(":")[1]) * 60) / 3600, 2
        )
        return result
    except:
        return None


@track_total_runtime
def calculate_constraints(row) -> list[I]:
    constraints = []
    if row["night_obs"] == "Yes":
        constraints.append(I.NIGHT)
    elif row["avoid_sunrise_sunset"] == "Yes":
        constraints.append(I.SUNRISE_SUNSET)
        constraints.append(I.SUNSET_SUNRISE)

    # If neither night_obs nor avoid_sunrise_sunset was selected
    if not constraints:
        constraints.append(I.ALL_DAY)

    return constraints


@track_total_runtime
def calculate_observations(dataFrame, observation_filter) -> Tuple[Observation]:
    try:
        # Convert durations to hours and round off
        dataFrame["duration_hours"] = dataFrame["simulated_duration"].apply(
            lambda x: round(0 if math.isnan(x) else x / 3600, 2)
        )

        # Convert LST start and end times to floating point hours
        dataFrame["lst_start_hours"] = dataFrame["lst_start"].apply(convert_to_hours)
        dataFrame["lst_end_hours"] = dataFrame["lst_start_end"].apply(convert_to_hours)

        # Build observations using list comprehension for efficiency
        observations = [
            Observation(
                id=row["id"],
                lst_window_start=row["lst_start_hours"],
                lst_window_end=row["lst_end_hours"],
                utc_constraints=constraint,
                duration=row["duration_hours"],
                proposal_id=row["proposal_id"],
            )
            for _, row in dataFrame.iterrows()
            if row["lst_end_hours"] - row["lst_start_hours"] > 0
            for constraint in calculate_constraints(row)
        ]

        return tuple(filter(observation_filter, observations))
    except Exception as e:
        raise ValueError("Error parsing CSV - please check input.", e)
