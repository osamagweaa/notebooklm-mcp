"""Windows-safe wrapper for the NotebookLM CLI.

On some Windows setups the asyncio event loop Playwright receives is a
SelectorEventLoop, which cannot spawn subprocesses and makes
`notebooklm login` crash with NotImplementedError. Forcing the Proactor
policy before Playwright starts avoids that.

Usage:
    uv run python win_login.py            # runs `notebooklm login`
    uv run python win_login.py list       # any other CLI command
"""

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

sys.argv = ["notebooklm"] + (sys.argv[1:] or ["login"])

from notebooklm.notebooklm_cli import main

main()
