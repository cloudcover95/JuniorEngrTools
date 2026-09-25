"""Simple-span mid-point screen. I and S must be real section values."""
E_STEEL = 29_000_000.0


def hung(span_ft: float, p_lb: float, s_in3: float, i_in4: float, fb_psi: float = 21600.0) -> dict:
    L = span_ft * 12.0
    m_inlb = p_lb * L / 4.0
    fb = m_inlb / s_in3 if s_in3 else float("inf")
    delta = (p_lb * L**3) / (48.0 * E_STEEL * i_in4) if i_in4 else float("inf")
    lim = L / 360.0
    return {
        "m_ftlb": round(m_inlb / 12.0, 1),
        "fb_psi": round(fb, 1),
        "delta_in": round(delta, 3),
        "delta_allow_L360_in": round(lim, 3),
        "ok_stress": fb <= fb_psi,
        "ok_defl": delta <= lim,
        "pe_stamp": False,
        "header_if": p_lb >= 500,
    }
