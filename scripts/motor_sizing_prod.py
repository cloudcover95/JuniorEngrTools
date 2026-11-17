#!/usr/bin/env python3
"""motor_sizing_prod.py - shaft power, torque, speed and gear-reduction screening CLI.

Stdlib only, offline. No network, no sockets, no servers.
JuniorEngrTools / JuniorCloud LLC. Additive tool; screening estimates only.

Relations:
    P[W] = T[N*m] * omega[rad/s],  omega = 2*pi*rpm/60
    Through a reduction of ratio R and efficiency eta:
        T_out = T_in * R * eta,  rpm_out = rpm_in / R
"""
import argparse
import json
import math
import sys

HP_W = 745.69987158227


def power_w(torque_nm, rpm):
    return torque_nm * 2.0 * math.pi * rpm / 60.0


def torque_nm(power, rpm):
    if rpm <= 0:
        raise SystemExit("rpm must be > 0")
    return power * 60.0 / (2.0 * math.pi * rpm)


def reduce_drive(t_in, rpm_in, ratio, eta):
    if ratio <= 0:
        raise SystemExit("ratio must be > 0")
    if not 0 < eta <= 1:
        raise SystemExit("efficiency must be in (0, 1]")
    t_out = t_in * ratio * eta
    rpm_out = rpm_in / ratio
    return {"torque_out_Nm": t_out, "rpm_out": rpm_out,
            "power_out_W": power_w(t_out, rpm_out),
            "power_in_W": power_w(t_in, rpm_in), "ratio": ratio, "efficiency": eta}


def required_motor(load_torque, load_rpm, ratio, eta, service_factor):
    """Motor power and torque needed to drive a load through a reduction."""
    p_load = power_w(load_torque, load_rpm)
    p_motor = p_load / eta * service_factor
    motor_rpm = load_rpm * ratio
    return {"load_power_W": p_load, "motor_power_W": p_motor,
            "motor_power_hp": p_motor / HP_W, "motor_rpm": motor_rpm,
            "motor_torque_Nm": torque_nm(p_motor, motor_rpm)}


def build_parser():
    p = argparse.ArgumentParser(
        description="Motor power/torque/speed and gear-reduction screening calculator.")
    p.add_argument("--json", action="store_true", help="emit JSON instead of text")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("power", help="power from torque (N*m) and rpm")
    a.add_argument("--torque", type=float, required=True)
    a.add_argument("--rpm", type=float, required=True)
    b = sub.add_parser("torque", help="torque from power (W) and rpm")
    b.add_argument("--power", type=float, required=True)
    b.add_argument("--rpm", type=float, required=True)
    c = sub.add_parser("reduce", help="output of a gear reduction")
    c.add_argument("--torque", type=float, required=True)
    c.add_argument("--rpm", type=float, required=True)
    c.add_argument("--ratio", type=float, required=True)
    c.add_argument("--eta", type=float, default=0.9)
    d = sub.add_parser("size", help="motor needed for a load through a reduction")
    d.add_argument("--load-torque", type=float, required=True)
    d.add_argument("--load-rpm", type=float, required=True)
    d.add_argument("--ratio", type=float, default=1.0)
    d.add_argument("--eta", type=float, default=0.9)
    d.add_argument("--service-factor", type=float, default=1.25)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.cmd == "power":
        w = power_w(args.torque, args.rpm)
        out = {"power_W": w, "power_hp": w / HP_W}
    elif args.cmd == "torque":
        out = {"torque_Nm": torque_nm(args.power, args.rpm)}
    elif args.cmd == "reduce":
        out = reduce_drive(args.torque, args.rpm, args.ratio, args.eta)
    else:
        out = required_motor(args.load_torque, args.load_rpm, args.ratio,
                             args.eta, args.service_factor)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        for k, v in out.items():
            print("%-16s %.6g" % (k, v))
    return 0


if __name__ == "__main__":
    sys.exit(main())
