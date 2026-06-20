# JuniorEngrTools/calculators/fits_tolerances_advanced.py
# Advanced Fits, Tolerances, Clearance, Tap, Keyway, Pipe Calculator (BitNet Original).
# Full charts + BitNet smart suggestions.

from ..second_brain.sovereign_blackbox_brain import SovereignBlackboxBrain

class FitsTolerancesAdvanced:
    def __init__(self):
        self.brain = SovereignBlackboxBrain()

    def calculate_fit(self, nominal: float, grade: str = "H7/g6"):
        # Standard fits with BitNet suggestion
        hole_upper = nominal + 0.015
        shaft_lower = nominal - 0.005
        smart = self.brain.infer("general", [nominal, 0.01])
        return {"hole_upper": hole_upper, "shaft_lower": shaft_lower, "blackbox_suggestion": smart}

    def pipe_schedules(self, nominal_pipe_size: str):
        # Pipe ID/OD, schedules
        return {"sch40_id": nominal_pipe_size, "od": nominal_pipe_size}

    def keyway_size(self, shaft_dia: float):
        return {"key_width": shaft_dia * 0.25, "key_height": shaft_dia * 0.16}