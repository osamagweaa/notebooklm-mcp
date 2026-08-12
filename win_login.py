"""Windows-safe wrapper for the NotebookLM CLI.

Why this exists
---------------
`notebooklm/notebooklm_cli.py` forces the selector event loop at import time
on Windows:

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

That works around an unrelated IOCP hang, but a SelectorEventLoop cannot spawn
subprocesses on Windows, so `notebooklm login` always dies with
NotImplementedError when Playwright tries to launch the browser.

The import order below is the whole fix: import the CLI module first (letting it
set the selector policy), then put the Proactor policy back before running any
command. Setting the policy *before* the import does nothing — the import
silently overwrites it.

Usage:
    uv run python win_login.py            # runs `notebooklm login`
    uv run python win_login.py list       # any other CLI command
"""

import asyncio
import sys

from notebooklm import notebooklm_cli

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    print(f"[win_login] policy: {type(asyncio.get_event_loop_policy()).__name__}")

sys.argv = ["notebooklm"] + (sys.argv[1:] or ["login"])

notebooklm_cli.main()
