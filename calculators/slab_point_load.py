"""Crude slab screen. ACI 360 is more than P/h^2."""

def wheel(h_in: float, p_lb: float, fc_psi: float = 4000.0) -> dict:
    fr = 7.5 * (fc_psi**0.5)
    sig = (3.0 * p_lb) / (2.0 * h_in * h_in) if h_in else float("inf")
    return {
        "fr_psi": round(fr, 1),
        "sigma_approx_psi": round(sig, 1),
        "ratio_fr_over_sigma": round(fr / sig, 2) if sig else None,
        "h2_vs_4in": round((h_in / 4.0) ** 2, 2),
        "pe_stamp": False,
    }
