"""NEC-shaped estimate only. Art. 220 is a full calc."""
CU_LB_PER_FT_250 = 0.77  # rough 250 kcmil

def service(va: float, volts: float = 240.0, run_ft: float = 80.0) -> dict:
    amp = va / volts if volts else 0.0
    return {
        "amp_est": round(amp, 1),
        "cu_lb_est_two_wire": round(2 * run_ft * CU_LB_PER_FT_250, 1),
        "pe_stamp": False,
        "nec_220": False,
    }
