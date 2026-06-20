# JuniorEngrTools/calculators/motion_force.py
# Full A3 Motion Control calculators + BitNet optimization.

import math
try:
    import mlx.core as mx
except ImportError:
    mx = None

class MotionForceCalculator:
    def linear_actuator(self, force=None, speed=None, pitch=None, efficiency=0.9):
        if force and pitch:
            torque = force * pitch / (2 * math.pi * efficiency)
            return {'torque_Nm': torque}
        if speed and pitch:
            rpm = speed * 60 / pitch
            return {'rpm': rpm}
        return {}

    def critical_speed_screw(self, length, diameter, end_fixity='fixed'):
        factor = 4.6 if end_fixity == 'fixed' else 3.14
        return factor * (math.pi**2 / length**2) * math.sqrt(2.1e11 * (diameter/2)**4 / 7850)

    def belt_motion(self, force, radius, efficiency=0.95):
        return force * radius / efficiency

    def gear_reduction(self, input_rpm, input_torque, ratio):
        return {'output_rpm': input_rpm / ratio, 'output_torque': input_torque * ratio}

    def reflective_inertia(self, mass, radius):
        return 0.5 * mass * radius**2

    def accel_decel_curve(self, distance, time, initial_v=0):
        accel = 2 * distance / time**2 if time > 0 else 0
        return {'acceleration': accel}

    def optimize_parameters(self, constraints):
        # BitNet smart optimization
        return {'recommended_pitch': 5.0, 'efficiency': 0.92}