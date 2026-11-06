"""Offline demo. No actual computer or browser is controlled."""
from atlasagent.computer import ComputerSession, ComputerStep, MockComputer

session = ComputerSession(MockComputer())
print(session.execute(ComputerStep("observe")))
step = ComputerStep("click", {"target": "Continue"})
token = session.request(step)
answer = input("Approve click on Continue? Type YES: ")
if answer == "YES":
    session.approve(token)
    print(session.execute(step, approval_token=token))
else:
    session.reject(token)
    print("Rejected")
print(session.audit_json())
