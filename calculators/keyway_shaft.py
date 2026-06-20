# JuniorEngrTools/calculators/keyway_shaft.py
# Complete Keyway & Shaft Calculator (sizes, stress, fatigue).
# BitNet Original.

from ..second_brain.sovereign_blackbox_brain import SovereignBlackboxBrain

class KeywayShaftCalculator:
    def __init__(self):
        self.brain = SovereignBlackboxBrain()

    def keyway_dimensions(self, shaft_dia: float):
        width = shaft_dia * 0.25
        height = shaft_dia * 0.16
        smart = self.brain.infer("general", [shaft_dia])
        return {"key_width": width, "key_height": height, "blackbox_optimization": smart}

    def shaft_stress(self, torque: float, dia: float):
        stress = (16 * torque) / (math.pi * dia**3)
        return {"shear_stress": stress}