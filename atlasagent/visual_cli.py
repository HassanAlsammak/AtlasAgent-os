"""Local-only visual agent CLI. Every proposed action needs human approval."""
from __future__ import annotations
import argparse
from .desktop import DesktopAdapter
from .visual_agent import run_visual_session, suggest_action


def main():
    parser = argparse.ArgumentParser(description="AtlasAgent visual desktop assistant")
    parser.add_argument("--goal", required=True, help="Desktop task; avoid secrets")
    parser.add_argument("--max-steps", type=int, default=10)
    args = parser.parse_args()
    adapter = DesktopAdapter()
    print("WARNING: Screenshots are sent to your configured vision API.")
    print("Close sensitive windows. Move pointer to top-left to abort.")
    if input("Consent to screenshot upload? Type YES: ").strip() != "YES":
        print("Cancelled")
        return

    def approve(decision):
        details = f"Proposed: {decision.action}; reason: {decision.reason}"
        if decision.action == "click":
            details += f"; coordinates: {decision.x},{decision.y}"
        elif decision.action == "type":
            details += f"; text: {decision.text!r}"
        elif decision.action == "scroll":
            details += f"; direction: {decision.direction}"
        print(details)
        return input("Approve this ONE action? Type YES: ").strip() == "YES"

    try:
        for event in run_visual_session(args.goal, adapter, suggest_action,
                                        approve, max_steps=args.max_steps):
            print(event)
    except KeyboardInterrupt:
        print("Stopped by user")
    except Exception as exc:
        print(f"Stopped after error ({type(exc).__name__}): {exc}")


if __name__ == "__main__":
    main()
