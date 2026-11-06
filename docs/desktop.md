# Real desktop control — experimental

This is an **interactive local controller**, not an autonomous AI agent. It can click screen coordinates, type ASCII/keyboard text supported by PyAutoGUI, scroll, and report desktop size/pointer location. It does not understand screenshots, find UI elements, open apps by name, or plan tasks from natural language.

## Windows setup

```powershell
git clone https://github.com/HassanAlsammak/AtlasAgent-os.git
cd AtlasAgent-os
py -m venv .venv
.venv\Scripts\python -m pip install -e ".[desktop]"
.venv\Scripts\python -m atlasagent.desktop_cli
```

Try `observe`, then `click 500,300` to click a point inside your desktop. For each action, the program displays its arguments and requires you to type **YES**. Type `quit` to stop. Move the mouse to the top-left corner for PyAutoGUI's emergency failsafe. Use Ctrl+C to stop the CLI.

## Safety limitations

- Run only on your own machine, never on an untrusted or remote server.
- No remote API for desktop access. Do not wire this directly to the public web app.
- Typed text may include secrets: the CLI prints the proposed action and its contents before approval. Avoid entering passwords, recovery codes, or private information.
- Approval is per action, not a blanket authorization.
- No operating system sandbox or window allowlist. The operator must inspect each action.
- No screenshot recognition, model-driven planning, or automatic multi-step execution yet.
- GUI automation can be unreliable, especially across DPI scaling and multiple monitors.
