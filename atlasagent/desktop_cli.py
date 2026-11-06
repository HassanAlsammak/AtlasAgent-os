"""Interactive desktop controller: explicit human consent for every mutation."""
from __future__ import annotations
import argparse

from .computer import ComputerSession, ComputerStep
from .desktop import DesktopAdapter

def main() -> None:
    parser = argparse.ArgumentParser(description="AtlasAgent OS local desktop control")
    parser.add_argument("--max-steps", type=int, default=20)
    args = parser.parse_args()
    session = ComputerSession(DesktopAdapter(), max_steps=args.max_steps)
    print("AtlasAgent Desktop (local only). Move mouse to top-left to trigger PyAutoGUI failsafe.")
    print("Commands: observe | click X,Y | type TEXT | scroll up/down | quit")
    while True:
        try:
            line = input("atlas> ").strip()
            if line in ("quit", "exit"):
                break
            if line == "observe":
                step = ComputerStep("observe")
            elif line.startswith("click "):
                step = ComputerStep("click", {"target": line[6:].strip()})
            elif line.startswith("type "):
                step = ComputerStep("type", {"text": line[5:]})
            elif line.startswith("scroll "):
                step = ComputerStep("scroll", {"direction": line[7:].strip()})
            else:
                print("Unknown command")
                continue
            token = session.request(step)
            if token is not None:
                print(f"Requested action: {step.action}; args: {dict(step.arguments)!r}")
                if input("Approve this one action? Type YES: ").strip() != "YES":
                    session.reject(token)
                    print("Rejected")
                    continue
                session.approve(token)
            print(session.execute(step, approval_token=token))
        except (ValueError, PermissionError, RuntimeError) as exc:
            print(f"Error: {exc}")
        except KeyboardInterrupt:
            print("\nStopped")
            break

if __name__ == "__main__":
    main()
