"""Standalone NotebookLM login for Windows.

Bypasses Playwright's sync API entirely: builds a ProactorEventLoop by
hand and drives the browser through the async API, so the
SelectorEventLoop / NotImplementedError crash cannot occur.

Usage:
    uv run python login_windows.py
"""

import asyncio
import subprocess
import sys

from notebooklm.paths import get_browser_profile_dir, get_storage_path


def ensure_chromium() -> None:
    try:
        result = subprocess.run(
            ["playwright", "install", "--dry-run", "chromium"],
            capture_output=True,
            text=True,
        )
        out = result.stdout.lower()
        if "chromium" in out and "will download" in out:
            print("Chromium not installed. Installing now (one-time)...")
            subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        print(f"Chromium pre-flight check failed ({e}); proceeding anyway.")


async def login() -> None:
    from playwright.async_api import async_playwright

    storage_path = get_storage_path()
    browser_profile = get_browser_profile_dir()
    storage_path.parent.mkdir(parents=True, exist_ok=True)
    browser_profile.mkdir(parents=True, exist_ok=True)

    print("Opening browser for Google login...")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=str(browser_profile),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--password-store=basic",
            ],
            ignore_default_args=["--enable-automation"],
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("https://notebooklm.google.com/")

        print("\nInstructions:")
        print("1. Complete the Google login in the browser window")
        print("2. Wait until you see the NotebookLM homepage")
        print("3. Press ENTER here to save and close\n")
        await asyncio.get_running_loop().run_in_executor(
            None, input, "[Press ENTER when logged in] "
        )

        current_url = page.url
        if "notebooklm.google.com" not in current_url:
            print(f"Warning: current URL is {current_url}; saving anyway.")

        await context.storage_state(path=str(storage_path))
        await context.close()

    print(f"\nAuthentication saved to: {storage_path}")


def main() -> None:
    ensure_chromium()
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
        print(f"[login_windows] event loop: {type(loop).__name__}")
        try:
            loop.run_until_complete(login())
        finally:
            loop.close()
    else:
        asyncio.run(login())


if __name__ == "__main__":
    main()
