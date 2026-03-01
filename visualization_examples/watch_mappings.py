"""Watch responses/*_mapping.md files and auto-regenerate + refresh Chrome on save.

Usage:
    python watch_mappings.py
"""
import sys
import os
import re
import glob
import time
import subprocess
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


RESPONSES_DIR = Path(__file__).parent / "responses"
PROJECT_ROOT = Path(__file__).parent


def derive_paths(mapping_md: str):
    """Given a *_mapping.md path, derive the script, response, and html paths."""
    basename = os.path.basename(mapping_md)
    m = re.match(r'^(\d+)', basename)
    if not m:
        raise ValueError(f"Cannot extract number prefix from: {basename}")

    num = m.group(1)
    scripts = glob.glob(str(PROJECT_ROOT / f"{num}_*.py"))
    if not scripts:
        raise FileNotFoundError(f"No script matching: {PROJECT_ROOT}/{num}_*.py")

    script_path = scripts[0]
    response_path = str(RESPONSES_DIR / f"{num}_prompt+response.txt")
    html_path = str(RESPONSES_DIR / f"{num}_mapping_viewer.html")

    return script_path, response_path, html_path


def regenerate_html(mapping_md: str):
    script_path, response_path, html_path = derive_paths(mapping_md)

    print(f"Regenerating: {os.path.basename(html_path)}")
    result = subprocess.run(
        [sys.executable, "visualizer.py", script_path, response_path,
         os.path.abspath(mapping_md), html_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
        return None
    print(result.stdout.strip())
    return html_path


def refresh_chrome_tab(html_path: str):
    """Connect to Chrome via remote debugging and reload the matching tab."""
    abs_html = os.path.abspath(html_path)
    file_url = f"file://{abs_html}"

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright not available - skipping browser refresh")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
        except Exception:
            print("Chrome not running with --remote-debugging-port=9222")
            print(f"Start Chrome with: DISPLAY=:0 google-chrome --remote-debugging-port=9222 --no-sandbox --user-data-dir=/tmp/chrome-debug &")
            print(f"Then open: {file_url}")
            return

        refreshed = False
        for context in browser.contexts:
            for page in context.pages:
                if abs_html in page.url or file_url in page.url:
                    page.reload()
                    refreshed = True
                    print(f"Refreshed tab: {page.url}")
                    break

        if not refreshed:
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()
            page.goto(file_url)
            print(f"Opened new tab: {file_url}")

        browser.close()


class MappingHandler(FileSystemEventHandler):
    def __init__(self):
        self._last_triggered = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if not (path.name.endswith("_mapping.md") and path.parent == RESPONSES_DIR):
            return

        # Debounce: editors often fire multiple events on save
        now = time.time()
        if now - self._last_triggered.get(str(path), 0) < 1.0:
            return
        self._last_triggered[str(path)] = now

        print(f"\n[{time.strftime('%H:%M:%S')}] Detected save: {path.name}")
        html_path = regenerate_html(str(path))
        if html_path:
            refresh_chrome_tab(html_path)


if __name__ == "__main__":
    handler = MappingHandler()
    observer = Observer()
    observer.schedule(handler, str(RESPONSES_DIR), recursive=False)
    observer.start()

    print(f"Watching {RESPONSES_DIR} for *_mapping.md changes...")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
