# JuniorEngrTools/calculators/structural.py
# Structural calculators with standards suggestion.

import math

class StructuralCalculator:
    def beam_max_stress(self, moment, section_modulus):
        return moment / section_modulus

    def moment_of_inertia_rect(self, b, h):
        return b * h**3 / 12

    def fits_and_tolerances(self, nominal, grade='H7/g6'):
        return {'hole_upper': nominal + 0.015, 'shaft_lower': nominal - 0.005}

    def suggest_standard(self, application, constraints):
        if 'pressure' in application.lower():
            return ['API 650', 'ASME BPVC Section VIII']
        return ['ISO 2768', 'Relevant ASTM spec']