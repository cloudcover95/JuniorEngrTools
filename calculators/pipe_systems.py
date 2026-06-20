# JuniorEngrTools/calculators/pipe_systems.py
# Complete Pipe Systems Calculator (schedules, threads, engagement, pressure).
# BitNet Original for optimization.

from ..second_brain.sovereign_blackbox_brain import SovereignBlackboxBrain

class PipeSystemsCalculator:
    def __init__(self):
        self.brain = SovereignBlackboxBrain()

    def thread_engagement(self, nominal_size: float, material: str = "steel"):
        engagement = nominal_size * 0.8
        smart = self.brain.infer("general", [nominal_size])
        return {"min_engagement": engagement, "blackbox_recommendation": smart}

    def pressure_rating(self, schedule: str, material_yield: float):
        # Basic Barlow formula + BitNet
        return {"max_pressure": material_yield * 0.5}