# Experimental visual desktop assistant

This is a **human-approved, local Windows desktop prototype**, not an
autonomous GitHub coding agent. It can capture screenshots, ask a
vision-capable chat-completions API to suggest a single action, and (after
explicit human approval) click, type, or scroll. It re-observes the screen
after each approved action. Errors stop the run; the user can restart it.

## Install

```powershell
python -m pip install -e ".[desktop]"
$env:ATLAS_VISION_API_KEY="your-api-key"
$env:ATLAS_VISION_MODEL="your-vision-capable-model"
python -m atlasagent.visual_cli --goal "Open the GitHub repository page" --max-steps 8
```

Optional: `ATLAS_VISION_ENDPOINT` (HTTPS OpenAI-compatible chat completions
endpoint; default `https://api.openai.com/v1/chat/completions`).
The configured model/provider must accept image_url data URLs and return JSON
in a text completion. Provider compatibility and cost are not guaranteed.

## Privacy and safety

- **Screenshots leave your computer** and are sent to the configured provider.
  Close password managers, private messages, confidential documents, and
  payment windows first. No screenshots are intentionally written to disk.
- The assistant is not a sandbox or an accessibility-grade UI locator. Wrong
  coordinates and hallucinated actions are possible.
- Each proposed action is printed and requires typing `YES`. Reject to stop.
- Move mouse to top-left for PyAutoGUI failsafe. Ctrl+C also stops the CLI.
- Never approve credential entry, payments, destructive actions, permission
  changes, or GitHub merges. The prompt asks the model not to propose them,
  but **prompt instructions are not a security boundary**.
- This prototype does not edit code, authenticate to GitHub, create pull
  requests, or recover autonomously from errors. Those need separate
  permissioned integrations and tests.
- It is not exposed via the web service. Run only on a trusted local machine.
